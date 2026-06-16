# rag/generation/validate_generation.py
import os
import sys

# Ensure parent path resolution is correct
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from rag.ingestion.vector_db import vector_store_instance
from rag.generation.prompter import build_grounded_compliance_context

def run_generation_diagnostic():
    print("🚀 Running Phase 3: Standalone Prompt Generation validation check...")
    
    # 1. Boot up persistent database collections
    print("🧠 Synchronizing database connections...")
    vector_store_instance.seed_all_collections()
    
    # 2. Re-test our machinery spaces query
    test_query = "vessel needs to discharge bilge water sludge from machinery spaces"
    
    print(f"\nConstructing final LLM grounding block for query...")
    context_output = build_grounded_compliance_context("marpol", test_query, max_chunks=2)
    
    print("\n📦 Generated Prompt Context Envelope Preview:")
    print("-" * 60)
    print(context_output)
    print("-" * 60)
    
    print("\n🎉 [SUCCESS] Phase 3 Generation Validation Complete! Check 'rag/logs/generation.log' to view prompt trace timelines.")

if __name__ == "__main__":
    run_generation_diagnostic()