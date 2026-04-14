"""ChromaDB writer for Lumen - stores memories in ChromaDB collections."""

import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import chromadb
from chromadb.config import Settings


class ChromaWriter:
    """Writes synthesized content to ChromaDB collections."""

    def __init__(self, chroma_path: Optional[str] = None):
        self.chroma_path = chroma_path or os.getenv("CHROMA_PATH", "/home/mike/.claude_memory")
        self.client = chromadb.PersistentClient(
            path=self.chroma_path,
            settings=Settings(anonymized_telemetry=False)
        )
        self.embedding_model = "nomic-embed-text"
        self.collections = {}

    def _get_or_create_collection(self, name: str):
        """Get or create a ChromaDB collection."""
        if name not in self.collections:
            self.collections[name] = self.client.get_or_create_collection(
                name=name,
                metadata={"description": f"Lumen {name} memory collection"}
            )
        return self.collections[name]

    def _embed_text(self, text: str) -> List[float]:
        """Generate embedding using nomic-embed-text via Ollama."""
        import requests
        import json
        
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        try:
            response = requests.post(
                f"{ollama_url}/api/embeddings",
                json={"model": self.embedding_model, "prompt": text},
                timeout=60
            )
            response.raise_for_status()
            return response.json().get("embedding", [])
        except Exception as e:
            print(f"Embedding failed: {e}")
            return [0.0] * 768

    def write_memory(
        self,
        room,
        synthesized: Dict,
        session_id: str,
        token_count_original: int = 0,
        token_count_compressed: int = 0
    ) -> str:
        """Write a synthesized memory to the appropriate room collection."""
        collection = self._get_or_create_collection(room.collection_name)
        
        doc_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        content = self._build_document_content(synthesized)
        
        try:
            embedding = self._embed_text(content)
        except Exception:
            embedding = [0.0] * 768
        
        metadata = {
            "timestamp": timestamp,
            "session_id": session_id,
            "room": room.name,
            "confidence": synthesized.get("confidence", 0.5),
            "emotional_valence": synthesized.get("emotional_valence", "neutral"),
            "token_count_original": token_count_original,
            "token_count_compressed": token_count_compressed,
        }
        
        collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[content],
            metadatas=[metadata]
        )
        
        return doc_id

    def _build_document_content(self, synthesized: Dict) -> str:
        """Build document content from synthesized JSON."""
        parts = [synthesized.get("summary", "")]
        
        key_facts = synthesized.get("key_facts", [])
        if key_facts:
            parts.append("\n\nKey Facts:")
            for fact in key_facts:
                parts.append(f"- {fact}")
        
        connections = synthesized.get("connections", [])
        if connections:
            parts.append("\n\nConnections:")
            for conn in connections:
                parts.append(f"- {conn}")
        
        threads = synthesized.get("open_threads", [])
        if threads:
            parts.append("\n\nOpen Threads:")
            for thread in threads:
                parts.append(f"- {thread}")
        
        return "\n".join(parts)

    def query(
        self,
        query_text: str,
        room: Optional[str] = None,
        n_results: int = 5
    ) -> List[Dict]:
        """Query memories from ChromaDB."""
        query_embedding = self._embed_text(query_text)
        
        if room:
            collections_to_search = [room]
        else:
            collections_to_search = [c.name for c in self.client.list_collections()]
        
        all_results = []
        for collection_name in collections_to_search:
            collection = self._get_or_create_collection(collection_name)
            try:
                results = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=n_results
                )
                if results and results.get("documents"):
                    for i, doc in enumerate(results["documents"][0]):
                        all_results.append({
                            "room": collection_name,
                            "text": doc,
                            "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
                            "distance": results["distances"][0][i] if results.get("distances") else 0
                        })
            except Exception as e:
                print(f"Query failed for {collection_name}: {e}")
        
        all_results.sort(key=lambda x: x.get("distance", 999))
        return all_results[:n_results]

    def get_collection_stats(self) -> Dict:
        """Get statistics for all collections."""
        stats = {}
        for collection in self.client.list_collections():
            count = collection.count()
            if count > 0:
                room_name = collection.name.replace("lumen_", "")
                stats[room_name] = {
                    "collection": collection.name,
                    "count": count
                }
        return stats

    def get_last_ingestion(self) -> Optional[str]:
        """Get timestamp of last ingested memory."""
        for collection in self.client.list_collections():
            try:
                result = collection.get(limit=1, include=["metadatas"])
                if result and result.get("metadatas"):
                    return result["metadatas"][0].get("timestamp")
            except Exception:
                pass
        return None
