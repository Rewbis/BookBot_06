import streamlit as st
from datetime import datetime
from src.core.world_bible import WorldBibleManager

def mark_dirty():
    """Sets the registry as updated so the save reminder appears."""
    st.session_state.registry.last_updated = datetime.now()

def run_orchestrator(command: str, input_data: dict = None):
    """Invokes the Narrative Orchestrator with a specific command."""
    from src.core.orchestrator import create_narrative_graph
    
    # We get the graph but avoid caching it here to prevent pickling issues with session state
    graph = create_narrative_graph()
    
    initial_state = {
        "registry": st.session_state.registry,
        "command": command,
        "input_data": input_data,
        "last_agent_output": {},
        "error": None,
        "context": None,
        "client": st.session_state.client
    }
    
    # Run the graph
    result = graph.invoke(initial_state)
    
    # Update global state
    st.session_state.registry = result["registry"]
    # Refresh manager with new registry
    st.session_state.world_manager = WorldBibleManager(st.session_state.registry)
    return result
