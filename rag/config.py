# rag/config.py
import os

# Base directory navigation
RAG_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(RAG_DIR)
DATA_DIR = os.path.join(BASE_DIR, "data")
LOGS_DIR = os.path.join(RAG_DIR, "logs")
EMBEDDINGS_DB_DIR = os.path.join(RAG_DIR, "embeddings_db")

# Ensure logs directory exists safely
os.makedirs(LOGS_DIR, exist_ok=True)

# Model configuration settings
# 120MB offline model - fast download, 0 tokens consumed
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2" 

# Vector Database collection targets
COLLECTIONS = {
    "marpol": "marpol_rules_collection",
    "sire": "sire_questions_collection",
    "ism": "ism_requirements_collection"
}