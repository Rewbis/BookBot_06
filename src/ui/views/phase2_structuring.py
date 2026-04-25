import streamlit as st
import pandas as pd
from src.core.state import Chapter
from src.ui.utils import run_orchestrator, mark_dirty

def reindex_chapters():
    """Ensures chapter numbers are sequential based on current list order."""
    # We do NOT sort here, because the list order is the desired sequence
    for i, chap in enumerate(st.session_state.registry.chapters):
        chap.chapter_number = i + 1
    mark_dirty()

def render_phase2():
    st.header("💀 Phase 2: Structuring")
    st.info("The Skeleton: Build your chapter-by-chapter outline. Each block represents a narrative unit.")
    
    # --- Toolbar ---
    col_t1, col_t2 = st.columns([1, 4])
    with col_t1:
        target = st.session_state.registry.target_chapters
        if st.button(f"🗺️ 02a_skeleton_plotter: Plot {target} Chapters", help="The Skeleton Plotter will generate a full draft outline."):
            with st.status("Orchestrator: 02a_skeleton_plotter plotting...", expanded=True) as status:
                run_orchestrator("plot_skeleton")
                status.update(label="Skeleton Generated!", state="complete")
                st.rerun()
    
    st.divider()

    # --- Chapter Notebook ---
    chapters = st.session_state.registry.chapters
    if not chapters:
        st.info("No chapters yet. Trigger the Plotter above or add a manual chapter.")
        if st.button("➕ Add First Chapter"):
            st.session_state.registry.chapters.append(Chapter(chapter_number=1, title="New Chapter", summary=""))
            st.rerun()
    else:
        for i, chap in enumerate(chapters):
            with st.container():
                # Notebook header with chapter number and Title
                col_h1, col_h2 = st.columns([0.5, 4.5])
                with col_h1:
                    st.markdown(f"### #{chap.chapter_number}")
                with col_h2:
                    chap.title = st.text_input(f"Title", chap.title, key=f"title_{i}", on_change=mark_dirty, label_visibility="collapsed")
                
                # Summary area (The core output)
                chap.summary = st.text_area(f"Summary", chap.summary, height=100, key=f"summary_{i}", on_change=mark_dirty, label_visibility="collapsed", placeholder="What happens in this chapter? (3-4 sentences)")
                
                # Jupyter-style Controls
                ctrl1, ctrl2, ctrl3, ctrl4, ctrl_spacer = st.columns([1, 1, 1, 1, 4])
                with ctrl1:
                    if st.button("⬆️ Above", key=f"add_above_{i}", help="Add chapter above"):
                        chapters.insert(i, Chapter(chapter_number=0, title="New Chapter", summary=""))
                        reindex_chapters()
                        st.rerun()
                with ctrl2:
                    if st.button("⬇️ Below", key=f"add_below_{i}", help="Add chapter below"):
                        chapters.insert(i + 1, Chapter(chapter_number=0, title="New Chapter", summary=""))
                        reindex_chapters()
                        st.rerun()
                with ctrl3:
                    if st.button("🗑️ Del", key=f"del_{i}", help="Delete this chapter"):
                        chapters.pop(i)
                        reindex_chapters()
                        st.rerun()
                with ctrl4:
                    if st.button("💾 Save", key=f"save_{i}"):
                        st.session_state.pm.save_project(st.session_state.registry)
                        st.success(f"Chapter {chap.chapter_number} saved!")

                st.divider()

    if st.button("💾 Save Full Skeleton", use_container_width=True):
        st.session_state.pm.save_project(st.session_state.registry)
        st.success("Full skeleton persisted!")
