"""Session logger for Lumen - captures raw transcript input."""

import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional


class SessionLogger:
    """Captures raw transcript input from various sources."""

    RAW_OUTPUT = Path("/tmp/lumen_session_raw.txt")

    def __init__(self):
        self.session_id = str(uuid.uuid4())
        self.timestamp = datetime.utcnow().isoformat()
        self.content = ""

    def from_stdin(self) -> str:
        """Read transcript from stdin pipe."""
        if not sys.stdin.isatty():
            self.content = sys.stdin.read()
        else:
            self.content = ""
        return self.content

    def from_text(self, text: str) -> str:
        """Load transcript from direct text argument."""
        self.content = text
        return self.content

    def from_file(self, filepath: str) -> str:
        """Load transcript from file path."""
        path = Path(filepath)
        if path.exists():
            self.content = path.read_text()
        else:
            raise FileNotFoundError(f"Transcript file not found: {filepath}")
        return self.content

    def save_raw(self) -> Path:
        """Save raw transcript to temp file."""
        output = Path(self.RAW_OUTPUT)
        output.write_text(self.content)
        return output

    def get_metadata(self) -> dict:
        """Return session metadata."""
        return {
            "session_id": self.session_id,
            "timestamp": self.timestamp,
            "token_count": len(self.content.split()),
        }
