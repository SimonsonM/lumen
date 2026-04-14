# Lumen

Persistent Memory Architecture for Mike Simonson.

*"The moment before something begins."*

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         LUMEN PIPELINE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Raw Transcript                                                 │
│       │                                                         │
│       ▼                                                         │
│  ┌─────────────┐                                               │
│  │Token Counter│──< 2000──► Direct to Synthesis                │
│  └─────────────┘                                               │
│       │                                                         │
│       ▼ (2000-8000)                                             │
│  ┌─────────────┐                                               │
│  │    Qwen     │  Compress to 30-40%                           │
│  │ Compressor  │                                               │
│  └─────────────┘                                               │
│       │                                                         │
│       ▼ (>8000)                                                 │
│  ┌─────────────┐                                               │
│  │   Chunking  │  768 tokens + 512 overlap                    │
│  │ + Compress  │                                               │
│  └─────────────┘                                               │
│       │                                                         │
│       ▼                                                         │
│  ┌─────────────┐                                               │
│  │   Claude    │  Extract: summary, facts, connections,        │
│  │  Sonnet     │  threads, emotional valence, confidence      │
│  │ Synthesis   │                                               │
│  └─────────────┘                                               │
│       │                                                         │
│       ▼                                                         │
│  ┌─────────────┐                                               │
│  │   Expert    │  Score against 7 room experts               │
│  │   Router    │  Route to top 1-3 rooms                       │
│  └─────────────┘                                               │
│       │                                                         │
│       ▼                                                         │
│  ┌─────────────┐                                               │
│  │  ChromaDB   │  Write to room collections                    │
│  │   Writer    │  nomic-embed-text embeddings                  │
│  └─────────────┘                                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                       ROOM EXPERTS                              │
├─────────────┬──────────────────────────────────────────────────┤
│ Consciousness│ Philosophy, quantum mechanics, hard problem,     │
│             │ Orch-OR, psychedelics                            │
├─────────────┼──────────────────────────────────────────────────┤
│ Technical   │ Code, architecture, tools, debugging, stack      │
├─────────────┼──────────────────────────────────────────────────┤
│ Identity    │ Emotional threads, grief, personal history,      │
│             │ self-concept                                     │
├─────────────┼──────────────────────────────────────────────────┤
│ Creative    │ Art, Murica! universe, photography, skydiving     │
├─────────────┼──────────────────────────────────────────────────┤
│ Memory      │ Lumen itself, Dream Cycle, memory architecture   │
├─────────────┼──────────────────────────────────────────────────┤
│ Projects    │ Active builds, job search, consulting work       │
├─────────────┼──────────────────────────────────────────────────┤
│ Relationships│ Teagan, Mea, Debbie, Dexter, Sonny, others     │
└─────────────┴──────────────────────────────────────────────────┘
```

## Design Philosophy

Memory as reconstruction, not storage. Capture what landed, not everything said. Expert retrieval over flat search. Local, low-cost, owned.

## Installation

```bash
cd /home/mike/lumen
pip install -r requirements.txt --break-system-packages

# Set your Anthropic API key in .env
echo "ANTHROPIC_API_KEY=sk-..." >> .env
```

## Usage

### CLI Commands

```bash
# Query memory
lumen query "what did we discuss about Lumen?"

# Query specific room
lumen query "memory architecture" --room memory

# Ingest a transcript file
lumen ingest /path/to/transcript.txt

# Check status
lumen status

# Test synthesis
lumen test-synthesis "Today we designed Lumen..."
```

### MCP Server

Register with Claude Code:

```bash
claude mcp add lumen python /home/mike/lumen/lumen/mcp_server.py
```

Tools exposed:
- `lumen_query(text, room)` - Search memories
- `lumen_ingest(text, session_id)` - Ingest text
- `lumen_status()` - Get system stats

### Python API

```python
from lumen.cli import LumenPipeline

pipeline = LumenPipeline()
result = pipeline.ingest("Session transcript text...")
print(result["synthesized"]["summary"])
```

## Nightly Dream Cycle Integration

Add to crontab:

```bash
0 23 * * * /home/mike/.venv/bin/python /home/mike/lumen/lumen/cli.py dream >> /home/mike/lumen/logs/lumen_nightly.log 2>&1
```

## Components

| Component | File | Purpose |
|-----------|------|---------|
| Session Logger | `session_logger.py` | Captures raw transcript input |
| Token Counter | `token_counter.py` | Counts tokens, decides compression strategy |
| Compressor | `compressor.py` | Qwen compression to 30-40% |
| Synthesizer | `synthesizer.py` | Claude Sonnet structured extraction |
| Router | `router.py` | Routes to appropriate room experts |
| Chroma Writer | `chroma_writer.py` | Writes to ChromaDB collections |
| CLI | `cli.py` | Command-line interface |
| MCP Server | `mcp_server.py` | FastMCP server for agents |

## Validation

Run the test suite:

```bash
cd /home/mike/lumen
python -m pytest tests/ -v
```

Run integration test:

```bash
python tests/test_pipeline.py
```

Expected test input:
> "Today we designed Lumen, a memory architecture named after hello_world_01. It uses ChromaDB, seven room experts, hippocampal consolidation model, and Dream Cycle as the nightly feed. Mike wants memory as reconstruction, not storage."

Expected output: Routes to Memory (primary), Technical, Projects. Summary captures design philosophy.

## Directory Structure

```
/home/mike/lumen/
├── lumen/
│   ├── __init__.py
│   ├── cli.py
│   ├── session_logger.py
│   ├── token_counter.py
│   ├── compressor.py
│   ├── synthesizer.py
│   ├── router.py
│   ├── chroma_writer.py
│   ├── mcp_server.py
│   └── rooms/
│       ├── __init__.py
│       ├── base_room.py
│       ├── consciousness.py
│       ├── technical.py
│       ├── identity.py
│       ├── creative.py
│       ├── memory.py
│       ├── projects.py
│       └── relationships.py
├── logs/
├── tests/
│   └── test_pipeline.py
├── requirements.txt
├── .env
└── README.md
```

## Infrastructure

- ChromaDB: `/home/mike/.claude_memory`
- Ollama: `http://localhost:11434`
- Models: Qwen2.5:7b (compression), nomic-embed-text (embeddings)
- Claude: Sonnet 4 (synthesis)
