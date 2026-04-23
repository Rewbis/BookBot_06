import streamlit as st
import os
import json
import pandas as pd
from datetime import datetime
from src.core.state import ProjectRegistry, EntityType, TensionBeat, ShadowContext, Chapter
from src.core.llm_client import OllamaClient
from src.utils.project_manager import ProjectManager
from src.utils.importer_05 import Importer05
from src.core.world_bible import WorldBibleManager
from src.utils.logger import bot_logger

# Page Config
st.set_page_config(page_title="BookBot 06: Blackboard", layout="wide", page_icon="📖")

# Initialize Managers in Session State
if "pm" not in st.session_state:
    st.session_state.pm = ProjectManager()
if "registry" not in st.session_state:
    st.session_state.registry = ProjectRegistry()
if "client" not in st.session_state:
    st.session_state.client = OllamaClient()
if "world_manager" not in st.session_state:
    st.session_state.world_manager = WorldBibleManager(st.session_state.registry)
if "last_tab" not in st.session_state:
    st.session_state.last_tab = "Architectural Planning"

# --- Orchestrator Helper ---
@st.cache_resource
def get_graph():
    from src.core.orchestrator import create_blackboard_graph
    return create_blackboard_graph()

def mark_dirty():
    """Sets the registry as updated so the save reminder appears."""
    st.session_state.registry.last_updated = datetime.now()

def run_orchestrator(command: str, input_data: dict = None):
    """Invokes the Blackboard Orchestrator with a specific command."""
    graph = get_graph()
    
    initial_state = {
        "registry": st.session_state.registry,
        "command": command,
        "input_data": input_data,
        "last_agent_output": {},
        "error": None,
        "context": None,
        "client": st.session_state.client
    }
    
    # Run the graph
    result = graph.invoke(initial_state)
    
    # Update global state
    st.session_state.registry = result["registry"]
    # Refresh manager with new registry
    st.session_state.world_manager = WorldBibleManager(st.session_state.registry)
    return result["last_agent_output"]

# --- Sidebar ---
with st.sidebar:
    st.title("Sovereign Control")
    
    # Project Selector
    projects = st.session_state.pm.list_projects()
    project_titles = [f"{p['title']} ({p['id']})" for p in projects]
    
    if not project_titles:
        st.info("No projects found. Create one to get started.")
        selected_idx = None
    else:
        selected_idx = st.selectbox("Select Project", options=range(len(project_titles)), format_func=lambda i: project_titles[i], help="Switch between different story projects or snapshots.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Load", use_container_width=True, help="Load the selected project snapshot into the engine."):
            if selected_idx is not None and selected_idx < len(projects):
                project_id = projects[selected_idx]["id"]
                st.session_state.registry = st.session_state.pm.load_project(project_id)
                st.session_state.world_manager = WorldBibleManager(st.session_state.registry)
                st.rerun()
            else:
                st.warning("No project selected to load.")
    with col2:
        if st.button("New", use_container_width=True, help="Initialize a fresh project with a new Blackboard."):
            st.session_state.registry = st.session_state.pm.create_new_project("New Story Spark")
            st.session_state.world_manager = WorldBibleManager(st.session_state.registry)
            st.rerun()

    st.divider()
    
    # Telemetry
    st.subheader("Project Telemetry", help="Live monitoring of your story's data footprint and context usage.")
    tokens = st.session_state.registry.get_token_counts()
    st.metric("Total Tokens", f"{tokens['Total']:,}", help="Total estimated tokens across Bible, History, and Drafts.")
    
    with st.expander("Token Breakdown"):
        for cat, count in tokens.items():
            if cat != "Total":
                st.text(f"{cat}: {count:,}")
    
    # File Size (Mocked for current session if not saved yet)
    file_path = f"projects/project_{st.session_state.registry.project_id}.json"
    if os.path.exists(file_path):
        size_kb = os.path.getsize(file_path) / 1024
        st.metric("Registry Size", f"{size_kb:.2f} KB", help="The physical footprint of this project's memory.")
    else:
        st.info("Project not yet saved to disk.")

    st.divider()
    
    if st.button("💾 Save Snapshot", help="Commit the current Blackboard state to a permanent JSON snapshot."):
        path = st.session_state.pm.save_project(st.session_state.registry)
        st.success(f"Snapshot saved!")
        st.session_state.last_save_time = datetime.now()

    # Save Reminder
    if "last_save_time" not in st.session_state:
        st.session_state.last_save_time = datetime.now()
    
    if st.session_state.registry.last_updated > st.session_state.last_save_time:
        st.warning("⚠️ Unsaved Changes", help="You have made changes since the last save. Click 'Save Snapshot' to persist them.")

# --- Main UI ---
st.title("📖 BookBot 06: Blackboard Engine")

tabs = st.tabs([
    "Architectural Planning", 
    "World Bible (RAG)", 
    "Style & Voice",
    "Tension & Arcs", 
    "Drafting (Multi-Pass)", 
    "Audit Log"
])

# Import views (will need updates)
# from src.ui.views.plotting_view import render_plotting_view

with tabs[0]:
    st.header("🏗️ Architectural Planning")
    st.info("The Brain: This is where you define the 'North Star' and debate ideas with the contrarian Devil's Advocate.")
    st.session_state.registry.title = st.text_input("Book Title", st.session_state.registry.title, help="The working title of your masterpiece.", on_change=mark_dirty)
    st.session_state.registry.premise = st.text_area("Core Premise", st.session_state.registry.premise, height=150, help="The 'Spark' of your story. The Architect will expand this, and the Devil's Advocate will challenge it.", on_change=mark_dirty)
    
    col_btn, col_spacer = st.columns([1, 2])
    with col_btn:
        if st.button("🔥 Run Brainstormer", use_container_width=True, help="Trigger the Architect vs. Devil's Advocate debate to evolve your premise."):
            with st.status("Orchestrator: Running Brainstorm Phase...", expanded=True) as status:
                run_orchestrator("brainstorm", {"prompt": "Expand on the current premise and suggest new directions."})
                status.update(label="Brainstorming Complete!", state="complete")
                st.rerun()

    st.divider()
    
    # --- Skeleton Plotter Integration ---
    st.subheader("💀 Skeleton Plotter", help="Generate a high-level 20-chapter outline based on your premise.")
    if st.button("🗺️ Generate 20-Chapter Skeleton", help="The Skeleton Plotter will create a structured outline for your book."):
        with st.status("Orchestrator: Plotting Skeleton...", expanded=True) as status:
            run_orchestrator("plot_skeleton")
            status.update(label="Skeleton Generated!", state="complete")
            st.rerun()

    if st.session_state.registry.chapters:
        with st.expander("View/Edit Current Skeleton", expanded=False):
            for i, chap in enumerate(st.session_state.registry.chapters):
                col_c1, col_c2 = st.columns([1, 4])
                with col_c1:
                    chap.title = st.text_input(f"Ch {chap.chapter_number} Title", chap.title, key=f"title_{i}", on_change=mark_dirty)
                with col_c2:
                    chap.summary = st.text_area(f"Ch {chap.chapter_number} Summary", chap.summary, height=68, key=f"summary_{i}", on_change=mark_dirty)
            
            if st.button("💾 Save Skeleton Edits"):
                st.session_state.pm.save_project(st.session_state.registry)
                st.success("Skeleton edits saved!")

    st.divider()
    
    st.subheader("🗣️ Agent Debate (Cliché vs. Pivot)")
    if not st.session_state.registry.history:
        st.info("No debates yet. Trigger the Brainstormer to start.")
    else:
        for i, msg in enumerate(reversed(st.session_state.registry.history)):
            if msg.sender == "Architect":
                with st.chat_message("user", avatar="🏗️"):
                    msg.content = st.text_area(f"Architect's Suggestion {i}", msg.content, key=f"msg_{i}", on_change=mark_dirty)
                    if st.button(f"Save to Bible as Lore", key=f"save_lore_{i}"):
                        st.session_state.world_manager.upsert_entity(f"Idea {i}", EntityType.LORE, msg.content)
                        st.success("Saved to Bible!")
            else:
                with st.chat_message("assistant", avatar="😈"):
                    st.write(f"**The Devil's Advocate**: {msg.content}")
                    reasoning = msg.metadata.get("reasoning", "This direction challenges existing tropes to ensure a unique hook.")
                    st.error(f"DA REASONING: {reasoning}")

with tabs[1]:
    st.header("📚 The World Bible")
    st.info("The Memory: This structured repository stores every character, location, and rule to prevent AI hallucinations and continuity drift.")
    
    manager = st.session_state.world_manager
    
    # --- Lore Query Section ---
    with st.expander("🔍 Query Lore (RAG Test)", expanded=False):
        q = st.text_input("Enter a query to find relevant lore:", help="Search your story's memory. This uses RAG to find the most contextually relevant entities for your query.")
        if q:
            results = manager.query_lore(q)
            if results:
                for e in results:
                    st.markdown(f"**{e.name}** ({e.entity_type.value})")
                    st.caption(e.description)
            else:
                st.warning("No matching lore found.")

    st.divider()

    # --- Lore Architect (Agentic Lore Generation) ---
    st.subheader("🖋️ Lore Architect", help="Ask the Librarian to brainstorm and create structured lore for you.")
    lore_topic = st.text_input("Topic to expand (e.g. 'The Three Brothers', 'Magic System')", placeholder="Enter a concept to flesh out...")
    if st.button("✨ Brainstorm & Add to Bible", help="The Librarian will generate multiple entities based on this topic and add them to the Bible."):
        if not lore_topic:
            st.error("Please enter a topic.")
        else:
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
            st.write("No entities recorded yet.")
        else:
            for i, entity in enumerate(st.session_state.registry.world_bible.entities):
                with st.expander(f"{entity.name} ({entity.entity_type.value})"):
                    entity.name = st.text_input("Name", entity.name, key=f"ent_name_{i}")
                    entity.description = st.text_area("Description", entity.description, key=f"ent_desc_{i}")
                    if entity.attributes:
                        st.write("**Attributes**:")
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
        st.subheader("Add New Entity", help="Define a new story element. These attributes are hard-coded into the AI's context to ensure consistency.")
        with st.form("new_entity_form"):
            e_name = st.text_input("Name", help="e.g. 'Captain Thorne' or 'The Crimson Keep'")
            e_type = st.selectbox("Type", options=[t.value for t in EntityType], help="Categorize the entity for better RAG retrieval.")
            e_desc = st.text_area("Description", help="Detailed lore or physical description.")
            e_attr_key = st.text_input("Attr Key (optional)", help="e.g. 'Eye Color'")
            e_attr_val = st.text_input("Attr Value (optional)", help="e.g. 'Emerald Green'")
            
            if st.form_submit_button("Add to Bible"):
                attrs = {e_attr_key: e_attr_val} if e_attr_key else {}
                manager.upsert_entity(e_name, EntityType(e_type), e_desc, attrs)
                st.success(f"Added {e_name}!")
                st.rerun()

with tabs[2]:
    st.header("🎭 Style & Voice")
    st.info("The Persona: Define the prose style, add sample texts, and set rules for the Stylist agent.")
    
    profile = st.session_state.registry.style_profile
    
    col_v, col_r = st.columns([1, 1])
    with col_v:
        st.subheader("Voice Description")
        profile.voice_description = st.text_area("How should the AI write?", profile.voice_description, height=100, help="Describe the overall tone and voice (e.g., 'Gothic, verb-heavy, and melancholic').")
        
        st.subheader("Stylistic Rules")
        new_rule = st.text_input("Add a rule", placeholder="e.g. 'Never use adverbs'", key="new_rule")
        if st.button("Add Rule"):
            if new_rule and new_rule not in profile.style_rules:
                profile.style_rules.append(new_rule)
                st.rerun()
        
        for i, rule in enumerate(profile.style_rules):
            col_rule, col_del = st.columns([4, 1])
            col_rule.write(f"- {rule}")
            if col_del.button("🗑️", key=f"del_rule_{i}"):
                profile.style_rules.pop(i)
                st.rerun()

    with col_r:
        st.subheader("Style Samples")
        new_sample = st.text_area("Add a sample text", placeholder="Paste a paragraph that captures the desired style...", height=150, key="new_sample")
        if st.button("Add Sample"):
            if new_sample and new_sample not in profile.sample_texts:
                profile.sample_texts.append(new_sample)
                st.rerun()
        
        for i, sample in enumerate(profile.sample_texts):
            with st.expander(f"Sample {i+1} (Preview)"):
                preview = sample[:200]
                if len(sample) > 200: preview += "..."
                st.text(preview)
                if st.button("Delete Sample", key=f"del_sample_{i}"):
                    profile.sample_texts.pop(i)
                    st.rerun()

with tabs[3]:
    st.header("📈 Tension & Arc Visualization")
    st.info("Pacing visualization and emotional arc simulation.")
    
    import pandas as pd
    
    # --- Data Preparation ---
    beats = st.session_state.registry.tension_graph
    if beats:
        # Prepare data for multiple series
        # We'll use Chapter Number as the index
        chart_data = []
        for b in beats:
            data_point = {
                "Chapter": b.chapter_number,
                "Tension": b.tension_level,
                "Emotion": b.emotion
            }
            # Add character arcs if defined in metadata or attributes
            # Future: add real arc tracking
            
            chart_data.append(data_point)
        
        df = pd.DataFrame(chart_data).set_index("Chapter")
        
        # Display the chart
        st.line_chart(df, height=300)
        
        with st.expander("Detailed Beat Data"):
            for i, b in enumerate(st.session_state.registry.tension_graph):
                col_b1, col_b2, col_b3 = st.columns([1, 1, 3])
                with col_b1:
                    b.tension_level = st.slider(f"Ch {b.chapter_number} Tension", 1, 10, b.tension_level, key=f"tens_{i}")
                with col_b2:
                    b.emotion = st.text_input(f"Emotion", b.emotion, key=f"emo_{i}")
                with col_b3:
                    b.summary = st.text_area(f"Summary", b.summary, key=f"sum_{i}")
                if st.button(f"Remove Beat {i}", key=f"del_beat_{i}"):
                    st.session_state.registry.tension_graph.pop(i)
                    st.rerun()
            
            if st.button("💾 Save Tension Edits"):
                st.session_state.pm.save_project(st.session_state.registry)
                st.success("Tension beats saved!")
    else:
        st.write("No tension beats recorded yet. Use the Architect to generate a skeleton with tension levels.")

    st.divider()

    # --- Manual Beat Entry ---
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Add Tension Beat")
        with st.form("new_beat_form"):
            b_chap = st.number_input("Chapter", min_value=1, value=len(beats)+1, help="The chapter this tension peak/valley occurs in.")
            b_level = st.slider("Tension Level", 1, 10, 5, help="1 is a cozy breather; 10 is a world-shattering climax.")
            b_emotion = st.text_input("Primary Emotion", placeholder="e.g. Dread", help="The dominant 'feeling' of this beat.")
            b_summary = st.text_area("Beat Summary", help="A brief description of what drives the tension in this chapter.")
            
            if st.form_submit_button("Add Beat"):
                new_beat = TensionBeat(
                    chapter_number=b_chap,
                    tension_level=b_level,
                    emotion=b_emotion,
                    summary=b_summary
                )
                st.session_state.registry.tension_graph.append(new_beat)
                st.session_state.registry.tension_graph.sort(key=lambda x: x.chapter_number)
                st.rerun()
    
    with col2:
        st.subheader("Visualization Space")
        st.write("This area is reserved for character-specific arc overlays and thematic resonance tracking.")
        st.info("Future: Add toggles to overlay specific character arcs from the World Bible.")

with tabs[4]:
    st.header("✍️ Split-Screen Drafting")
    st.info("The Soul: This view allows you to watch the AI 'sculpt' prose through 4 passes, followed by Auditor consistency checks and Shadow Agent subtext analysis.")
    
    if not st.session_state.registry.chapters:
        st.warning("No chapters defined yet. Add a chapter in the Architect tab or build a skeleton.")
        if st.button("Add Mock Chapter for Testing", help="Quickly generate a placeholder chapter to test the drafting flow."):
            st.session_state.registry.chapters.append(Chapter(
                chapter_number=1,
                title="The Cold Light",
                content="",
                audit_logs=[]
            ))
            st.rerun()
    else:
        # Chapter Selector
        chap_ids = [f"Chapter {c.chapter_number}: {c.title}" for c in st.session_state.registry.chapters]
        selected_chap_idx = st.selectbox("Select Chapter to Draft", range(len(chap_ids)))
        
        if selected_chap_idx is not None:
            current_chap = st.session_state.registry.chapters[selected_chap_idx]

            col_left, col_right = st.columns(2)
            
            with col_left:
                st.subheader("🖋️ AI Multi-Pass Draft")
                
                # Display current content or generation status
                content = current_chap.content
                draft_area = st.text_area("Final Sculpt (Pass 4)", content, height=500, key=f"draft_{selected_chap_idx}")
                
                # Save edits back to registry
                if draft_area != content:
                    current_chap.content = draft_area

                if st.button("🚀 Trigger Multi-Pass Generation", help="Orchestrate the Action, Sensory, Dialogue, and Style agents to sculpt this chapter in real-time."):
                    with st.status("Orchestrator: Sculpting Prose...", expanded=True) as status:
                        # Pull beats from user input (could be enhanced to pull from skeleton)
                        user_beats = st.session_state.registry.premise # Fallback for now
                        
                        run_orchestrator("draft", {
                            "beats": user_beats,
                            "chapter_index": selected_chap_idx
                        })
                        
                        status.update(label="Drafting Complete!", state="complete", expanded=False)
                        st.rerun()

            with col_right:
                st.subheader("⚖️ Auditor Redlines")
                issues = current_chap.audit_logs
                if not issues:
                    st.success("No critical logic gaps detected in the current draft.")
                else:
                    for issue in issues:
                        with st.chat_message("assistant", avatar="⚖️"):
                            st.error(f"**Issue**: {issue.get('description')}")
                            st.caption(f"Severity: {issue.get('severity', 'medium').upper()}")
                
                st.divider()
                st.subheader("🌚 Shadow Context")
                shadow = st.session_state.registry.shadow_context
                
                with st.expander("🧠 Character Knowledge", expanded=True):
                    if not shadow.character_knowledge:
                        st.info("No knowledge states tracked yet. The Shadow Agent will populate this after drafting.")
                    else:
                        for char, ks in shadow.character_knowledge.items():
                            st.markdown(f"**{char}**")
                            if ks.known_facts: st.caption(f"Facts: {', '.join(ks.known_facts)}")
                            if ks.suspicions: st.caption(f"Suspicions: {', '.join(ks.suspicions)}")
                            if ks.hidden_secrets: st.caption(f"Secrets: {', '.join(ks.hidden_secrets)}")
                
                col_sub, col_iro = st.columns(2)
                with col_sub:
                    st.caption("🎭 Active Subtext")
                    if not shadow.active_subtext:
                        st.write("None")
                    else:
                        for sub in shadow.active_subtext:
                            st.write(f"- {sub}")
                
                with col_iro:
                    st.caption("👁️ Dramatic Irony")
                    if not shadow.dramatic_irony:
                        st.write("None")
                    else:
                        for irony in shadow.dramatic_irony:
                            st.write(f"- {irony}")
                
                if st.button("🗑️ Clear Shadow State", help="Reset all knowledge and subtext for this project."):
                    st.session_state.registry.shadow_context = ShadowContext()
                    st.rerun()

with tabs[5]:
    st.header("⚖️ Audit & Conflict Registry")
    
    col_reg, col_logs = st.columns([1, 1])
    
    with col_reg:
        st.subheader("Conflict Registry", help="Real-time contradictions detected between your draft and the World Bible.")
        if not st.session_state.registry.conflict_registry:
            st.success("No active lore conflicts detected.")
        else:
            for conflict in st.session_state.registry.conflict_registry:
                st.error(f"{conflict.severity.upper()}: {conflict.description}")

    with col_logs:
        st.subheader("Session Logs", help="The last 10 background events and LLM interactions.")
        logs = bot_logger.get_recent_logs(20) # Get last 20 lines
        st.code(logs, language="text")
        if st.button("🔄 Refresh Logs"):
            st.rerun()
