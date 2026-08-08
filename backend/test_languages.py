import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.modules.cv.builders.languages_builder import LanguagesBuilder

text = """
🌎 LANGUAGES
English - Native
Spanish: B2
French
Programming Languages (C++)
"""
builder = LanguagesBuilder()
result = builder.build(text)
for l in result.data:
    print(l.model_dump())
