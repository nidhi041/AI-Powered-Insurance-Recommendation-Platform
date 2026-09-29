"""
migrate_embeddings.py
---------------------
One-time migration: re-embeds all existing ChromaDB documents using ONNXMiniLM_L6_V2.

Run once from the backend directory:
    python migrate_embeddings.py
"""

import chromadb
from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2

CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "insurance_policies"
BATCH_SIZE = 50


def migrate():
    print("=== ChromaDB Embedding Migration ===\n")
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    try:
        old_col = client.get_collection(name=COLLECTION_NAME)
        total = old_col.count()
        print(f"Found existing collection with {total} chunks.")
    except Exception as e:
        print(f"Collection not found: {e}")
        return

    if total == 0:
        client.delete_collection(name=COLLECTION_NAME)
        ef = ONNXMiniLM_L6_V2()
        client.create_collection(name=COLLECTION_NAME, metadata={"hnsw:space": "cosine"}, embedding_function=ef)
        print("Empty collection recreated with ONNX embeddings.")
        return

    print(f"Fetching all {total} chunks...")
    all_data = old_col.get(include=["documents", "metadatas"])
    ids = all_data.get("ids", [])
    documents = all_data.get("documents", [])
    metadatas = all_data.get("metadatas", [])
    print(f"Fetched {len(ids)} chunks.\n")

    print("Deleting old collection...")
    client.delete_collection(name=COLLECTION_NAME)

    print("Creating new collection with ONNXMiniLM_L6_V2...")
    ef = ONNXMiniLM_L6_V2()
    new_col = client.create_collection(name=COLLECTION_NAME, metadata={"hnsw:space": "cosine"}, embedding_function=ef)

    total_chunks = len(ids)
    print(f"Re-inserting {total_chunks} chunks in batches of {BATCH_SIZE}...")
    for batch_start in range(0, total_chunks, BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, total_chunks)
        new_col.add(
            ids=ids[batch_start:batch_end],
            documents=documents[batch_start:batch_end],
            metadatas=metadatas[batch_start:batch_end],
        )
        print(f"  Batch {batch_start + 1}-{batch_end} / {total_chunks} done.")

    print(f"\nMigration complete! {total_chunks} chunks re-embedded with ONNX.")
    print(f"New collection count: {new_col.count()}")


if __name__ == "__main__":
    migrate()
