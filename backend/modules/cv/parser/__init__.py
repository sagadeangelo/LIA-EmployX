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
JSON
        │
        ▼
Validator
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

from .schema_loader import SchemaLoader
from .prompt_builder import PromptBuilder
from .validator import CVValidator
from .json_parser import JSONParser
from .profile_mapper import ProfileMapper

__all__ = [
    "SchemaLoader",
    "PromptBuilder",
    "CVValidator",
    "JSONParser",
    "ProfileMapper",
]