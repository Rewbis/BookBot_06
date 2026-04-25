import streamlit as st
from src.core.state import EntityType
from src.ui.utils import run_orchestrator, mark_dirty

def render_phase1():
    st.header("🏗️ Phase 1: Brainstorming")
    st.info("The Brain: Define your 'North Star' and watch the debate unfold between the Architect and the Devil's Advocate.")
    
    # 1. Top of Body: Project Identity
    col_t1, col_t2, col_t3, col_t4 = st.columns([2, 1, 1, 1])
    with col_t1:
        st.session_state.registry.title = st.text_input("📖 Book Title", st.session_state.registry.title, help="The working title of your masterpiece.", on_change=mark_dirty)
    with col_t2:
        st.session_state.registry.tone = st.selectbox("🎭 Tone", ["Dark", "Whimsical", "Hard Sci-Fi", "Noir", "Cozy", "Epic"], index=0, on_change=mark_dirty)
    with col_t3:
        st.session_state.registry.target_chapters = st.number_input("📚 Chapters", min_value=1, max_value=100, value=st.session_state.registry.target_chapters, on_change=mark_dirty)
    with col_t4:
        st.session_state.registry.target_word_count = st.number_input("📝 Word Count", min_value=1000, max_value=500000, step=5000, value=st.session_state.registry.target_word_count, on_change=mark_dirty)

    # 2. Core Input
    st.session_state.registry.premise = st.text_area("🔮 Core Premise", st.session_state.registry.premise, height=150, placeholder="Enter your story's 'Spark' here...", help="The Architect will expand this, and the Devil's Advocate will challenge it.", on_change=mark_dirty)
    
    col_btn, col_save = st.columns([1, 1])
    with col_btn:
        if st.button("🔥 Launch 3-Step Brainstorm", use_container_width=True):
            with st.status("Orchestrating Phase 1 Debate...", expanded=True) as status:
                run_orchestrator("brainstorm", {"prompt": st.session_state.registry.premise})
                status.update(label="Debate Complete!", state="complete")
                st.rerun()
    
    st.divider()
    
    # 3. Structured Debate Sequence
    st.subheader("🗣️ The Blackboard Debate")
    
    if not st.session_state.registry.history:
        st.info("No active debate. Enter a premise and launch the brainstorm to begin.")
    else:
        # We look for the last 3 messages to show the latest sequence
        # Architect (Initial) -> DA -> Architect (Refined)
        history = st.session_state.registry.history
        
        # Display in chronological order for the flow
        for i, msg in enumerate(history):
            if "Architect (Initial)" in msg.sender:
                with st.chat_message("user", avatar="🏗️"):
                    st.write("**Architect (Phase 1a: Expansion)**")
                    st.write(msg.content)
                    if st.button("Save as World Lore", key=f"save_lore_init_{i}"):
                        st.session_state.world_manager.upsert_entity(f"Concept {i}", EntityType.LORE, msg.content)
                        st.success("Added to World Bible!")
            
            elif "Devil's Advocate" in msg.sender:
                with st.chat_message("assistant", avatar="😈"):
                    st.write("**Devil's Advocate (Phase 1b: Critique)**")
                    st.write(msg.content)
                    if "critique" in msg.metadata:
                        st.error(f"Reasoning: {msg.metadata['critique'].get('reasoning', 'No reasoning provided.')}")
            
            elif "Architect (Refined)" in msg.sender:
                with st.chat_message("user", avatar="🚀"):
                    st.write("**Architect (Phase 1c: Final Refinement)**")
                    st.write(msg.content)
    
    st.divider()
    
    # 4. Final Artifact: The Refined Vision
    st.subheader("🏁 Phase 1 Output: The Refined Vision")
    st.info("This is the 'Hardened' vision of your story. It will be passed to the Skeleton Plotter in Phase 2.")
    
    st.session_state.registry.final_vision = st.text_area(
        "Edit Final Vision", 
        st.session_state.registry.final_vision, 
        height=300, 
        help="This text serves as the primary input for Phase 2: Structuring.",
        on_change=mark_dirty
    )
    
    if st.button("💾 Save Final Vision"):
        st.session_state.pm.save_project(st.session_state.registry)
        st.success("Final Vision saved as the artifact for Phase 2!")
