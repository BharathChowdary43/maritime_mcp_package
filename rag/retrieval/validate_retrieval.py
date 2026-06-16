# rag/retrieval/validate_retrieval.py
import os
import sys

# Ensure parent path resolution is correct
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from rag.ingestion.vector_db import vector_store_instance
from rag.retrieval.search_engine import semantic_query_lookup

def run_retrieval_diagnostic():
    print("🚀 Running Phase 2: Standalone Vector Retrieval validation check...")
    
    # 1. Force background boot-up database seeding
    print("🧠 Seeding in-memory vector database arrays (RAM)...")
    vector_store_instance.seed_all_collections()
    
    # 2. Hard test query using synonyms not present in the files
    test_synonym_query = "vessel needs to discharge bilge water sludge from machinery spaces"
    
    print(f"\n🔮 Triggering Semantic Query Check for: \"{test_synonym_query}\"")
    matches = semantic_query_lookup("marpol", test_synonym_query, top_k=2)
    
    print("\n📊 Search Results Preview from Memory:")
    if not matches:
        print("  ❌ FAILURE: Search engine returned absolutely zero matches.")
        return

    for idx, match in enumerate(matches, 1):
        print(f"\n  [MATCH {idx}] (Distance: {match['distance']:.4f} | Confidence: {match['confidence']})")
        # Print a short snippet of the textified document block
        print(f"  Snippet: {match['text'][:140]}...")
        
    print("\n🎉 [SUCCESS] Phase 2 Retrieval Validation Complete! Check 'rag/logs/retrieval.log' to trace distance scores.")

if __name__ == "__main__":
    run_retrieval_diagnostic()