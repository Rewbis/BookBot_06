# BookBot 06 Roadmap & Backlog

This document tracks the evolution of the BookBot Narrative Engine, bridging the gap between foundational design and active development.

## User Journey: The Vision
**The Goal**: Empower a solo author to move from "Spark to Manuscript" in a weekend.

1. **Spark**: The author enters a premise ("A lighthouse keeper discovers the light is powered by captured memories").
2. **Expansion**: The **Brainstormer** and **Continuity Expert** suggest the lighthouse is actually a prison for forgotten gods.
3. **Skeleton**: The **Skeleton Plotter** generates 20 chapters, ensuring the mystery unravels at the right pace.
4. **Story Beats**: The author refines Chapter 5, adding a specific twist about the keeper's own lost memories.
5. **Drafting**: The **Drafting Agent** generates 1,500 words for Chapter 1, using a "Melancholic, Sea-Salted" tone.
6. **Polish**: The author reviews the full manuscript, exports it to Markdown, and uses the **Marketing Agent** to write the back-cover blurb.

---

## Backlog (Prioritized)

### 1. Blackboard Foundation [Must Have]
- **Task**: Overhaul `state.py` to support World Bible, Conflict Registry, and Tension Graph.
- **Task**: Implement `ProjectManager` for full-project snapshots (Save/Load).
- **UI**: Integrate project selector and snapshot controls into sidebar.

### 2. The Lore Engine & Adversaries [Must Have]
- **Task**: Implement Agent 01c (Devil's Advocate) to challenge clichés in Phase 1.
- **Task**: Implement Agent 03a (The Librarian) for RAG-based artifact population.
- **Task**: Implement Agent 03b (The Auditor) for logical gap detection.

### 3. Multi-Pass Drafting [Must Have]
- **Task**: Implement the 3-layer drafting fleet (Action -> Sensory -> Dialogue).
- **UI**: Build the "Split-Screen" drafting view with real-time Auditor redlines.

### 4. Emotional Arc & Tension [Should Have]
- **Task**: Implement Tension Graph simulation in the Skeleton Plotter.
- **UI**: Build the Tension Visualizer chart.

### 5. The Shadow Agent [Should Have]
- **Task**: Implement knowledge tracking to manage subtext and info-dumps.

---

## Completed (Changelog)

### Phase 1 & 2 Foundations
- **Task**: Established Pydantic Registry for state management.
- **Task**: Implemented Agent 01a (Brainstormer) and 01b (Continuity).
- **Task**: Implemented Agent 02a (Skeleton Plotter) and 02c (Formatter).
- **Task**: Created 6-tab Streamlit UI with Dark Mode.
- **Date completed**: 2026-04-22.

### Sticky Header UI
- **Task**: Frozen the title and tab selector to improve navigation during long scrolls.
- **Date completed**: 2026-04-22.

### Legacy Migration (BB05 -> BB06)
- **Task**: Built `Importer05` utility to bring forward logs from previous versions.
- **Date completed**: 2026-04-22.
