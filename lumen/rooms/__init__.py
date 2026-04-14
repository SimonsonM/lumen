"""Room expert modules for Lumen memory architecture."""

from lumen.rooms.base_room import BaseRoom
from lumen.rooms.consciousness import ConsciousnessRoom
from lumen.rooms.technical import TechnicalRoom
from lumen.rooms.identity import IdentityRoom
from lumen.rooms.creative import CreativeRoom
from lumen.rooms.memory import MemoryRoom
from lumen.rooms.projects import ProjectsRoom
from lumen.rooms.relationships import RelationshipsRoom

__all__ = [
    "BaseRoom",
    "ConsciousnessRoom",
    "TechnicalRoom",
    "IdentityRoom",
    "CreativeRoom",
    "MemoryRoom",
    "ProjectsRoom",
    "RelationshipsRoom",
]

ALL_ROOMS = [
    ConsciousnessRoom(),
    TechnicalRoom(),
    IdentityRoom(),
    CreativeRoom(),
    MemoryRoom(),
    ProjectsRoom(),
    RelationshipsRoom(),
]
