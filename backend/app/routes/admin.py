"""
admin.py
--------
Admin-protected endpoints:
  GET    /admin/policies          — list all indexed documents
  DELETE /admin/policy/{doc_id}   — delete a document from ChromaDB
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
    UpdateMetadataResponse
)
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
# Admin endpoints
# ---------------------------------------------------------------------------

@router.patch(
    "/admin/policy/{doc_id}",
    response_model=UpdateMetadataResponse,
    status_code=status.HTTP_200_OK,
    summary="Update policy document metadata (admin only)",
)
async def update_policy_metadata(
    doc_id: str,
    request: UpdateMetadataRequest,
    _: str = Depends(_verify_admin),
) -> UpdateMetadataResponse:
    """Update the source name for a policy document."""
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


# ---------------------------------------------------------------------------
# Admin endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/admin/policies",
    response_model=AdminPoliciesResponse,
    status_code=status.HTTP_200_OK,
    summary="List all indexed policy documents (admin only)",
    description="Returns a list of all documents stored in ChromaDB with chunk counts.",
)
async def list_policies(
    _: str = Depends(_verify_admin),
) -> AdminPoliciesResponse:
    """Get metadata for all uploaded and indexed policy documents."""
    logger.info("Admin: listing all policies.")
    docs = list_documents()
    return AdminPoliciesResponse(
        policies=[PolicyDocument(**d) for d in docs],
        total=len(docs),
    )


@router.delete(
    "/admin/policy/{doc_id}",
    response_model=DeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete a policy document (admin only)",
    description=(
        "Immediately removes all chunks for the given document_id from ChromaDB. "
        "The document will no longer be used in future recommendations or chats."
    ),
)
async def delete_policy(
    doc_id: str,
    _: str = Depends(_verify_admin),
) -> DeleteResponse:
    """Delete a policy document from the vector store by its document ID."""
    logger.info("Admin: deleting document '%s'.", doc_id)

    success = delete_document(doc_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No document found with id '{doc_id}'.",
        )

    return DeleteResponse(
        message=f"Document '{doc_id}' and all its chunks have been deleted.",
        deleted_id=doc_id,
    )
