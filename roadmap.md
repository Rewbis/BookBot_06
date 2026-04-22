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

### 1. Phase 3: Story Expansion [Must Have]
- **Task**: Implement Agent 03 (Story Architect) to expand 3-sentence skeletons into detailed scene beats.
- **UI**: Build the `story_beats_view.py` to allow manual editing of beats before drafting.
- *Added 2026-04-22. Dependent on: Phase 2 completion.*

### 2. Phase 4: Prose Drafting [Must Have]
- **Task**: Implement Agent 04 (Drafting Agent) to convert scene beats into full prose.
- **Context**: Ensure the agent has access to the Style Specs and previous chapter summaries to maintain continuity.
- *Added 2026-04-22. Dependent on: Phase 3 completion.*

### 3. Agent 02b: Skeleton Refinement Loop [Should Have]
- **Task**: Fully integrate the `SkeletonRefiner` agent into the UI. Currently, it exists in code but isn't triggered in the plotting flow.
- **Goal**: Allow the user to "Critique" the skeleton and have the AI suggest improvements.
- *Added 2026-04-22.*

### 4. LangGraph Orchestration [Should Have]
- **Task**: Move from direct agent calls in UI views to a formal LangGraph state machine.
- **Benefit**: Allows for easier "rewinding" of states and complex conditional loops (e.g., "Refine until user approves").
- *Added 2026-04-22.*

### 5. Multimodal Assets (Phase 5/6) [Nice to Have]
- **Task**: Add agents for cover art prompt generation and marketing copy.
- *Added 2026-04-22.*

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
