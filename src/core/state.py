from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class Character(BaseModel):
    name: str = ""
    description: str = ""
    arc: str = ""

class WorldSpecs(BaseModel):
    setting: str = ""
    history: str = ""
    rules: str = ""
    other: str = ""

class StyleSpecs(BaseModel):
    """Narrative style, tone, and voice constraints."""
    tone: str = ""
    voice: str = ""
    vocabulary: str = ""
    pov_global: str = "Third Person Limited"
    tense: str = "Past"

class PlotSpecs(BaseModel):
    """Core plot premise, goals, and conflicts."""
    book_title: str = "Untitled Project"
    premise: str = ""
    goals: str = ""
    conflicts: str = ""
    stakes: str = ""
    style: StyleSpecs = Field(default_factory=StyleSpecs)

# --- Phase Specific Models ---

class Phase1State(BaseModel):
    """User Inputs & Initial Brainstorming"""
    premise: str = ""
    world: WorldSpecs = Field(default_factory=WorldSpecs)
    characters: List[Character] = Field(default_factory=list)
    completeness_check: Optional[str] = None

class Phase2Chapter(BaseModel):
    """A single chapter skeleton (3-4 sentences)"""
    chapter_number: int
    title: str = ""
    summary: str = ""

class Phase2State(BaseModel):
    """Chapter Skeletons"""
    chapters: List[Phase2Chapter] = Field(default_factory=list)

class Phase3Chapter(BaseModel):
    """Detailed chapter story with beats and arcs"""
    chapter_number: int
    title: str = ""
    story_details: str = ""
    character_arc_notes: str = ""
    plot_threads: List[str] = Field(default_factory=list)
    scene_beats: List[str] = Field(default_factory=list)

class Phase3State(BaseModel):
    """Detailed Story Outlines"""
    chapters: List[Phase3Chapter] = Field(default_factory=list)

class Phase4Chapter(BaseModel):
    """Prose draft for a chapter"""
    chapter_number: int
    draft_content: str = ""
    word_count: int = 0
    last_1000_words: str = "" # For context pruning consistency

class Phase4State(BaseModel):
    """First Drafts"""
    chapters: List[Phase4Chapter] = Field(default_factory=list)

class Phase5State(BaseModel):
    """Final Manuscript & Art Prompts"""
    final_manuscript: str = ""
    illustration_prompts: Dict[str, str] = Field(default_factory=dict) # e.g. {"Cover": "prompt..."}

class Phase6State(BaseModel):
    """Marketing & Publish Readiness"""
    cover_copy: str = ""
    marketing_copy: str = ""
    back_cover_text: str = ""

# --- Root Registry ---

class ProjectRegistry(BaseModel):
    """The central source of truth for a BookBot_06 project."""
    project_id: str = Field(default_factory=lambda: datetime.now().strftime("%Y%m%d_%H%M%S"))
    metadata: PlotSpecs = Field(default_factory=PlotSpecs)
    
    phase1: Phase1State = Field(default_factory=Phase1State)
    phase2: Phase2State = Field(default_factory=Phase2State)
    phase3: Phase3State = Field(default_factory=Phase3State)
    phase4: Phase4State = Field(default_factory=Phase4State)
    phase5: Phase5State = Field(default_factory=Phase5State)
    phase6: Phase6State = Field(default_factory=Phase6State)
    
    current_phase: int = 1
    last_updated: datetime = Field(default_factory=datetime.now)

    def log_entry(self):
        """Prepares a dictionary representation for persistence."""
        return {
            "project_id": self.project_id,
            "title": self.metadata.book_title,
            "phase": self.current_phase,
            "data": self.model_dump(mode='json')
        }
