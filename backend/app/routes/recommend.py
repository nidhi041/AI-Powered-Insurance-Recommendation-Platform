"""
recommend.py
------------
POST /recommend — accepts user profile, runs RAG, returns structured JSON.
"""

import logging
from fastapi import APIRouter, HTTPException, status

from app.models.policy import UserProfile, RecommendationResponse
from app.services.rag_service import (
    EmbeddingModelError,
    IndexedPolicyRetrievalError,
    VectorStoreError,
    query_documents,
)
from app.services.ai_agent import generate_recommendation
from app.services import document_store

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Recommend"])


def _build_rag_query(profile: UserProfile) -> str:
    """
    Construct a STRONG and targeted query using ALL profile fields
    with special focus on disease-specific clauses like waiting period.
    """
    conditions_str = ", ".join(profile.conditions)

    base_query = f"""
    Find relevant health insurance policies for the following user:

    Age: {profile.age}
    Lifestyle: {profile.lifestyle}
    Medical Conditions: {conditions_str}
    Income Range: {profile.income}
    City Type: {profile.city}

    Extract and focus on:
    - policy name
    - insurer name
    - premium cost
    - coverage amount
    - waiting period (especially for pre-existing diseases like {conditions_str})
    - inclusions and exclusions
    - copay and sub-limits
    - claim process (cashless or reimbursement)
    """

    # 🔥 CRITICAL BOOST (WAITING PERIOD FIX)
    boosted_query = f"""
    Health insurance for patients with {conditions_str}.

    IMPORTANT:
    - Find waiting period for pre-existing diseases like {conditions_str}
    - Extract exact waiting period value if mentioned anywhere
    - Look for terms like "pre-existing disease waiting period"

    {base_query}
    """

    return boosted_query


@router.post(
    "/recommend",
    response_model=RecommendationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get personalised insurance recommendations",
    description=(
        "Accepts a user profile, retrieves relevant policy chunks via RAG, "
        "and returns structured recommendations."
    ),
)
async def get_recommendation(profile: UserProfile) -> RecommendationResponse:
    """
    Generate AI-powered insurance recommendations grounded in uploaded policy documents.

    Flow:
    1. Build strong RAG query
    2. Retrieve documents
    3. Pass FULL context to AI
    4. Return structured response
    """

    logger.info("Recommendation request for user: %s", profile.full_name)

    # Step 1: Build query
    query = _build_rag_query(profile)
    logger.debug("RAG query: %s", query)

    # Step 2: Retrieve documents
    try:
        documents = query_documents(query)
    except EmbeddingModelError as exc:
        logger.exception("Policy embedding model failed during retrieval.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The policy embedding model is unavailable. Please try again later.",
        ) from exc
    except VectorStoreError as exc:
        logger.exception("ChromaDB policy retrieval failed.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Policy index storage is unavailable. Please try again later.",
        ) from exc
    except IndexedPolicyRetrievalError as exc:
        logger.exception("Indexed policy chunks could not be retrieved.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Policy chunks are indexed but could not be retrieved. "
                "Please ask an admin to check the policy index."
            ),
        ) from exc
    except Exception as exc:
        logger.exception("Unexpected policy retrieval failure.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Policy retrieval failed due to an internal backend error. Please try again later.",
        ) from exc

    if not documents:
        try:
            records = document_store.list_all_documents()
        except Exception as exc:
            logger.exception("Could not inspect policy indexing status.")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="The policy document status database is unavailable. Please try again later.",
            ) from exc

        processing_statuses = {
            record.get("processing_status")
            for record in records
        }
        if processing_statuses.intersection({"pending", "processing"}):
            detail = "Policy documents are still being indexed. Please try again shortly."
        elif "failed" in processing_statuses:
            detail = (
                "Policy document indexing failed. Ask an admin to check the upload "
                "status and upload the policy again."
            )
        elif "completed" in processing_statuses:
            detail = (
                "Uploaded policy records exist, but no indexed policy chunks are "
                "available. The knowledge base may need to be reindexed."
            )
        else:
            detail = "No indexed policy documents are available. Please ask an admin to upload PDFs first."

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
        )

    # 🔥 CRITICAL FIX: PASS MORE CONTEXT
    context_documents = documents  # instead of documents[:8]

    logger.info("Using %d document chunks for AI.", len(context_documents))

    # Step 3: Generate recommendation
    try:
        recommendation = generate_recommendation(
            user_profile=profile,
            documents=context_documents,
        )

    except ValueError as exc:
        logger.exception("AI agent returned an invalid structured response.")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The recommendation service returned an invalid response. Please try again.",
        ) from exc

    except Exception as exc:
        logger.exception("Recommendation generation failed.")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The recommendation service is temporarily unavailable. Please try again later.",
        ) from exc

    # Step 4: Final validation
    if not recommendation.comparison_table:
        logger.warning("Empty comparison table generated.")

    logger.info(
        "Recommendation generated successfully for %s — %d policies compared.",
        profile.full_name,
        len(recommendation.comparison_table),
    )

    return recommendation