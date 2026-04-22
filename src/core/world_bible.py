from typing import List, Dict, Any, Optional
from src.core.state import ProjectRegistry, WorldEntity, EntityType, Conflict
from datetime import datetime

class WorldBibleManager:
    """Manages RAG-based retrieval and consistency checks for the World Bible."""

    def __init__(self, registry: ProjectRegistry):
        self.registry = registry

    def upsert_entity(self, name: str, entity_type: EntityType, description: str, attributes: Optional[Dict[str, Any]] = None) -> WorldEntity:
        """Adds or updates an entity in the bible."""
        # Check if entity already exists by name
        existing = next((e for e in self.registry.world_bible.entities if e.name.lower() == name.lower()), None)
        
        if existing:
            existing.description = description
            if attributes:
                existing.attributes.update(attributes)
            existing.last_updated = datetime.now()
            return existing
        else:
            new_entity = WorldEntity(
                name=name,
                entity_type=entity_type,
                description=description,
                attributes=attributes or {}
            )
            self.registry.world_bible.entities.append(new_entity)
            return new_entity

    def query_lore(self, query: str, top_k: int = 3) -> List[WorldEntity]:
        """
        Retrieves relevant entities based on a query.
        For now, uses simple keyword matching. In future, integrate vector search.
        """
        query_words = set(query.lower().split())
        scored_entities = []

        for entity in self.registry.world_bible.entities:
            score = 0
            entity_text = (entity.name + " " + entity.description + " " + str(entity.attributes)).lower()
            for word in query_words:
                if word in entity_text:
                    score += 1
            if score > 0:
                scored_entities.append((score, entity))

        # Sort by score and return top_k
        scored_entities.sort(key=lambda x: x[0], reverse=True)
        return [e[1] for e in scored_entities[:top_k]]

    def detect_conflicts(self, new_text: str) -> List[Conflict]:
        """
        Detects potential contradictions between new text and the World Bible.
        Example: "Character X has blue eyes" vs "Character X has green eyes".
        """
        conflicts = []
        # This is a placeholder for more advanced NLP-based conflict detection.
        # For now, we do a simple check for attribute-based conflicts if entities are mentioned.
        
        for entity in self.registry.world_bible.entities:
            if entity.name.lower() in new_text.lower():
                for attr, value in entity.attributes.items():
                    # Simple check: if attribute name is in text but value isn't
                    if attr.lower() in new_text.lower() and str(value).lower() not in new_text.lower():
                        conflicts.append(Conflict(
                            description=f"Potential conflict for {entity.name}: {attr} might be mismatched.",
                            affected_entities=[entity.name],
                            severity="medium"
                        ))
        
        return conflicts

    def get_context_chunk(self, query: str) -> str:
        """Generates a text chunk of relevant lore for LLM context injection."""
        relevant = self.query_lore(query)
        if not relevant:
            return "No specific lore found for this context."
        
        context = "Relevant Lore from World Bible:\n"
        for e in relevant:
            context += f"- {e.name} ({e.entity_type.value}): {e.description}\n"
            if e.attributes:
                context += f"  Attributes: {e.attributes}\n"
        return context
