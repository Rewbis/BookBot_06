import streamlit as st
import os
import json
from datetime import datetime
from src.core.state import ProjectRegistry
from src.core.llm_client import OllamaClient
from src.utils.importer_05 import Importer05

# Page Config
st.set_page_config(page_title="BookBot 06", layout="wide", page_icon="📖")

# Custom CSS for Sticky Header
st.markdown("""
    <style>
    /* Reduce padding at the top */
    .block-container {
        padding-top: 1rem;
    }
    
    /* Make the header sticky */
    div[data-testid="stVerticalBlock"] > div:has(div.sticky-header) {
        position: sticky;
        top: 2.875rem;
        background-color: #0E1117;
        z-index: 999;
        padding-bottom: 10px;
        border-bottom: 1px solid #31333F;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize Session State
if "registry" not in st.session_state:
    st.session_state.registry = ProjectRegistry()
if "client" not in st.session_state:
    st.session_state.client = OllamaClient()

# --- Sidebar ---
with st.sidebar:
    st.title("Project Controls")
    st.markdown(f"**Title**: {st.session_state.registry.metadata.book_title}")
    st.markdown(f"**Current Phase**: {st.session_state.registry.current_phase}")
    
    st.divider()
    
    # Save/Load
    if st.button("Save Registry", help="Save the current project state to /logs"):
        path = f"logs/registry_{st.session_state.registry.project_id}.json"
        with open(path, 'w') as f:
            json.dump(st.session_state.registry.model_dump(mode='json'), f, indent=4)
        st.success(f"Saved to {path}")

    # Import 05 Log
    st.header("Import Legacy")
    uploaded_file = st.file_uploader("Upload BookBot 05 Log (.json)", type="json")
    if uploaded_file:
        try:
            legacy_data = json.load(uploaded_file)
            new_registry = Importer05.migrate_to_registry(legacy_data)
            st.session_state.registry = new_registry
            st.success("Successfully imported legacy log!")
            st.rerun()
        except Exception as e:
            st.error(f"Import failed: {e}")

# --- Main UI ---
header_container = st.container()
with header_container:
    st.markdown('<div class="sticky-header"></div>', unsafe_allow_html=True)
    st.title("📖 BookBot 06: Sovereign Narrative Engine")

    tabs = st.tabs([
        "1. Plotting", 
        "2. Structuring (Skeleton)", 
        "3. Story Beats", 
        "4. Drafting", 
        "5. Manuscript", 
        "6. Publish"
    ])

from src.ui.views.plotting_view import render_plotting_view
from src.ui.views.skeleton_view import render_skeleton_view

# Plotting View
with tabs[0]:
    render_plotting_view(st.session_state.registry)

# Skeleton View
with tabs[1]:
    render_skeleton_view(st.session_state.registry)

# Placeholder for other tabs
for i in range(2, 6):
    with tabs[i]:
        st.info(f"Phase {i+1} logic not yet implemented in this preview.")
