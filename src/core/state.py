from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum

class EntityType(str, Enum):
    CHARACTER = "character"
    LOCATION = "location"
    ITEM = "item"
    LORE = "lore"

class WorldEntity(BaseModel):
    """A structured entity in the World Bible."""
    id: str = Field(default_factory=lambda: datetime.now().strftime("%H%M%S%f"))
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
    id: str = Field(default_factory=lambda: datetime.now().strftime("%H%M%S%f"))
    description: str = ""
    affected_entities: List[str] = Field(default_factory=list)
    severity: str = "medium" # low, medium, high
    resolved: bool = False
    timestamp: datetime = Field(default_factory=datetime.now)

class TensionBeat(BaseModel):
    """An emotional data point for pacing analysis."""
    chapter_number: int
    tension_level: int = 5 # 1-10
    emotion: str = "" # e.g. "Dread", "Joy", "Relief"
    summary: str = ""

class AgentMessage(BaseModel):
    """A message in the blackboard or history."""
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
    
    # The Blackboard
    world_bible: WorldBible = Field(default_factory=WorldBible)
    conflict_registry: List[Conflict] = Field(default_factory=list)
    tension_graph: List[TensionBeat] = Field(default_factory=list)
    
    # Message History (Agent Debates & Logs)
    history: List[AgentMessage] = Field(default_factory=list)
    agent_memory: Dict[str, str] = Field(default_factory=dict) # Transient internal monologues
    
    # Production Data (Manuscript)
    chapters: List[Dict[str, Any]] = Field(default_factory=list) # Flexible chapter structure
    
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
            "Chapters": count_tokens(str(self.chapters)),
            "Total": 0
        }
        counts["Total"] = sum(counts.values())
        return counts
