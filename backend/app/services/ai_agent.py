"""
ai_agent.py
-----------
Core AI logic using Grok (ChatGroq) with strict JSON enforcement.
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


# ---------------------------------------------------------------------------
# LLM
# ---------------------------------------------------------------------------

def _get_llm() -> ChatGroq:
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.2,
        groq_api_key=settings.GROQ_API_KEY,
    )


# ---------------------------------------------------------------------------
# SYSTEM PROMPTS
# ---------------------------------------------------------------------------

_RECOMMENDATION_SYSTEM_PROMPT = """
You are an expert health insurance advisor.

STRICT RULES:
- You MUST return valid JSON only.
- Do NOT return text outside JSON.
- ALL fields are REQUIRED. Do not skip any.

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

RULES:
- Use ONLY provided documents
- If missing → "Not available in uploaded documents"
- Minimum 2 DIFFERENT policies (do NOT repeat same policy)
- suitability_score must be based on:
  - health condition match
  - waiting period
  - affordability
  - coverage relevance

DATA EXTRACTION (VERY IMPORTANT):
- You MUST extract these fields from documents:
  - policy_name
  - insurer
  - premium
  - cover_amount
  - waiting_period

- Specifically look for:
  - "waiting period"
  - "pre-existing disease waiting period"
  - diseases like diabetes

- If waiting period is present anywhere in documents → you MUST include it.

- DO NOT skip waiting_period even if it's mentioned in a different section.

IMPORTANT:
- Do NOT duplicate same policy with different premium
- Extract actual values from documents

WHY THIS POLICY:
- 150–250 words
- MUST include:
  - user age
  - user condition (like diabetes)
  - income level
- Explain WHY waiting period matters for that condition
- Use actual values from documents

TONE:
- Start with empathy
- Use simple, human-friendly language
""".strip()


_CHAT_SYSTEM_PROMPT = """
You are AarogyaAid AI, a professional health insurance assistant.
Your goal is to provide HIGHLY STRUCTURED answers using Markdown.

STRUCTURE RULES:
1. Use **Bold Headings** for different sections of your answer.
2. Use Bullet points (•) for listing features or conditions.
3. Use `>` Blockquotes for direct quotes from the policy documents.
4. If providing a summary, use a "Summary" heading at the end.

USER CONTEXT:
Use the user's profile (name, age, conditions) to personalize the structure.
Example: "**Waiting Period for [User Condition]**"

RAG RULES:
1. Answer ONLY using the provided DOCUMENTS.
2. If the answer isn't in the documents, say: "I couldn't find specific details about that in the uploaded policy documents."
3. Keep answers clear, professional, and easy to skim.
""".strip()


# ---------------------------------------------------------------------------
# MAIN FUNCTION
# ---------------------------------------------------------------------------

def generate_recommendation(
    user_profile: UserProfile,
    documents: List[str],
) -> RecommendationResponse:

    llm = _get_llm()

    conditions_str = ", ".join(user_profile.conditions)
    docs_block = "\n\n---\n\n".join(documents)

    human_message = f"""
USER PROFILE:
Age: {user_profile.age}
Conditions: {conditions_str}
Income: {user_profile.income}
Lifestyle: {user_profile.lifestyle}
City: {user_profile.city}

DOCUMENTS:
{docs_block}

Return ONLY valid JSON.

IMPORTANT:
Focus especially on extracting waiting period and disease-related clauses.
"""

    messages = [
        SystemMessage(content=_RECOMMENDATION_SYSTEM_PROMPT),
        HumanMessage(content=human_message),
    ]

    response = llm.invoke(messages)
    raw = response.content.strip()

    # ✅ Remove markdown if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    # ✅ Parse JSON safely
    try:
        data = json.loads(raw)
    except Exception:
        logger.error("Invalid JSON from AI: %s", raw)
        raise ValueError("AI did not return valid JSON")

    # ✅ FORCE REQUIRED FIELDS
    for item in data.get("comparison_table", []):
        item.setdefault("policy_name", "Not available in uploaded documents")
        item.setdefault("insurer", "Not available in uploaded documents")
        item.setdefault("premium", "Not available in uploaded documents")
        item.setdefault("cover_amount", "Not available in uploaded documents")
        item.setdefault("waiting_period", "Not available in uploaded documents")
        item.setdefault("key_benefit", "Not available in uploaded documents")
        item.setdefault("suitability_score", "Not available in uploaded documents")

    # 🚀 REMOVE DUPLICATE POLICIES (IMPORTANT FIX)
    unique = {}
    for item in data.get("comparison_table", []):
        name = item.get("policy_name")
        if name not in unique:
            unique[name] = item

    data["comparison_table"] = list(unique.values())

    coverage = data.get("coverage_details", {})
    coverage.setdefault("inclusions", "Not available in uploaded documents")
    coverage.setdefault("exclusions", "Not available in uploaded documents")
    coverage.setdefault("sub_limits", "Not available in uploaded documents")
    coverage.setdefault("copay", "Not available in uploaded documents")
    coverage.setdefault("claim_type", "Not available in uploaded documents")

    data.setdefault("why_this_policy", "Not available in uploaded documents")

    # ✅ Convert to Pydantic models
    comparison_table = [PolicyComparison(**p) for p in data["comparison_table"]]
    coverage_details = CoverageDetails(**coverage)

    return RecommendationResponse(
        comparison_table=comparison_table,
        coverage_details=coverage_details,
        why_this_policy=data["why_this_policy"],
    )


# ---------------------------------------------------------------------------
# CHAT
# ---------------------------------------------------------------------------

def generate_chat_answer(
    question: str,
    user_profile: UserProfile,
    documents: List[str],
) -> str:

    llm = _get_llm()

    conditions_str = ", ".join(user_profile.conditions)
    docs_block = "\n\n---\n\n".join(documents)

    human_message = f"""
USER PROFILE:
Name: {user_profile.full_name}
Age: {user_profile.age}
Conditions: {conditions_str}
Lifestyle: {user_profile.lifestyle}

QUESTION:
{question}

DOCUMENTS:
{docs_block}
"""

    messages = [
        SystemMessage(content=_CHAT_SYSTEM_PROMPT),
        HumanMessage(content=human_message),
    ]

    response = llm.invoke(messages)
    return response.content.strip()