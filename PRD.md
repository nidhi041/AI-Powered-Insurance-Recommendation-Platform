PRD — AI-Powered Insurance Recommendation Platform
1. User Profile
The primary user of this platform is an Indian adult (age 25–60) who is looking to purchase health insurance but lacks deep understanding of insurance terminology and policy differences.
Most users:
Have limited financial literacy regarding insurance
Are overwhelmed by multiple policy options
Fear choosing the wrong policy and facing claim rejection during emergencies
May be disclosing health conditions (e.g., diabetes, hypertension) for the first time in a digital system
Their biggest fear:
“If you buy the wrong policy, you will not get your money back at the time of hospitalization.”

2. Problem Statement
Choosing the right health insurance policy in India is complex due to:
Technical jargon (waiting period, co-pay, exclusions)
Hidden clauses in policy documents
Lack of personalized recommendations based on health conditions
Comparison platforms focusing on price rather than suitability
Users often:
Choose cheaper plans without understanding coverage gaps
Ignore exclusions related to pre-existing diseases
Do not understand long-term implications (waiting periods, claim limits)
This leads to:
Financial risk during medical emergencies

3. Feature Priority (Based on 54-hour constraint)
High Priority (Must Build)
User Profile Form (6 fields exactly)
AI Recommendation Engine (RAG-based)
Structured Output:
Comparison Table
Coverage Details
Why This Policy Explanation
Chat Explainer (policy-specific)
Admin Panel (upload/delete policies)
Medium Priority
Basic authentication for admin
Simple UI (clean and readable)
Out of Scope
Payment integration
Real insurer APIs
Advanced analytics dashboard

4. Logic (CORE)
The recommendation system works in 3 stages:
Step 1: Profile Understanding
The system collects:
Age → Determines risk category and premium sensitivity
Lifestyle → Impacts risk weighting (active vs sedentary)
Pre-existing conditions → Filters policies with acceptable waiting periods and exclusions
Income → Sets affordability threshold
City tier → Adjusts hospital network relevance

Step 2: Policy Retrieval (RAG)
The system:
Parses uploaded policy documents
Splits them into meaningful chunks
Stores embeddings in vector database
When a user submits their profile:
Query is generated using profile fields
Relevant policy chunks are retrieved

Step 3: AI Decision Making
The AI:
Compares multiple policies
Extracts:
Premium
Waiting period
Coverage
Exclusions
Generates a Suitability Score based on:
Match with health condition
Affordability
Waiting period length
Coverage adequacy

Step 4: Response Generation
The system produces:
Comparison Table (Top 2–3 policies)
Coverage Detail Table (Best policy)
Personalized Explanation

5. Assumptions
Policy documents contain structured or semi-structured data
Users provide honest health information
Insurance policies follow standard terminology (waiting period, co-pay)
Vector search can retrieve relevant policy sections accurately

6. Out of Scope
Real-time premium calculation APIs
Fraud detection
Multi-user login system
Mobile app



