from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


# ---------------------------------------------------------------------------
# Enums for strict field validation
# ---------------------------------------------------------------------------

class Lifestyle(str, Enum):
    sedentary = "Sedentary"
    moderate = "Moderate"
    active = "Active"
    athlete = "Athlete"


class Condition(str, Enum):
    diabetes = "Diabetes"
    hypertension = "Hypertension"
    asthma = "Asthma"
    cardiac = "Cardiac"
    none = "None"
    other = "Other"


class Income(str, Enum):
    under_3l = "under 3L"
    three_to_8l = "3-8L"
    eight_to_15l = "8-15L"
    above_15l = "15L+"


class City(str, Enum):
    metro = "Metro"
    tier2 = "Tier-2"
    tier3 = "Tier-3"


# ---------------------------------------------------------------------------
# User Profile — EXACTLY 6 fields
# ---------------------------------------------------------------------------

class UserProfile(BaseModel):
    full_name: str = Field(..., description="Full name of the user")
    age: int = Field(..., ge=1, le=120, description="Age of the user")
    lifestyle: str = Field(..., description="Activity level")
    conditions: List[str] = Field(..., description="Pre-existing medical conditions")
    income: str = Field(..., description="Annual income bracket")
    city: str = Field(..., description="City tier of residence")


# ---------------------------------------------------------------------------
# Recommendation Output — strict 3-section format
# ---------------------------------------------------------------------------

class PolicyComparison(BaseModel):
    policy_name: str
    insurer: str
    premium: str
    cover_amount: str
    waiting_period: str
    key_benefit: str
    suitability_score: str


class CoverageDetails(BaseModel):
    inclusions: str
    exclusions: str
    sub_limits: str
    copay: str
    claim_type: str


class RecommendationResponse(BaseModel):
    comparison_table: List[PolicyComparison]
    coverage_details: CoverageDetails
    why_this_policy: str


# ---------------------------------------------------------------------------
# Chat models
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    question: str = Field(..., description="User's question about insurance")
    user_profile: UserProfile = Field(..., description="User profile for contextual answers")
    session_id: Optional[str] = Field(None, description="Optional session identifier")


class ChatResponse(BaseModel):
    answer: str
    session_id: Optional[str] = None


# ---------------------------------------------------------------------------
# Upload / Admin models
# ---------------------------------------------------------------------------

class UploadResponse(BaseModel):
    message: str
    chunks_stored: int
    document_id: str


class PolicyDocument(BaseModel):
    id: str
    source: str
    chunk_count: int


class AdminPoliciesResponse(BaseModel):
    policies: List[PolicyDocument]
    total: int


class DeleteResponse(BaseModel):
    message: str
    deleted_id: str


class UpdateMetadataRequest(BaseModel):
    source: str


class UpdateMetadataResponse(BaseModel):
    message: str
    updated_id: str
