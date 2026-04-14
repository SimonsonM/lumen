"""Token counter for Lumen pipeline."""

import tiktoken


class TokenCounter:
    """Counts tokens in text using tiktoken."""

    def __init__(self, model: str = "cl100k_base"):
        self.encoding = tiktoken.get_encoding(model)

    def count(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.encoding.encode(text))

    def count_messages(self, messages: list) -> int:
        """Count tokens in a list of message dicts."""
        total = 0
        for msg in messages:
            total += 3
            total += self.count(msg.get("content", ""))
            total += self.count(msg.get("role", ""))
        total += 3
        return total

    def needs_compression(self, token_count: int) -> tuple[bool, str]:
        """Determine if content needs compression.
        
        Returns (needs_compression, strategy):
        - (<2000): "direct" - skip compression
        - (2000-8000): "compress" - use Qwen compression
        - (>8000): "chunk" - split into overlapping segments
        """
        if token_count < 2000:
            return False, "direct"
        elif token_count <= 8000:
            return True, "compress"
        else:
            return True, "chunk"

    def chunk_text(self, text: str, chunk_size: int = 768, overlap: int = 512) -> list[str]:
        """Split text into overlapping chunks."""
        tokens = self.encoding.encode(text)
        chunks = []
        
        start = 0
        while start < len(tokens):
            end = start + chunk_size
            chunk_tokens = tokens[start:end]
            chunk_text = self.encoding.decode(chunk_tokens)
            chunks.append(chunk_text)
            start = end - overlap
            
            if start >= len(tokens):
                break
        
        return chunks
