from typing import Dict, Any, List, Optional
from .llm_client import OllamaClient
from .state import ProjectRegistry, Phase2Chapter

class BaseAgent:
    def __init__(self, client: OllamaClient):
        self.client = client

    def run(self, **kwargs) -> Any:
        raise NotImplementedError

class Brainstormer(BaseAgent):
    """Agent 01a: Focuses on expanding the premise and world-building."""
    def run(self, registry: ProjectRegistry, prompt: str) -> Dict[str, Any]:
        system_prompt = "You are Agent 01a 'Brainstormer'. Expand on the user's premise, world, and characters. Respond in JSON."
        user_content = f"Project: {registry.metadata.book_title}\nCurrent Premise: {registry.phase1.premise}\nUser Input: {prompt}\n\nRequired JSON format:\n{{\"expanded_premise\": \"...\", \"world_details\": \"...\", \"new_characters\": [{{ \"name\": \"...\", \"description\": \"...\" }}]}}"
        
        response = self.client.prompt(system_prompt, user_content)
        return self.client._clean_json(response)

class ContinuityExpert(BaseAgent):
    """Agent 01b: Checks the premise and world for logical inconsistencies."""
    def run(self, registry: ProjectRegistry) -> Dict[str, Any]:
        system_prompt = "You are Agent 01b 'Continuity Expert'. Analyze the project for internal contradictions. Respond in JSON."
        user_content = (
            f"Title: {registry.metadata.book_title}\n"
            f"Premise: {registry.phase1.premise}\n"
            f"World: {registry.phase1.world.model_dump()}\n"
            f"Characters: {[c.model_dump() for c in registry.phase1.characters]}\n"
            "\nIdentify any logical flaws or continuity risks. Required JSON: {\"risks\": [\"...\"], \"suggestions\": [\"...\"]}"
        )
        response = self.client.prompt(system_prompt, user_content)
        return self.client._clean_json(response)

class SkeletonPlotter(BaseAgent):
    """Agent 02a: Generates a high-level 20-chapter skeleton."""
    def run(self, registry: ProjectRegistry, count: int = 20) -> Dict[str, Any]:
        system_prompt = f"You are Agent 02a 'Skeleton Plotter'. Design a {count}-chapter high-level skeleton. Respond in JSON."
        user_content = (
            f"Title: {registry.metadata.book_title}\n"
            f"Premise: {registry.phase1.premise}\n"
            f"World: {registry.phase1.world.setting}\n"
            "TASK: Generate the skeleton. Each chapter must have exactly 3 to 4 sentences describing the main plot points.\n"
            "\nRequired JSON format:\n"
            "{\"chapters\": [{\"chapter_number\": 1, \"title\": \"...\", \"summary\": \"3-4 sentences...\"}]}"
        )
        
        response = self.client.prompt(system_prompt, user_content)
        return self.client._clean_json(response)

class SkeletonRefiner(BaseAgent):
    """Agent 02b: Critiques the skeleton for pacing and structure."""
    def run(self, registry: ProjectRegistry, skeleton_data: Dict[str, Any]) -> Dict[str, Any]:
        system_prompt = "You are Agent 02b 'Skeleton Refiner'. Critique the chapter skeleton for pacing and structural issues. Respond in JSON."
        user_content = f"""Skeleton: {skeleton_data}

Required JSON:
{{
  "structural_critique": "...",
  "pacing_score": 1-10,
  "improvement_steps": ["..."]
}}
"""
        
        response = self.client.prompt(system_prompt, user_content)
        return self.client._clean_json(response)

class SkeletonFormatter(BaseAgent):
    """Agent 02c: Ensures the skeleton is perfectly formatted and consistent."""
    def run(self, raw_data: Dict[str, Any]) -> List[Phase2Chapter]:
        # This agent performs deterministic cleaning or simple validation
        chapters = []
        for i, c in enumerate(raw_data.get('chapters', [])):
            chapters.append(Phase2Chapter(
                chapter_number=c.get('chapter_number', i+1),
                title=c.get('title', "Untitled"),
                summary=c.get('summary', "")
            ))
        return chapters
