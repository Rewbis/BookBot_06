import json
from pathlib import Path
from typing import Dict, Any
from src.core.state import (
    ProjectRegistry, Phase1State, Phase2State, Phase3State, 
    Phase2Chapter, Phase3Chapter, Character, WorldSpecs, PlotSpecs, StyleSpecs
)

class Importer05:
    """Utility to migrate BookBot_05 legacy logs to BookBot_06 Registry format."""

    @staticmethod
    def load_legacy_log(file_path: str) -> Dict[str, Any]:
        with open(file_path, 'r') as f:
            return json.load(f)

    @staticmethod
    def migrate_to_registry(legacy_data: Dict[str, Any]) -> ProjectRegistry:
        data = legacy_data.get('data', {})
        
        # 1. Metadata
        plot_legacy = data.get('plot', {})
        style_legacy = data.get('style', {})
        
        style = StyleSpecs(
            tone=style_legacy.get('tone', ""),
            voice=style_legacy.get('voice', ""),
            vocabulary=style_legacy.get('vocabulary', ""),
            pov_global=style_legacy.get('pov_global', "Third Person Limited"),
            tense=style_legacy.get('tense', "Past")
        )
        
        metadata = PlotSpecs(
            book_title=legacy_data.get('book_title', "Untitled"),
            premise=plot_legacy.get('goals', ""), # Goals is where the premise often lived
            goals=plot_legacy.get('goals', ""),
            conflicts=plot_legacy.get('conflicts', ""),
            stakes=plot_legacy.get('stakes', ""),
            style=style
        )

        registry = ProjectRegistry(metadata=metadata)

        # 2. Phase 1 State
        world_legacy = data.get('world', {})
        world = WorldSpecs(
            setting=world_legacy.get('setting', ""),
            history=world_legacy.get('history', ""),
            rules=world_legacy.get('rules', ""),
            other=world_legacy.get('other', "")
        )
        
        chars_legacy = data.get('characters', [])
        characters = [
            Character(name=c.get('name', ""), description=c.get('archetype', ""), arc=c.get('notes', ""))
            for c in chars_legacy
        ]
        
        registry.phase1 = Phase1State(
            premise=metadata.premise,
            world=world,
            characters=characters
        )

        # 3. Phase 2 & 3 State (Mapping Chapters)
        chapters_legacy = data.get('chapters', [])
        phase2_chapters = []
        phase3_chapters = []
        
        for c in chapters_legacy:
            # Phase 2: Skeleton (Summary)
            p2 = Phase2Chapter(
                chapter_number=c.get('chapter_number', 0),
                title=c.get('title', "Untitled"),
                summary=c.get('summary', "")
            )
            phase2_chapters.append(p2)
            
            # Phase 3: Story (If detailed notes exist)
            if c.get('scene_notes'):
                p3 = Phase3Chapter(
                    chapter_number=c.get('chapter_number', 0),
                    title=c.get('title', "Untitled"),
                    story_details=c.get('summary', ""),
                    scene_beats=c.get('scene_notes', "").split('\n'),
                    plot_threads=[c.get('plot_thread_a', ""), c.get('plot_thread_b', "")]
                )
                phase3_chapters.append(p3)

        registry.phase2 = Phase2State(chapters=phase2_chapters)
        registry.phase3 = Phase3State(chapters=phase3_chapters)

        # Set phase based on progress
        if phase3_chapters:
            registry.current_phase = 3
        elif phase2_chapters:
            registry.current_phase = 2
        else:
            registry.current_phase = 1

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

if __name__ == "__main__":
    # Test migration for A Tricky Tail
    src = "e:/Coding/BookBot_05/logs/log_A_tricky_tail_20260418_195429.json"
    dest = "e:/Coding/BookBot_06/logs/migrated_tricky_tail.json"
    run_migration(src, dest)
