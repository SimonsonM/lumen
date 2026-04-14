"""Memory room - memory architecture, Lumen itself, Dream Cycle, AI cognition."""

from lumen.rooms.base_room import BaseRoom


class MemoryRoom(BaseRoom):
    """Expert on memory architecture and AI cognition."""

    @property
    def name(self) -> str:
        return "memory"

    @property
    def collection_name(self) -> str:
        return "lumen_memory"

    @property
    def domain(self) -> str:
        return "memory architecture, Lumen, Dream Cycle, AI cognition, knowledge systems"

    @property
    def retrieval_prompt(self) -> str:
        return (
            "You are answering questions about memory architecture and AI cognition. "
            "Focus on: Lumen, Dream Cycle, memory systems, knowledge retrieval, "
            "hippocampal consolidation, and AI memory design."
        )

    @property
    def ingestion_prompt(self) -> str:
        return (
            "Extract memory architecture content: Lumen design, Dream Cycle, "
            "memory systems, AI cognition patterns, and knowledge architecture. "
            "Preserve technical design decisions and integration points."
        )

    def _calculate_domain_score(self, text: str) -> float:
        score = 0.0
        memory_keywords = [
            "lumen", "memory", "dream cycle", "chroma", "chromadb", "embed",
            "vector", "retrieval", "consolidation", "hippocampal", "expert",
            "room", "rooms", "synthesis", "compression", "transcript",
            "session", "knowledge", "persistence", "persistent",
            "architecture", "system", "design", "component", "pipeline",
            "ai memory", "agent memory", "context window", "forgetting",
            "reconstruction", "semantic", "episodic"
        ]
        for kw in memory_keywords:
            if kw in text:
                score += 0.18
        return min(score, 1.0)
