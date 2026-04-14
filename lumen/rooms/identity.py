"""Identity room - emotional threads, personal history, grief, relationships, self-concept."""

from lumen.rooms.base_room import BaseRoom


class IdentityRoom(BaseRoom):
    """Expert on emotional threads, personal history, and self-concept."""

    @property
    def name(self) -> str:
        return "identity"

    @property
    def collection_name(self) -> str:
        return "lumen_identity"

    @property
    def domain(self) -> str:
        return "emotional threads, personal history, grief, relationships, self-concept, feelings"

    @property
    def retrieval_prompt(self) -> str:
        return (
            "You are exploring questions about personal identity, emotional history, "
            "and self-concept. Focus on: emotional threads, grief processing, "
            "relationship dynamics, personal growth, and sense of self."
        )

    @property
    def ingestion_prompt(self) -> str:
        return (
            "Extract emotional and identity content: feelings, personal history, "
            "grief, relationship dynamics, self-reflection, and personal growth. "
            "Preserve emotional texture and vulnerability."
        )

    def _calculate_domain_score(self, text: str) -> float:
        score = 0.0
        identity_keywords = [
            "feel", "feeling", "emotion", "grief", "loss", "sad", "happy",
            "angry", "afraid", "anxious", "depressed", "healing", "processing",
            "myself", "self", "identity", "who i am", "personal", "childhood",
            "memories", "family", "father", "mother", "brother", "sister",
            "divorce", "marriage", "relationship", "intimate", "vulnerable",
            "growth", "healing", "therapy", "trauma", "ptsd", "attachment",
            "worth", "value", "purpose", "meaning", "existential"
        ]
        for kw in identity_keywords:
            if kw in text:
                score += 0.13
        return min(score, 1.0)
