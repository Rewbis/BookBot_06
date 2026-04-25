import streamlit as st
import os
from datetime import datetime
from src.core.state import ProjectRegistry
from src.core.llm_client import OllamaClient
from src.utils.project_manager import ProjectManager
from src.core.world_bible import WorldBibleManager

# Import Views
from src.ui.views.phase1_brainstorming import render_phase1
from src.ui.views.phase2_structuring import render_phase2
from src.ui.views.phase3_world_building import render_phase3
from src.ui.views.phase4_drafting import render_phase4
from src.ui.views.phase5_audit import render_phase5
from src.ui.views.phase6_export import render_phase6

# Page Config
st.set_page_config(page_title="BookBot 06: Narrative Engine", layout="wide", page_icon="📖")

# Initialize Managers in Session State
if "pm" not in st.session_state:
    st.session_state.pm = ProjectManager()
if "registry" not in st.session_state:
    st.session_state.registry = ProjectRegistry()
if "client" not in st.session_state:
    st.session_state.client = OllamaClient()
if "world_manager" not in st.session_state:
    st.session_state.world_manager = WorldBibleManager(st.session_state.registry)

# --- Sidebar ---
with st.sidebar:
    st.title("Sovereign Control")
    
    # Project Selector
    projects = st.session_state.pm.list_projects()
    project_titles = [f"{p['title']} ({p['id']})" for p in projects]
    
    if not project_titles:
        st.info("No projects found. Create one to get started.")
        selected_idx = None
    else:
        selected_idx = st.selectbox("Select Project", options=range(len(project_titles)), format_func=lambda i: project_titles[i])
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Load", use_container_width=True):
            if selected_idx is not None:
                project_id = projects[selected_idx]["id"]
                st.session_state.registry = st.session_state.pm.load_project(project_id)
                st.session_state.world_manager = WorldBibleManager(st.session_state.registry)
                st.rerun()
    with col2:
        if st.button("New", use_container_width=True):
            st.session_state.registry = st.session_state.pm.create_new_project("New Story Spark")
            st.session_state.world_manager = WorldBibleManager(st.session_state.registry)
            st.rerun()

    st.divider()
    
    # Telemetry
    st.subheader("Project Telemetry")
    tokens = st.session_state.registry.get_token_counts()
    st.metric("Total Tokens", f"{tokens['Total']:,}")
    
    # File Size
    file_path = f"projects/project_{st.session_state.registry.project_id}.json"
    if os.path.exists(file_path):
        size_kb = os.path.getsize(file_path) / 1024
        st.metric("Registry Size", f"{size_kb:.2f} KB")

    st.divider()
    
    if st.button("💾 Save Snapshot", use_container_width=True):
        st.session_state.pm.save_project(st.session_state.registry)
        st.success("Snapshot saved!")
        st.session_state.last_save_time = datetime.now()

    # Save Reminder
    if "last_save_time" not in st.session_state:
        st.session_state.last_save_time = datetime.now()
    
    if st.session_state.registry.last_updated > st.session_state.last_save_time:
        st.warning("⚠️ Unsaved Changes")

# --- Main UI ---
st.title("📖 BookBot 06: Narrative Engine")

tabs = st.tabs([
    "Phase 1: Brainstorming", 
    "Phase 2: Structuring",
    "Phase 3: World Building", 
    "Phase 4: Multi-Pass Drafting", 
    "Phase 5: Audit & Shadow",
    "Phase 6: Export & Marketing"
])

with tabs[0]: render_phase1()
with tabs[1]: render_phase2()
with tabs[2]: render_phase3()
with tabs[3]: render_phase4()
with tabs[4]: render_phase5()
with tabs[5]: render_phase6()
