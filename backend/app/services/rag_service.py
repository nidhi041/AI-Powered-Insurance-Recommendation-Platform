"""
rag_service.py
--------------
RAG service using ChromaDB's ONNX-backed embedding function for fast uploads.

Optimized for:
- Fast uploads (ONNX MiniLM instead of PyTorch)
- Faster retrieval
- Policy-level diversity
- Singleton ChromaDB client + collection
- Preserving recommendation quality
- Avoiding duplicate uploads of the same policy
"""

import logging
import uuid
from typing import List, Dict, Any, Optional

import chromadb
from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2

from app.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Pre-initialize the ONNX embedding model as a module-level singleton.
# This avoids a ~30-60s cold-start penalty on the first upload request.
# The model is ~23 MB and is cached by ONNX Runtime after the first load.
# ---------------------------------------------------------------------------
_embedding_fn: Optional[ONNXMiniLM_L6_V2] = None


def _get_embedding_fn() -> ONNXMiniLM_L6_V2:
    """Return (or create) the shared ONNX embedding function."""
    global _embedding_fn
    if _embedding_fn is None:
        logger.info("Loading ONNXMiniLM_L6_V2 embedding model...")
        _embedding_fn = ONNXMiniLM_L6_V2()
        logger.info("Embedding model loaded.")
    return _embedding_fn


def prewarm_embedding_model() -> None:
    """
    Call at server startup to load the ONNX model and run one dummy
    embedding so it is fully JIT-compiled before the first real upload.
    """
    ef = _get_embedding_fn()
    ef(["prewarm"])  # one dummy inference to trigger ONNX compilation
    logger.info("Embedding model pre-warmed and ready.")  


# ---------------------------------------------------------------------------
# Singleton ChromaDB client + collection
# ---------------------------------------------------------------------------

_chroma_client: Optional[chromadb.PersistentClient] = None
_collection: Optional[chromadb.Collection] = None


# ---------------------------------------------------------------------------
# ChromaDB
# ---------------------------------------------------------------------------

def _get_collection() -> chromadb.Collection:
    """
    Create the ChromaDB client and collection only once.

    Keeping these as singletons avoids reconnecting to ChromaDB
    on every request.
    """
    global _chroma_client, _collection

    if _collection is None:
        logger.info("Initializing ChromaDB with ONNX fast embeddings...")

        _chroma_client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR,
        )

        # Reuse the pre-warmed singleton — no extra model load on each request.
        _collection = _chroma_client.get_or_create_collection(
            name="insurance_policies",
            metadata={"hnsw:space": "cosine"},
            embedding_function=_get_embedding_fn(),
        )

        logger.info(
            "ChromaDB collection ready. Existing documents: %d",
            _collection.count(),
        )

    return _collection


# ---------------------------------------------------------------------------
# Store document
# ---------------------------------------------------------------------------

def store_document(
    chunks: List[str],
    source_name: str,
) -> str:
    """
    Store policy chunks in ChromaDB.

    Each upload receives a unique document_id, while the original
    source filename is preserved in metadata.
    """

    if not chunks:
        raise ValueError("No chunks supplied for storage.")

    collection = _get_collection()

    document_id = str(uuid.uuid4())

    logger.info(
        "Storing document '%s' with %d chunks",
        source_name,
        len(chunks),
    )

    ids = [
        f"{document_id}_chunk_{i}"
        for i in range(len(chunks))
    ]

    metadatas = [
        {
            "document_id": document_id,
            "source": source_name,
            "chunk_index": i,
        }
        for i in range(len(chunks))
    ]

    # -----------------------------------------------------------------------
    # FAST PATH: pre-compute all embeddings in ONE call using the singleton
    # ONNX model, then pass them as pre-computed embeddings to ChromaDB.
    #
    # Why this is fast:
    # 1. The ONNX model runs all chunks in a single batched inference call.
    # 2. ChromaDB receives pre-computed embeddings — it skips its internal
    #    embedding step entirely.
    # 3. A single collection.add() call means ChromaDB builds and persists
    #    the HNSW index exactly ONCE (vs. once per batch previously).
    # -----------------------------------------------------------------------
    ef = _get_embedding_fn()
    logger.info("Computing embeddings for %d chunks...", len(chunks))
    embeddings = ef(chunks)  # List[List[float]]

    logger.info("Storing %d pre-embedded chunks in ChromaDB...", len(chunks))
    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    logger.info(
        "Stored %d chunks for document '%s' (id=%s)",
        len(chunks),
        source_name,
        document_id,
    )

    return document_id



# ---------------------------------------------------------------------------
# Query documents
# ---------------------------------------------------------------------------

def query_documents(query: str) -> List[str]:
    """
    Retrieve relevant policy chunks with policy-level diversity.

    Strategy:
    1. Retrieve a small candidate pool from Chroma.
    2. Prefer different policy sources.
    3. Keep the final result count at TOP_K_RESULTS.
    4. Preserve the most relevant chunks.

    This avoids returning multiple chunks from the same policy when
    several different policies are available.
    """

    if not query or not query.strip():
        return []

    collection = _get_collection()

    total_chunks = collection.count()

    if total_chunks == 0:
        logger.warning("No documents found in ChromaDB.")
        return []

    logger.info("Querying insurance policy documents...")

    # ------------------------------------------------------------------
    # Candidate retrieval
    # ------------------------------------------------------------------
    # Previously 20 candidates were retrieved.
    # 12 gives enough room for policy diversity while reducing
    # unnecessary retrieval work.
    # ------------------------------------------------------------------

    candidate_k = min(12, total_chunks)

    results = collection.query(
        query_texts=[query],
        n_results=candidate_k,
        include=[
            "documents",
            "metadatas",
            "distances",
        ],
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    candidates = []

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances,
    ):
        if not document:
            continue

        candidates.append(
            {
                "document": document,
                "metadata": metadata or {},
                "distance": distance,
            }
        )

    if not candidates:
        logger.warning("ChromaDB returned no relevant documents.")
        return []

    # Chroma normally returns results by relevance, but explicitly
    # sorting keeps behaviour deterministic.
    candidates.sort(
        key=lambda item: item["distance"]
    )

    # ------------------------------------------------------------------
    # First pass:
    # Select the best chunk from each DIFFERENT POLICY SOURCE.
    #
    # IMPORTANT:
    # We use "source", not "document_id".
    #
    # Multiple uploads of the same PDF have different UUIDs but the
    # same source filename. They should not be treated as different
    # insurance policies.
    # ------------------------------------------------------------------

    selected = []
    seen_sources = set()

    for item in candidates:

        source = item["metadata"].get(
            "source",
            "unknown",
        )

        # Normalize source for comparison.
        normalized_source = str(source).strip().lower()

        if normalized_source not in seen_sources:

            selected.append(item)
            seen_sources.add(normalized_source)

            logger.info(
                "Added policy source '%s' to diversified retrieval.",
                source,
            )

    # ------------------------------------------------------------------
    # Second pass:
    # Fill remaining slots with the most relevant chunks.
    # ------------------------------------------------------------------

    max_results = min(
        settings.TOP_K_RESULTS,
        len(candidates),
    )

    selected_item_ids = {
        id(item)
        for item in selected
    }

    for item in candidates:

        if len(selected) >= max_results:
            break

        if id(item) in selected_item_ids:
            continue

        selected.append(item)

    # ------------------------------------------------------------------
    # Final relevance ordering
    # ------------------------------------------------------------------

    selected.sort(
        key=lambda item: item["distance"]
    )

    final_selected = selected[:max_results]

    final_docs = [
        item["document"]
        for item in final_selected
    ]

    policy_sources = {
        str(
            item["metadata"].get(
                "source",
                "unknown",
            )
        ).strip().lower()
        for item in final_selected
    }

    logger.info(
        "Retrieved %d relevant chunks from %d different policy sources.",
        len(final_docs),
        len(policy_sources),
    )

    return final_docs


# ---------------------------------------------------------------------------
# List documents
# ---------------------------------------------------------------------------

def list_documents() -> List[Dict[str, Any]]:
    """
    Return uploaded policy documents grouped by document_id.
    """

    collection = _get_collection()

    if collection.count() == 0:
        return []

    result = collection.get(
        include=["metadatas"],
    )

    metadatas = result.get(
        "metadatas",
        [],
    )

    doc_map: Dict[str, Dict[str, Any]] = {}

    for meta in metadatas:

        if not meta:
            continue

        doc_id = meta.get(
            "document_id",
            "unknown",
        )

        if doc_id not in doc_map:
            doc_map[doc_id] = {
                "id": doc_id,
                "source": meta.get(
                    "source",
                    "unknown",
                ),
                "chunk_count": 0,
            }

        doc_map[doc_id]["chunk_count"] += 1

    return list(doc_map.values())


# ---------------------------------------------------------------------------
# Delete document
# ---------------------------------------------------------------------------

def delete_document(doc_id: str) -> bool:
    """
    Delete all chunks belonging to a specific uploaded document.
    """

    collection = _get_collection()

    result = collection.get(
        where={
            "document_id": doc_id,
        },
        include=["metadatas"],
    )

    chunk_ids = result.get(
        "ids",
        [],
    )

    if not chunk_ids:
        logger.warning(
            "No chunks found for document_id=%s",
            doc_id,
        )
        return False

    collection.delete(
        ids=chunk_ids,
    )

    logger.info(
        "Deleted %d chunks for document_id=%s",
        len(chunk_ids),
        doc_id,
    )

    return True


# ---------------------------------------------------------------------------
# Update document metadata
# ---------------------------------------------------------------------------

def update_document_metadata(
    doc_id: str,
    new_source: str,
) -> bool:
    """
    Update the source filename for all chunks belonging to a document.
    """

    collection = _get_collection()

    result = collection.get(
        where={
            "document_id": doc_id,
        },
        include=["metadatas"],
    )

    ids = result.get(
        "ids",
        [],
    )

    if not ids:
        logger.warning(
            "No chunks found for document_id=%s to update.",
            doc_id,
        )
        return False

    metadatas = result.get(
        "metadatas",
        [],
    )

    for meta in metadatas:
        if meta:
            meta["source"] = new_source

    collection.update(
        ids=ids,
        metadatas=metadatas,
    )

    logger.info(
        "Updated source name to '%s' for document_id=%s",
        new_source,
        doc_id,
    )

    return True