# Anti-Patterns & Lessons Learned

This document serves as a "Negative Knowledge Base" to prevent repeating architectural mistakes identified in previous iterations (v0.5 and earlier).

## 1. The "Phase Regression" Pattern
**Observation**: In BookBot_05, developing Phase 4 (Polish/Review) caused breakages in the core logic of Phases 1-3.
**Root Cause**: Tight coupling between UI state and narrative logic, and lack of regression testing.
**Solution for 06**: 
- Implement **Phase Isolation**: Each phase must have a discrete "Input Schema" and "Output Schema".
- Changes to Phase 4 logic should never modify the interface or data structures expected by Phase 1.

## 2. "Over-LLMing" (Prompt Escalation)
**Observation**: Using complex prompt instructions to force the LLM to output "valid JSON only" often fails and increases latency.
**Root Cause**: Attempting to force a probabilistic model to act as a deterministic parser.
**Solution for 06**: 
- **Pythonic-First Cleaning**: Assume the LLM will be verbose. Use Python string manipulation, regex, and block-stripping (e.g., removing `<think>` tags) *before* passing content to a JSON loader.
- **Lower Model Tier**: Use smaller models for utility tasks, reserving larger models for creative ideation.

## 3. Monolithic State Bloat
**Observation**: Carrying the entire book context in a single large JSON object can lead to context-window expiration and performance lag.
**Solution for 06**: 
- **Fragmented Context**: Use a "Registry" pattern where the LLM only receives the *locally relevant* context.
- **Progression Continuity**: The Draft Writer (Phase 4) should receive the **Chapter Story** + **World Bible Summary** + **Previous Chapter Summary** + **Last 1000 words of previous chapter**. This ensures stylistic and narrative continuity without overloading the context window.
