import streamlit as st
from src.ui.utils import run_orchestrator

def render_phase6():
    st.header("🚀 Phase 6: Export & Marketing")
    st.info("The Closer: Export your manuscript and generate marketing materials.")
    
    col_ex, col_mk = st.columns(2)
    with col_ex:
        st.subheader("📦 Manuscript Export")
        if st.button("📄 Export to Markdown", use_container_width=True):
            full_text = f"# {st.session_state.registry.title}\n\n"
            for chap in st.session_state.registry.chapters:
                full_text += f"## Chapter {chap.chapter_number}: {chap.title}\n\n{chap.content}\n\n"
            
            st.download_button("Download .md File", full_text, file_name=f"{st.session_state.registry.title}.md")
    
    with col_mk:
        st.subheader("📣 06a_marketing_agent")
        task = st.text_input("Marketing Task", value="Write a back-cover blurb.")
        if st.button("✨ Generate Marketing Copy", use_container_width=True):
            with st.status("Orchestrator: Generating Marketing...", expanded=True) as status:
                res = run_orchestrator("marketing", {"task": task})
                st.session_state.marketing_output = res.get("marketing_copy", "No output.")
                status.update(label="Marketing Copy Ready!", state="complete")
        
        if "marketing_output" in st.session_state:
            st.divider()
            st.write(st.session_state.marketing_output)
