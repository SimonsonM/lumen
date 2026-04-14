"""Integration tests for Lumen pipeline."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from lumen.session_logger import SessionLogger
from lumen.token_counter import TokenCounter
from lumen.router import ExpertRouter
from lumen.rooms import ALL_ROOMS


def test_session_logger():
    logger = SessionLogger()
    text = "Test session about Lumen architecture"
    logger.from_text(text)
    
    assert logger.content == text
    assert logger.session_id
    assert logger.timestamp
    print("Session logger: PASS")


def test_token_counter():
    counter = TokenCounter()
    text = "This is a test transcript for token counting."
    count = counter.count(text)
    
    assert count > 0
    
    needs_comp, strategy = counter.needs_compression(count)
    assert strategy == "direct"
    
    needs_comp, strategy = counter.needs_compression(5000)
    assert strategy == "compress"
    
    needs_comp, strategy = counter.needs_compression(10000)
    assert strategy == "chunk"
    
    print("Token counter: PASS")


def test_chunking():
    counter = TokenCounter()
    long_text = " ".join(["word"] * 1000)
    chunks = counter.chunk_text(long_text, chunk_size=200, overlap=50)
    
    assert len(chunks) > 1
    print(f"Chunking: PASS (created {len(chunks)} chunks)")


def test_router_scoring():
    router = ExpertRouter()
    
    lumen_content = {
        "summary": "Designed Lumen memory architecture with ChromaDB and room experts",
        "key_facts": ["Lumen uses ChromaDB", "Has seven room experts", "Named after hello_world_01"],
        "connections": ["Similar to Dream Cycle"],
        "open_threads": ["Build not yet started"],
        "emotional_valence": "positive",
        "confidence": 0.8
    }
    
    routes = router.route(lumen_content)
    
    assert len(routes) >= 1
    room_names = [r[0].name for r in routes]
    
    assert "memory" in room_names or "technical" in room_names
    
    print(f"Router scoring: PASS")
    print(f"  Routes: {[(r.name, f'{s:.2f}') for r, s in routes]}")


def test_room_scoring():
    memory_room = next(r for r in ALL_ROOMS if r.name == "memory")
    
    lumen_content = {
        "summary": "Building Lumen with ChromaDB",
        "key_facts": ["Lumen", "ChromaDB", "Dream Cycle"]
    }
    
    score = memory_room.score_content(lumen_content)
    assert score > 0.3
    
    technical_room = next(r for r in ALL_ROOMS if r.name == "technical")
    score2 = technical_room.score_content(lumen_content)
    assert score2 > 0
    
    print(f"Room scoring: PASS (memory: {score:.2f}, technical: {score2:.2f})")


def test_all_rooms():
    for room in ALL_ROOMS:
        assert room.name
        assert room.collection_name
        assert room.domain
        assert room.retrieval_prompt
        assert room.ingestion_prompt
    print(f"All rooms ({len(ALL_ROOMS)}): PASS")


if __name__ == "__main__":
    test_session_logger()
    test_token_counter()
    test_chunking()
    test_room_scoring()
    test_router_scoring()
    test_all_rooms()
    print("\n=== All tests passed ===")
