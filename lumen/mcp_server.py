"""Lumen MCP Server - FastMCP server exposing Lumen to other agents."""

import os
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from fastmcp import FastMCP

from lumen.session_logger import SessionLogger
from lumen.token_counter import TokenCounter
from lumen.compressor import QwenCompressor
from lumen.synthesizer import SonnetSynthesizer
from lumen.router import ExpertRouter
from lumen.chroma_writer import ChromaWriter

load_dotenv()

mcp = FastMCP("lumen")

pipeline_initialized = False
pipeline = None


def get_pipeline():
    global pipeline_initialized, pipeline
    if not pipeline_initialized:
        pipeline = LumenPipeline()
        pipeline_initialized = True
    return pipeline


class LumenPipeline:
    def __init__(self):
        self.logger = SessionLogger()
        self.counter = TokenCounter()
        self.compressor = QwenCompressor()
        self.synthesizer = SonnetSynthesizer()
        self.router = ExpertRouter()
        self.writer = ChromaWriter()

    def ingest(self, text: str, session_id: Optional[str] = None) -> dict:
        if session_id:
            self.logger.session_id = session_id
        self.logger.from_text(text)
        
        token_count = self.counter.count(text)
        needs_compression, strategy = self.counter.needs_compression(token_count)
        
        if needs_compression:
            if strategy == "chunk":
                chunks = self.counter.chunk_text(text)
                compressed_chunks = [self.compressor.compress_chunk(c) for c in chunks]
                synthesized = self.synthesizer.synthesize_chunks(compressed_chunks)
                compressed_count = sum(self.counter.count(c) for c in compressed_chunks)
            else:
                compressed = self.compressor.compress(text)
                synthesized = self.synthesizer.synthesize(compressed)
                compressed_count = self.counter.count(compressed)
        else:
            synthesized = self.synthesizer.synthesize(text)
            compressed_count = token_count

        routes = self.router.route(synthesized)
        
        doc_ids = []
        for room, confidence in routes:
            doc_id = self.writer.write_memory(
                room=room,
                synthesized=synthesized,
                session_id=self.logger.session_id,
                token_count_original=token_count,
                token_count_compressed=compressed_count
            )
            doc_ids.append(doc_id)

        return {
            "session_id": self.logger.session_id,
            "timestamp": self.logger.timestamp,
            "token_count": token_count,
            "strategy": strategy,
            "routes": [(r.name, c) for r, c in routes],
            "synthesized": synthesized,
            "doc_ids": doc_ids
        }


@mcp.tool()
def lumen_query(text: str, room: Optional[str] = None, top_k: int = 5) -> dict:
    """Query Lumen memory system.
    
    Args:
        text: Query text to search for
        room: Optional room name to filter results
        top_k: Number of results to return (default 5)
    
    Returns:
        List of relevant memory results with metadata
    """
    writer = ChromaWriter()
    results = writer.query(text, room=room, n_results=top_k)
    
    formatted_results = []
    for result in results:
        formatted_results.append({
            "room": result["room"],
            "text": result["text"],
            "confidence": result.get("metadata", {}).get("confidence"),
            "emotional_valence": result.get("metadata", {}).get("emotional_valence"),
            "timestamp": result.get("metadata", {}).get("timestamp"),
        })
    
    return {"results": formatted_results, "count": len(formatted_results)}


@mcp.tool()
def lumen_ingest(text: str, session_id: Optional[str] = None) -> dict:
    """Ingest text into Lumen memory system.
    
    Args:
        text: Text content to ingest
        session_id: Optional session ID for tracking
    
    Returns:
        Ingestion result with routing and synthesis info
    """
    p = get_pipeline()
    result = p.ingest(text, session_id)
    return result


@mcp.tool()
def lumen_status() -> dict:
    """Get Lumen system status and statistics.
    
    Returns:
        Collection stats including document counts and last ingestion time
    """
    writer = ChromaWriter()
    stats = writer.get_collection_stats()
    last_ingestion = writer.get_last_ingestion()
    
    return {
        "collections": stats,
        "total_memories": sum(s["count"] for s in stats.values()),
        "last_ingestion": last_ingestion,
    }


if __name__ == "__main__":
    mcp.run()
