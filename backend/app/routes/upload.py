"""
upload.py
---------
POST /upload-policy — accepts a PDF, validates it, stores metadata immediately,
then kicks off heavy processing (extraction + embedding + ChromaDB) as a
FastAPI BackgroundTask so the HTTP response returns in < 2 seconds.

Flow:
  1.  Validate MIME type and file extension                [< 1 ms]
  2.  Read bytes + validate size + compute SHA-256 hash   [< 5 ms]
  3.  Duplicate guard (same hash → return existing record) [< 5 ms]
  4.  Create document record in SQLite (status=pending)   [< 5 ms]
  5.  Return HTTP 202 Accepted with document_id            [< 50 ms total]
  6.  BackgroundTask: extract → chunk → embed → ChromaDB  [30 s – 3 min]
  7.  Update document record: status=completed/failed

The frontend can immediately show the document card with status "processing"
and poll GET /admin/documents/{id} for status updates.
"""

import asyncio
import hashlib
import logging
from functools import partial

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile, status

from app.config import settings
from app.models.policy import AsyncUploadResponse
from app.services import document_store
from app.services.parser import chunk_text, extract_text_from_pdf
from app.services.rag_service import store_document
from app.routes.admin import _verify_admin

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Upload"])


# ---------------------------------------------------------------------------
# Background processing worker
# ---------------------------------------------------------------------------

def _process_document_sync(doc_id: str, file_bytes: bytes, filename: str) -> None:
    """
    Heavy synchronous processing: PDF extraction → chunking → embedding → ChromaDB.

    This runs in a thread-pool executor so it doesn't block the event loop.
    The document record is updated to 'processing', then 'completed' or 'failed'.
    """
    logger.info("[bg] Starting processing for doc_id=%s filename='%s'", doc_id, filename)
    document_store.update_status(doc_id, "processing")

    try:
        # Step 1: Extract text from PDF
        text = extract_text_from_pdf(file_bytes)

        # Step 2: Chunk text
        chunks = chunk_text(text)
        if not chunks:
            raise ValueError("No text chunks could be created from the PDF.")

        # Step 3: Generate embeddings + store in ChromaDB
        store_document(chunks, source_name=filename, document_id=doc_id)

        # Step 4: Mark completed
        document_store.update_status(doc_id, "completed", chunk_count=len(chunks))
        logger.info(
            "[bg] Completed doc_id=%s: %d chunks indexed from '%s'",
            doc_id, len(chunks), filename,
        )

    except Exception as exc:  # noqa: BLE001
        error_msg = str(exc)
        logger.exception("[bg] Processing FAILED for doc_id=%s: %s", doc_id, error_msg)
        document_store.update_status(doc_id, "failed", error=error_msg)


# ---------------------------------------------------------------------------
# Upload endpoint
# ---------------------------------------------------------------------------

@router.post(
    "/upload-policy",
    response_model=AsyncUploadResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Upload an insurance policy PDF (async processing)",
    description=(
        "Accepts a PDF file. Returns immediately with a document_id and "
        "status='processing'. Heavy operations (text extraction, embedding, "
        "ChromaDB indexing) run in the background. Poll "
        "GET /admin/documents/{id} for status updates."
    ),
)
async def upload_policy(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    _: str = Depends(_verify_admin),
) -> AsyncUploadResponse:
    """
    Upload and asynchronously index a new insurance policy document.

    - **file**: PDF file (multipart/form-data)
    """

    # -----------------------------------------------------------------------
    # 1. Validate file extension
    # -----------------------------------------------------------------------
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only PDF files are accepted.",
        )

    logger.info("Received upload: '%s'", file.filename)

    # -----------------------------------------------------------------------
    # 2. Read bytes & validate
    # -----------------------------------------------------------------------
    try:
        file_bytes = await file.read()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read uploaded file: {exc}",
        ) from exc

    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    if len(file_bytes) > settings.MAX_PDF_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=(
                f"File too large. Maximum allowed size is "
                f"{settings.MAX_PDF_SIZE_BYTES // (1024 * 1024)} MB."
            ),
        )

    # -----------------------------------------------------------------------
    # 3. Compute SHA-256 hash for duplicate detection
    # -----------------------------------------------------------------------
    file_hash = hashlib.sha256(file_bytes).hexdigest()

    # -----------------------------------------------------------------------
    # 4. Duplicate guard
    # -----------------------------------------------------------------------
    existing = document_store.get_document_by_hash(file_hash)
    if existing:
        logger.info(
            "Duplicate upload detected for '%s' (hash=%s). Returning existing doc_id=%s",
            file.filename, file_hash, existing["id"],
        )
        return AsyncUploadResponse(
            document_id=existing["id"],
            filename=existing["original_filename"],
            status=existing["processing_status"],
            message=(
                f"This file was already uploaded. "
                f"Existing document id: {existing['id']}. "
                f"Status: {existing['processing_status']}."
            ),
            is_duplicate=True,
        )

    # -----------------------------------------------------------------------
    # 5. Create persistent metadata record (status = pending)
    #    This write happens BEFORE background processing, so even if the
    #    server restarts during indexing the record survives.
    # -----------------------------------------------------------------------
    safe_filename = file.filename.strip()
    doc_id = document_store.create_document_record(
        filename=safe_filename,
        original_filename=safe_filename,
        file_size_bytes=len(file_bytes),
        file_hash=file_hash,
    )

    if doc_id is None:
        # Extremely rare race condition — another request with same hash
        # inserted between our check and our insert.
        existing = document_store.get_document_by_hash(file_hash)
        if existing:
            return AsyncUploadResponse(
                document_id=existing["id"],
                filename=existing["original_filename"],
                status=existing["processing_status"],
                message="Duplicate file already being processed.",
                is_duplicate=True,
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create document record.",
        )

    # -----------------------------------------------------------------------
    # 6. Enqueue background processing
    #    file_bytes are already in memory — safe to pass to the background
    #    task (UploadFile is closed after the response is sent).
    # -----------------------------------------------------------------------
    background_tasks.add_task(
        _process_document_sync,
        doc_id,
        file_bytes,
        safe_filename,
    )

    logger.info(
        "Upload accepted for '%s' (doc_id=%s). Background processing queued.",
        safe_filename, doc_id,
    )

    # -----------------------------------------------------------------------
    # 7. Return immediately — < 1 second from upload completion
    # -----------------------------------------------------------------------
    return AsyncUploadResponse(
        document_id=doc_id,
        filename=safe_filename,
        status="pending",
        message=(
            f"Policy '{safe_filename}' received and queued for processing. "
            f"Poll GET /admin/documents/{doc_id} for status updates."
        ),
        is_duplicate=False,
    )
