"""Base room class for Lumen expert rooms."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class BaseRoom(ABC):
    """Abstract base class for all Lumen room experts.
    
    Each room has a domain specialty and maintains its own ChromaDB collection.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Room name."""
        pass

    @property
    @abstractmethod
    def collection_name(self) -> str:
        """ChromaDB collection name for this room."""
        pass

    @property
    @abstractmethod
    def domain(self) -> str:
        """Domain description for this room."""
        pass

    @property
    def retrieval_prompt(self) -> str:
        """Prompt used at query time to focus retrieval."""
        return f"You are answering questions about {self.domain}."

    @property
    def ingestion_prompt(self) -> str:
        """Prompt used at write time to filter/annotate content."""
        return (
            f"From this content about {self.domain}, extract: "
            "key facts, concepts, decisions, and any unresolved questions. "
            "Preserve emotional texture and named entities."
        )

    def score_content(self, content: Dict) -> float:
        """Score how well content matches this room's domain.
        
        Returns confidence score 0.0-1.0.
        """
        text = content.get("summary", "") + " " + " ".join(content.get("key_facts", []))
        text_lower = text.lower()
        return self._calculate_domain_score(text_lower)

    @abstractmethod
    def _calculate_domain_score(self, text: str) -> float:
        """Room-specific scoring logic."""
        pass

    def format_for_retrieval(self, documents: List[Dict]) -> str:
        """Format retrieved documents for presentation."""
        if not documents:
            return f"No relevant memories found in {self.name}."

        formatted = [f"=== {self.name} ==="]
        for doc in documents:
            formatted.append(f"\n[{doc.get('timestamp', 'unknown')}]")
            formatted.append(doc.get("text", ""))
            if doc.get("emotional_valence"):
                formatted.append(f"(valence: {doc['emotional_valence']})")
        return "\n".join(formatted)

    def filter_content(self, content: Dict) -> Dict:
        """Filter and annotate content for this room's domain."""
        return {
            "room": self.name,
            "collection": self.collection_name,
            "content": content.get("summary", ""),
            "facts": content.get("key_facts", []),
            "threads": content.get("open_threads", []),
            "connections": content.get("connections", []),
        }
