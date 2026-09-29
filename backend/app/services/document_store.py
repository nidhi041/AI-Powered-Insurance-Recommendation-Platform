"""
document_store.py
-----------------
Persistent SQLite-based metadata store for uploaded policy documents.

WHY SQLITE?
- Works identically on localhost and on Render (with a persistent disk path).
- Zero additional infrastructure (no Redis, no separate DB service).
- Survives backend restarts as long as the DB file is on a persistent path.
- Stores document lifecycle: PENDING → PROCESSING → COMPLETED / FAILED.
- Independent of ChromaDB — the document record is created BEFORE vector
  indexing begins, so a restart mid-processing still shows the document.

IMPORTANT FOR RENDER:
  Set DOCUMENT_DB_PATH to a path inside a Render Persistent Disk, e.g.:
    /var/data/insureiq.db
  Without a persistent disk the SQLite file is lost on redeploy, but this
  is still far better than the previous in-memory-only approach.
"""

import logging
import sqlite3
import threading
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.config import settings

logger = logging.getLogger(__name__)

# Module-level lock so that multi-threaded background workers can share the
# connection pool safely.
_db_lock = threading.Lock()

# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

_CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS policy_documents (
    id                TEXT PRIMARY KEY,
    filename          TEXT NOT NULL,
    original_filename TEXT NOT NULL,
    file_size_bytes   INTEGER,
    file_hash         TEXT,
    upload_timestamp  TEXT NOT NULL,
    processing_status TEXT NOT NULL DEFAULT 'pending',
    processing_error  TEXT,
    processed_at      TEXT,
    chunk_count       INTEGER,
    UNIQUE(file_hash)
);
"""

# ---------------------------------------------------------------------------
# Connection helper
# ---------------------------------------------------------------------------

def _get_connection() -> sqlite3.Connection:
    """Return a SQLite connection with WAL mode and row_factory set."""
    conn = sqlite3.connect(
        settings.DOCUMENT_DB_PATH,
        check_same_thread=False,
        timeout=10,
    )
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")   # concurrent reads
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def init_db() -> None:
    """Create tables if they don't already exist. Called at startup."""
    with _db_lock:
        conn = _get_connection()
        try:
            conn.execute(_CREATE_TABLE_SQL)
            conn.commit()
            logger.info("Document store initialised at: %s", settings.DOCUMENT_DB_PATH)
        finally:
            conn.close()


# ---------------------------------------------------------------------------
# CRUD helpers
# ---------------------------------------------------------------------------

def create_document_record(
    filename: str,
    original_filename: str,
    file_size_bytes: int,
    file_hash: Optional[str] = None,
) -> Optional[str]:
    """
    Insert a new document record with status='pending'.

    Returns the new document ID, or None if a document with the same
    file_hash already exists (duplicate upload guard).
    """
    doc_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    with _db_lock:
        conn = _get_connection()
        try:
            # Duplicate check — if file_hash already exists, return None
            if file_hash:
                existing = conn.execute(
                    "SELECT id FROM policy_documents WHERE file_hash = ?",
                    (file_hash,),
                ).fetchone()
                if existing:
                    logger.info(
                        "Duplicate upload detected (hash=%s), existing id=%s",
                        file_hash,
                        existing["id"],
                    )
                    return None  # caller should treat as duplicate

            conn.execute(
                """
                INSERT INTO policy_documents
                    (id, filename, original_filename, file_size_bytes,
                     file_hash, upload_timestamp, processing_status)
                VALUES (?, ?, ?, ?, ?, ?, 'pending')
                """,
                (doc_id, filename, original_filename, file_size_bytes,
                 file_hash, now),
            )
            conn.commit()
            logger.info("Created document record id=%s filename='%s'", doc_id, filename)
            return doc_id
        finally:
            conn.close()


def update_status(
    doc_id: str,
    status: str,
    error: Optional[str] = None,
    chunk_count: Optional[int] = None,
) -> None:
    """
    Update the processing_status of a document.

    status must be one of: 'pending', 'processing', 'completed', 'failed'
    """
    now = datetime.now(timezone.utc).isoformat()

    with _db_lock:
        conn = _get_connection()
        try:
            conn.execute(
                """
                UPDATE policy_documents
                SET processing_status = ?,
                    processing_error  = ?,
                    processed_at      = ?,
                    chunk_count       = COALESCE(?, chunk_count)
                WHERE id = ?
                """,
                (status, error, now if status in ("completed", "failed") else None,
                 chunk_count, doc_id),
            )
            conn.commit()
            logger.info("Document %s -> status='%s'", doc_id, status)
        finally:
            conn.close()


def get_document(doc_id: str) -> Optional[Dict[str, Any]]:
    """Return a single document record as a dict, or None."""
    with _db_lock:
        conn = _get_connection()
        try:
            row = conn.execute(
                "SELECT * FROM policy_documents WHERE id = ?",
                (doc_id,),
            ).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()


def get_document_by_hash(file_hash: str) -> Optional[Dict[str, Any]]:
    """Return a document record matching the file hash, or None."""
    with _db_lock:
        conn = _get_connection()
        try:
            row = conn.execute(
                "SELECT * FROM policy_documents WHERE file_hash = ?",
                (file_hash,),
            ).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()


def list_all_documents() -> List[Dict[str, Any]]:
    """Return all document records ordered by upload timestamp descending."""
    with _db_lock:
        conn = _get_connection()
        try:
            rows = conn.execute(
                """
                SELECT * FROM policy_documents
                ORDER BY upload_timestamp DESC
                """,
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()


def delete_document_record(doc_id: str) -> bool:
    """Delete a document record. Returns True if a row was deleted."""
    with _db_lock:
        conn = _get_connection()
        try:
            cursor = conn.execute(
                "DELETE FROM policy_documents WHERE id = ?",
                (doc_id,),
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
