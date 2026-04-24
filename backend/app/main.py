"""
main.py
-------
FastAPI application entry point.

Run with:
    uvicorn app.main:app --reload
"""

import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.routes import upload, recommend, chat, admin

# ---------------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Startup / shutdown lifecycle
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle — validate config on startup."""
    if not settings.GROQ_API_KEY:
        logger.critical(
            "GROQ_API_KEY is not set. "
            "Copy .env.example to .env and fill in the key."
        )
    logger.info("🚀 AI Insurance Recommendation API started.")
    logger.info("   Admin user  : %s", settings.ADMIN_USERNAME)
    logger.info("   ChromaDB dir: %s", settings.CHROMA_PERSIST_DIR)
    yield
    logger.info("🛑 AI Insurance Recommendation API shutting down.")


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(
    title="AI-Powered Insurance Recommendation API",
    description=(
        "A RAG-based backend that retrieves insurance policy data from uploaded PDFs "
        "and generates personalised health insurance recommendations using Groq LLMs. "
        "All answers are strictly grounded in uploaded documents — no hallucination."
    ),
    version="1.0.0",
    contact={
        "name": "AI Insurance Platform",
        "email": "support@aiinsurance.example.com",
    },
    license_info={"name": "MIT"},
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS Middleware (configure origins for production)
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Route registration
# ---------------------------------------------------------------------------

app.include_router(upload.router)
app.include_router(recommend.router)
app.include_router(chat.router)
app.include_router(admin.router)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.get("/", tags=["Health"], summary="API health check")
async def root():
    """Returns API status and available endpoints."""
    return JSONResponse(
        content={
            "status": "healthy",
            "service": "AI Insurance Recommendation API",
            "version": "1.0.0",
            "endpoints": {
                "docs":            "/docs",
                "redoc":           "/redoc",
                "upload_policy":   "POST /upload-policy",
                "recommend":       "POST /recommend",
                "chat":            "POST /chat",
                "admin_policies":  "GET  /admin/policies",
                "admin_delete":    "DELETE /admin/policy/{id}",
            },
        }
    )


@app.get("/health", tags=["Health"], summary="Liveness probe")
async def health():
    return {"status": "ok"}
