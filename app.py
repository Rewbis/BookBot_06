import streamlit as st
import os
import json
from datetime import datetime
from src.core.state import ProjectRegistry
from src.core.llm_client import OllamaClient
from src.utils.project_manager import ProjectManager
from src.utils.importer_05 import Importer05

# Page Config
st.set_page_config(page_title="BookBot 06: Blackboard", layout="wide", page_icon="📖")

# Initialize Managers
pm = ProjectManager()

# Custom CSS
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; }
    .stMetric { background-color: #1E2129; padding: 10px; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

# Initialize Session State
if "registry" not in st.session_state:
    st.session_state.registry = ProjectRegistry()
if "client" not in st.session_state:
    st.session_state.client = OllamaClient()

# --- Sidebar ---
with st.sidebar:
    st.title("Sovereign Control")
    
    # Project Selector
    projects = pm.list_projects()
    project_titles = [f"{p['title']} ({p['id']})" for p in projects]
    selected_idx = st.selectbox("Select Project", options=range(len(project_titles)), format_func=lambda i: project_titles[i], help="Switch between different story projects or snapshots.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Load", use_container_width=True, help="Load the selected project snapshot into the engine."):
            if selected_idx is not None:
                project_id = projects[selected_idx]["id"]
                st.session_state.registry = pm.load_project(project_id)
                st.rerun()
            else:
                st.warning("No project selected to load.")
    with col2:
        if st.button("New", use_container_width=True, help="Initialize a fresh project with a new Blackboard."):
            st.session_state.registry = pm.create_new_project("New Story Spark")
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
        path = pm.save_project(st.session_state.registry)
        st.success(f"Snapshot saved!")

# --- Main UI ---
st.title("📖 BookBot 06: Blackboard Engine")

tabs = st.tabs([
    "Architectural Planning", 
    "World Bible (RAG)", 
    "Tension & Arcs", 
    "Drafting (Multi-Pass)", 
    "Audit Log"
])

# Import views (will need updates)
# from src.ui.views.plotting_view import render_plotting_view

with tabs[0]:
    st.header("🏗️ Architectural Planning")
    st.info("The Brain: This is where you define the 'North Star' and debate ideas with the contrarian Devil's Advocate.")
    st.session_state.registry.title = st.text_input("Book Title", st.session_state.registry.title, help="The working title of your masterpiece.")
    st.session_state.registry.premise = st.text_area("Core Premise", st.session_state.registry.premise, height=150, help="The 'Spark' of your story. The Architect will expand this, and the Devil's Advocate will challenge it.")
    
    col_btn, col_spacer = st.columns([1, 2])
    with col_btn:
        if st.button("🔥 Run Brainstormer", use_container_width=True, help="Trigger the Architect vs. Devil's Advocate debate to evolve your premise."):
            with st.status("Agents Collaborating...", expanded=True) as status:
                from src.core.agents import Architect, DevilsAdvocate
                from src.core.state import AgentMessage
                
                client = st.session_state.client
                arch = Architect(client)
                da = DevilsAdvocate(client)
                
                status.write("Architect: Expanding premise...")
                res = arch.run(st.session_state.registry, "Expand on the current premise and suggest new directions.")
                
                # Format plan nicely if it's a list
                plan = res.get('plan', 'No plan generated.')
                if isinstance(plan, list):
                    plan_str = "\n".join([f"- {item.get('step', item) if isinstance(item, dict) else item}" for item in plan])
                else:
                    plan_str = str(plan)
                
                st.session_state.registry.history.append(AgentMessage(sender="Architect", content=plan_str))
                
                status.write("Devil's Advocate: Challenging clichés...")
                critique = da.run(st.session_state.registry, plan_str)
                
                # Format critique nicely
                pivot = critique.get('pivot_suggestion', 'No pivot suggested.')
                if isinstance(pivot, list):
                    pivot_str = "\n".join([f"- {item}" for item in pivot])
                else:
                    pivot_str = str(pivot)
                
                st.session_state.registry.history.append(AgentMessage(sender="Devil's Advocate", content=pivot_str))
                
                status.update(label="Debate Complete!", state="complete")
                st.rerun()

    st.divider()
    
    st.subheader("🗣️ Agent Debate (Cliché vs. Pivot)")
    if not st.session_state.registry.history:
        st.info("No debates yet. Trigger the Brainstormer to start.")
    else:
        for msg in reversed(st.session_state.registry.history):
            if msg.sender == "Architect":
                with st.chat_message("user", avatar="🏗️"):
                    st.write(f"**The Architect**: {msg.content}")
            else:
                with st.chat_message("assistant", avatar="😈"):
                    st.write(f"**The Devil's Advocate**: {msg.content}")
                    st.error("DA REASONING: This direction challenges existing tropes to ensure a unique hook.")

with tabs[1]:
    st.header("📚 The World Bible")
    st.info("The Memory: This structured repository stores every character, location, and rule to prevent AI hallucinations and continuity drift.")
    
    from src.core.world_bible import WorldBibleManager
    from src.core.state import EntityType
    
    manager = WorldBibleManager(st.session_state.registry)
    
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
            with st.status(f"Librarian researching {lore_topic}...", expanded=True) as status:
                from src.core.agents import Librarian
                client = st.session_state.client
                lib = Librarian(client)
                
                # Get existing context to avoid contradictions
                context = manager.get_context_chunk(lore_topic)
                
                res = lib.run(st.session_state.registry, lore_topic, context)
                new_entities = res.get('new_entities', [])
                
                if not new_entities:
                    st.warning("Librarian couldn't generate specific entities for this topic.")
                else:
                    for ent_data in new_entities:
                        name = ent_data.get('name', 'Unnamed')
                        e_type_str = ent_data.get('type', 'other').lower()
                        # Map to EntityType enum
                        try:
                            from src.core.state import EntityType
                            e_type = EntityType(e_type_str)
                        except ValueError:
                            e_type = EntityType.OTHER
                            
                        desc = ent_data.get('description', '')
                        attrs = ent_data.get('attributes', {})
                        
                        manager.upsert_entity(name, e_type, desc, attrs)
                        status.write(f"Added: **{name}** ({e_type.value})")
                
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
                    st.write(f"**Description**: {entity.description}")
                    if entity.attributes:
                        st.write("**Attributes**:")
                        st.json(entity.attributes)
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
            # For now, let's mock a character arc if any exist
            for i, entity in enumerate(st.session_state.registry.world_bible.entities):
                if entity.entity_type.value == "character":
                    # Heuristic: Generate a pseudo-arc for visualization space
                    data_point[f"{entity.name} Arc"] = (b.tension_level + i) % 10
            
            chart_data.append(data_point)
        
        df = pd.DataFrame(chart_data).set_index("Chapter")
        
        # Display the chart
        st.line_chart(df, height=300)
        
        with st.expander("Detailed Beat Data"):
            st.table(chart_data)
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
                from src.core.state import TensionBeat
                new_beat = TensionBeat(
                    chapter_number=b_chap,
                    tension_level=b_level,
                    emotion=b_emotion,
                    summary=b_summary
                )
                st.session_state.registry.tension_graph.append(new_beat)
                # Sort beats by chapter
                st.session_state.registry.tension_graph.sort(key=lambda x: x.chapter_number)
                st.rerun()
    
    with col2:
        st.subheader("Visualization Space")
        st.write("This area is reserved for character-specific arc overlays and thematic resonance tracking.")
        st.info("Future: Add toggles to overlay specific character arcs from the World Bible.")

with tabs[3]:
    st.header("✍️ Split-Screen Drafting")
    st.info("The Soul: This view allows you to watch the AI 'sculpt' prose through multiple passes (Action -> Sensory -> Dialogue), while the Auditor provides real-time consistency checks.")
    
    if not st.session_state.registry.chapters:
        st.warning("No chapters defined yet. Add a chapter in the Architect tab or build a skeleton.")
        if st.button("Add Mock Chapter for Testing", help="Quickly generate a placeholder chapter to test the drafting flow."):
            st.session_state.registry.chapters.append({
                "chapter_number": 1,
                "title": "The Cold Light",
                "content": "",
                "audit_logs": []
            })
            st.rerun()
    else:
        # Chapter Selector
        chap_ids = [f"Chapter {c['chapter_number']}: {c['title']}" for c in st.session_state.registry.chapters]
        selected_chap_idx = st.selectbox("Select Chapter to Draft", range(len(chap_ids)))
        
        if selected_chap_idx is not None:
            current_chap = st.session_state.registry.chapters[selected_chap_idx]

            col_left, col_right = st.columns(2)
            
            with col_left:
                st.subheader("🖋️ AI Multi-Pass Draft")
                
                # Display current content or generation status
                content = current_chap.get('content', "")
                draft_area = st.text_area("Final Scuplt (Pass 3)", content, height=500, key=f"draft_{selected_chap_idx}")
                
                if st.button("🚀 Trigger Multi-Pass Generation", help="Orchestrate the Action, Sensory, and Dialogue agents to sculpt this chapter in real-time."):
                    with st.status("Sculpting Prose...", expanded=True) as status:
                        from src.core.agents import ActionWriter, SensoryAgent, DialogueSpecialist, Auditor
                        from src.core.world_bible import WorldBibleManager
                        
                        client = st.session_state.client
                        beats = "The keeper enters the lantern room. The glass is frosted. The light is dead. He feels a chill that isn't from the wind."
                        
                        status.write("Pass 1: Action (The Bones)...")
                        p1 = ActionWriter(client).run(st.session_state.registry, beats)
                        
                        status.write("Pass 2: Sensory (The Atmosphere)...")
                        p2 = SensoryAgent(client).run(st.session_state.registry, p1)
                        
                        status.write("Pass 3: Dialogue & Voice (The Soul)...")
                        p3 = DialogueSpecialist(client).run(st.session_state.registry, p2)
                        
                        status.write("Auditing Logic & Lore...")
                        manager = WorldBibleManager(st.session_state.registry)
                        context = manager.get_context_chunk(beats)
                        audit_res = Auditor(client).run(st.session_state.registry, p3, context)
                        
                        # Update registry
                        current_chap['content'] = p3
                        current_chap['audit_logs'] = audit_res.get('issues', [])
                        
                        status.update(label="Drafting Complete!", state="complete", expanded=False)
                        st.rerun()

            with col_right:
                st.subheader("⚖️ Auditor Redlines")
                issues = current_chap.get('audit_logs', [])
                if not issues:
                    st.success("No critical logic gaps detected in the current draft.")
                else:
                    for issue in issues:
                        with st.chat_message("assistant", avatar="⚖️"):
                            st.error(f"**Issue**: {issue.get('description')}")
                            st.caption(f"Severity: {issue.get('severity', 'medium').upper()}")
                
                st.divider()
                st.subheader("Shadow Context")
                st.info("Subtext and Character Knowledge tracking will be displayed here.")

with tabs[4]:
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
        from src.utils.logger import bot_logger
        logs = bot_logger.get_recent_logs(20) # Get last 20 lines
        st.code(logs, language="text")
        if st.button("🔄 Refresh Logs"):
            st.rerun()
