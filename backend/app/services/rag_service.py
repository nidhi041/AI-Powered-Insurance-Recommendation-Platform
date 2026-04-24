"""
rag_service.py
--------------
Improved RAG service with better retrieval and ranking.
"""

import logging
import uuid
from typing import List, Dict, Any, Optional

import chromadb
from chromadb import Settings as ChromaSettings
from langchain_huggingface import HuggingFaceEmbeddings

from app.config import settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Singleton ChromaDB client + collection
# ---------------------------------------------------------------------------

_chroma_client: Optional[object] = None
_collection: Optional[object] = None
_embedder: Optional[object] = None


def _get_embedder():
    global _embedder
    if _embedder is None:
        logger.info("Loading embedding model...")
        _embedder = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
    return _embedder


def _get_collection() -> chromadb.Collection:
    global _chroma_client, _collection

    if _collection is None:
        logger.info("Initializing ChromaDB...")

        _chroma_client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR,
            settings=ChromaSettings(anonymized_telemetry=False),
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
# Public API
# ---------------------------------------------------------------------------

def store_document(chunks: List[str], source_name: str) -> str:
    collection = _get_collection()
    embedder = _get_embedder()

    document_id = str(uuid.uuid4())

    logger.info("Storing document: %s", source_name)

    embeddings = embedder.embed_documents(chunks)

    ids = [f"{document_id}_chunk_{i}" for i in range(len(chunks))]

    metadatas = [
        {
            "document_id": document_id,
            "source": source_name,
            "chunk_index": i,
        }
        for i in range(len(chunks))
    ]

    collection.add(
        ids=ids,
        embeddings=embeddings,
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


def query_documents(query: str) -> List[str]:
    """
    🔥 Improved retrieval: more chunks + better ranking
    """
    collection = _get_collection()
    embedder = _get_embedder()

    if collection.count() == 0:
        logger.warning("No documents found in ChromaDB.")
        return []

    logger.info("Querying documents...")

    query_embedding = embedder.embed_query(query)

    # 🚀 INCREASE RETRIEVAL (KEY FIX)
    top_k = min(15, collection.count())

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    documents = results.get("documents", [[]])[0]
    distances = results.get("distances", [[]])[0]

    # 🚀 SORT BY RELEVANCE
    ranked_docs = sorted(
        zip(documents, distances),
        key=lambda x: x[1]
    )

    # 🚀 RETURN MORE CONTEXT (IMPORTANT)
    final_docs = [doc for doc, _ in ranked_docs[:12]]

    logger.info("Retrieved %d high-quality chunks.", len(final_docs))

    return final_docs


def list_documents() -> List[Dict[str, Any]]:
    collection = _get_collection()

    if collection.count() == 0:
        return []

    result = collection.get(include=["metadatas"])
    metadatas = result.get("metadatas", [])

    doc_map: Dict[str, Dict[str, Any]] = {}

    for meta in metadatas:
        doc_id = meta.get("document_id", "unknown")

        if doc_id not in doc_map:
            doc_map[doc_id] = {
                "id": doc_id,
                "source": meta.get("source", "unknown"),
                "chunk_count": 0,
            }

        doc_map[doc_id]["chunk_count"] += 1

    return list(doc_map.values())


def delete_document(doc_id: str) -> bool:
    collection = _get_collection()

    result = collection.get(
        where={"document_id": doc_id},
        include=["metadatas"],
    )

    chunk_ids = result.get("ids", [])

    if not chunk_ids:
        logger.warning("No chunks found for document_id=%s", doc_id)
        return False

    collection.delete(ids=chunk_ids)

    logger.info("Deleted %d chunks for document_id=%s", len(chunk_ids), doc_id)

    return True


def update_document_metadata(doc_id: str, new_source: str) -> bool:
    collection = _get_collection()

    result = collection.get(
        where={"document_id": doc_id},
        include=["metadatas"],
    )

    ids = result.get("ids", [])
    if not ids:
        logger.warning("No chunks found for document_id=%s to update.", doc_id)
        return False

    metadatas = result.get("metadatas", [])
    for meta in metadatas:
        meta["source"] = new_source

    collection.update(
        ids=ids,
        metadatas=metadatas,
    )

    logger.info("Updated source name to '%s' for document_id=%s", new_source, doc_id)
    return True