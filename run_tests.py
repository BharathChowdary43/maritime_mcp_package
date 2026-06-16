import asyncio
import os
import json
import sys
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp import ClientSession
from maritime_mcp.client import MaritimeMCPClient

# Define structural query boundaries
test_queries = [
    "A vessel is 8nm offshore and needs to discharge bilge water. The SIRE inspector also asked about the passage plan during the last inspection. What MARPOL rules apply, and which SIRE question should the Chief Officer review?",
    "We are in the Baltic Sea and need to discharge treated sewage. What MARPOL restrictions apply, and which SIRE chapter would an inspector use to assess our compliance records?",
    "We are transiting the North Sea ECA and our bunker delivery note shows 0.08% sulphur fuel. The SIRE inspector also wants to see our VDR annual performance test certificate and our last enclosed space entry permit. Are we MARPOL compliant, and which SIRE questions cover the other two findings?"
]

async def run_end_to_end_evaluation():
    print("🚀 [INIT] Initializing Automated End-to-End Test Suite...")
    
    python_exe = sys.executable
    print(f"🎯 [ENV] Route target execution engine: {python_exe}")
    
    server_params = StdioServerParameters(
        command=python_exe,
        args=["maritime_mcp/server.py"],
        env=os.environ.copy()
    )
    
    print("📦 [SERVER] Spawning managed background MCP server...")
    
    async with stdio_client(server_params) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            print("🤝 [PROTOCOL] MCP Handshake complete. Session active.")
            
            # Run lifecycle configuration server tool discoverability synchronization passes
            await session.initialize()
            discovered_tools = await session.list_tools()
            
            client = MaritimeMCPClient(session, discovered_tools.tools)
            evaluation_matrix = {}
            
            for idx, query in enumerate(test_queries, 1):
                print(f"\n🔮 [AGENT EXECUTION] Running Evaluation Query {idx} of 3...")
                print(f"Prompt: \"{query}\"\n")
                
                final_answer = await client.execute_agent_loop(query, query_index=idx)
                print(f"✅ [QUERY {idx} COMPLETE] Response generated successfully.")
                
                evaluation_matrix[f"query_{idx}"] = {
                    "prompt": query,
                    "response": final_answer
                }
                
            # Render target compliance file outputs out to disk
            output_filepath = "./query_output.json"
            with open(output_filepath, "w", encoding="utf-8") as f:
                json.dump(evaluation_matrix, f, indent=2, ensure_ascii=False)
                
            print(f"\n🎉 [SUCCESS] Evaluation data cleanly captured in: {output_filepath}")

if __name__ == "__main__":
    asyncio.run(run_end_to_end_evaluation())