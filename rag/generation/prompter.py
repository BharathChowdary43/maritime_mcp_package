# rag/generation/prompter.py
import logging
from rag.retrieval.search_engine import semantic_query_lookup
from rag.telemetry import generation_logger

def build_grounded_compliance_context(collection_key: str, user_query: str, max_chunks: int = 2) -> str:
    """
    Retrieves semantic hits and constructs a secure markdown grounding context block.
    Filters out extreme low-confidence data noise to prevent LLM confusion.
    """
    generation_logger.info(f"🏗️ [PROMPTER] Constructing context envelope for query: '{user_query}'")
    
    # Extract the top semantic matches from the retrieval engine
    matches = semantic_query_lookup(collection_key, user_query, top_k=max_chunks)
    
    if not matches:
        generation_logger.warning("⚠️ [PROMPTER EMPTY] Zero context chunks retrieved from vector search.")
        return "No local compliance database context records were located for this activity."

    context_segments = []
    
    for idx, match in enumerate(matches, 1):
        # High-threshold protective filter: skip chunks that are mathematically irrelevant
        if match["distance"] > 0.65:
            generation_logger.warning(
                f"   ├── [FILTERED OUT] Skipping Match [{idx}] due to extreme low semantic correlation "
                f"(Distance: {match['distance']:.4f})"
            )
            continue

        # Format surviving chunks with clean, explicit XML grounding markers
        chunk_text = (
            f"--- COMPLIANCE RECORD {idx} ---\n"
            f"Source: {match['metadata'].get('source_file', 'Unknown')}\n"
            f"Content: {match['text']}\n"
        )
        context_segments.append(chunk_text)

    if not context_segments:
        generation_logger.warning("⚠️ [PROMPTER FILTERED] All retrieved chunks failed distance threshold checks.")
        return "No highly correlated compliance database context records passed semantic verification filters."

    # Assemble the final context package
    final_context_block = (
        "=== MANDATORY REGULATORY DATABASE CONTEXT ===\n"
        "You must rely strictly on the verified local records below. Do not use external training knowledge.\n"
        "<context>\n"
        f"{chr(10).join(context_segments)}"
        "</context>\n"
        "============================================="
    )
    
    generation_logger.info(f"✅ [PROMPTER SUCCESS] Injected {len(context_segments)} grounded records into prompt envelope.")
    return final_context_block