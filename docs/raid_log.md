# RAID Log: BookBot_06

This document tracks Risks, Assumptions, Issues, and Dependencies to ensure project stability and informed decision-making.

## 1. Risks (R)
| ID | Description | Impact | Mitigation Strategy | Status |
|----|-------------|--------|---------------------|--------|
| R01 | Phase transition regressions. | High | Enforce strict unit testing and phase-specific state isolation. | Active |
| R02 | Local LLM bottlenecks. | Medium | Optimize prompts and use smaller models for utility tasks. | Active |
| R03 | LLM JSON parsing failures. | High | Use deterministic Python-based extraction instead of prompt escalation. | Active |
| R04 | Orchestration complexity (15+ agents). | Medium | Use LangGraph for structured state transitions and clear agent handoffs. | New |
| R05 | Consistency drift across 6 phases. | High | Implement "Continuity Expert" agent (Agent 04a) and enforce context history rules. | New |

## 2. Assumptions (A)
| ID | Description | Validation | Status |
|----|-------------|------------|--------|
| A01 | **Ollama** is running locally and serving models on default ports. | Check `ollama ps` and connectivity at runtime. | Validated |
| A02 | The author is using a modern Windows/PowerShell environment. | Verified via system metadata. | Validated |
| A03 | State persistence will rely on local filesystem JSON files for v0.6. | Document in Architecture. | Active |

## 3. Issues (I)
| ID | Description | Severity | Resolution Plan | Status |
|----|-------------|----------|-----------------|--------|
| I01 | LLM "thinking" blocks (e.g., `<think>`) cluttering output. | Low | Implement `_clean_json` utility to strip non-JSON content before parsing. | Open |

## 4. Dependencies (D)
| ID | Description | Version Requirement | Status |
|----|-------------|---------------------|--------|
| D01 | **Streamlit** | ^1.30.0 | Required |
| D02 | **LangChain / LangGraph** | Latest | Optional/Planned |
| D03 | **Ollama** | Latest | Required |
| D04 | **Tavily API** | Optional | Pending Key |
| D05 | **Image Gen API** (DALL-E/Midjourney) | Optional | For Phase 5 Cover/Illustration prompts |
