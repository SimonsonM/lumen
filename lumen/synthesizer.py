"""Claude Sonnet synthesis for Lumen pipeline."""

import json
import os
from typing import Dict, Optional
from anthropic import Anthropic


class SonnetSynthesizer:
    """Synthesizes compressed transcript into structured memory using Claude Sonnet."""

    SYNTHESIS_PROMPT = """You are synthesizing a conversation transcript into a structured memory for a personal memory system.

Extract and return a JSON object with these fields:
- "summary": 2-3 sentence summary capturing the core essence
- "key_facts": list of specific facts, decisions, or concrete details
- "connections": list of connections to prior context or existing knowledge
- "open_threads": list of unresolved questions or open tasks
- "emotional_valence": "positive", "negative", "neutral", or "complex"
- "confidence": a number 0.0-1.0 representing synthesis confidence

Transcript:
{transcript}

Return ONLY valid JSON, no markdown formatting or additional text."""

    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-sonnet-4-20250514"

    def synthesize(self, text: str) -> Dict:
        """Synthesize text into structured memory JSON."""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": self.SYNTHESIS_PROMPT.format(transcript=text)
                    }
                ]
            )
            response_text = response.content[0].text.strip()
            
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            result = json.loads(response_text)
            result["confidence"] = max(0.0, min(1.0, result.get("confidence", 0.7)))
            
            if result.get("emotional_valence") not in ["positive", "negative", "neutral", "complex"]:
                result["emotional_valence"] = "neutral"
            
            return result

        except Exception as e:
            print(f"Sonnet synthesis failed: {e}")
            return {
                "summary": text[:500] if len(text) > 500 else text,
                "key_facts": [],
                "connections": [],
                "open_threads": ["synthesis_failed"],
                "emotional_valence": "neutral",
                "confidence": 0.3
            }

    def synthesize_chunks(self, chunks: list[str]) -> Dict:
        """Synthesize multiple compressed chunks into single memory."""
        combined = "\n\n---\n\n".join(chunks)
        return self.synthesize(combined)
