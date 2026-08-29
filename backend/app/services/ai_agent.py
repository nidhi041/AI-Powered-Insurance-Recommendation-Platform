"""
ai_agent.py
-----------
Core AI logic using Groq (ChatGroq).

Features:
- Health insurance recommendations using uploaded policy documents
- Strict JSON output for recommendations
- Normal Markdown responses for chat
- Duplicate policy removal
- Required-field fallback handling
- Safe JSON parsing
- Groq model configurable through settings
"""

import json
import logging
from typing import List

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

from app.config import settings
from app.models.policy import (
    UserProfile,
    RecommendationResponse,
    PolicyComparison,
    CoverageDetails,
)

logger = logging.getLogger(__name__)


# ============================================================================
# LLM CONFIGURATION
# ============================================================================

# Current Groq model.
# You can override this through settings.GROQ_MODEL if your config supports it.
DEFAULT_GROQ_MODEL = "openai/gpt-oss-120b"


def _get_model_name() -> str:
    """
    Get the Groq model from application settings if available.
    Otherwise use the default working model.
    """

    model = getattr(settings, "GROQ_MODEL", None)

    if model and isinstance(model, str) and model.strip():
        return model.strip()

    return DEFAULT_GROQ_MODEL


def _get_recommendation_llm() -> ChatGroq:
    """
    LLM used for insurance recommendations.

    JSON response format is explicitly requested because the
    recommendation endpoint expects structured JSON.
    """

    return ChatGroq(
        model=_get_model_name(),
        temperature=0.2,
        groq_api_key=settings.GROQ_API_KEY,
        model_kwargs={
            "response_format": {
                "type": "json_object"
            }
        },
    )


def _get_chat_llm() -> ChatGroq:
    """
    LLM used for normal policy chat.

    No JSON response format because chat responses are Markdown.
    """

    return ChatGroq(
        model=_get_model_name(),
        temperature=0.2,
        groq_api_key=settings.GROQ_API_KEY,
    )


# ============================================================================
# SYSTEM PROMPTS
# ============================================================================

_RECOMMENDATION_SYSTEM_PROMPT = """
You are an expert health insurance advisor.

STRICT RULES:
- Return valid JSON only.
- Do NOT return Markdown.
- Do NOT return text outside the JSON object.
- ALL required fields must be present.
- Use ONLY information available in the provided policy documents.
- Never invent policy details.
- Never assume missing information.

OUTPUT FORMAT:

{
  "comparison_table": [
    {
      "policy_name": "",
      "insurer": "",
      "premium": "",
      "cover_amount": "",
      "waiting_period": "",
      "key_benefit": "",
      "suitability_score": ""
    }
  ],
  "coverage_details": {
    "inclusions": "",
    "exclusions": "",
    "sub_limits": "",
    "copay": "",
    "claim_type": ""
  },
  "why_this_policy": ""
}

COMPARISON TABLE RULES:
- Try to provide at least 2 DIFFERENT policies when the uploaded documents contain at least 2 different policies.
- NEVER duplicate the same policy.
- If only one policy exists in the uploaded documents, return only that policy.
- Do not create a fake second policy.
- Extract actual values from the documents.
- Do not change or fabricate premium or coverage values.

REQUIRED POLICY FIELDS:
- policy_name
- insurer
- premium
- cover_amount
- waiting_period
- key_benefit
- suitability_score

WAITING PERIOD:
- Pay special attention to waiting-period clauses.
- Look for:
  - waiting period
  - pre-existing disease waiting period
  - PED waiting period
  - specific disease waiting period
  - diabetes
  - hypertension
  - chronic conditions
- If a waiting period is present anywhere in the uploaded documents,
  include the actual information.
- Do not skip a waiting period simply because it appears in another section.
- If no waiting period information exists, use:
  "Not available in uploaded documents"

SUITABILITY SCORE:
Calculate the score based only on available information, considering:
- health condition match
- waiting period
- affordability
- coverage relevance

Do not invent numerical facts.

COVERAGE DETAILS:
The following fields are required:
- inclusions
- exclusions
- sub_limits
- copay
- claim_type

If information is unavailable:
"Not available in uploaded documents"

WHY THIS POLICY:
- Write approximately 150–250 words when enough information is available.
- Start with empathy.
- Mention:
  - user age
  - user condition
  - income level
- Explain why the waiting period matters for the user's condition.
- Use actual policy values from the documents.
- Do not invent information.

TONE:
- Professional
- Clear
- Human-friendly
- Easy to understand
""".strip()


_CHAT_SYSTEM_PROMPT = """
You are insureiq AI, a professional health insurance assistant.

Your goal is to answer questions using ONLY the provided uploaded policy
documents and the user's profile.

STRUCTURE RULES:
1. Use **Bold Headings** for different sections.
2. Use bullet points for lists.
3. Use `>` blockquotes only for short direct quotes from policy documents.
4. Keep answers clear and easy to skim.
5. If useful, end with a **Summary** section.

USER CONTEXT:
Use the user's profile when relevant:
- Name
- Age
- Conditions
- Lifestyle
- City
- Income

RAG RULES:
1. Answer ONLY using the provided DOCUMENTS.
2. Do not invent policy information.
3. Do not assume a policy benefit that isn't present in the documents.
4. If the answer isn't available in the documents, say:

"I couldn't find specific details about that in the uploaded policy documents."

5. If the user asks about waiting periods, specifically check the provided
documents for:
- waiting period
- pre-existing disease waiting period
- PED waiting period
- disease-specific waiting period
- condition-specific clauses

6. Keep answers professional and easy to understand.
""".strip()


# ============================================================================
# HELPERS
# ============================================================================

def _clean_json_response(raw: str) -> str:
    """
    Clean an LLM response before JSON parsing.

    Handles cases where the model accidentally returns:
    ```json
    {...}
    ```
    """

    if not raw:
        raise ValueError("AI returned an empty response")

    raw = raw.strip()

    if raw.startswith("```"):
        parts = raw.split("```")

        if len(parts) >= 2:
            raw = parts[1].strip()

            if raw.lower().startswith("json"):
                raw = raw[4:].strip()

    return raw


def _parse_json_response(raw: str) -> dict:
    """
    Safely parse JSON returned by the LLM.
    """

    cleaned = _clean_json_response(raw)

    try:
        data = json.loads(cleaned)

    except json.JSONDecodeError as exc:
        logger.error(
            "Invalid JSON returned by AI. Raw response: %s",
            cleaned,
        )

        raise ValueError(
            "AI did not return valid JSON"
        ) from exc

    if not isinstance(data, dict):
        raise ValueError(
            "AI returned JSON, but the response is not a JSON object"
        )

    return data


def _fallback(value: object) -> str:
    """
    Return a standard fallback value for missing information.
    """

    if value is None:
        return "Not available in uploaded documents"

    if isinstance(value, str) and not value.strip():
        return "Not available in uploaded documents"

    return str(value)


def _normalize_policy(item: dict) -> dict:
    """
    Ensure every policy contains all required fields.
    """

    if not isinstance(item, dict):
        item = {}

    return {
        "policy_name": _fallback(
            item.get("policy_name")
        ),
        "insurer": _fallback(
            item.get("insurer")
        ),
        "premium": _fallback(
            item.get("premium")
        ),
        "cover_amount": _fallback(
            item.get("cover_amount")
        ),
        "waiting_period": _fallback(
            item.get("waiting_period")
        ),
        "key_benefit": _fallback(
            item.get("key_benefit")
        ),
        "suitability_score": _fallback(
            item.get("suitability_score")
        ),
    }


def _remove_duplicate_policies(policies: List[dict]) -> List[dict]:
    """
    Remove duplicate policies by policy name.

    Comparison is case-insensitive and whitespace-insensitive.
    """

    unique = {}
    result = []

    for policy in policies:

        normalized = _normalize_policy(policy)

        name = normalized["policy_name"].strip().lower()

        if not name:
            name = "not available in uploaded documents"

        if name not in unique:
            unique[name] = True
            result.append(normalized)

    return result


def _normalize_coverage(coverage: object) -> dict:
    """
    Ensure all coverage fields exist.
    """

    if not isinstance(coverage, dict):
        coverage = {}

    return {
        "inclusions": _fallback(
            coverage.get("inclusions")
        ),
        "exclusions": _fallback(
            coverage.get("exclusions")
        ),
        "sub_limits": _fallback(
            coverage.get("sub_limits")
        ),
        "copay": _fallback(
            coverage.get("copay")
        ),
        "claim_type": _fallback(
            coverage.get("claim_type")
        ),
    }


def _build_documents_block(documents: List[str]) -> str:
    """
    Combine retrieved RAG documents into one prompt section.
    """

    if not documents:
        return "No policy documents were retrieved."

    cleaned_documents = []

    for index, document in enumerate(documents, start=1):

        if not document:
            continue

        cleaned_documents.append(
            f"DOCUMENT {index}:\n{document}"
        )

    if not cleaned_documents:
        return "No policy documents were retrieved."

    return "\n\n---\n\n".join(cleaned_documents)


# ============================================================================
# RECOMMENDATION
# ============================================================================

def generate_recommendation(
    user_profile: UserProfile,
    documents: List[str],
) -> RecommendationResponse:
    """
    Generate insurance policy recommendations.

    Uses:
    - User profile
    - Retrieved RAG policy documents
    - Groq LLM
    - Strict JSON response
    """

    if not settings.GROQ_API_KEY:
        raise ValueError(
            "GROQ_API_KEY is not configured."
        )

    if not documents:
        raise ValueError(
            "No policy documents were provided."
        )

    llm = _get_recommendation_llm()

    conditions_str = ", ".join(
        user_profile.conditions or []
    )

    docs_block = _build_documents_block(documents)

    human_message = f"""
USER PROFILE:

Age:
{user_profile.age}

Conditions:
{conditions_str}

Income:
{user_profile.income}

Lifestyle:
{user_profile.lifestyle}

City:
{user_profile.city}

--------------------------------------------------

UPLOADED POLICY DOCUMENTS:

{docs_block}

--------------------------------------------------

TASK:

Analyze the uploaded policy documents for this user.

Focus especially on:
- policy name
- insurer
- premium
- cover amount
- waiting period
- pre-existing disease waiting period
- disease-related clauses
- exclusions
- sub-limits
- co-pay
- claim type
- key benefits

Return ONLY the required JSON object.

Do not create policies that are not present in the documents.
"""

    messages = [
        SystemMessage(
            content=_RECOMMENDATION_SYSTEM_PROMPT
        ),
        HumanMessage(
            content=human_message
        ),
    ]

    try:
        response = llm.invoke(messages)

    except Exception as exc:
        logger.exception(
            "Groq recommendation generation failed."
        )

        raise RuntimeError(
            f"AI recommendation generation failed: {exc}"
        ) from exc

    raw = response.content

    if isinstance(raw, list):
        raw = "".join(
            str(part) for part in raw
        )

    raw = str(raw).strip()

    logger.info(
        "Received recommendation response from Groq."
    )

    # ------------------------------------------------------------------------
    # Parse JSON
    # ------------------------------------------------------------------------

    data = _parse_json_response(raw)

    # ------------------------------------------------------------------------
    # Comparison table
    # ------------------------------------------------------------------------

    comparison_data = data.get(
        "comparison_table",
        []
    )

    if not isinstance(comparison_data, list):
        comparison_data = []

    comparison_data = _remove_duplicate_policies(
        comparison_data
    )

    # ------------------------------------------------------------------------
    # Coverage details
    # ------------------------------------------------------------------------

    coverage_data = _normalize_coverage(
        data.get("coverage_details", {})
    )

    # ------------------------------------------------------------------------
    # Why this policy
    # ------------------------------------------------------------------------

    why_this_policy = _fallback(
        data.get("why_this_policy")
    )

    # ------------------------------------------------------------------------
    # Convert to Pydantic models
    # ------------------------------------------------------------------------

    try:

        comparison_table = [
            PolicyComparison(**policy)
            for policy in comparison_data
        ]

        coverage_details = CoverageDetails(
            **coverage_data
        )

        return RecommendationResponse(
            comparison_table=comparison_table,
            coverage_details=coverage_details,
            why_this_policy=why_this_policy,
        )

    except Exception as exc:

        logger.exception(
            "Failed to convert AI recommendation to Pydantic models."
        )

        raise ValueError(
            f"Invalid recommendation data returned by AI: {exc}"
        ) from exc


# ============================================================================
# CHAT
# ============================================================================

def generate_chat_answer(
    question: str,
    user_profile: UserProfile,
    documents: List[str],
) -> str:
    """
    Generate a conversational answer about uploaded insurance policies.

    Unlike recommendations, chat responses are normal Markdown.
    """

    if not settings.GROQ_API_KEY:
        raise ValueError(
            "GROQ_API_KEY is not configured."
        )

    if not question or not question.strip():
        raise ValueError(
            "Question cannot be empty."
        )

    if not documents:
        return (
            "I couldn't find specific details about that "
            "in the uploaded policy documents."
        )

    llm = _get_chat_llm()

    conditions_str = ", ".join(
        user_profile.conditions or []
    )

    docs_block = _build_documents_block(documents)

    human_message = f"""
USER PROFILE:

Name:
{user_profile.full_name}

Age:
{user_profile.age}

Conditions:
{conditions_str}

Income:
{user_profile.income}

Lifestyle:
{user_profile.lifestyle}

City:
{user_profile.city}

--------------------------------------------------

USER QUESTION:

{question}

--------------------------------------------------

UPLOADED POLICY DOCUMENTS:

{docs_block}

--------------------------------------------------

Answer the user's question using ONLY the uploaded documents.

If the requested information is not present in the documents, clearly say:

"I couldn't find specific details about that in the uploaded policy documents."
"""

    messages = [
        SystemMessage(
            content=_CHAT_SYSTEM_PROMPT
        ),
        HumanMessage(
            content=human_message
        ),
    ]

    try:

        response = llm.invoke(messages)

    except Exception as exc:

        logger.exception(
            "Groq chat generation failed."
        )

        raise RuntimeError(
            f"AI chat generation failed: {exc}"
        ) from exc

    raw = response.content

    if isinstance(raw, list):
        raw = "".join(
            str(part) for part in raw
        )

    return str(raw).strip()