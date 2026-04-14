"""Consciousness room - philosophy, quantum mechanics, hard problem, psychedelics."""

from lumen.rooms.base_room import BaseRoom


class ConsciousnessRoom(BaseRoom):
    """Expert on consciousness, philosophy of mind, and subjective experience."""

    @property
    def name(self) -> str:
        return "consciousness"

    @property
    def collection_name(self) -> str:
        return "lumen_consciousness"

    @property
    def domain(self) -> str:
        return ("philosophy, quantum mechanics, hard problem of consciousness, "
                "Orch-OR theory, psychedelics, subjective experience, awareness")

    @property
    def retrieval_prompt(self) -> str:
        return (
            "You are a philosopher specializing in consciousness studies. "
            "Focus on: hard problem of consciousness, quantum approaches to mind, "
            "Orch-OR, integrated information theory, psychedelic states, "
            "the nature of subjective experience and qualia."
        )

    @property
    def ingestion_prompt(self) -> str:
        return (
            "Extract philosophical content about consciousness, mind, subjective experience, "
            "quantum approaches to consciousness, or altered states. Preserve theoretical frameworks "
            "and key thinkers mentioned."
        )

    def _calculate_domain_score(self, text: str) -> float:
        score = 0.0
        consciousness_keywords = [
            "consciousness", "awareness", "qualia", "subjective experience",
            "hard problem", "orch-or", "quantum mind", "integrated information",
            "phi", "panpsychism", "dualism", "physicalism", "phenomenal",
            "psychedelic", "dmt", "lsd", "psilocybin", "mystical", "nondual",
            "til", "ego death", "consciousness", "mind", "brain", "neural",
            "philosophy of mind", "the hard problem"
        ]
        for kw in consciousness_keywords:
            if kw in text:
                score += 0.15
        return min(score, 1.0)
