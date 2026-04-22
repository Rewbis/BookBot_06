import streamlit as st
from src.core.state import ProjectRegistry
from src.core.agents import SkeletonPlotter, SkeletonFormatter

def render_skeleton_view(registry: ProjectRegistry):
    st.header("Phase 2: Chapter Skeletons")
    st.markdown("A high-level 20-chapter outline. Each chapter is 3-4 sentences.")
    
    if not registry.phase2.chapters:
        st.info("No skeletons generated yet.")
        if st.button("Generate 20-Chapter Skeleton", type="primary"):
            with st.spinner("Plotting initial skeleton..."):
                agent = SkeletonPlotter(st.session_state.client)
                result = agent.run(registry)
                
                if "error" in result:
                    st.error(f"Error: {result['error']}")
                else:
                    formatter = SkeletonFormatter(st.session_state.client)
                    registry.phase2.chapters = formatter.run(result)
                    st.success("Skeleton generated!")
                    st.rerun()
    else:
        # Actions
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("Regenerate Skeleton", help="Discard current and start over"):
                registry.phase2.chapters = []
                st.rerun()
        
        st.divider()
        
        # Display Chapters
        for ch in registry.phase2.chapters:
            with st.expander(f"Chapter {ch.chapter_number}: {ch.title}"):
                ch.title = st.text_input(f"Title", ch.title, key=f"p2_title_{ch.chapter_number}")
                ch.summary = st.text_area(f"Summary (3-4 sentences)", ch.summary, height=100, key=f"p2_sum_{ch.chapter_number}")
                
        # Bulk Export button
        if st.button("Commit Skeleton to Phase 3"):
            registry.current_phase = 3
            st.success("Skeletons committed! Move to Phase 3 for detailed beats.")
            st.rerun()
