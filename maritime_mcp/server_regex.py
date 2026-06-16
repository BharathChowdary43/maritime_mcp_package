import os
import json
import logging
import sys
from fastmcp import FastMCP

# 1. Setup structured corporate logging to stderr so it doesn't corrupt stdout
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger("maritime_mcp_server")

# 2. Initialize FastMCP
mcp = FastMCP("Maritime-Compliance-Server")

# 3. Resolve the path to our data directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

def load_json_data(filename):
    path = os.path.join(DATA_DIR, filename)
    try:
        if not os.path.exists(path):
            logger.error(f"Critical Error: File not found at path -> {path}")
            return []
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load data file {filename}: {str(e)}")
        return []

# Load database arrays safely into RAM memory
sire_db = load_json_data("sire_questions.json")
marpol_db = load_json_data("marpol_rules.json")
ism_db = load_json_data("ism_requirements.json")


@mcp.tool()
def sire_lookup(keyword: str = None, ref_id: str = None) -> str:
    """
    Look up a SIRE 2.0 inspection question by a reference ID or keyword search.
    Use this tool when the inspector references a specific question code or asks about particular equipment checks.
    """
    logger.info(f"[TOOL CALL] sire_lookup invoked with keyword='{keyword}', ref_id='{ref_id}'")
    matches = []

    if ref_id:
        ref_clean = str(ref_id).strip().lower()
        for q in sire_db:
            if ref_clean in str(q.get("ref", "")).strip().lower():
                matches.append(q)
                
    if keyword:
        k_lower = str(keyword).lower().strip()
        search_words = [w for w in k_lower.split() if len(w) > 2]
        
        for q in sire_db:
            q_text = str(q.get("question_text") or "").lower()
            c_title = str(q.get("chapter_title") or "").lower()
            evidence = str(q.get("expected_evidence") or "").lower()
            guidance = str(q.get("guidance_notes") or "").lower()
            
            full_match = (k_lower in q_text or k_lower in c_title or k_lower in evidence)
            word_match = any(word in q_text or word in c_title or word in evidence or word in guidance for word in search_words) if search_words else False
            
            if full_match or word_match:
                if q not in matches:
                    matches.append(q)

    if not matches:
        return f"No SIRE 2.0 questions found matching parameters (keyword: {keyword}, ref_id: {ref_id})."

    formatted_results = []
    for m in matches:
        formatted_results.append(
            f"📋 SIRE Ref: {m.get('ref')} | Chapter {m.get('chapter')}: {m.get('chapter_title')}\n"
            f"Question: {m.get('question_text')}\n"
            f"Objective: {m.get('objective')}\n"
            f"Expected Evidence: {m.get('expected_evidence')}\n"
            f"Guidance: {m.get('guidance_notes')}"
        )
    return "\n\n---\n\n".join(formatted_results)


@mcp.tool()
def marpol_check(activity: str) -> str:
    """
    Given a vessel operational activity description, look up applicable MARPOL Annex rules 
    and return strict compliance requirements. Use this tool whenever the user mentions 
    discharging waste, bilge water, sewage, fuel sulphur content, or transiting special areas/ECAs.
    """
    logger.info(f"[TOOL CALL] marpol_check invoked with activity='{activity}'")
    matches = []
    a_lower = str(activity).lower().strip() if activity else ""

    for rule in marpol_db:
        keyword_match = any(k.lower() in a_lower for k in rule.get("applies_to_activities", []))
        
        title_lower = str(rule.get("title") or "").lower()
        req_lower = str(rule.get("requirement") or "").lower()
        annex_lower = str(rule.get("annex") or "").lower()
        
        text_match = False
        if a_lower:
            text_match = (
                a_lower in title_lower or a_lower in req_lower or a_lower in annex_lower or
                title_lower in a_lower or annex_lower in a_lower or
                any(word in a_lower for word in title_lower.split() if len(word) > 3)
            )

        if keyword_match or text_match:
            matches.append(rule)

    if not matches:
        return f"No specific MARPOL rules found mapping directly to the activity description: '{activity}'."

    formatted_results = []
    for r in matches:
        formatted_results.append(
            f"⚖️ MARPOL Reference: {r.get('rule_ref')} ({r.get('annex')}) - {r.get('title')}\n"
            f"Core Law Requirement: {r.get('requirement')}\n"
            f"Legal Threshold/Limits: {r.get('threshold')}\n"
            f"Equipment Required on Board: {r.get('equipment_required')}\n"
            f"Mandatory Log/Record Keeping: {r.get('record_keeping')}"
        )
    return "\n\n---\n\n".join(formatted_results)


@mcp.tool()
def ism_requirement(operation_type: str) -> str:
    """
    Retrieve ISM Code (International Safety Management) mandatory system requirements 
    for a given Safety Management System (SMS) element, operation type, or emergency scenario.
    Use this tool when queries ask about drills, procedures, maintenance, master's authority, or safety policies.
    """
    logger.info(f"[TOOL CALL] ism_requirement invoked with operation_type='{operation_type}'")
    matches = []
    op_lower = str(operation_type).lower().strip() if operation_type else ""

    for element in ism_db:
        title_lower = str(element.get("title") or "").lower()
        req_lower = str(element.get("requirement_text") or "").lower()
        
        tag_match = any(tag.lower() in op_lower for tag in element.get("applies_to_operations", []))
        
        text_match = False
        if op_lower:
            text_match = (
                op_lower in title_lower or op_lower in req_lower or
                title_lower in op_lower or
                any(word in op_lower for word in title_lower.split() if len(word) > 3)
            )
            
        if tag_match or text_match:
            matches.append(element)

    if not matches:
        return f"No ISM Code requirements located matching the element parameters: '{operation_type}'."

    formatted_results = []
    for e in matches:
        formatted_results.append(
            f"🛡️ ISM Section: {e.get('ism_section')} - {e.get('title')}\n"
            f"Mandatory System Requirement: {e.get('requirement_text')}\n"
            f"Audit Frequency Track: {e.get('frequency')}\n"
            f"Required Verifiable Evidence: {e.get('evidence_required')}\n"
            f"Associated Certification: {e.get('certificate') or 'None mandatory'}"
        )
    return "\n\n---\n\n".join(formatted_results)

if __name__ == "__main__":
    mcp.run(transport="stdio")