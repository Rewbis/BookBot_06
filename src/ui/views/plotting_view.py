import streamlit as st
from src.core.state import ProjectRegistry
from src.core.agents import Brainstormer

def render_plotting_view(registry: ProjectRegistry):
    st.header("Phase 1: Plotting & User Inputs")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("High-Level Premise")
        registry.metadata.book_title = st.text_input("Book Title", registry.metadata.book_title)
        registry.phase1.premise = st.text_area("Initial Premise / Goal", registry.phase1.premise, height=200)
        
        if st.button("Brainstorm & Expand", help="Invokes Agent 01a to flesh out your idea"):
            with st.spinner("Brainstorming..."):
                agent = Brainstormer(st.session_state.client)
                result = agent.run(registry, "Expand on the central conflict.")
                if "expanded_premise" in result:
                    registry.phase1.premise = result["expanded_premise"]
                    st.success("Premise expanded!")
                    st.rerun()

    with col2:
        st.subheader("Characters")
        for i, char in enumerate(registry.phase1.characters):
            with st.expander(f"{char.name} ({char.description[:30]}...)"):
                char.name = st.text_input(f"Name", char.name, key=f"char_name_{i}")
                char.description = st.text_area(f"Description", char.description, key=f"char_desc_{i}")
                char.arc = st.text_area(f"Character Arc", char.arc, key=f"char_arc_{i}")
        
        if st.button("Add Character"):
            from src.core.state import Character
            registry.phase1.characters.append(Character(name="New Character"))
            st.rerun()

    st.divider()
    st.subheader("World Building")
    w1, w2 = st.columns(2)
    with w1:
        registry.phase1.world.setting = st.text_area("Setting", registry.phase1.world.setting)
        registry.phase1.world.rules = st.text_area("Magic/Universal Rules", registry.phase1.world.rules)
    with w2:
        registry.phase1.world.history = st.text_area("History", registry.phase1.world.history)
        registry.phase1.world.other = st.text_area("Other Notes", registry.phase1.world.other)
