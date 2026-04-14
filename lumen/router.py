"""Expert Router for Lumen - routes content to appropriate rooms."""

from typing import Dict, List, Tuple
from lumen.rooms import ALL_ROOMS, BaseRoom


class ExpertRouter:
    """Routes synthesized content to appropriate room experts."""

    def __init__(self):
        self.rooms = ALL_ROOMS

    def route(self, synthesized: Dict) -> List[Tuple[BaseRoom, float]]:
        """Route content to rooms based on relevance scores.
        
        Returns list of (room, confidence) tuples sorted by confidence.
        Returns top 1-3 rooms with confidence > 0.1.
        """
        scored = []
        for room in self.rooms:
            score = room.score_content(synthesized)
            if score > 0.1:
                scored.append((room, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:3]

    def get_primary_room(self, synthesized: Dict) -> BaseRoom:
        """Get the primary room for this content."""
        routes = self.route(synthesized)
        if routes:
            return routes[0][0]
        return self.rooms[1]

    def format_routing(self, routes: List[Tuple[BaseRoom, float]]) -> str:
        """Format routing decisions for display."""
        if not routes:
            return "No significant room matches found."
        
        lines = ["Room Routing:"]
        for room, score in routes:
            lines.append(f"  - {room.name}: {score:.2f}")
        return "\n".join(lines)
