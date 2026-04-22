# Foundational Design: BookBot_06

A definitive design source for the BookBot Narrative Engine. This document preserves system purpose, architectural decisions, and project boundaries across development sessions.

## 1. System Purpose
BookBot_06 is an agentic creative writing partner designed to evolve raw concepts into publishable literary works. It minimizes cognitive load for authors by automating structural plotting, chapter drafting, and revision cycles while maintaining high human curatorial control.

## 2. Scope Boundaries (MoSCoW)

### Must Have
- **Phase 1-4 Core**: User Input checking, Skeleton generation (3-4 sentence outlines), Story expansion (detailed arcs/beats), and Draft generation.
- **Local Sovereignty**: All LLM processing hosted locally via **Ollama**.
- **Deterministic Robustness**: Pythonic cleaning for LLM outputs to prevent parsing failures.
- **Registry System**: Centralized state management for chapters and plot threads.

### Should Have
- **Phase 4 Integration**: Automated review, critique, and polishing workflows.
- **Agent Orchestration**: Modular orchestration using **LangGraph**.
- **Observability**: Integration with **LangSmith** (optional/local) for prompt refinement.

### Nice to Have
- **Autonomous Research**: Integration with **Tavily** for world-building fact-checking.
- **Phase 5-6 Support**: Multimodal assets (Cover/Illustration prompts) and Marketing/Copywriting agents.

### Won't Have (v0.6)
- **Direct Publishing**: Automated upload to KDP/IngramSpark.
- **Cloud-Only Hosting**: Strictly avoids reliance on proprietary black-box APIs for core logic.

## 3. Architecture Summary
- **UI Layer**: Streamlit-based interactive dashboard.
- **Logic Layer (Narrative Engine)**: A fleet of 15+ specialized agents orchestrated by LangGraph.
- **Persistence Layer**: JSON-based state snapshots and Markdown exports.

Detailed details can be found in [docs/architecture.md](file:///e:/Coding/BookBot_06/docs/architecture.md).

## 4. Key Design Decisions (KDD)
- **Dec Decision 01: Logic-First Parsing**: We avoid "prompt-engineering" for data format compliance. We use regex and deterministic Python to extract JSON from LLM noise.
- **Dec Decision 02: Phase Decoupling**: The lifecycle is split into 6 distinct phases (Input -> Skeleton -> Story -> Draft -> Manuscript -> Publish). Each phase must operate on a shared state object but remain independent to prevent regressions.
- **Dec Decision 03: Structural Granularity**: We distinguish between the **Skeleton** (high-level 3-4 sentence plot events) and the **Story** (full-depth scene details, character arcs, and plot threads).

## 5. Document Navigation
- [Architecture & Tech Stack](file:///e:/Coding/BookBot_06/docs/architecture.md)
- [Narrative Workflow](file:///e:/Coding/BookBot_06/docs/narrative_workflow.md)
- [RAID Log (Risks & Assumptions)](file:///e:/Coding/BookBot_06/docs/raid_log.md)
- [Anti-Patterns & Lessons Learned](file:///e:/Coding/BookBot_06/docs/anti_patterns.md)
- [Roadmap & Backlog](file:///e:/Coding/BookBot_06/roadmap.md)
