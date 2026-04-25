import json
from pathlib import Path
from typing import Dict, Any
from src.core.state import (
    ProjectRegistry, WorldEntity, EntityType, WorldBible
)

class Importer05:
    """Utility to migrate BookBot_05 legacy logs to the new Narrative Registry format."""

    @staticmethod
    def load_legacy_log(file_path: str) -> Dict[str, Any]:
        with open(file_path, 'r') as f:
            return json.load(f)

    @staticmethod
    def migrate_to_registry(legacy_data: Dict[str, Any]) -> ProjectRegistry:
        data = legacy_data.get('data', {})
        
        # 1. Core Metadata
        plot_legacy = data.get('plot', {})
        style_legacy = data.get('style', {})
        
        registry = ProjectRegistry(
            title=legacy_data.get('book_title', "Untitled"),
            premise=plot_legacy.get('goals', ""),
            tone=style_legacy.get('tone', "Neutral"),
            voice=style_legacy.get('voice', "")
        )

        # 2. World Bible Entities
        world_legacy = data.get('world', {})
        if world_legacy.get('setting'):
            registry.world_bible.entities.append(WorldEntity(
                name="Primary Setting",
                entity_type=EntityType.LOCATION,
                description=world_legacy.get('setting', ""),
                attributes={"history": world_legacy.get('history', ""), "rules": world_legacy.get('rules', "")}
            ))
        
        chars_legacy = data.get('characters', [])
        for c in chars_legacy:
            registry.world_bible.entities.append(WorldEntity(
                name=c.get('name', "Unknown Character"),
                entity_type=EntityType.CHARACTER,
                description=c.get('archetype', ""),
                attributes={"arc": c.get('notes', "")}
            ))

        # 3. Chapters
        chapters_legacy = data.get('chapters', [])
        for c in chapters_legacy:
            registry.chapters.append({
                "chapter_number": c.get('chapter_number', 0),
                "title": c.get('title', "Untitled"),
                "content": c.get('summary', ""), # Summary becomes the initial content
                "scene_beats": c.get('scene_notes', "").split('\n') if c.get('scene_notes') else [],
                "audit_logs": []
            })

        registry.current_phase = "Imported"
        return registry

def run_migration(source_path: str, output_path: str):
    try:
        legacy = Importer05.load_legacy_log(source_path)
        registry = Importer05.migrate_to_registry(legacy)
        
        with open(output_path, 'w') as f:
            json.dump(registry.model_dump(mode='json'), f, indent=4)
        
        print(f"Migration complete: {source_path} -> {output_path}")
        return registry
    except Exception as e:
        print(f"Migration failed: {str(e)}")
        return None
