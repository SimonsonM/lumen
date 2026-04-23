"""Obsidian vault mirror for Lumen sessions.

After a successful ingestion, writes a single markdown note to an Obsidian
vault summarizing the session: the synthesized content, the rooms touched,
and the emotional valence. One file per session, not one per memory.

This is a projection, not the source of truth. ChromaDB remains canonical.
The vault note exists for human browsability, graph view, and Dataview
queries over memory over time.

Config via environment variables (loaded from .env):
    LUMEN_VAULT_ENABLED        default: false
    LUMEN_VAULT_PATH           default: ~/vault/20-Projects/lumen-sessions
    LUMEN_VAULT_CONCEPT_LINKS  default: true
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


def _env_bool(name: str, default: bool = False) -> bool:
    val = os.getenv(name, "").strip().lower()
    if val in ("1", "true", "yes", "on"):
        return True
    if val in ("0", "false", "no", "off"):
        return False
    return default


def _slug(s: str, maxlen: int = 40) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")
    return slug[:maxlen] or "session"


def _yaml_str(s: str) -> str:
    """Escape a string for safe inclusion as a YAML scalar."""
    if s is None:
        return '""'
    s = str(s).replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ").strip()
    return f'"{s}"'


class VaultMirror:
    """Writes Lumen session notes to an Obsidian vault."""

    def __init__(self):
        self.enabled = _env_bool("LUMEN_VAULT_ENABLED", False)
        self.vault_path = Path(
            os.getenv("LUMEN_VAULT_PATH", "~/vault/20-Projects/lumen-sessions")
        ).expanduser()
        self.concept_links = _env_bool("LUMEN_VAULT_CONCEPT_LINKS", True)

    def write_session(
        self,
        session_id: str,
        timestamp: str,
        synthesized: Dict,
        routes: List,
        token_count: int,
        compressed_count: int,
        doc_ids: List[str],
    ) -> Optional[Path]:
        """Write a single session note. Returns the path, or None if disabled/failed."""
        if not self.enabled:
            return None

        try:
            self.vault_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"[lumen.vault] mkdir failed: {e}")
            return None

        # Filename: YYYY-MM-DDTHHMM-<session-slug>.md
        try:
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except Exception:
            dt = datetime.utcnow()
        stamp = dt.strftime("%Y-%m-%dT%H%M")
        short_id = (session_id or "")[:8]
        filename = f"{stamp}-{short_id}.md"
        dest = self.vault_path / filename

        summary = synthesized.get("summary", "") or ""
        key_facts = synthesized.get("key_facts", []) or []
        connections = synthesized.get("connections", []) or []
        open_threads = synthesized.get("open_threads", []) or []
        valence = synthesized.get("emotional_valence", "neutral")
        confidence = synthesized.get("confidence", 0.5)

        # Route info: [(Room, confidence), ...]
        route_names = []
        for entry in routes:
            try:
                room_name = entry[0].name if hasattr(entry[0], "name") else str(entry[0])
                route_names.append(room_name)
            except Exception:
                continue

        # Derive a title for the note from the summary's first sentence.
        first_line = summary.strip().split("\n")[0].strip()
        if first_line:
            if len(first_line) <= 80:
                title = first_line
            else:
                # Cut on word boundary, not mid-word
                cut = first_line[:80].rsplit(" ", 1)[0]
                title = f"{cut}…" if cut else first_line[:80]
        else:
            title = f"Session {short_id}"

        # Frontmatter
        tag_list = ["lumen-session"] + route_names
        tags_yaml = "[" + ", ".join(tag_list) + "]"
        frontmatter_lines = [
            "---",
            f"type: lumen-session",
            f"session_id: {session_id}",
            f"timestamp: {timestamp}",
            f"rooms: [{', '.join(route_names)}]",
            f"confidence: {confidence}",
            f"emotional_valence: {_yaml_str(valence)}",
            f"token_count: {token_count}",
            f"token_count_compressed: {compressed_count}",
            f"doc_ids: [{', '.join(doc_ids)}]",
            f"tags: {tags_yaml}",
            "---",
            "",
        ]

        body_lines = [f"# {title}", ""]

        if summary:
            body_lines += ["## Summary", "", summary, ""]

        if key_facts:
            body_lines += ["## Key facts", ""]
            body_lines += [f"- {self._maybe_link(f)}" for f in key_facts]
            body_lines += [""]

        if connections:
            body_lines += ["## Connections", ""]
            body_lines += [f"- {self._maybe_link(c)}" for c in connections]
            body_lines += [""]

        if open_threads:
            body_lines += ["## Open threads", ""]
            body_lines += [f"- {t}" for t in open_threads]
            body_lines += [""]

        if route_names:
            body_lines += ["## Routed to rooms", ""]
            for name, conf in [(r[0].name, r[1]) for r in routes if hasattr(r[0], "name")]:
                body_lines += [f"- **{name}** (confidence: {conf:.2f})"]
            body_lines += [""]

        body_lines += [
            "---",
            f"*Session `{short_id}` captured at {timestamp}. "
            f"{token_count} tokens in, {compressed_count} after compression. "
            f"ChromaDB is canonical; this note is a projection.*",
        ]

        try:
            dest.write_text("\n".join(frontmatter_lines + body_lines))
            return dest
        except Exception as e:
            print(f"[lumen.vault] write failed: {e}")
            return None

    def _maybe_link(self, text: str) -> str:
        """If concept linking is on and the text looks like a known concept,
        wrap it as a wikilink. Heuristic: proper-noun-like terms in the text.
        Disabled by default for v1 — kept simple and predictable.
        """
        if not self.concept_links:
            return text
        return text
