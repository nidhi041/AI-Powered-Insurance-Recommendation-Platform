"""
upload.py
---------
POST /upload-policy — accepts a PDF, parses it, stores in ChromaDB.
"""

import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends

from app.models.policy import UploadResponse
from app.services.parser import extract_text_from_pdf, chunk_text
from app.services.rag_service import store_document
from app.routes.admin import _verify_admin

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Upload"])


@router.post(
    "/upload-policy",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload an insurance policy PDF",
    description=(
        "Accept a PDF file, extract its text, split into chunks, "
        "embed using OpenAI, and persist in ChromaDB."
    ),
)
async def upload_policy(
    file: UploadFile = File(...),
    _: str = Depends(_verify_admin)
) -> UploadResponse:
    """
    Upload and index a new insurance policy document.

    - **file**: PDF file (multipart/form-data)
    """
    # --- Validate file type ---
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only PDF files are accepted.",
        )

    logger.info("Received upload: '%s'", file.filename)

    try:
        file_bytes = await file.read()
        if not file_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty.",
            )

        # 1. Extract text from PDF
        text = extract_text_from_pdf(file_bytes)

        # 2. Split into chunks
        chunks = chunk_text(text)
        if not chunks:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="No text chunks could be created from the PDF.",
            )

        # 3. Store in ChromaDB
        document_id = store_document(chunks, source_name=file.filename)

        logger.info(
            "Successfully indexed '%s': %d chunks, doc_id=%s",
            file.filename, len(chunks), document_id,
        )

        return UploadResponse(
            message=f"Policy '{file.filename}' uploaded and indexed successfully.",
            chunks_stored=len(chunks),
            document_id=document_id,
        )

    except HTTPException:
        raise
    except ValueError as exc:
        logger.error("Parsing error for '%s': %s", file.filename, exc)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        logger.exception("Unexpected error during upload of '%s'.", file.filename)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process document: {exc}",
        ) from exc
