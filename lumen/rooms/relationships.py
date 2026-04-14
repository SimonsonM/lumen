"""Relationships room - key people in the user's life."""

from lumen.rooms.base_room import BaseRoom


class RelationshipsRoom(BaseRoom):
    """Expert on relationships and social connections."""

    @property
    def name(self) -> str:
        return "relationships"

    @property
    def collection_name(self) -> str:
        return "lumen_relationships"

    @property
    def domain(self) -> str:
        return ("relationships with key people, "
                "and other important people")

    @property
    def retrieval_prompt(self) -> str:
        return (
            "You are exploring content about relationships and social connections. "
            "Focus on: named people, "
            "and other important relationships."
        )

    @property
    def ingestion_prompt(self) -> str:
        return (
            "Extract relationship content: interactions with named people, "
            "relationship dynamics, social plans, and important connections. "
            "Preserve context about each relationship."
        )

    def _calculate_domain_score(self, text: str) -> float:
        score = 0.0
        relationship_keywords = [
            "relationship", "friend", "family", "partner", "date", "dinner",
            "lunch", "meet", "visit", "call", "text", "message", "talked",
            "coffee", "hang out", "together", "relationship"
        ]
        text_lower = text.lower()
        for kw in relationship_keywords:
            if kw in text_lower:
                score += 0.15
        return min(score, 1.0)
