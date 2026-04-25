import streamlit as st
from src.ui.utils import run_orchestrator, mark_dirty

def render_phase4():
    st.header("✍️ Phase 4: Multi-Pass Drafting")
    st.info("The Soul: Sculpt prose through 4 passes (Action -> Sensory -> Dialogue -> Style).")
    
    # --- Style & Voice Config ---
    with st.expander("🎭 Style & Voice Configuration", expanded=False):
        profile = st.session_state.registry.style_profile
        col_v, col_r = st.columns(2)
        with col_v:
            profile.voice_description = st.text_area("Voice Description", profile.voice_description, height=100)
            new_rule = st.text_input("Add Stylistic Rule")
            if st.button("Add Rule"):
                if new_rule and new_rule not in profile.style_rules:
                    profile.style_rules.append(new_rule)
                    st.rerun()
            for i, rule in enumerate(profile.style_rules):
                st.text(f"- {rule}")
        with col_r:
            new_sample = st.text_area("Add Style Sample", height=100)
            if st.button("Add Sample"):
                if new_sample and new_sample not in profile.sample_texts:
                    profile.sample_texts.append(new_sample)
                    st.rerun()
            for i, sample in enumerate(profile.sample_texts):
                st.caption(f"Sample {i+1}: {sample[:50]}...")

    st.divider()

    # --- Drafting View ---
    if not st.session_state.registry.chapters:
        st.warning("No chapters yet. Go to Phase 2 to build a skeleton.")
    else:
        chap_ids = [f"Chapter {c.chapter_number}: {c.title}" for c in st.session_state.registry.chapters]
        selected_chap_idx = st.selectbox("Select Chapter to Draft", range(len(chap_ids)))
        
        if selected_chap_idx is not None:
            current_chap = st.session_state.registry.chapters[selected_chap_idx]
            col_left, col_right = st.columns(2)
            
            with col_left:
                st.subheader("🖋️ AI Multi-Pass Draft")
                content = current_chap.content
                draft_area = st.text_area("Prose Area", content, height=500, key=f"draft_{selected_chap_idx}")
                if draft_area != content:
                    current_chap.content = draft_area
                    mark_dirty()

                if st.button("🚀 Trigger 4-Pass Generation"):
                    with st.status("Orchestrator: Sculpting Prose...", expanded=True) as status:
                        run_orchestrator("draft", {"beats": current_chap.summary, "chapter_index": selected_chap_idx})
                        status.update(label="Drafting Complete!", state="complete")
                        st.rerun()

            with col_right:
                st.subheader("⚖️ Continuity & Shadow")
                with st.expander("🧠 Shadow Knowledge", expanded=True):
                    shadow = st.session_state.registry.shadow_context
                    if not shadow.character_knowledge:
                        st.info("No knowledge states tracked yet.")
                    else:
                        for char, ks in shadow.character_knowledge.items():
                            st.markdown(f"**{char}**")
                            st.caption(f"Facts: {', '.join(ks.known_facts)}")

                with st.expander("🎭 Active Subtext", expanded=False):
                    for sub in shadow.active_subtext:
                        st.write(f"- {sub}")
