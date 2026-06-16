# rag/ingestion/chunker.py
import os
import json
from rag.config import DATA_DIR
from rag.telemetry import ingestion_logger

def load_and_chunk_json(filename: str, processing_type: str) -> list:
    """
    Reads structured JSON records and normalizes them into unified text blocks
    enriched with semantic string signs to guide embedding dimensions.
    """
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        ingestion_logger.error(f"Ingestion Error: Targeted asset missing at -> {path}")
        return []
        
    with open(path, "r", encoding="utf-8") as f:
        records = json.load(f)
        
    chunks = []
    for idx, item in enumerate(records):
        document_text = ""
        metadata = {"source_file": filename, "origin_index": idx}
        
        if processing_type == "marpol":
            document_text = (
                f"MARPOL Regulatory Reference Code: {item.get('rule_ref', 'N/A')}. "
                f"Annex Classification Category: {item.get('annex', 'N/A')}. "
                f"Regulation Subject Title: {item.get('title', 'N/A')}. "
                f"Core Legal Requirement Text: {item.get('requirement', 'N/A')}. "
                f"Legal Threshold Limits & Operational Discharging Boundaries: {item.get('threshold', 'N/A')}."
            )
            # Retain original properties as clean metadata dictionary filters
            metadata.update({k: str(v) for k, v in item.items()})
            
        elif processing_type == "sire":
            document_text = (
                f"SIRE 2.0 Inspection Checklist Reference Code: {item.get('ref', 'N/A')}. "
                f"Chapter Index: {item.get('chapter', 'N/A')} - {item.get('chapter_title', 'N/A')}. "
                f"Vessel Inspector Question: {item.get('question_text', 'N/A')}. "
                f"Required Core Objective Goal: {item.get('objective', 'N/A')}. "
                f"Expected Physical Document Verification Evidence: {item.get('expected_evidence', 'N/A')}."
            )
            metadata.update({k: str(v) for k, v in item.items()})
            
        elif processing_type == "ism":
            document_text = (
                f"ISM Code Safety Management System Clause: {item.get('ism_section', 'N/A')}. "
                f"SMS Operational Policy Focus: {item.get('title', 'N/A')}. "
                f"Mandatory System Auditing Requirement: {item.get('requirement_text', 'N/A')}."
            )
            metadata.update({k: str(v) for k, v in item.items()})
            
        if document_text:
            chunks.append({"document": document_text, "metadata": metadata, "id": f"{processing_type}_{idx}"})
            
    ingestion_logger.info(f"Successfully processed {len(chunks)} chunks from source target '{filename}'")
    return chunks