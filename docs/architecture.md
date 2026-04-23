# Architecture Summary: BookBot_06

This document outlines the high-level architecture and component interactions of the BookBot Narrative Engine.

## 1. System Overview
BookBot_06 follows a **Blackboard Architecture** where **LangGraph** serves as the orchestrator, managing a shared "World Bible" and "Blackboard" that specialized agents collaborate on asynchronously.

## 2. Component Diagram
The following diagram visualizes the collaborative nature of the Blackboard model.

```mermaid
graph TD
    User((Author)) -->|Interacts| UI[Sovereign Dashboard]
    UI -->|Action| Orchestrator[LangGraph Orchestrator]
    
    subgraph "The Blackboard (Shared State)"
        Registry[(Project Snapshot)]
        Bible[(World Bible RAG)]
        Graph[(Tension Graph)]
        Messages[(Agent Debates)]
    end
    
    Orchestrator <--> Registry
    Orchestrator <--> Bible
    
    subgraph "Collaborative Fleet"
        subgraph "Phase 1: Brainstorming"
            Agent_Arch[Architect]
            Agent_DA[Devil's Advocate]
        end
        
        subgraph "Phase 2 & 3: Structure & Lore"
            Agent_Skel[Skeleton Plotter]
            Agent_Lib[Librarian]
        end
        
        subgraph "Phase 4: Drafting (4-Pass)"
            Agent_Cont[Continuity Expert]
            Pass1[Action Agent]
            Pass2[Sensory Agent]
            Pass3[Dialogue Specialist]
            Pass4[Stylist Agent]
        end

        subgraph "Phase 5: Polishing"
            Agent_Aud[Auditor]
            Agent_Sha[Shadow Agent]
        end
    end
    
    Orchestrator --- Agent_Arch
    Orchestrator --- Agent_DA
    Orchestrator --- Agent_Lib
    Orchestrator --- Agent_Cont
    Orchestrator --- Pass1
    Orchestrator --- Pass2
    Orchestrator --- Pass3
    Orchestrator --- Pass4
    Orchestrator --- Agent_Aud
    Orchestrator --- Agent_Sha
    
    subgraph "Infrastructure"
        Collaborative_Fleet --> LocalLLM{{Local Ollama}}
        Agent_Lib -.-> VectorDB[(FAISS / Chroma)]
    end
```

## 3. Layer Definitions

### UI Layer (Sovereign Dashboard)
A responsive dashboard providing views for different facets of creation:
- **World Bible Tab**: Full management of characters, locations, and items.
- **Style & Voice**: Configuration for tone, stylistic rules, and reference samples.
- **Tension Visualizer**: Interactive chart showing emotional pacing.
- **Split-Screen Drafting**: AI multi-pass drafting on the left, adversarial redlines and shadow context on the right.
- **Audit Log**: Conflict registry and real-time session telemetry.
- **Project Selector**: Sidebar for managing snapshots and iterations.

### Orchestration Layer (LangGraph)
Manages the "Blackboard." It ensures that:
- Agents are triggered based on state changes (e.g., if a new character is added, the Librarian updates the Bible).
- Multi-pass loops for drafting are executed in sequence.
- Conflict warnings are surfaced to the user.

### Agent Layer (The Fleet)
A non-linear fleet of specialized personas organized by creation phase:

- **Phase 1: Brainstorming**
    - **The Architect**: Manages high-level schema and plot "North Star."
    - **The Devil's Advocate**: Contrarian that challenges clichés and forces creative pivots.
- **Phase 2: Structuring**
    - **The Skeleton Plotter**: Generates chapter beats and tension arcs.
- **Phase 3: World Building**
    - **The Librarian**: RAG-based lookup; populates the world with meaningful artifacts.
- **Phase 4: Drafting (4-Pass Fleet)**
    - **The Continuity Expert**: (Pass 0) Validates scene beats against the Bible before drafting.
    - **Drafting Agents**: Sequential sculpting (Action -> Sensory -> Dialogue -> Style).
- **Phase 5: Polishing & Audit**
    - **The Auditor**: Logic gap checker (e.g., "How did he get to the tower if the tide was in?").
    - **The Shadow Agent**: Tracks unspoken subtext and character knowledge states.
- **Phase 6: Export & Marketing**
    - **Marketing Agent**: (Planned) Generates blurbs, meta-data, and query letters.

### Robustness Layer (Deterministic Logic)
The "Pythonic-First" component that protects the system from LLM non-determinism. It performs:
- **Block Stripping**: Removing thinking tags or conversational filler.
- **JSON Validation**: Ensuring the agent's output conforms to the registry schema.
- **Fallback Handling**: Graceful degradation if the LLM fails to provide a usable response.
