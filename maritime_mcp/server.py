# maritime_mcp/server.py
import os
import logging
import sys
from fastmcp import FastMCP

# 1. Setup structured logging to stderr to prevent stdout pipe corruption
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger("maritime_mcp_server")

# 2. Initialize FastMCP
mcp = FastMCP("Maritime-Compliance-RAG-Server")

# 3. Import our decoupled, standalone RAG system modules
try:
    from rag.ingestion.vector_db import vector_store_instance
    from rag.generation.prompter import build_grounded_compliance_context
    
    # Trigger database cache check and seeding on boot-up
    vector_store_instance.seed_all_collections()
    RAG_OPERATIONAL = True
    logger.info("🟢 [SERVER ROOT] Decoupled RAG Component safely wired and operational.")
except Exception as e:
    logger.error(f"❌ [SERVER FAIL] Failed to initialize RAG module: {str(e)}")
    RAG_OPERATIONAL = False


@mcp.tool()
def marpol_check(activity: str) -> str:
    """
    Given a vessel operational activity description, look up applicable MARPOL Annex rules 
    using vector similarity semantic search. Use this tool whenever the user mentions 
    discharging waste, bilge water, sewage, fuel sulphur content, or transiting special areas/ECAs.
    """
    logger.info(f"[MCP TOOL CALL] marpol_check invoked for: '{activity}'")
    
    if not RAG_OPERATIONAL:
        return "Error: Internal RAG retrieval component is currently un-operational."
        
    # Query our generation layer to construct a grounded context envelope
    context_payload = build_grounded_compliance_context("marpol", activity, max_chunks=2)
    return context_payload


@mcp.tool()
def sire_lookup(keyword: str = None, ref_id: str = None) -> str:
    """
    Look up a SIRE 2.0 inspection question using semantic similarity vector search.
    Use this tool when the inspector references a specific question code or asks about particular equipment checks.
    """
    logger.info(f"[MCP TOOL CALL] sire_lookup invoked for keyword='{keyword}', ref_id='{ref_id}'")
    
    if not RAG_OPERATIONAL:
        return "Error: Internal RAG retrieval component is currently un-operational."
        
    # Route target argument parameter based on what the agent fills
    search_query = str(ref_id) if ref_id else str(keyword)
    
    context_payload = build_grounded_compliance_context("sire", search_query, max_chunks=2)
    return context_payload


@mcp.tool()
def ism_requirement(operation_type: str) -> str:
    """
    Retrieve ISM Code mandatory system requirements using vector similarity semantic search.
    Use this tool when queries ask about drills, procedures, maintenance, master's authority, or safety policies.
    """
    logger.info(f"[MCP TOOL CALL] ism_requirement invoked for: '{operation_type}'")
    
    if not RAG_OPERATIONAL:
        return "Error: Internal RAG retrieval component is currently un-operational."
        
    context_payload = build_grounded_compliance_context("ism", operation_type, max_chunks=2)
    return context_payload


if __name__ == "__main__":
    mcp.run(transport="stdio")