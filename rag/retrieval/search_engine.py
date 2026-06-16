# rag/retrieval/search_engine.py
from rag.ingestion.vector_db import vector_store_instance
from rag.telemetry import retrieval_logger

def semantic_query_lookup(collection_key: str, user_query: str, top_k: int = 5) -> list:
    """
    Queries an in-memory ChromaDB collection using vector semantic similarity.
    Logs mathematical distance scores to ensure retrieval grounding accuracy.
    """
    if collection_key not in vector_store_instance.collections:
        retrieval_logger.error(f"Retrieval Error: Targeted collection key '{collection_key}' does not exist.")
        return []

    retrieval_logger.info(f"🔍 [QUERY ENGINES] Executing vector search on '{collection_key}' space...")
    retrieval_logger.info(f"   ↳ Parameter Text: '{user_query}'")

    collection = vector_store_instance.collections[collection_key]
    
    # Query the collection space
    results = collection.query(
        query_texts=[user_query],
        n_results=top_k
    )

    if not results or not results["documents"] or not results["documents"][0]:
        retrieval_logger.warning(f"⚠️ [ZERO HITS] Vector similarity space returned empty for query: '{user_query}'")
        return []

    processed_matches = []
    
    # Unpack ChromaDB's multidimensional array outputs
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    for i in range(len(documents)):
        doc_text = documents[i]
        meta_dict = metadatas[i]
        dist_score = distances[i]

        # Log exact mathematical confidence metrics to the log trace file
        retrieval_logger.info(
            f"   ├── Match [{i+1}] ID: {meta_dict.get('origin_index', 'N/A')} "
            f"| Cosine Distance Score: {dist_score:.4f}"
        )

        # Clear architectural flag if confidence drops drastically
        confidence = "HIGH" if dist_score < 0.45 else "LOW"
        if confidence == "LOW":
            retrieval_logger.warning(f"   └── ⚠️ POOR SEMANTIC CORRELATION detected on Match [{i+1}]!")

        processed_matches.append({
            "text": doc_text,
            "metadata": meta_dict,
            "distance": dist_score,
            "confidence": confidence
        })

    return processed_matches