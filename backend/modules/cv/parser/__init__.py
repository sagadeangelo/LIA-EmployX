"""
===============================================================
LIA EmployX

Smart CV Parser

Convierte el texto extraído de un CV en un
ProfessionalProfile utilizando IA.

Flujo:

DocumentContent
        │
        ▼
SchemaLoader
        │
        ▼
PromptBuilder
        │
        ▼
LLM Manager
        │
        ▼
Gemma / Qwen
        │
        ▼
JSONParser
        │
        ▼
CVValidator
        │
        ▼
ProfileMapper
        │
        ▼
ProfessionalProfile

Autor:
LIA EmployX Team
===============================================================
"""

from .cv_section_splitter import CVSectionSplitter
from .parser_orchestrator import ParserOrchestrator
from .json_parser import JSONParser
from .validator import CVValidator
from .prompt_builder import PromptBuilder
from .profile_mapper import ProfileMapper
from .schema_loader import SchemaLoader

__all__ = [
    "CVSectionSplitter",
    "ParserOrchestrator",
    "JSONParser",
    "CVValidator",
    "PromptBuilder",
    "ProfileMapper",
    "SchemaLoader",
]