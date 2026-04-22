from typing import Dict, Any, List, Optional
from .llm_client import OllamaClient
from .state import ProjectRegistry, AgentMessage

class BaseAgent:
    def __init__(self, client: OllamaClient):
        self.client = client

    def get_system_prompt(self, registry: ProjectRegistry) -> str:
        raise NotImplementedError

    def run(self, registry: ProjectRegistry, **kwargs) -> Any:
        raise NotImplementedError

class Architect(BaseAgent):
    """The Architect: Manages high-level schema and the 'North Star'.
    
    Sets the structural boundaries and thematic goals of the story. 
    Responsible for expanding premises and ensuring all other agents 
    stay aligned with the core vision.
    """
    def get_system_prompt(self, registry: ProjectRegistry) -> str:
        return (
            "You are 'The Architect'. Your role is to maintain the structural integrity and thematic 'North Star' of the book. "
            f"Title: {registry.title}. Tone: {registry.tone}. North Star: {registry.north_star}. "
            "Respond in JSON format."
        )

    def run(self, registry: ProjectRegistry, prompt: str) -> Dict[str, Any]:
        """Runs the Architect to expand on a concept or refine structure."""
        system = self.get_system_prompt(registry)
        user = f"Context: {registry.premise}\nTask: {prompt}\n\nReturn JSON with 'plan' and 'reasoning'."
        response = self.client.prompt(system, user)
        return self.client._clean_json(response)

class DevilsAdvocate(BaseAgent):
    """The Devil's Advocate: Identifies clichés and forces creative pivots.
    
    Acts as an adversarial critic to prevent generic storytelling. 
    It intentionally looks for tropes and suggests high-impact creative deviations.
    """
    def get_system_prompt(self, registry: ProjectRegistry) -> str:
        return (
            "You are 'The Devil's Advocate'. You are a contrarian literary critic. Your job is to find clichés, predictable tropes, "
            "and generic plot points. You must challenge the author to pivot towards more unique and interesting ideas."
        )

    def run(self, registry: ProjectRegistry, idea: str) -> Dict[str, Any]:
        """Analyzes an idea for clichés and returns pivot suggestions."""
        system = self.get_system_prompt(registry)
        user = f"Current Idea: {idea}\n\nAnalyze for clichés and suggest a 'Pivot'. Return JSON: {{\"cliches\": [\"...\"], \"pivot_suggestion\": \"...\", \"saturation_score\": 0-100}}"
        response = self.client.prompt(system, user)
        return self.client._clean_json(response)

class Librarian(BaseAgent):
    """The Librarian: RAG-based lookup and artifact population.
    
    Manages the World Bible by creating structured lore entries. 
    Ensures that new world-building details are logically consistent with existing facts.
    """
    def get_system_prompt(self, registry: ProjectRegistry) -> str:
        return "You are 'The Librarian'. You manage the World Bible. You ensure new facts are recorded and existing lore is retrieved accurately."

    def run(self, registry: ProjectRegistry, query: str, bible_context: str) -> Dict[str, Any]:
        """Generates new lore entities based on a topic and existing bible context."""
        system = self.get_system_prompt(registry)
        user = f"Relevant Lore: {bible_context}\nTask: {query}\n\nIdentify new entities or facts to add to the Bible. Return JSON: {{\"new_entities\": [{{ \"name\": \"...\", \"type\": \"...\", \"description\": \"...\" }}]}}"
        response = self.client.prompt(system, user)
        return self.client._clean_json(response)

class Auditor(BaseAgent):
    """The Auditor: Logic gap checker and consistency validator.
    
    Scans drafts for physical impossibilities, lore contradictions, 
    and narrative logic gaps.
    """
    def get_system_prompt(self, registry: ProjectRegistry) -> str:
        return "You are 'The Auditor'. You check for logic gaps, physical impossibilities, and continuity errors in the narrative."

    def run(self, registry: ProjectRegistry, draft: str, bible_context: str) -> Dict[str, Any]:
        """Audits a draft against the World Bible and returns a list of issues."""
        system = self.get_system_prompt(registry)
        user = f"World Bible Context: {bible_context}\nDraft to Audit: {draft}\n\nIdentify any logic gaps or contradictions. Return JSON: {{\"issues\": [{{ \"description\": \"...\", \"severity\": \"...\" }}]}}"
        response = self.client.prompt(system, user)
        return self.client._clean_json(response)

class ActionWriter(BaseAgent):
    """Pass 1: The Skeleton - Focuses on dry action and movement.
    
    Strips away all atmosphere and dialogue to focus purely on 
    what characters DO and where they GO.
    """
    def run(self, registry: ProjectRegistry, beats: str) -> str:
        """Generates a dry, action-only draft for a scene."""
        system = "You are 'Action Writer'. Write a dry, plain-language 'Pass 1' draft focusing only on character actions, movement, and plot progression. No flowery prose."
        user = f"Beats: {beats}\n\nWrite the skeletal action for this scene."
        return self.client.prompt(system, user)

class SensoryAgent(BaseAgent):
    """Pass 2: The Sensory - Adds atmosphere, smell, sound, and feeling.
    
    Enriches a dry action draft with deep sensory immersion. 
    Focuses on the 'five senses' and emotional resonance.
    """
    def run(self, registry: ProjectRegistry, dry_draft: str) -> str:
        """Layers sensory details onto a dry action draft."""
        system = "You are 'Sensory Agent'. Take a dry draft and layer in sensory details: smell, sound, texture, and atmosphere. Enrich the world without changing the action."
        user = f"Dry Draft: {dry_draft}\n\nLayer in sensory depth."
        return self.client.prompt(system, user)

class DialogueSpecialist(BaseAgent):
    """Pass 3: The Dialogue - Refines character voices and unique jargon.
    
    Fine-tunes spoken lines to ensure they match character personalities, 
    social standing, and background.
    """
    def run(self, registry: ProjectRegistry, enriched_draft: str) -> str:
        """Refines dialogue within an enriched draft."""
        system = "You are 'Dialogue Specialist'. Refine all spoken lines to ensure unique character voices, appropriate jargon, and natural flow. Ensure dialogue matches character personalities."
        user = f"Enriched Draft: {enriched_draft}\n\nRefine the dialogue."
        return self.client.prompt(system, user)
