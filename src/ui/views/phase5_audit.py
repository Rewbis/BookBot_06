import streamlit as st
from src.utils.logger import bot_logger

def render_phase5():
    st.header("⚖️ Phase 5: Audit & Shadow")
    st.info("The Auditor: Review logic gaps and system-wide consistency.")
    
    col_reg, col_logs = st.columns([1, 1])
    with col_reg:
        st.subheader("Conflict Registry")
        if not st.session_state.registry.conflict_registry:
            st.success("No active lore conflicts detected.")
        else:
            for conflict in st.session_state.registry.conflict_registry:
                st.error(f"{conflict.severity.upper()}: {conflict.description}")

    with col_logs:
        st.subheader("Session Logs")
        logs = bot_logger.get_recent_logs(20)
        st.code(logs, language="text")
        if st.button("🔄 Refresh Logs"):
            st.rerun()
