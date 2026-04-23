from typing import TypedDict, Annotated, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from .state import ProjectRegistry, AgentMessage, EntityType, KnowledgeState, Chapter
from .agents import Architect, DevilsAdvocate, Librarian, Auditor, ActionWriter, SensoryAgent, DialogueSpecialist, Stylist, ShadowAgent, ContinuityExpert, SkeletonPlotter, SkeletonFormatter
from .llm_client import OllamaClient
from .world_bible import WorldBibleManager
from langgraph.graph import START

class GraphState(TypedDict):
    """The state passed between nodes in the Blackboard Orchestrator."""
    registry: ProjectRegistry
    command: Optional[str] # "brainstorm", "draft", "librarian", etc.
    input_data: Optional[Dict[str, Any]] # e.g. {"beats": "..."}
    last_agent_output: Dict[str, Any]
    error: Optional[str]
    context: Optional[str] # Temporary context for RAG
    client: Optional[OllamaClient]

def brainstorm_node(state: GraphState) -> GraphState:
    """Expansion phase with Devil's Advocate intervention."""
    client = state.get('client') or OllamaClient()
    arch = Architect(client)
    da = DevilsAdvocate(client)
    
    # Use prompt from input_data if available, else default
    prompt = (state.get('input_data') or {}).get('prompt', "Expand on the current premise and suggest new directions.")
    
    # 1. Generate expansion
    res = arch.run(state['registry'], prompt)
    
    # 2. Challenge with Devil's Advocate
    plan_str = str(res.get('plan', ''))
    critique = da.run(state['registry'], plan_str)
    
    # Update History (Agent Debate)
    state['registry'].history.append(AgentMessage(sender="Architect", content=plan_str))
    state['registry'].history.append(AgentMessage(sender="Devil's Advocate", content=str(critique.get('pivot_suggestion', ''))))
    
    state['last_agent_output'] = critique
    return state

def librarian_node(state: GraphState) -> GraphState:
    """Artifact population and world-building expansion."""
    client = state.get('client') or OllamaClient()
    lib = Librarian(client)
    manager = WorldBibleManager(state['registry'])
    
    topic = (state.get('input_data') or {}).get('topic', "")
    context = manager.get_context_chunk(topic)
    
    res = lib.run(state['registry'], topic, context)
    new_entities = res.get('new_entities', [])
    
    for ent_data in new_entities:
        name = ent_data.get('name', 'Unnamed')
        e_type = EntityType.LORE
        
        manager.upsert_entity(name, e_type, ent_data.get('description', ''), ent_data.get('attributes', {}))
        
    state['last_agent_output'] = res
    return state

def plot_skeleton_node(state: GraphState) -> GraphState:
    """Generates a high-level plot outline."""
    client = state.get('client') or OllamaClient()
    plotter = SkeletonPlotter(client)
    formatter = SkeletonFormatter(client)
    
    # 1. Plot
    raw_skeleton = plotter.run(state['registry'])
    
    # 2. Format
    chapters = formatter.run(raw_skeleton)
    
    # Update registry
    state['registry'].chapters = chapters
    
    state['last_agent_output'] = {"chapters": chapters}
    return state

def multi_pass_draft_node(state: GraphState) -> GraphState:
    """4-Pass Drafting sequence: Action -> Sensory -> Dialogue -> Style."""
    client = state.get('client') or OllamaClient()
    continuity_expert = ContinuityExpert(client)
    action_writer = ActionWriter(client)
    sensory_agent = SensoryAgent(client)
    dialogue_specialist = DialogueSpecialist(client)
    stylist = Stylist(client)
    shadow_agent = ShadowAgent(client)
    auditor = Auditor(client)
    
    # Use beats from input_data
    beats = (state.get('input_data') or {}).get('beats', "The scene begins.")
    chapter_index = (state.get('input_data') or {}).get('chapter_index', -1)
    
    # Pass 0: Continuity Check
    continuity_brief = continuity_expert.run(state['registry'], beats, chapter_index)
    
    # Pass 1: Action
    p1 = action_writer.run(state['registry'], beats, continuity_brief)
    
    if "Error connecting to Ollama" in p1:
        state['error'] = f"Drafting failed at Pass 1: {p1}"
        return state
    
    # Pass 2: Sensory
    p2 = sensory_agent.run(state['registry'], p1)
    
    # Pass 3: Dialogue
    p3 = dialogue_specialist.run(state['registry'], p2)
    
    # Pass 4: Style
    p4 = stylist.run(state['registry'], p3)
    
    # Audit
    manager = WorldBibleManager(state['registry'])
    context = manager.get_context_chunk(beats)
    audit_res = auditor.run(state['registry'], p4, context)
    
    # Shadow Analysis
    shadow_res = shadow_agent.run(state['registry'], p4)
    # Update Shadow Context
    for update in shadow_res.get('knowledge_updates', []):
        char = update.get('character', 'Unknown')
        if char not in state['registry'].shadow_context.character_knowledge:
            state['registry'].shadow_context.character_knowledge[char] = KnowledgeState(character_name=char)
        
        ks = state['registry'].shadow_context.character_knowledge[char]
        content = update.get('content', '')
        u_type = update.get('type', 'fact').lower()
        
        if u_type == 'fact' and content not in ks.known_facts:
            ks.known_facts.append(content)
        elif u_type == 'suspicion' and content not in ks.suspicions:
            ks.suspicions.append(content)
        elif u_type == 'secret' and content not in ks.hidden_secrets:
            ks.hidden_secrets.append(content)

    for sub in shadow_res.get('subtext', []):
        if sub not in state['registry'].shadow_context.active_subtext:
            state['registry'].shadow_context.active_subtext.append(sub)
            
    for irony in shadow_res.get('irony', []):
        if irony not in state['registry'].shadow_context.dramatic_irony:
            state['registry'].shadow_context.dramatic_irony.append(irony)

    # Update registry with draft
    if chapter_index >= 0 and chapter_index < len(state['registry'].chapters):
        state['registry'].chapters[chapter_index].content = p4
        state['registry'].chapters[chapter_index].audit_logs = audit_res.get('issues', [])
    else:
        # Fallback to appending if index is invalid
        state['registry'].chapters.append(Chapter(
            chapter_number=len(state['registry'].chapters) + 1,
            title=f"New Chapter {len(state['registry'].chapters) + 1}",
            content=p4,
            audit_logs=audit_res.get('issues', [])
        ))
    
    state['last_agent_output'] = {
        "final_draft": p4, 
        "audit": audit_res, 
        "shadow": shadow_res,
        "continuity": continuity_brief
    }
    return state

def router(state: GraphState):
    """Routes to the correct node based on the command."""
    cmd = state.get("command")
    if cmd == "brainstorm":
        return "brainstorm"
    elif cmd == "draft":
        return "draft"
    elif cmd == "librarian":
        return "librarian"
    elif cmd == "plot_skeleton":
        return "plot_skeleton"
    return "error"

def error_node(state: GraphState) -> GraphState:
    """Fallback node for unknown commands."""
    state['error'] = f"Unknown or missing command: {state.get('command')}"
    return state

def create_blackboard_graph():
    """Builds the Blackboard LangGraph for BookBot_06."""
    workflow = StateGraph(GraphState)
    
    workflow.add_node("brainstorm", brainstorm_node)
    workflow.add_node("draft", multi_pass_draft_node)
    workflow.add_node("librarian", librarian_node)
    workflow.add_node("plot_skeleton", plot_skeleton_node)
    workflow.add_node("error", error_node)
    
    # Set entry point to a routing logic
    workflow.add_conditional_edges(START, router)
    
    workflow.add_edge("brainstorm", END)
    workflow.add_edge("draft", END)
    workflow.add_edge("librarian", END)
    workflow.add_edge("plot_skeleton", END)
    workflow.add_edge("error", END)
    
    return workflow.compile()
