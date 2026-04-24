"""
chat.py
-------
POST /chat — accepts a question + user profile, answers using RAG + LLM.
Session context is maintained server-side via an in-memory store (keyed by session_id).
The user's profile is stored on first call and reused automatically.
"""

import logging
import uuid
from typing import Dict, List

from fastapi import APIRouter, HTTPException, status

from app.models.policy import ChatRequest, ChatResponse, UserProfile
from app.services.rag_service import query_documents
from app.services.ai_agent import generate_chat_answer

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Chat"])


# ---------------------------------------------------------------------------
# In-memory session store  {session_id: {"profile": UserProfile, "history": [str]}}
# ---------------------------------------------------------------------------
# NOTE: For production, replace with Redis or a persistent store.

_session_store: Dict[str, Dict] = {}


def _get_or_create_session(session_id: str | None, profile: UserProfile) -> str:
    """Return existing session_id or create a new session, saving the profile."""
    if session_id and session_id in _session_store:
        # Update profile in case it changed
        _session_store[session_id]["profile"] = profile
        return session_id

    new_id = session_id or str(uuid.uuid4())
    _session_store[new_id] = {"profile": profile, "history": []}
    logger.info("Created new chat session: %s", new_id)
    return new_id


@router.post(
    "/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Ask an insurance question (session-aware)",
    description=(
        "Accepts a user question and profile. "
        "Retrieves relevant policy chunks via RAG and answers using the LLM. "
        "Maintains session memory — pass the returned session_id in subsequent calls."
    ),
)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Answer insurance questions grounded in uploaded policy documents.

    - Pass **session_id** from previous response to continue a session.
    - The user profile is stored server-side after the first call.
    - All answers use ONLY retrieved document content — no hallucination.
    """
    logger.info("Chat request — session=%s, question='%s'",
                request.session_id, request.question[:80])

    # Step 1: Manage session
    session_id = _get_or_create_session(request.session_id, request.user_profile)
    profile: UserProfile = _session_store[session_id]["profile"]

    # Step 2: Build a contextual query from the question + profile
    conditions_str = ", ".join(profile.conditions)
    enriched_query = (
        f"{request.question} "
        f"for a {profile.age}-year-old with {conditions_str} "
        f"in a {profile.city} city earning {profile.income}."
    )

    # Step 3: Retrieve relevant chunks
    documents: List[str] = query_documents(enriched_query)
    if not documents:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "No policy documents are available in the knowledge base. "
                "Please ask an admin to upload insurance policy PDFs first."
            ),
        )

    # Step 4: Generate answer
    try:
        answer = generate_chat_answer(
            question=request.question,
            user_profile=profile,
            documents=documents,
        )
    except Exception as exc:
        logger.exception("Chat answer generation failed for session=%s.", session_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate answer: {exc}",
        ) from exc

    # Step 5: Append to session history
    _session_store[session_id]["history"].append({
        "question": request.question,
        "answer": answer,
    })

    logger.info("Chat answer generated for session=%s.", session_id)
    return ChatResponse(answer=answer, session_id=session_id)
