# rag/telemetry.py
import os
import logging
from rag.config import LOGS_DIR

def setup_logger(name: str, log_file: str, level=logging.INFO) -> logging.Logger:
    """Creates an isolated file logger pointing to a specific telemetry script."""
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    
    handler = logging.FileHandler(os.path.join(LOGS_DIR, log_file), encoding='utf-8')
    handler.setFormatter(formatter)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    # Prevent duplicate root streaming corruption
    logger.propagate = False 
    
    if not logger.handlers:
        logger.addHandler(handler)
        
    return logger

# Export dedicated component telemetry lines
ingestion_logger = setup_logger("rag_ingestion", "ingestion.log")
retrieval_logger = setup_logger("rag_retrieval", "retrieval.log")
generation_logger = setup_logger("rag_generation", "generation.log")