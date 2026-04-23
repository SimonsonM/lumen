"""Lumen CLI - Query interface for Lumen memory system."""

import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

import click
from dotenv import load_dotenv

from lumen.session_logger import SessionLogger
from lumen.token_counter import TokenCounter
from lumen.compressor import QwenCompressor
from lumen.synthesizer import SonnetSynthesizer
from lumen.router import ExpertRouter
from lumen.chroma_writer import ChromaWriter
from lumen.vault_mirror import VaultMirror
from lumen.rooms import ALL_ROOMS

load_dotenv()


class LumenPipeline:
    """Full Lumen ingestion pipeline."""

    def __init__(self):
        self.logger = SessionLogger()
        self.counter = TokenCounter()
        self.compressor = QwenCompressor()
        self.synthesizer = SonnetSynthesizer()
        self.router = ExpertRouter()
        self.writer = ChromaWriter()
        self.vault = VaultMirror()

    def ingest(self, text: str, session_id: Optional[str] = None) -> dict:
        """Run full ingestion pipeline on text."""
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

        vault_path = None
        try:
            vp = self.vault.write_session(
                session_id=self.logger.session_id,
                timestamp=self.logger.timestamp,
                synthesized=synthesized,
                routes=routes,
                token_count=token_count,
                compressed_count=compressed_count,
                doc_ids=doc_ids,
            )
            if vp is not None:
                vault_path = str(vp)
        except Exception as e:
            print(f"[lumen.vault] mirror error: {e}")

        return {
            "session_id": self.logger.session_id,
            "timestamp": self.logger.timestamp,
            "token_count": token_count,
            "strategy": strategy,
            "routes": [(r.name, c) for r, c in routes],
            "synthesized": synthesized,
            "doc_ids": doc_ids,
            "vault_path": vault_path,
        }


@click.group()
def cli():
    """Lumen - Persistent Memory Architecture."""
    pass


@cli.command()
@click.argument("text")
@click.option("--room", "-r", help="Filter to specific room")
@click.option("--top-k", "-k", default=5, help="Number of results to return")
def query(text: str, room: Optional[str], top_k: int):
    """Query Lumen memory."""
    writer = ChromaWriter()
    
    results = writer.query(text, room=room, n_results=top_k)
    
    if not results:
        click.echo("No results found.")
        return
    
    for i, result in enumerate(results, 1):
        click.echo(f"\n--- Result {i} ({result['room']}) ---")
        click.echo(f"Confidence: {result.get('metadata', {}).get('confidence', 'N/A')}")
        click.echo(f"Valence: {result.get('metadata', {}).get('emotional_valence', 'N/A')}")
        click.echo(f"\n{result['text'][:500]}...")


@cli.command()
@click.argument("file", type=click.Path(exists=True))
def ingest(file: str):
    """Ingest a transcript file into Lumen."""
    pipeline = LumenPipeline()
    
    logger = SessionLogger()
    text = logger.from_file(file)
    
    click.echo(f"Ingesting {logger.get_metadata()['token_count']} tokens...")
    
    result = pipeline.ingest(text)
    
    click.echo("\n=== Ingestion Complete ===")
    click.echo(f"Session ID: {result['session_id']}")
    click.echo(f"Strategy: {result['strategy']}")
    click.echo(f"Routed to: {', '.join(f'{r[0]} ({r[1]:.2f})' for r in result['routes'])}")
    click.echo(f"\nSummary: {result['synthesized'].get('summary', 'N/A')}")


@cli.command()
def status():
    """Show Lumen status and statistics."""
    writer = ChromaWriter()
    stats = writer.get_collection_stats()
    last_ingestion = writer.get_last_ingestion()
    
    click.echo("=== Lumen Status ===\n")
    
    if not stats:
        click.echo("No memories stored yet.")
        return
    
    click.echo("Collections:")
    total = 0
    for room, info in sorted(stats.items(), key=lambda x: x[1]["count"], reverse=True):
        click.echo(f"  {room:15} {info['count']:5} documents")
        total += info["count"]
    
    click.echo(f"\nTotal memories: {total}")
    if last_ingestion:
        click.echo(f"Last ingestion: {last_ingestion}")


@cli.command()
def dream():
    """Trigger manual Dream Cycle consolidation."""
    click.echo("Dream Cycle consolidation not yet connected to external Dream Cycle.")
    click.echo("This hook will be activated when Dream Cycle Phase 1 integration is complete.")


@cli.command()
@click.argument("text")
def test_synthesis(text: str):
    """Test synthesis without storage."""
    pipeline = LumenPipeline()
    result = pipeline.ingest(text)
    import json
    click.echo(json.dumps(result["synthesized"], indent=2))


if __name__ == "__main__":
    cli()
