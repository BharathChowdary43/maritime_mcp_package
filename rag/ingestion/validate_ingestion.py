# rag/ingestion/validate_ingestion.py
import os
import sys

# Ensure parent path resolution is correct
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from rag.ingestion.vector_db import vector_store_instance
from rag.config import COLLECTIONS

def run_ingestion_diagnostic():
    print("🔄 Running standalone Data Ingestion validation sweep...")
    
    try:
        # Trigger the full parsing and embedding conversion cycle
        vector_store_instance.seed_all_collections()
        
        print("\n📊 Diagnostics Audit Manifest:")
        for key, col_name in COLLECTIONS.items():
            count = vector_store_instance.collections[key].count()
            print(f"  ├── Collection: '{col_name}' ➡️ Embedded Count: {count} items loaded in RAM.")
            
            if count == 0:
                print(f"  ❌ WARNING: Collection '{key}' is completely empty! Check raw JSON data fields.")
                return
                
        print("\n🎉 [SUCCESS] Phase 1 Ingestion Validation Complete! Check 'rag/logs/ingestion.log' for details.")
        
    except Exception as e:
        print(f"\n❌ Ingestion Phase Failed with Runtime Exception: {str(e)}")
        print("Review your package dependencies and ensure sentence-transformers is installed.")

if __name__ == "__main__":
    run_ingestion_diagnostic()