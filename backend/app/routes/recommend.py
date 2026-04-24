"""
recommend.py
------------
POST /recommend — accepts user profile, runs RAG, returns structured JSON.
"""

import logging
from fastapi import APIRouter, HTTPException, status

from app.models.policy import UserProfile, RecommendationResponse
from app.services.rag_service import query_documents
from app.services.ai_agent import generate_recommendation

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
    documents = query_documents(query)

    if not documents:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No policy documents found. Please upload PDFs first.",
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
        logger.error("AI agent parse error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI agent returned invalid structured response: {exc}",
        ) from exc

    except Exception as exc:
        logger.exception("Unexpected error in AI agent.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Recommendation generation failed: {exc}",
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