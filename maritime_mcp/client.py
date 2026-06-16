import logging
from typing import TypedDict, Annotated, List
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from mcp import ClientSession

load_dotenv()
logger = logging.getLogger("maritime_mcp_client")

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]

class MaritimeMCPClient:
    def __init__(self, session: ClientSession, tool_schemas: List):
        self.session = session
        self.tool_schemas = tool_schemas
        
        # Configure alternative high-speed model backend engine
        self.llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.0)
        
        # Enhancement: Add a strict system prompt to control tool evaluation behaviors
        self.system_instruction = (
            "You are an expert Maritime Compliance Auditor. When answering queries, you must rely "
            "strictly on the text returned by the available lookup tools. If a tool returns no matches "
            "or empty results for an activity like bilge water or sewage, state clearly that the specific "
            "threshold is not present in the local database files—DO NOT manufacture or hallucinate "
            "regulations (like Ballast Water rules for bilge water) out of your general knowledge."
        )
        self.graph = self._compile_langgraph_workflow()

    def _compile_langgraph_workflow(self) -> StateGraph:
        builder = StateGraph(AgentState)

        # Node A: Reasoning Backbone
        # Inside call_reasoning_backbone node in client.py
        async def call_reasoning_backbone(state: AgentState):
            from langchain_core.messages import SystemMessage
            messages = [SystemMessage(content=self.system_instruction)] + state["messages"]
            # ... keep the rest of the tool binding and ainvoke logic exactly the same
            langchain_tools = []
            
            for t in self.tool_schemas:
                if t.name == "sire_lookup":
                    @tool(t.name)
                    def sire_lookup(keyword: str = None, ref_id: str = None) -> str:
                        """Dynamic placeholder docstring for LangChain validation pipeline."""
                        pass
                    sire_lookup.description = t.description
                    langchain_tools.append(sire_lookup)
                    
                elif t.name == "marpol_check":
                    @tool(t.name)
                    def marpol_check(activity: str) -> str:
                        """Dynamic placeholder docstring for LangChain validation pipeline."""
                        pass
                    marpol_check.description = t.description
                    langchain_tools.append(marpol_check)
                    
                elif t.name == "ism_requirement":
                    @tool(t.name)
                    def ism_requirement(operation_type: str) -> str:
                        """Dynamic placeholder docstring for LangChain validation pipeline."""
                        pass
                    ism_requirement.description = t.description
                    langchain_tools.append(ism_requirement)
                
            llm_with_tools = self.llm.bind_tools(langchain_tools)
            response = await llm_with_tools.ainvoke(messages)
            return {"messages": [response]}

        # Node B: Remote MCP Tool Executor
        async def execute_mcp_tool(state: AgentState):
            last_message = state["messages"][-1]
            tool_outputs = []
            
            for tool_call in last_message.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                
                logger.info(f"🤖 [CLIENT ACTION] Executing remote tool '{tool_name}' via MCP Server...")
                try:
                    server_result = await self.session.call_tool(tool_name, arguments=tool_args)
                    result_text = "".join([c.text for c in server_result.content if c.type == "text"])
                    
                    tool_outputs.append(ToolMessage(
                        content=result_text, 
                        tool_call_id=tool_call["id"], 
                        name=tool_name
                    ))
                except Exception as e:
                    logger.error(f"Failed to execute tool {tool_name}: {str(e)}")
                    tool_outputs.append(ToolMessage(
                        content=f"Error executing tool: {str(e)}", 
                        tool_call_id=tool_call["id"], 
                        name=tool_name
                    ))
            return {"messages": tool_outputs}

        # Dynamic Memory Safety Router
        def should_continue_loop(state: AgentState):
            messages = state["messages"]
            last_message = messages[-1]
            
            tool_call_count = sum(1 for m in messages if isinstance(m, ToolMessage))
            if tool_call_count >= 3:
                logger.info("🛑 [ROUTER INTERVENTION] Max tool calls reached. Forcing loop convergence.")
                return END
                
            if not getattr(last_message, "tool_calls", None):
                return END
            return "tools"

        # Construct and stitch state graph nodes
        builder.add_node("agent", call_reasoning_backbone)
        builder.add_node("tools", execute_mcp_tool)
        
        builder.add_edge(START, "agent")
        builder.add_conditional_edges("agent", should_continue_loop)
        builder.add_edge("tools", "agent")

        from langgraph.checkpoint.memory import MemorySaver
        return builder.compile(checkpointer=MemorySaver())

    async def execute_agent_loop(self, user_prompt: str, query_index: int = 1) -> str:
        """Streams user query through the compiled state-graph safely isolating threads."""
        config = {"configurable": {"thread_id": f"maritime_evaluation_run_{query_index}"}, "recursion_limit": 10}
        inputs = {"messages": [HumanMessage(content=user_prompt)]}
        
        async for event in self.graph.astream(inputs, config=config):
            for node_name, _ in event.items():
                print(f"📍 [NODE TRANSITION] Activating: '{node_name}'")
                
        final_state = await self.graph.aget_state(config)
        messages_history = final_state.values.get("messages", [])
        
        for msg in reversed(messages_history):
            if isinstance(msg, AIMessage) and msg.content:
                return str(msg.content).strip()
                
        return "Error: Could not extract final answer text from state history graph."