from typing import TypedDict, Annotated, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from .state import ProjectRegistry, AgentMessage, EntityType, KnowledgeState, Chapter, Conflict
from .agents import (
    Phase01a_Architect, Phase01b_DevilsAdvocate, Phase03a_Librarian, 
    Phase04ab_ContinuityAction, Phase04cd_SensoryDialogue, Phase04e_Stylist, 
    Phase05ab_AuditShadow, Phase02a_SkeletonPlotter, Phase02b_SkeletonFormatter, 
    Phase06a_MarketingAgent
)
from .llm_client import OllamaClient
from .world_bible import WorldBibleManager
from langgraph.graph import START

class GraphState(TypedDict):
    """The state passed between nodes in the Phased Pipeline Orchestrator."""
    registry: ProjectRegistry
    command: Optional[str] # "brainstorm", "draft", "librarian", etc.
    input_data: Optional[Dict[str, Any]] # e.g. {"beats": "..."}
    last_agent_output: Dict[str, Any]
    error: Optional[str]
    context: Optional[str] # Temporary context for RAG
    client: Optional[OllamaClient]

def brainstorm_node(state: GraphState) -> GraphState:
    """Expansion phase with Devil's Advocate intervention.
    
    Sequence:
    1. Architect generates initial expansion.
    2. Devil's Advocate critiques and suggests a pivot.
    3. Architect incorporates critique for a final refined vision.
    """
    client = state.get('client') or OllamaClient()
    arch = Phase01a_Architect(client)
    da = Phase01b_DevilsAdvocate(client)
    
    # Use prompt from input_data if available, else default
    prompt = (state.get('input_data') or {}).get('prompt', "Expand on the current premise and suggest new directions.")
    
    # 1. Initial Expansion (Architect)
    res1 = arch.run(state['registry'], prompt)
    plan1 = str(res1.get('plan', 'No plan generated.'))
    
    # 2. Challenge (Devil's Advocate)
    critique = da.run(state['registry'], plan1)
    pivot = str(critique.get('pivot_suggestion', 'No pivot suggested.'))
    
    # 3. Final Refinement (Architect)
    refine_prompt = f"Original Plan: {plan1}\n\nCritique: {pivot}\n\nIncorporate this critique and provide a FINAL, hardened version of the vision."
    res2 = arch.run(state['registry'], refine_prompt)
    plan2 = str(res2.get('plan', 'No refined plan generated.'))
    
    # Update History and Registry
    state['registry'].final_vision = plan2
    state['registry'].history.append(AgentMessage(sender="01a_architect", content=plan1))
    state['registry'].history.append(AgentMessage(sender="01b_devils_advocate", content=pivot, metadata=critique))
    state['registry'].history.append(AgentMessage(sender="01a_architect", content=plan2))
    
    state['last_agent_output'] = {
        "initial": plan1,
        "critique": critique,
        "final": plan2
    }
    return state

def librarian_node(state: GraphState) -> GraphState:
    """Artifact population and world-building expansion."""
    client = state.get('client') or OllamaClient()
    lib = Phase03a_Librarian(client)
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
    state['registry'].history.append(AgentMessage(sender="03a_librarian", content=f"Added {len(new_entities)} new entities to the Bible.", metadata=res))
    return state

def plot_skeleton_node(state: GraphState) -> GraphState:
    """Generates a high-level plot outline."""
    client = state.get('client') or OllamaClient()
    plotter = Phase02a_SkeletonPlotter(client)
    formatter = Phase02b_SkeletonFormatter(client)
    
    # 1. Plot
    raw_skeleton = plotter.run(state['registry'])
    
    # 2. Format
    chapters = formatter.run(raw_skeleton)
    
    # Update registry
    state['registry'].chapters = chapters
    
    state['last_agent_output'] = {"chapters": chapters}
    state['registry'].history.append(AgentMessage(sender="02a_skeleton_plotter", content=f"Generated {len(chapters)} chapter beats."))
    return state

def multi_pass_draft_node(state: GraphState) -> GraphState:
    """3-Step Drafting sequence: Continuity/Action -> Sensory/Dialogue -> Style.
    Utilizes local state for sequential sculpting.
    """
    client = state.get('client') or OllamaClient()
    ca_agent = Phase04ab_ContinuityAction(client)
    sd_agent = Phase04cd_SensoryDialogue(client)
    stylist = Phase04e_Stylist(client)
    audit_shadow = Phase05ab_AuditShadow(client)
    
    # Use beats from input_data
    beats = (state.get('input_data') or {}).get('beats', "The scene begins.")
    chapter_index = (state.get('input_data') or {}).get('chapter_index', -1)
    
    # Step 1: Continuity & Action
    p1 = ca_agent.run(state['registry'], beats, chapter_index)
    if "Error connecting to Ollama" in p1:
        state['error'] = f"Drafting failed at Step 1: {p1}"
        return state
    
    # Step 2: Sensory & Dialogue
    p2 = sd_agent.run(state['registry'], p1)
    if "pass failed" in p2 or "Error connecting" in p2:
        state['error'] = f"Drafting failed at Step 2: {p2}"
        return state
    
    # Step 3: Style
    final_draft = stylist.run(state['registry'], p2)
    if "pass failed" in final_draft or "Error connecting" in final_draft:
        state['error'] = f"Drafting failed at Step 3: {final_draft}"
        return state
    
    # Audit & Shadow Analysis
    analysis = audit_shadow.run(state['registry'], final_draft)
    
    # Update Shadow Context
    for update in analysis.get('knowledge_updates', []):
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

    for sub in analysis.get('subtext', []):
        if sub not in state['registry'].shadow_context.active_subtext:
            state['registry'].shadow_context.active_subtext.append(sub)
            
    for irony in analysis.get('irony', []):
        if irony not in state['registry'].shadow_context.dramatic_irony:
            state['registry'].shadow_context.dramatic_irony.append(irony)

    # Update registry with draft
    issues = analysis.get('issues', [])
    if chapter_index >= 0 and chapter_index < len(state['registry'].chapters):
        state['registry'].chapters[chapter_index].content = final_draft
        state['registry'].chapters[chapter_index].audit_logs = issues
    else:
        # Fallback to appending if index is invalid
        state['registry'].chapters.append(Chapter(
            chapter_number=len(state['registry'].chapters) + 1,
            title=f"New Chapter {len(state['registry'].chapters) + 1}",
            content=final_draft,
            audit_logs=issues
        ))
    
    # Populate global conflict registry
    for issue in issues:
        state['registry'].conflict_registry.append(Conflict(
            description=issue.get('description', ''),
            severity=issue.get('severity', 'medium')
        ))
    
    # Update History
    state['registry'].history.append(AgentMessage(sender="04ab_continuity_action", content=p1))
    state['registry'].history.append(AgentMessage(sender="04cd_sensory_dialogue", content=p2))
    state['registry'].history.append(AgentMessage(sender="04e_stylist", content=final_draft))
    state['registry'].history.append(AgentMessage(sender="05ab_audit_shadow", content=f"Found {len(issues)} issues.", metadata=analysis))

    state['last_agent_output'] = {
        "final_draft": final_draft, 
        "audit": analysis, 
        "shadow": analysis
    }
    return state
def marketing_node(state: GraphState) -> GraphState:
    """Generates marketing copy for the project."""
    client = state.get('client') or OllamaClient()
    marketer = Phase06a_MarketingAgent(client)
    
    task = (state.get('input_data') or {}).get('task', "Write a back-cover blurb.")
    res = marketer.run(state['registry'], task)
    
    state['last_agent_output'] = {"marketing_copy": res}
    state['registry'].history.append(AgentMessage(sender="06a_marketing_agent", content=res))
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
    elif cmd == "marketing":
        return "marketing"
    return "error"

def error_node(state: GraphState) -> GraphState:
    """Fallback node for unknown commands."""
    state['error'] = f"Unknown or missing command: {state.get('command')}"
    return state

def create_narrative_graph():
    """Builds the Phased Pipeline LangGraph for BookBot_06."""
    workflow = StateGraph(GraphState)
    
    workflow.add_node("brainstorm", brainstorm_node)
    workflow.add_node("draft", multi_pass_draft_node)
    workflow.add_node("librarian", librarian_node)
    workflow.add_node("plot_skeleton", plot_skeleton_node)
    workflow.add_node("marketing", marketing_node)
    workflow.add_node("error", error_node)
    
    # Set entry point to a routing logic
    workflow.add_conditional_edges(START, router)
    
    workflow.add_edge("brainstorm", END)
    workflow.add_edge("draft", END)
    workflow.add_edge("librarian", END)
    workflow.add_edge("plot_skeleton", END)
    workflow.add_edge("marketing", END)
    workflow.add_edge("error", END)
    
    return workflow.compile()
