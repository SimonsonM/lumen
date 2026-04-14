"""Technical room - code, architecture, tools, debugging."""

from lumen.rooms.base_room import BaseRoom


class TechnicalRoom(BaseRoom):
    """Expert on software development, architecture, and technical decisions."""

    @property
    def name(self) -> str:
        return "technical"

    @property
    def collection_name(self) -> str:
        return "lumen_technical"

    @property
    def domain(self) -> str:
        return "code, software architecture, tools, builds, debugging, stack decisions, programming"

    @property
    def retrieval_prompt(self) -> str:
        return (
            "You are answering technical questions about software development. "
            "Focus on: code implementations, architecture decisions, tool usage, "
            "debugging solutions, stack choices, and technical best practices."
        )

    @property
    def ingestion_prompt(self) -> str:
        return (
            "Extract technical content: code solutions, architecture decisions, "
            "tool configurations, debugging approaches, and stack decisions. "
            "Preserve technical details and implementation specifics."
        )

    def _calculate_domain_score(self, text: str) -> float:
        score = 0.0
        tech_keywords = [
            "python", "javascript", "typescript", "rust", "go", "java", "c++",
            "api", "database", "server", "client", "frontend", "backend",
            "docker", "kubernetes", "git", "cli", "framework", "library",
            "debug", "error", "bug", "fix", "implement", "architecture",
            "config", "deploy", "build", "test", "optimize", "performance",
            "memory", "storage", "query", "endpoint", "route", "middleware",
            "class", "function", "module", "package", "dependency",
            "ollama", "chroma", "anthropic", "mcp", "llm", "model",
            "json", "html", "css", "react", "vue", "node", "fastapi"
        ]
        for kw in tech_keywords:
            if kw in text:
                score += 0.12
        return min(score, 1.0)
