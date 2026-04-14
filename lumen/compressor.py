"""Qwen compression for Lumen pipeline."""

import os
import requests
from pathlib import Path


class QwenCompressor:
    """Compresses transcript using Qwen2.5:7b via Ollama."""

    OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    COMPRESSED_OUTPUT = Path("/tmp/lumen_compressed.txt")

    COMPRESSION_PROMPT = """You are compressing a conversation transcript for a personal memory system.

Task: Strip filler, preserve signal. Keep:
- Emotional texture and reactions
- Technical decisions and conclusions
- Named entities and specific references
- Open threads and unresolved questions
- Stated intentions and future plans

Target: 30-40% of original token count.

Transcript:
{transcript}

Compressed version:"""

    def __init__(self):
        self.model = "qwen2.5:7b"

    def compress(self, text: str) -> str:
        """Compress text using Qwen via Ollama."""
        prompt = self.COMPRESSION_PROMPT.format(transcript=text)

        try:
            response = requests.post(
                f"{self.OLLAMA_URL}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": 2000,
                    }
                },
                timeout=120
            )
            response.raise_for_status()
            result = response.json()
            compressed = result.get("response", "").strip()
        except requests.exceptions.RequestException as e:
            print(f"Ollama request failed: {e}")
            compressed = text[:int(len(text) * 0.4)]

        output = Path(self.COMPRESSED_OUTPUT)
        output.write_text(compressed)
        return compressed

    def compress_chunk(self, text: str) -> str:
        """Compress a single chunk of a larger transcript."""
        return self.compress(text)
