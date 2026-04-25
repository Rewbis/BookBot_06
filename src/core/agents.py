from typing import Dict, Any, List, Optional
from .llm_client import OllamaClient
from .state import ProjectRegistry, AgentMessage, Chapter

class BaseAgent:
    def __init__(self, client: OllamaClient):
        self.client = client

    def _safe_prompt(self, system: str, user: str, temperature: float = 0.7) -> Optional[str]:
        """Prompts the LLM and returns None if a connection error occurs."""
        result = self.client.prompt(system, user, temperature=temperature)
        if result.startswith("Error connecting to Ollama"):
            return None
        return result

    def _get_world_context(self, registry: ProjectRegistry, query: str = "") -> str:
        """Retrieves relevant world bible context for the agent."""
        from .world_bible import WorldBibleManager
        manager = WorldBibleManager(registry)
        return manager.get_context_chunk(query)

    def _get_manuscript_context(self, registry: ProjectRegistry, chapter_index: int) -> str:
        """Retrieves a summary of the previous chapter context."""
        if chapter_index <= 0 or not registry.chapters:
            return "No previous chapter context."
        
        prev_idx = chapter_index - 1
        if prev_idx < len(registry.chapters):
            prev = registry.chapters[prev_idx]
            content = prev.content
            words = content.split()
            # Return last 500 words for context
            tail = " ".join(words[-500:])
            return f"Previous Chapter Summary (Tail): ...{tail}"
        return "No previous chapter context."

    def get_system_prompt(self, registry: ProjectRegistry) -> str:
        raise NotImplementedError

    def run(self, registry: ProjectRegistry, **kwargs) -> Any:
        raise NotImplementedError

    def _safe_prompt(self, system: str, user: str) -> Optional[str]:
        """Wrapper for client.prompt that handles errors and empty responses."""
        try:
            res = self.client.prompt(system, user)
            if not res or "Error connecting to Ollama" in res:
                return None
            return res
        except Exception:
            return None

class Phase04ab_ContinuityAction(BaseAgent):
    """Agent 04ab: Analyzes continuity and writes the initial action-oriented draft."""
    def get_system_prompt(self, registry: ProjectRegistry) -> str:
        return (
            "You are the 'Continuity & Action Writer'. Your role is to ensure narrative integrity while drafting the scene's physical foundation.\n"
            "1. Continuity: Analyze the scene beats against the World Bible and previous chapters to ensure no established facts are violated.\n"
            "2. Action: Write a dry, plain-language 'Pass 1' draft focusing only on character actions, movement, and plot progression.\n"
            "Respect character names, locations, and established lore while ensuring the physical action is clear and logical."
        )

    def run(self, registry: ProjectRegistry, beats: str, chapter_index: int) -> str:
        system = self.get_system_prompt(registry)
        bible_context = self._get_world_context(registry, beats)
        prev_context = self._get_manuscript_context(registry, chapter_index)
        
        user = f"Current Scene Beats: {beats}\n\nWorld Bible Context: {bible_context}\n\nPrevious Chapter Context: {prev_context}\n\nWrite the skeletal action for this scene while strictly adhering to continuity."
        return self._safe_prompt(system, user) or "Continuity & Action draft failed (Ollama error)."

class Phase01a_Architect(BaseAgent):
    """Agent 01a: Manages high-level schema and the 'North Star'.
    
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

class Phase01b_DevilsAdvocate(BaseAgent):
    """Agent 01b: Identifies clichés and forces creative pivots.
    
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

class Phase03a_Librarian(BaseAgent):
    """Agent 03a: RAG-based lookup and artifact population.
    
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



class Phase04cd_SensoryDialogue(BaseAgent):
    """Agent 04cd: Layers sensory details and refines character dialogue."""
    def run(self, registry: ProjectRegistry, dry_draft: str) -> str:
        """Layers sensory details and refines dialogue within a dry draft."""
        bible_context = self._get_world_context(registry, dry_draft)
        system = (
            "You are the 'Sensory & Dialogue Specialist'. Your job is to enrich a dry action draft.\n"
            "1. Sensory: Enforce the atmospheric rules and location details from the context. Layer in smell, sound, texture, and feeling.\n"
            "2. Dialogue: Refine all spoken lines. Use character profiles to ensure unique voices, accents, and jargon.\n"
            "Maintain the core action while elevating the prose's immersive quality and vocal authenticity."
        )
        user = f"Context: {bible_context}\n\nDry Draft: {dry_draft}\n\nEnrich this scene with sensory depth and unique character dialogue."
        return self._safe_prompt(system, user) or "Sensory & Dialogue pass failed (Ollama error)."


class Phase04e_Stylist(BaseAgent):
    """Agent 04e: The Stylist - Enforces tone, voice, and specific stylistic rules.
    
    Uses provided sample texts and rules to ensure the final draft 
    matches the author's intended prose style.
    """
    def get_system_prompt(self, registry: ProjectRegistry) -> str:
        profile = registry.style_profile
        rules_section = f"Style Rules:\n" + "\n".join([f"- {r}" for r in profile.style_rules]) if profile.style_rules else ""
        samples_section = f"Reference Samples:\n" + "\n\n".join([f"Sample {i+1}:\n{s}" for i, s in enumerate(profile.sample_texts)]) if profile.sample_texts else ""
        
        return (
            "You are 'The Stylist'. Your job is to refine prose to match a specific artistic voice. "
            f"Voice Description: {profile.voice_description}\n"
            f"{rules_section}\n"
            f"{samples_section}\n"
            "Maintain the core action and dialogue while elevating the prose to match this style."
        )

    def run(self, registry: ProjectRegistry, draft: str) -> str:
        """Refines a draft to match the style profile."""
        system = self.get_system_prompt(registry)
        user = f"Draft to Refine:\n{draft}\n\nApply the style rules and voice to this draft."
        return self._safe_prompt(system, user) or "Stylist pass failed (Ollama error)."

class Phase05ab_AuditShadow(BaseAgent):
    """Agent 05ab: Performs logic audits and tracks unspoken subtext/knowledge."""
    def get_system_prompt(self, registry: ProjectRegistry) -> str:
        conflicts = "\n".join([f"- {c.description}" for c in registry.conflict_registry if not c.resolved])
        shadow = registry.shadow_context
        subtext_list = "\n".join([f"- {s}" for s in shadow.active_subtext]) if shadow.active_subtext else "None"
        
        return (
            "You are the 'Audit & Shadow Agent'. You perform a dual analysis of story drafts.\n"
            "1. Audit: Check for logic gaps, physical impossibilities, and continuity errors.\n"
            f"Known Unresolved Conflicts:\n{conflicts or 'None'}\n"
            "2. Shadow: Track character knowledge updates, unspoken tensions (subtext), and dramatic irony.\n"
            f"Current Active Subtext:\n{subtext_list}\n"
            "Respond in JSON format."
        )

    def run(self, registry: ProjectRegistry, draft: str) -> Dict[str, Any]:
        """Audits a draft and identifies subtext updates."""
        system = self.get_system_prompt(registry)
        bible_context = self._get_world_context(registry, draft)
        user = (
            f"Draft to Analyze:\n{draft}\n\n"
            f"World Bible Context:\n{bible_context}\n\n"
            "Perform Audit and Shadow Analysis. Return JSON:\n"
            "{\n"
            "  \"issues\": [{\"description\": \"...\", \"severity\": \"low/medium/high\"}],\n"
            "  \"knowledge_updates\": [{\"character\": \"...\", \"type\": \"fact/suspicion/secret\", \"content\": \"...\"}],\n"
            "  \"subtext\": [\"...\"],\n"
            "  \"irony\": [\"...\"]\n"
            "}"
        )
        response = self._safe_prompt(system, user)
        if not response: return {"issues": [], "knowledge_updates": [], "subtext": [], "irony": []}
        return self.client._clean_json(response)

class Phase02a_SkeletonPlotter(BaseAgent):
    """Agent 02a: Generates a high-level 20-chapter outline."""
    def get_system_prompt(self, registry: ProjectRegistry) -> str:
        return (
            "You are 'The Skeleton Plotter'. Your role is to take a premise and expand it into a structured 20-chapter outline. "
            "Each chapter should have a title and a 3-4 sentence summary of the key plot beats. "
            "Ensure the pacing follows a traditional dramatic arc with rising tension and a clear climax."
        )

    def run(self, registry: ProjectRegistry) -> Dict[str, Any]:
        system = self.get_system_prompt(registry)
        # Use final_vision if Phase 1 has been run, otherwise fallback to premise
        vision = registry.final_vision if registry.final_vision else registry.premise
        
        user = (
            f"Final Vision / Premise: {vision}\n"
            f"North Star: {registry.north_star}\n"
            f"Target Chapter Count: {registry.target_chapters}\n"
            f"Total Target Word Count: {registry.target_word_count}\n\n"
            f"Generate a {registry.target_chapters}-chapter outline. Ensure the pacing matches the word count goal. "
            "Return JSON with a list of chapters, each containing 'number', 'title', and 'summary'."
        )
        response = self.client.prompt(system, user)
        return self.client._clean_json(response)

class Phase02b_SkeletonFormatter(BaseAgent):
    """Agent 02b: Ensures the skeleton output matches the ProjectRegistry schema."""
    def run(self, raw_skeleton: Dict[str, Any]) -> List[Chapter]:
        # This is a deterministic agent that cleans and maps the JSON to our Chapter model
        # though it can also use the LLM to 'fix' broken JSON if needed.
        chapters = []
        raw_list = raw_skeleton.get('chapters', [])
        
        for i, item in enumerate(raw_list):
            chapters.append(Chapter(
                chapter_number=item.get('number', i + 1),
                title=item.get('title', f"Chapter {i + 1}"),
                summary=item.get('summary', ""),
                content="", # Prose is empty at this stage
                audit_logs=[]
            ))
        return chapters
class Phase06a_MarketingAgent(BaseAgent):
    """Agent 06a: Generates marketing copy, blurbs, and query letters."""
    def get_system_prompt(self, registry: ProjectRegistry) -> str:
        return (
            "You are 'The Marketing Agent'. Your job is to take a completed book skeleton and prose samples "
            "to generate high-impact marketing copy. This includes back-cover blurbs, social media teasers, "
            "and formal query letters for agents/publishers."
        )

    def run(self, registry: ProjectRegistry, task: str) -> str:
        system = self.get_system_prompt(registry)
        context = f"Title: {registry.title}\nPremise: {registry.premise}\nNorth Star: {registry.north_star}\n"
        if registry.chapters:
            context += f"Chapter 1 Summary: {registry.chapters[0].summary}\n"
        
        user = f"Context: {context}\nTask: {task}\n\nGenerate the requested marketing content."
        return self._safe_prompt(system, user) or "Marketing generation failed (Ollama error)."
