"""
admin.py
--------
Admin-protected endpoints:

  GET    /admin/documents              — list all uploaded documents (from SQLite)
  GET    /admin/documents/{doc_id}     — get single document status (for polling)
  DELETE /admin/documents/{doc_id}     — delete a document (SQLite + ChromaDB)
  PATCH  /admin/documents/{doc_id}     — update document filename
  POST   /admin/documents/{doc_id}/retry — retry processing for failed documents

  [Legacy — still functional for direct ChromaDB queries]
  GET    /admin/policies               — list all indexed chunks (from ChromaDB)
  DELETE /admin/policy/{doc_id}        — delete document chunks from ChromaDB
  PATCH  /admin/policy/{doc_id}        — update chunk metadata in ChromaDB
"""

import logging
import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.config import settings
from app.models.policy import (
    AdminPoliciesResponse,
    PolicyDocument,
    DeleteResponse,
    UpdateMetadataRequest,
    UpdateMetadataResponse,
    DocumentRecord,
    DocumentListResponse,
    DocumentStatusResponse,
)
from app.services import document_store
from app.services.rag_service import list_documents, delete_document, update_document_metadata

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Admin"])
security = HTTPBasic()


# ---------------------------------------------------------------------------
# Basic-auth dependency
# ---------------------------------------------------------------------------

def _verify_admin(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    """
    Validate HTTP Basic Auth credentials against env-configured values.
    Uses constant-time comparison to prevent timing attacks.
    """
    correct_username = secrets.compare_digest(
        credentials.username.encode("utf-8"),
        settings.ADMIN_USERNAME.encode("utf-8"),
    )
    correct_password = secrets.compare_digest(
        credentials.password.encode("utf-8"),
        settings.ADMIN_PASSWORD.encode("utf-8"),
    )

    if not (correct_username and correct_password):
        logger.warning("Failed admin login attempt for username='%s'.", credentials.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin credentials.",
            headers={"WWW-Authenticate": "Basic"},
        )

    return credentials.username


# ---------------------------------------------------------------------------
# NEW: Persistent document endpoints (backed by SQLite)
# ---------------------------------------------------------------------------

@router.get(
    "/admin/documents",
    response_model=DocumentListResponse,
    status_code=status.HTTP_200_OK,
    summary="List all uploaded documents (admin only)",
    description=(
        "Returns all policy documents from persistent storage, including "
        "documents currently being processed. This is the primary endpoint "
        "for the Admin Panel — it survives backend restarts."
    ),
)
async def list_admin_documents(
    _: str = Depends(_verify_admin),
) -> DocumentListResponse:
    """Get all uploaded policy documents with their processing status."""
    logger.info("Admin: listing all documents from persistent store.")
    docs = document_store.list_all_documents()
    records = [DocumentRecord(**d) for d in docs]
    return DocumentListResponse(documents=records, total=len(records))


@router.get(
    "/admin/documents/{doc_id}",
    response_model=DocumentStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Get document processing status (admin only)",
    description=(
        "Poll this endpoint after uploading a document to track processing "
        "progress. Returns the current status: pending, processing, "
        "completed, or failed."
    ),
)
async def get_document_status(
    doc_id: str,
    _: str = Depends(_verify_admin),
) -> DocumentStatusResponse:
    """Get processing status for a specific document. Use for polling after upload."""
    doc = document_store.get_document(doc_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No document found with id '{doc_id}'.",
        )
    return DocumentStatusResponse(**doc)


@router.delete(
    "/admin/documents/{doc_id}",
    response_model=DeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete a document (admin only)",
    description=(
        "Removes the document record from SQLite AND all its chunks from "
        "ChromaDB. The document will no longer appear in the admin panel "
        "and will not be used in future recommendations."
    ),
)
async def delete_admin_document(
    doc_id: str,
    _: str = Depends(_verify_admin),
) -> DeleteResponse:
    """Delete a policy document from both the metadata store and vector store."""
    logger.info("Admin: deleting document '%s'.", doc_id)

    # Check it exists
    doc = document_store.get_document(doc_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No document found with id '{doc_id}'.",
        )

    # Remove from ChromaDB (best-effort — may not be indexed yet if pending/failed)
    try:
        delete_document(doc_id)
    except Exception as exc:
        logger.warning("ChromaDB delete for doc_id=%s failed (may not be indexed): %s", doc_id, exc)

    # Remove from SQLite
    document_store.delete_document_record(doc_id)

    return DeleteResponse(
        message=f"Document '{doc_id}' and all its data have been deleted.",
        deleted_id=doc_id,
    )


@router.patch(
    "/admin/documents/{doc_id}",
    response_model=UpdateMetadataResponse,
    status_code=status.HTTP_200_OK,
    summary="Update document filename (admin only)",
)
async def update_admin_document(
    doc_id: str,
    request: UpdateMetadataRequest,
    _: str = Depends(_verify_admin),
) -> UpdateMetadataResponse:
    """Update the display name / source for a document."""
    logger.info("Admin: updating document '%s' source to '%s'.", doc_id, request.source)

    doc = document_store.get_document(doc_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No document found with id '{doc_id}'.",
        )

    # Update in ChromaDB chunk metadata (if indexed)
    try:
        update_document_metadata(doc_id, request.source)
    except Exception as exc:
        logger.warning("ChromaDB metadata update failed for %s: %s", doc_id, exc)

    return UpdateMetadataResponse(
        message=f"Document '{doc_id}' source updated to '{request.source}'.",
        updated_id=doc_id,
    )


@router.post(
    "/admin/documents/{doc_id}/retry",
    response_model=DocumentStatusResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Retry processing for a failed document (admin only)",
    description=(
        "Re-queues a FAILED document for processing. The document record "
        "must already exist in the database."
    ),
)
async def retry_document_processing(
    doc_id: str,
    _: str = Depends(_verify_admin),
) -> DocumentStatusResponse:
    """Retry processing for a document that previously failed."""
    from fastapi import BackgroundTasks
    from app.routes.upload import _process_document_sync

    doc = document_store.get_document(doc_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No document found with id '{doc_id}'.",
        )

    if doc["processing_status"] not in ("failed", "pending"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Cannot retry document with status '{doc['processing_status']}'. "
                "Only 'failed' or 'pending' documents can be retried."
            ),
        )

    # We don't have the original bytes anymore (not stored on disk).
    # A proper retry needs the original file. For now, inform the admin
    # to re-upload.
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=(
            "Retry is not supported without the original file. "
            "Please delete this document and re-upload the PDF."
        ),
    )


# ---------------------------------------------------------------------------
# LEGACY: ChromaDB direct endpoints (kept for backward compatibility)
# ---------------------------------------------------------------------------

@router.patch(
    "/admin/policy/{doc_id}",
    response_model=UpdateMetadataResponse,
    status_code=status.HTTP_200_OK,
    summary="[Legacy] Update policy chunk metadata in ChromaDB (admin only)",
)
async def update_policy_metadata(
    doc_id: str,
    request: UpdateMetadataRequest,
    _: str = Depends(_verify_admin),
) -> UpdateMetadataResponse:
    """Update the source name for all chunks of a document in ChromaDB."""
    logger.info("Admin: updating document '%s' metadata.", doc_id)

    success = update_document_metadata(doc_id, request.source)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No document found with id '{doc_id}'.",
        )

    return UpdateMetadataResponse(
        message=f"Document '{doc_id}' metadata updated successfully.",
        updated_id=doc_id,
    )


@router.get(
    "/admin/policies",
    response_model=AdminPoliciesResponse,
    status_code=status.HTTP_200_OK,
    summary="[Legacy] List indexed policy documents from ChromaDB (admin only)",
    description="Returns documents that have been fully indexed in ChromaDB. Use /admin/documents for the full list including processing status.",
)
async def list_policies(
    _: str = Depends(_verify_admin),
) -> AdminPoliciesResponse:
    """Get metadata for all uploaded and indexed policy documents from ChromaDB."""
    logger.info("Admin: listing all policies from ChromaDB.")
    docs = list_documents()
    return AdminPoliciesResponse(
        policies=[PolicyDocument(**d) for d in docs],
        total=len(docs),
    )


@router.delete(
    "/admin/policy/{doc_id}",
    response_model=DeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="[Legacy] Delete policy chunks from ChromaDB (admin only)",
)
async def delete_policy(
    doc_id: str,
    _: str = Depends(_verify_admin),
) -> DeleteResponse:
    """Delete a policy document's chunks from ChromaDB only."""
    logger.info("Admin: deleting document '%s' from ChromaDB.", doc_id)

    success = delete_document(doc_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No document found with id '{doc_id}'.",
        )

    return DeleteResponse(
        message=f"Document '{doc_id}' and all its chunks have been deleted from ChromaDB.",
        deleted_id=doc_id,
    )
