from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum
import uuid

class EntityType(str, Enum):
    CHARACTER = "character"
    LOCATION = "location"
    ITEM = "item"
    LORE = "lore"
    OTHER = "other"

class StyleProfile(BaseModel):
    """Configuration for the Stylist agent."""
    sample_texts: List[str] = Field(default_factory=list)
    style_rules: List[str] = Field(default_factory=list)
    voice_description: str = "Standard literary prose"

class KnowledgeState(BaseModel):
    """Tracks what specific characters (or the reader) know."""
    character_name: str = ""
    known_facts: List[str] = Field(default_factory=list)
    suspicions: List[str] = Field(default_factory=list)
    hidden_secrets: List[str] = Field(default_factory=list)

class ShadowContext(BaseModel):
    """The 'under-the-hood' state tracked by the Shadow Agent."""
    character_knowledge: Dict[str, KnowledgeState] = Field(default_factory=dict)
    active_subtext: List[str] = Field(default_factory=list) # Unspoken tensions/themes
    dramatic_irony: List[str] = Field(default_factory=list) # Facts reader knows but characters don't

class Chapter(BaseModel):
    """A single chapter of the manuscript."""
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    chapter_number: int
    title: str = "Untitled Chapter"
    summary: str = ""
    content: str = ""
    audit_logs: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class WorldEntity(BaseModel):
    """A structured entity in the World Bible."""
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    name: str = ""
    entity_type: EntityType = EntityType.LORE
    description: str = ""
    attributes: Dict[str, Any] = Field(default_factory=dict) # e.g. {"eye_color": "green", "status": "alive"}
    last_updated: datetime = Field(default_factory=datetime.now)

class WorldBible(BaseModel):
    """The central source of truth for all story facts."""
    entities: List[WorldEntity] = Field(default_factory=list)
    global_rules: List[str] = Field(default_factory=list)
    history: str = ""

class Conflict(BaseModel):
    """A detected contradiction in the story."""
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    description: str = ""
    affected_entities: List[str] = Field(default_factory=list)
    severity: str = "medium" # low, medium, high
    resolved: bool = False
    timestamp: datetime = Field(default_factory=datetime.now)


class AgentMessage(BaseModel):
    """A message in the project history or agent logs."""
    sender: str = "" # e.g. "Brainstormer", "Devil's Advocate"
    content: str = ""
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ProjectRegistry(BaseModel):
    """The Sovereign Source of Truth for a BookBot_06 project."""
    project_id: str = Field(default_factory=lambda: datetime.now().strftime("%Y%m%d_%H%M%S"))
    
    # Core Narrative Data
    title: str = "Untitled Project"
    premise: str = ""
    tone: str = "Neutral"
    voice: str = ""
    north_star: str = "" # The intended ending or theme
    final_vision: str = "" # The refined output of Phase 1
    target_chapters: int = 20
    target_word_count: int = 50000
    
    # Style & Voice
    style_profile: StyleProfile = Field(default_factory=StyleProfile)
    
    # The Blackboard
    world_bible: WorldBible = Field(default_factory=WorldBible)
    shadow_context: ShadowContext = Field(default_factory=ShadowContext)
    conflict_registry: List[Conflict] = Field(default_factory=list)
    
    # Message History (Agent Debates & Logs)
    history: List[AgentMessage] = Field(default_factory=list)
    agent_memory: Dict[str, str] = Field(default_factory=dict) # Transient internal monologues
    
    # Production Data (Manuscript)
    chapters: List[Chapter] = Field(default_factory=list) # Structured chapters
    
    # Metadata
    current_phase: str = "Brainstorming"
    last_updated: datetime = Field(default_factory=datetime.now)

    def log_entry(self):
        """Prepares a dictionary representation for persistence."""
        return {
            "project_id": self.project_id,
            "title": self.title,
            "phase": self.current_phase,
            "data": self.model_dump(mode='json')
        }
    
    def get_token_counts(self) -> Dict[str, int]:
        """Heuristic for token counts broken down by category."""
        # Simple word-based heuristic: words * 1.3
        def count_tokens(text: str) -> int:
            return int(len(text.split()) * 1.3)

        counts = {
            "World Bible": count_tokens(str(self.world_bible.model_dump())),
            "History": count_tokens(" ".join([m.content for m in self.history])),
            "Chapters": count_tokens(str([c.model_dump() for c in self.chapters])),
        }
        counts["Total"] = sum(counts.values())
        return counts
