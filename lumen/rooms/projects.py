"""Projects room - active builds, job search, consulting work, MikeAndClaudesGreatAdventure."""

from lumen.rooms.base_room import BaseRoom


class ProjectsRoom(BaseRoom):
    """Expert on active projects, work, and creative builds."""

    @property
    def name(self) -> str:
        return "projects"

    @property
    def collection_name(self) -> str:
        return "lumen_projects"

    @property
    def domain(self) -> str:
        return "active builds, job search, consulting work, MikeAndClaudesGreatAdventure, projects"

    @property
    def retrieval_prompt(self) -> str:
        return (
            "You are answering questions about active projects and work. "
            "Focus on: project status, consulting work, job search progress, "
            "MikeAndClaudesGreatAdventure, and active builds."
        )

    @property
    def ingestion_prompt(self) -> str:
        return (
            "Extract project content: active builds, work progress, job search, "
            "consulting engagements, and creative projects. "
            "Preserve project status and next steps."
        )

    def _calculate_domain_score(self, text: str) -> float:
        score = 0.0
        project_keywords = [
            "project", "build", "working on", "progress", "status",
            "consulting", "client", "contract", "freelance", "job",
            "interview", "resume", "cv", "searching for", "opportunity",
            "mikeandclaudesgreatadventure", "adventure", "quest",
            "complete", "done", "in progress", "started", "launching",
            "deadline", "milestone", "sprint", "feature", "ship",
            "deploy", "release", "version", "iterate"
        ]
        for kw in project_keywords:
            if kw in text:
                score += 0.13
        return min(score, 1.0)
