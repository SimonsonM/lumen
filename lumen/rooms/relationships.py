"""Relationships room - Teagan, Mea, Debbie, Dexter, Sonny, Bryan, William, Andrea."""

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
        return ("relationships with Teagan, Mea, Debbie, Dexter, Sonny, Bryan, "
                "William, Andrea, and other important people")

    @property
    def retrieval_prompt(self) -> str:
        return (
            "You are exploring content about relationships and social connections. "
            "Focus on: Teagan, Mea, Debbie, Dexter, Sonny, Bryan, William, Andrea, "
            "and other important relationships in Mike's life."
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
        people = ["teagan", "mea", "debbie", "dexter", "sonny", "bryan", "william", "andrea"]
        relationship_keywords = [
            "relationship", "friend", "family", "partner", "date", "dinner",
            "lunch", "meet", "visit", "call", "text", "message", "talked",
            "coffee", "hang out", "together", "relationship"
        ]
        text_lower = text.lower()
        for person in people:
            if person in text_lower:
                score += 0.35
        for kw in relationship_keywords:
            if kw in text_lower:
                score += 0.08
        return min(score, 1.0)
