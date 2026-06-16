# rag/ingestion/vector_db.py
import os
import chromadb
from chromadb.utils import embedding_functions
from rag.config import EMBEDDING_MODEL_NAME, COLLECTIONS, EMBEDDINGS_DB_DIR
from rag.telemetry import ingestion_logger
from rag.ingestion.chunker import load_and_chunk_json

class PersistentVectorStore:
    def __init__(self):
        ingestion_logger.info(f"💾 Initializing Persistent ChromaDB Layer at: {EMBEDDINGS_DB_DIR}")
        
        # PRODUCTION UPGRADE: Use PersistentClient instead of an ephemeral Client
        self.client = chromadb.PersistentClient(path=EMBEDDINGS_DB_DIR)
        
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL_NAME
        )
        
        self.collections = {}
        for key, collection_name in COLLECTIONS.items():
            self.collections[key] = self.client.get_or_create_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )

    def seed_all_collections(self):
        """
        Smart Ingestion Module: If embeddings already exist on disk, 
        it skips generation entirely. If not, it builds them fresh.
        """
        ingestion_logger.info("🎬 Checking persistent embedding status...")
        
        targets = [
            ("marpol_rules.json", "marpol"),
            ("sire_questions.json", "sire"),
            ("ism_requirements.json", "ism")
        ]
        
        for file, key in targets:
            collection = self.collections[key]
            
            # SMART CHECK: Check if data is already inside the disk cache folder
            existing_count = collection.count()
            if existing_count > 0:
                ingestion_logger.info(f"📦 [DISK HIT] Collection '{key}' already contains {existing_count} vectors. Skipping embedding phase!")
                continue
                
            # If empty, generate them fresh
            ingestion_logger.info(f"🔥 [DISK MISS] Collection '{key}' is empty. Generating vectors fresh...")
            chunks = load_and_chunk_json(file, key)
            if not chunks:
                continue
                
            documents = [c["document"] for c in chunks]
            metadatas = [c["metadata"] for c in chunks]
            ids = [c["id"] for c in chunks]
            
            collection.add(documents=documents, metadatas=metadatas, ids=ids)
            ingestion_logger.info(f"✅ Saved {len(ids)} newly generated vectors to local disk cache.")
            
        ingestion_logger.info("🎉 Embedding storage synchronization complete.")

# Singleton operational instance to maintain dynamic global memory state context
vector_store_instance = PersistentVectorStore()