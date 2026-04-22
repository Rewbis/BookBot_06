from typing import TypedDict, Annotated, List, Dict, Any
from langgraph.graph import StateGraph, END
from .state import ProjectRegistry, Phase2Chapter
from .agents import Brainstormer, SkeletonPlotter, SkeletonFormatter
from .llm_client import OllamaClient

class GraphState(TypedDict):
    """The state passed between nodes in LangGraph."""
    registry: ProjectRegistry
    last_agent_output: Dict[str, Any]
    error: Optional[str]

def brainstorm_node(state: GraphState) -> GraphState:
    """Invokes the Brainstormer agent."""
    client = OllamaClient() # In production, this should be injected
    agent = Brainstormer(client)
    
    # Simulate a user prompt for now or fetch from a temporary field
    prompt = "Give me some more depth on the magic system."
    result = agent.run(state['registry'], prompt)
    
    # Update registry (simplified update)
    state['registry'].phase1.premise = result.get('expanded_premise', state['registry'].phase1.premise)
    state['last_agent_output'] = result
    return state

def skeleton_node(state: GraphState) -> GraphState:
    """Invokes the Skeleton Plotter agent."""
    client = OllamaClient()
    agent = SkeletonPlotter(client)
    
    result = agent.run(state['registry'])
    
    if "error" in result:
        state['error'] = result["error"]
        return state
        
    formatter = SkeletonFormatter(client)
    chapters = formatter.run(result)
    
    state['registry'].phase2.chapters = chapters
    state['last_agent_output'] = result
    return state

def create_narrative_graph():
    """Builds the LangGraph for the BookBot narrative engine."""
    workflow = StateGraph(GraphState)
    
    # Add nodes
    workflow.add_node("brainstorm", brainstorm_node)
    workflow.add_node("skeleton", skeleton_node)
    
    # Define edges (simplified for now)
    workflow.set_entry_point("brainstorm")
    workflow.add_edge("brainstorm", "skeleton")
    workflow.add_edge("skeleton", END)
    
    return workflow.compile()
