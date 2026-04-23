# Foundational Design: BookBot_06

A definitive design source for the BookBot Narrative Engine. This document preserves system purpose, architectural decisions, and project boundaries across development sessions.

## 1. System Purpose
BookBot_06 is an agentic creative writing partner designed to evolve raw concepts into publishable literary works. It utilizes a **Blackboard Architecture** where a central "World Bible" ensures consistency while specialized agents (adversaries, librarians, and stylists) collaborate to build the narrative.

## 2. Scope Boundaries (MoSCoW)

### Must Have
- **Blackboard Architecture**: A central "World State" (The Bible) that agents watch and update to ensure consistency.
- **Lore Engine (RAG)**: Proactive retrieval-augmented generation to prevent "continuity drift".
- **Continuity Expert**: Dedicated validator (Phase 4, Pass 0) that ensures scene beats align with established lore before drafting begins.
- **Adversarial Agents**: Contrarian agents like "The Devil's Advocate" to challenge clichés and force creative pivots.
- **4-Pass Drafting**: A sequential sculpting process: Action (Bones) -> Sensory (Atmosphere) -> Dialogue (Voice) -> Style (Persona).
- **Shadow Agent**: Deep subtext tracking and character knowledge state management.
- **Conflict Registry**: Automated detection of logical contradictions in the manuscript.
- **Local Sovereignty**: All LLM processing hosted locally via **Ollama**.
- **Registry System**: Centralized state management with full snapshot save/load functionality.

### Should Have
- **Emotional Arc Simulation**: Tension Graph calculation to ensure pacing payoffs.
- **Split-Screen UI**: Real-time "Redline" feedback from critique agents during drafting.

### Nice to Have
- **Autonomous Research**: Integration with **Tavily** for world-building fact-checking.
- **Phase 6 Support**: Multimodal assets (Cover/Illustration prompts) and Marketing/Copywriting agents.

### Won't Have (v0.6)
- **Direct Publishing**: Automated upload to KDP/IngramSpark.
- **Cloud-Only Hosting**: Strictly avoids reliance on proprietary black-box APIs for core logic.

## 3. Architecture Summary
- **UI Layer**: Streamlit-based "Sovereign Dashboard" with split-screen drafting and tension graphs.
- **Logic Layer (Narrative Engine)**: A Blackboard-based fleet of specialized agents orchestrated by LangGraph.
- **Persistence Layer**: JSON-based full-project snapshots and World Bible registries.

Further details can be found in [docs/architecture.md](file:///e:/Coding/BookBot_06/docs/architecture.md).

## 4. Key Design Decisions (KDD)
- **Design Decision 01: Blackboard-First Orchestration**: We move away from linear 1-6 pipelines. Agents react to changes in the World Bible and Blackboard, allowing for non-linear iteration.
- **Design Decision 02: Multi-Pass Layering**: Prose is never generated in one go. It is "sculpted" through sequential passes (Action -> Sensory -> Dialogue -> Style) to ensure quality and stylistic consistency.
- **Design Decision 03: Adversarial Validation**: Every creative output is challenged by a critic (Devil's Advocate, Auditor, or Stylist) before being committed to the registry.
- **Design Decision 04: Structured Lore (The Bible)**: Characters, locations, and items are stored as structured entities with tracked attributes to prevent hallucinations.
- **Design Decision 05: Logic-First Parsing**: We avoid "prompt-engineering" for data format compliance. We use regex and deterministic Python to extract JSON from LLM noise.

## 5. Document Navigation
- [Architecture & Tech Stack](file:///e:/Coding/BookBot_06/docs/architecture.md)
- [Narrative Workflow](file:///e:/Coding/BookBot_06/docs/narrative_workflow.md)
- [RAID Log (Risks & Assumptions)](file:///e:/Coding/BookBot_06/docs/raid_log.md)
- [Anti-Patterns & Lessons Learned](file:///e:/Coding/BookBot_06/docs/anti_patterns.md)
- [Roadmap & Backlog](file:///e:/Coding/BookBot_06/roadmap.md)
