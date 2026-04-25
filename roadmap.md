# BookBot 06 Roadmap & Backlog

This document tracks the evolution of the BookBot Narrative Engine, bridging the gap between foundational design and active development.

## User Journey: The Vision
**The Goal**: Empower a solo author to move from "Spark to Manuscript" in a weekend.

1. **Spark**: The author enters a premise ("A lighthouse keeper discovers the light is powered by captured memories").
2. **Phase 1 (Brainstorming)**: The **01a_architect** and **01b_devils_advocate** debate the premise, suggesting the lighthouse is actually a prison for forgotten gods.
3. **Phase 2 (Structuring)**: The **02a_skeleton_plotter** generates 20 chapters, ensuring the mystery unravels at the right pace.
4. **Phase 3 (World Building)**: The **03a_librarian** populates the "World Bible" with character details and lore artifacts.
5. **Phase 4 (Drafting)**: The **04ab-e_drafting_fleet** generates prose using the 3-step system.
6. **Phase 5 (Audit & Polish)**: The **05ab_audit_shadow** flags consistency gaps and tracks unspoken subtext.
7. **Phase 6 (Export)**: The author reviews the full manuscript and exports it to Markdown.

---

## Backlog (Prioritized)


### 2. Infrastructure [Should Have]
- **Task**: Vector DB Integration (FAISS/Chroma) for more robust Librarian retrieval.
- **Task**: Tavily API integration for autonomous research/fact-checking.

### 4. Auto-Save Enhancements
- **UI**: Added "Save Required" visual indicators to the sidebar.
- **Task**: Integrated automatic 'last_updated' tracking in the ProjectRegistry.

---

## Completed (Changelog)

### 6-Phase UI Sync & Export Engine
- **UI**: Restructured the entire dashboard into a strict 6-phase lifecycle (Brainstorming -> Structuring -> World Building -> Drafting -> Audit -> Export).
- **Task**: Implemented Agent **06a_marketing_agent** for Phase 6 copy generation (Status: **Untested**).
- **Task**: Plumbed Phase 6 into the LangGraph orchestrator.
- **UI**: Integrated Markdown Export utility for final manuscripts.
- **Date completed**: 2026-04-23.

### Phased Pipeline Foundation
- **Task**: Overhauled `state.py` to support World Bible and Conflict Registry.
- **Task**: Implemented `ProjectManager` for full-project snapshots (Save/Load).
- **UI**: Integrated project selector and snapshot controls into sidebar.
- **Date completed**: 2026-04-23.

### Phase 1 & 2 Foundations
- **Task**: Established Pydantic Registry for state management.
- **Task**: Implemented Agents **01a_architect** and **04a_continuity_expert**.
- **Task**: Implemented Agents **02a_skeleton_plotter** and **02b_skeleton_formatter**.
- **Task**: Created 6-tab Streamlit UI with Dark Mode.
- **Date completed**: 2026-04-22.

### Legacy Migration & UI Fixes
- **Task**: Built `Importer05` utility to bring forward logs from previous versions.
- **Task**: Froze the title and tab selector to improve navigation during long scrolls.
- **Date completed**: 2026-04-22.

### Consolidated Drafting & Shadow Engine
- **Task**: Implemented the 3-step drafting fleet (**04ab_continuity_action** -> **04cd_sensory_dialogue** -> **04e_stylist**).
- **Task**: Implemented Agent **05ab_audit_shadow** for unified logic audit and subtext tracking.
- **UI**: Built the "Split-Screen" drafting view with real-time **05ab_audit_shadow** redlines and subtext visibility.
### Editability & Plotting Refinements
- **Task**: Implemented **02a_skeleton_plotter** and **02b_skeleton_formatter**.
- **UI**: Integrated Skeleton Plotter UI and editability into Architectural Planning tab.
- **UI**: Enabled direct editing for World Bible entities.
- **UI**: Added "Save Required" indicator to sidebar.
- **Date completed**: 2026-04-23.
