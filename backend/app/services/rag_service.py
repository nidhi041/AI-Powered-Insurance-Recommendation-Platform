"""
rag_service.py
--------------
RAG service using ChromaDB's built-in embedding function.

The embedding model is managed by Chroma itself, avoiding
the heavy Sentence Transformers / PyTorch dependency and
external embedding API calls.
"""

import logging
import uuid
from typing import List, Dict, Any, Optional

import chromadb

from app.config import settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Singleton ChromaDB client + collection
# ---------------------------------------------------------------------------

_chroma_client: Optional[chromadb.PersistentClient] = None
_collection: Optional[chromadb.Collection] = None


# ---------------------------------------------------------------------------
# ChromaDB
# ---------------------------------------------------------------------------

def _get_collection() -> chromadb.Collection:
    global _chroma_client, _collection

    if _collection is None:
        logger.info("Initializing ChromaDB...")

        _chroma_client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR,
        )

        _collection = _chroma_client.get_or_create_collection(
            name="insurance_policies",
            metadata={"hnsw:space": "cosine"},
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

    # Chroma generates embeddings automatically.
    collection.add(
        ids=ids,
        documents=chunks,
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
    Retrieve relevant policy chunks with document-level diversity.

    Instead of returning all top-k chunks from potentially one policy,
    retrieve a larger candidate set and ensure that multiple policy
    documents are represented when available.
    """

    if not query or not query.strip():
        return []

    collection = _get_collection()

    total_documents = collection.count()

    if total_documents == 0:
        logger.warning("No documents found in ChromaDB.")
        return []

    logger.info("Querying insurance policy documents...")

    # Retrieve a larger candidate pool first.
    candidate_k = min(20, total_documents)

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
        candidates.append(
            {
                "document": document,
                "metadata": metadata or {},
                "distance": distance,
            }
        )

    # Chroma normally returns results ordered by relevance,
    # but explicitly sort to guarantee this behaviour.
    candidates.sort(
        key=lambda item: item["distance"]
    )

    # ------------------------------------------------------------------
    # First pass: guarantee representation from different policies.
    # ------------------------------------------------------------------

    selected = []
    seen_document_ids = set()

    for item in candidates:

        document_id = item["metadata"].get(
            "document_id",
            "unknown",
        )

        if document_id not in seen_document_ids:

            selected.append(item)
            seen_document_ids.add(document_id)

            logger.info(
                "Added policy '%s' to diversified retrieval.",
                item["metadata"].get(
                    "source",
                    "unknown",
                ),
            )

    # ------------------------------------------------------------------
    # Second pass: fill remaining slots with highest relevance.
    # ------------------------------------------------------------------

    max_results = min(
        settings.TOP_K_RESULTS,
        len(candidates),
    )

    selected_ids = {
        id(item)
        for item in selected
    }

    for item in candidates:

        if len(selected) >= max_results:
            break

        if id(item) in selected_ids:
            continue

        selected.append(item)

    # Sort final context by relevance.
    selected.sort(
        key=lambda item: item["distance"]
    )

    final_docs = [
        item["document"]
        for item in selected[:max_results]
    ]

    logger.info(
        "Retrieved %d relevant chunks from %d different policies.",
        len(final_docs),
        len({
            item["metadata"].get(
                "document_id",
                "unknown",
            )
            for item in selected[:max_results]
        }),
    )

    return final_docs


# ---------------------------------------------------------------------------
# List documents
# ---------------------------------------------------------------------------

def list_documents() -> List[Dict[str, Any]]:

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