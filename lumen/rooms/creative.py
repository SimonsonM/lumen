"""Creative room - art, Murica! universe, photography, skydiving, design."""

from lumen.rooms.base_room import BaseRoom


class CreativeRoom(BaseRoom):
    """Expert on creative pursuits, art, and adventure."""

    @property
    def name(self) -> str:
        return "creative"

    @property
    def collection_name(self) -> str:
        return "lumen_creative"

    @property
    def domain(self) -> str:
        return "art, creative projects, Murica! universe, photography, skydiving, design, aesthetics"

    @property
    def retrieval_prompt(self) -> str:
        return (
            "You are exploring creative and artistic content. "
            "Focus on: art projects, photography, creative writing, design, "
            "skydiving adventures, the Murica! universe, and aesthetic pursuits."
        )

    @property
    def ingestion_prompt(self) -> str:
        return (
            "Extract creative content: art projects, photography, creative writing, "
            "design work, skydiving experiences, and aesthetic explorations. "
            "Preserve creative vision and artistic intent."
        )

    def _calculate_domain_score(self, text: str) -> float:
        score = 0.0
        creative_keywords = [
            "art", "creative", "photo", "photography", "design", "aesthetic",
            "skydiving", "skydive", "jump", "creative writing", "fiction",
            "murica", "universe", "character", "story", "narrative",
            "camera", "lens", "image", "visual", "illustration", "painting",
            "draw", "sketch", "music", "song", "poetry", "adventure",
            "thrill", "extreme", "risk", "freedom", "flight"
        ]
        for kw in creative_keywords:
            if kw in text:
                score += 0.15
        return min(score, 1.0)
