import streamlit as st
from src.ui.utils import run_orchestrator, mark_dirty

def render_phase4():
    st.header("✍️ Phase 4: Multi-Pass Drafting")
    st.info("The Soul: Sculpt prose through 3 steps (Continuity/Action -> Sensory/Dialogue -> Style).")
    
    # Initialize chapter selection state if not present
    if "selected_chap_idx_sb" not in st.session_state:
        st.session_state.selected_chap_idx_sb = 0

    def approve_and_next():
        current_idx = st.session_state.selected_chap_idx_sb
        if current_idx < len(st.session_state.registry.chapters) - 1:
            st.session_state.selected_chap_idx_sb = current_idx + 1
    
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
        selected_chap_idx = st.selectbox("Select Chapter to Draft", range(len(chap_ids)), format_func=lambda i: chap_ids[i], key="selected_chap_idx_sb")
        
        if selected_chap_idx is not None:
            current_chap = st.session_state.registry.chapters[selected_chap_idx]
            col_left, col_right = st.columns(2)
            
            with col_left:
                st.subheader("🖋️ AI 3-Step Draft")
                content = current_chap.content
                draft_area = st.text_area("Prose Area", content, height=500, key=f"draft_{selected_chap_idx}")
                if draft_area != content:
                    current_chap.content = draft_area
                    mark_dirty()

                if st.button("🚀 Trigger 3-Step Generation"):
                    with st.status("Orchestrator: Sculpting Prose...", expanded=True) as status:
                        result = run_orchestrator("draft", {"beats": current_chap.summary, "chapter_index": selected_chap_idx})
                        
                        if result.get("error"):
                            status.update(label=f"Drafting Failed: {result['error']}", state="error")
                            st.error(result["error"])
                        else:
                            # Clear the widget state to force it to pick up the new registry value on rerun
                            key = f"draft_{selected_chap_idx}"
                            if key in st.session_state:
                                del st.session_state[key]
                                
                            status.update(label="Drafting Complete!", state="complete")
                            st.rerun()

                st.divider()
                st.button("✅ Approve & Next Chapter", on_click=approve_and_next)
                if st.session_state.selected_chap_idx_sb == len(chap_ids) - 1 and st.session_state.registry.chapters[st.session_state.selected_chap_idx_sb].content:
                    st.success("Manuscript drafting complete!")

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

                with st.expander("📝 Recent AI Passes", expanded=False):
                    draft_ids = ["04ab_continuity_action", "04cd_sensory_dialogue", "04e_stylist"]
                    recent_passes = [m for m in st.session_state.registry.history if m.sender in draft_ids][-3:]
                    for msg in recent_passes:
                        st.markdown(f"**{msg.sender}**")
                        st.caption(msg.content[:200] + "..." if len(msg.content) > 200 else msg.content)
