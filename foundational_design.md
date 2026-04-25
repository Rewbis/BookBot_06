# Foundational Design: BookBot_06

A definitive design source for the BookBot Narrative Engine. This document preserves system purpose, architectural decisions, and project boundaries across development sessions.

## 1. System Purpose
BookBot_06 follows a **Phased Pipeline with Shared State**, where specialized agents assist the author through a 6-phase lifecycle.

## 2. Scope Boundaries (MoSCoW)

### Must Have
- 6 phases of writing. Planning, Outline, Beats, Drafting, Revision, Export. each with ai agents dedicated to it's completion, assisting the human user and working together to create the best possible book.
- **Phased Pipeline**: A clear 6-phase progression from Planning to Export.
- **Lore Engine (RAG)**: Proactive retrieval-augmented generation to prevent "continuity drift".
- **04ab_continuity_action**: Combined validator and skeletal drafter that ensures scene beats align with lore.
- **3-Pass Drafting**: A sequential sculpting process: **04ab_continuity_action** -> **04cd_sensory_dialogue** -> **04e_stylist**.
- **05ab_audit_shadow**: Dual-purpose agent for logic gap detection and subtext/knowledge tracking.
- **Local Sovereignty**: All LLM processing hosted locally via **Ollama**.
- **Registry System**: Centralized state management with full snapshot save/load functionality.

### Should Have
- **Split-Screen UI**: Real-time "Redline" feedback from critique agents during drafting.
- **Phase 6: Export & Marketing**: **06a_marketing_agent** is implemented for blurb/query generation, but remains **untested**.

### Nice to Have
- **Autonomous Research**: Integration with **Tavily** for world-building fact-checking.
- **Phase 6 Support**: Multimodal assets (Cover/Illustration prompts) and Marketing/Copywriting agents.

### Won't Have (v0.6)
- **Direct Publishing**: Automated upload to KDP/IngramSpark.
- **Cloud-Only Hosting**: Strictly avoids reliance on proprietary black-box APIs for core logic.

## 3. Architecture Summary
- **UI Layer**: Streamlit-based "Sovereign Dashboard" with split-screen drafting and real-time state visibility.
- **Logic Layer (Narrative Engine)**: A phased pipeline fleet of specialized agents orchestrated by LangGraph, utilizing a shared state registry for cross-phase continuity.
- **Persistence Layer**: JSON-based full-project snapshots and World Bible registries.

Further details can be found in [docs/architecture.md](file:///e:/Coding/BookBot_06/docs/architecture.md).

## 4. Key Design Decisions (KDD)
- **Design Decision 01: Phased Execution**: We follow a strict 6-phase linear progression. Agents are context-aware and pull from the shared World Bible to maintain continuity across phases.
- **Design Decision 02: Multi-Pass Layering**: Prose is never generated in one go. It is "sculpted" through sequential passes (Action -> Sensory -> Dialogue -> Style) to ensure quality and stylistic consistency.
- **Design Decision 03: Adversarial Validation**: Every creative output is challenged by a critic (**01b_devils_advocate**, **05ab_audit_shadow**, or **04e_stylist**) before being committed to the registry.
- **Design Decision 04: Structured Lore (The Bible)**: Characters, locations, and items are stored as structured entities with tracked attributes to prevent hallucinations.
- **Design Decision 05: Logic-First Parsing**: We avoid "prompt-engineering" for data format compliance. We use regex and deterministic Python to extract JSON from LLM noise.

## 5. Document Navigation
- [Architecture & Tech Stack](file:///e:/Coding/BookBot_06/docs/architecture.md)
- [Narrative Workflow](file:///e:/Coding/BookBot_06/docs/narrative_workflow.md)
- [RAID Log (Risks & Assumptions)](file:///e:/Coding/BookBot_06/docs/raid_log.md)
- [Anti-Patterns & Lessons Learned](file:///e:/Coding/BookBot_06/docs/anti_patterns.md)
- [Roadmap & Backlog](file:///e:/Coding/BookBot_06/roadmap.md)
