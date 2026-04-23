# BookBot 06 Roadmap & Backlog

This document tracks the evolution of the BookBot Narrative Engine, bridging the gap between foundational design and active development.

## User Journey: The Vision
**The Goal**: Empower a solo author to move from "Spark to Manuscript" in a weekend.

1. **Spark**: The author enters a premise ("A lighthouse keeper discovers the light is powered by captured memories").
2. **Phase 1 (Brainstorming)**: The **Brainstormer** and **Devil's Advocate** debate the premise, suggesting the lighthouse is actually a prison for forgotten gods.
3. **Phase 2 (Structuring)**: The **Skeleton Plotter** generates 20 chapters, ensuring the mystery unravels at the right pace.
4. **Phase 3 (World Building)**: The **Librarian** populates the "World Bible" with character details and lore artifacts.
5. **Phase 4 (Drafting)**: The **Drafting Fleet** generates prose using the 4-pass system (Action -> Sensory -> Dialogue -> Style).
6. **Phase 5 (Audit & Polish)**: The **Auditor** flags consistency gaps and the **Shadow Agent** tracks unspoken subtext.
7. **Phase 6 (Export)**: The author reviews the full manuscript and exports it to Markdown.

---

## Backlog (Prioritized)

### 1. Blackboard Foundation [Must Have]
- **Task**: Overhaul `state.py` to support World Bible, Conflict Registry, and Tension Graph.
- **Task**: Implement `ProjectManager` for full-project snapshots (Save/Load).
- **UI**: Integrate project selector and snapshot controls into sidebar.

### 2. The Lore Engine & Adversaries [Must Have]
- **Task**: Implement Agent 01c (Devil's Advocate) to challenge clichés in Phase 1.
- **Task**: Implement Agent 03a (The Librarian) for RAG-based artifact population.
### 3. Emotional Arc & Tension [Should Have]
- **Task**: Implement Tension Graph simulation in the Skeleton Plotter.
- **UI**: Build the Tension Visualizer chart.

### 4. Auto-Save Enhancements
- **UI**: Added "Save Required" visual indicators to the sidebar.
- **Task**: Integrated automatic 'last_updated' tracking in the ProjectRegistry.

---

## Completed (Changelog)

### Phase 1 & 2 Foundations
- **Task**: Established Pydantic Registry for state management.
- **Task**: Implemented Agent 01a (Brainstormer) and 01b (Continuity).
- **Task**: Implemented Agent 02a (Skeleton Plotter) and 02c (Formatter).
- **Task**: Created 6-tab Streamlit UI with Dark Mode.
- **Date completed**: 2026-04-22.

### Legacy Migration & UI Fixes
- **Task**: Built `Importer05` utility to bring forward logs from previous versions.
- **Task**: Froze the title and tab selector to improve navigation during long scrolls.
- **Date completed**: 2026-04-22.

### 4-Pass Drafting & Shadow Engine
- **Task**: Implemented the 4-layer drafting fleet (Action -> Sensory -> Dialogue -> Style).
- **Task**: Implemented Agent 04a (Continuity Expert) as pre-draft validator.
- **Task**: Implemented Agent 05a (The Auditor) for logic gap detection.
- **Task**: Implemented Agent 05b (The Shadow Agent) for subtext and knowledge tracking.
- **UI**: Built the "Split-Screen" drafting view with real-time Auditor redlines and Shadow Context visibility.
### Editability & Plotting Refinements
- **Task**: Implemented `SkeletonPlotter` (Agent 02a) and `SkeletonFormatter` (Agent 02c).
- **UI**: Integrated Skeleton Plotter UI and editability into Architectural Planning tab.
- **UI**: Enabled direct editing for World Bible entities and Tension beats.
- **UI**: Added "Save Required" indicator to sidebar.
- **Date completed**: 2026-04-23.
