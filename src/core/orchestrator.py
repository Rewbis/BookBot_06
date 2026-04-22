from typing import TypedDict, Annotated, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from .state import ProjectRegistry, AgentMessage
from .agents import Architect, DevilsAdvocate, Librarian, Auditor, ActionWriter, SensoryAgent, DialogueSpecialist
from .llm_client import OllamaClient
from .world_bible import WorldBibleManager

class GraphState(TypedDict):
    """The state passed between nodes in the Blackboard Orchestrator."""
    registry: ProjectRegistry
    last_agent_output: Dict[str, Any]
    error: Optional[str]
    context: Optional[str] # Temporary context for RAG

def brainstorm_node(state: GraphState) -> GraphState:
    """Expansion phase with Devil's Advocate intervention."""
    client = OllamaClient()
    arch = Architect(client)
    da = DevilsAdvocate(client)
    
    # 1. Generate expansion
    res = arch.run(state['registry'], "Expand on the current premise and suggest new directions.")
    
    # 2. Challenge with Devil's Advocate
    critique = da.run(state['registry'], res.get('plan', ''))
    
    # Update History (Agent Debate)
    state['registry'].history.append(AgentMessage(sender="Architect", content=str(res.get('plan'))))
    state['registry'].history.append(AgentMessage(sender="Devil's Advocate", content=str(critique.get('pivot_suggestion'))))
    
    state['last_agent_output'] = critique
    return state

def multi_pass_draft_node(state: GraphState) -> GraphState:
    """3-Pass Drafting sequence: Action -> Sensory -> Dialogue."""
    client = OllamaClient()
    action_writer = ActionWriter(client)
    sensory_agent = SensoryAgent(client)
    dialogue_specialist = DialogueSpecialist(client)
    auditor = Auditor(client)
    
    beats = "The keeper enters the lantern room and finds the light is cold."
    
    # Pass 1: Action
    p1 = action_writer.run(state['registry'], beats)
    
    # Pass 2: Sensory
    p2 = sensory_agent.run(state['registry'], p1)
    
    # Pass 3: Dialogue
    p3 = dialogue_specialist.run(state['registry'], p2)
    
    # Audit
    manager = WorldBibleManager(state['registry'])
    context = manager.get_context_chunk(beats)
    audit_res = auditor.run(state['registry'], p3, context)
    
    # Update registry with draft
    state['registry'].chapters.append({
        "chapter_number": len(state['registry'].chapters) + 1,
        "content": p3,
        "audit_logs": audit_res.get('issues', [])
    })
    
    state['last_agent_output'] = {"final_draft": p3, "audit": audit_res}
    return state

def create_blackboard_graph():
    """Builds the Blackboard LangGraph for BookBot_06."""
    workflow = StateGraph(GraphState)
    
    workflow.add_node("brainstorm", brainstorm_node)
    workflow.add_node("draft", multi_pass_draft_node)
    
    workflow.set_entry_point("brainstorm")
    workflow.add_edge("brainstorm", "draft")
    workflow.add_edge("draft", END)
    
    return workflow.compile()
