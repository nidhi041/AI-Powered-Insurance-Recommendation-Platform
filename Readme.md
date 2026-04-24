# AarogyaAid — AI-Powered Health Insurance Intelligence

Health insurance policies are dense, jargon-heavy, and often more stressful than the health issues themselves. AarogyaAid is a retrieval-augmented AI platform designed to simplify this decision.

Instead of listing policies based only on premiums, AarogyaAid reads actual insurance documents and explains — in clear, human terms — why a specific policy fits a user’s medical and financial profile.

---

## Features

### User Features

* Structured user profiling (Age, Lifestyle, Conditions, Income, City)
* AI-powered insurance recommendations
* Comparison table of policies
* Coverage breakdown (inclusions, exclusions, sub-limits, co-pay)
* Personalized explanation ("Why this policy")
* Context-aware chat explainer for insurance terms

---

### Admin Features

* Upload insurance policy documents (PDF only)
* View indexed policies
* Delete policies (removes data from vector database instantly)
* Secure access via environment-based authentication

---

## System Architecture

The system follows a Retrieval-Augmented Generation (RAG) architecture:

```
User Profile → Query Builder → Vector Database (policy chunks)
            → AI Agent → Structured Recommendation
            → Chat Explainer (context-aware)
```

---

## Why AI / RAG Approach?

Traditional insurance platforms rely on rule-based filtering or keyword search. These approaches fail in real-world usage:

* Context Gap: A condition like "Diabetes" may appear under different terminology such as "chronic metabolic disorders"
* No Trade-off Reasoning: Cannot balance premium vs benefits
* Static Logic: Adding new policies requires manual updates

RAG solves this by:

* Allowing the system to process real policy documents
* Ensuring outputs are grounded in actual data
* Enabling instant scalability when new PDFs are uploaded

---

## End-to-End Flow (User Journey)

1. User provides profile details (age, lifestyle, conditions, income, city)
2. System constructs a context-aware query
3. Relevant policy clauses are retrieved from the vector database
4. AI agent evaluates retrieved clauses against the user profile
5. System generates:

   * Comparison table
   * Coverage breakdown
   * Personalized explanation
6. User interacts further using the chat explainer

---

## Tech Stack & Reasoning

| Component | Choice         | Justification                                        |
| --------- | -------------- | ---------------------------------------------------- |
| Frontend  | React (Vite)   | Efficient UI state handling and modular architecture |
| Backend   | FastAPI        | Asynchronous performance, ideal for AI workflows     |
| Vector DB | ChromaDB       | Lightweight, local storage with persistence          |
| LLM       | Groq (Llama-3) | High-speed inference for real-time responses         |
| Styling   | Tailwind CSS   | Clean and minimal UI design system                   |

---

## AI Strategy & Recommendation Logic

The system uses a weighted alignment model instead of simple ranking:

* Health Context (40%): Focus on disease coverage and waiting periods
* Financial Fit (30%): Aligns premium with income bracket
* Geographic Fit (20%): Considers hospital network relevance by city
* Lifestyle Factor (10%): Adjusts recommendations based on risk profile

The goal is to recommend the most suitable policy, not just the cheapest one.

---

## Output Format (Strict Contract)

The system returns a structured JSON response to ensure consistency:

* comparison_table
  Includes policy name, insurer, premium, coverage, waiting period, key benefit, and suitability score

* coverage_details
  Includes inclusions, exclusions, sub-limits, co-pay, and claim type

* why_this_policy
  A personalized explanation referencing the user profile

This structure ensures reliable UI rendering and predictable data handling.

---

## RAG Pipeline

1. Upload PDF → extract text → chunk into segments
2. Convert chunks into embeddings and store in vector database
3. Retrieve top relevant chunks based on user query
4. Pass retrieved context to AI agent
5. Generate grounded response

### Chunking Strategy

* Fixed-size chunks with overlap
* Preserves clause-level meaning
* Prevents loss of important policy details

---

## Grounding Guarantee

The system enforces a strict no-hallucination policy:

* All responses are derived only from retrieved documents
* If information is missing, the system returns:

```
Information not available in uploaded documents
```

This ensures reliability in financial decision-making.

---

## Chat Explainer

The chat assistant acts as an insurance explainer:

* Defines key terms such as co-pay, waiting period, and NCB
* Uses the user’s profile for contextual responses
* Maintains session continuity

Example:
A question about waiting period for diabetes will include a personalized explanation based on the user’s profile.

---

## Setup Instructions

### Backend

```
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```
cd frontend
npm install
npm run dev
```

---

## Environment Variables

Create a `.env` file in the backend directory:

```
GROQ_API_KEY=your_key_here
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_secure_password
```

---

## Limitations

* Performance may vary with very large PDFs
* Dependent on quality and structure of uploaded documents
* No real-time integration with insurer APIs

---

## Future Improvements

* OCR support for scanned policy documents
* Real-time insurer API integration
* Improved ranking and scoring model
* Multi-user and family insurance support

---

## Key Design Philosophy

Insurance decisions involve both financial and emotional factors.

This system is designed with:

* Clarity over complexity
* Explainability over black-box outputs
* Empathy over automation

The goal is to help users make informed decisions with confidence.

---

## Built For

AarogyaAid AI Engineering Assessment
Focus: grounded AI, transparency, and user-centric design
