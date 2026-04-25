import streamlit as st
from src.core.state import EntityType
from src.ui.utils import run_orchestrator

def render_phase3():
    st.header("📚 Phase 3: World Building")
    st.info("The Memory: Store every character, location, and rule to prevent continuity drift.")
    
    manager = st.session_state.world_manager
    
    # --- Lore Architect ---
    st.subheader("🖋️ Lore Architect", help="Ask the Librarian to brainstorm and create structured lore for you.")
    lore_topic = st.text_input("Topic to expand (e.g. 'Magic System')", placeholder="Enter a concept to flesh out...")
    if st.button("✨ Brainstorm & Add to Bible"):
        if lore_topic:
            with st.status(f"Orchestrator: Librarian researching {lore_topic}...", expanded=True) as status:
                run_orchestrator("librarian", {"topic": lore_topic})
                status.update(label="Lore Generation Complete!", state="complete")
                st.rerun()

    st.divider()

    # --- Entity Management ---
    col_list, col_form = st.columns([1.5, 1])
    with col_list:
        st.subheader("Current Entities")
        if not st.session_state.registry.world_bible.entities:
            st.write("No entities yet.")
        else:
            for i, entity in enumerate(st.session_state.registry.world_bible.entities):
                with st.expander(f"{entity.name} ({entity.entity_type.value})"):
                    entity.name = st.text_input("Name", entity.name, key=f"ent_name_{i}")
                    entity.description = st.text_area("Description", entity.description, key=f"ent_desc_{i}")
                    if entity.attributes:
                        st.json(entity.attributes)
                    
                    col_e1, col_e2 = st.columns(2)
                    with col_e1:
                        if st.button("Update", key=f"upd_{entity.id}"):
                            st.success(f"Updated {entity.name}")
                            st.rerun()
                    with col_e2:
                        if st.button("Delete", key=f"del_{entity.id}"):
                            st.session_state.registry.world_bible.entities.pop(i)
                            st.rerun()

    with col_form:
        st.subheader("Add New Entity")
        with st.form("new_entity_form"):
            e_name = st.text_input("Name")
            e_type = st.selectbox("Type", options=[t.value for t in EntityType])
            e_desc = st.text_area("Description")
            if st.form_submit_button("Add to Bible"):
                manager.upsert_entity(e_name, EntityType(e_type), e_desc)
                st.success(f"Added {e_name}!")
                st.rerun()
