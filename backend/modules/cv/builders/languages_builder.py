import re
from typing import List
from backend.modules.cv.builders.base_builder import BaseBuilder, BuildResult
from backend.modules.cv.models.cv_language import CVLanguage

class LanguagesBuilder(BaseBuilder[List[CVLanguage]]):
    _HEADERS = {"languages", "idiomas", "languageskills", "habilidadeslingüísticas"}

    def build(self, text: str) -> BuildResult[List[CVLanguage]]:
        warnings = []
        if not text.strip():
            warnings.append("Sección de idiomas vacía.")
            return BuildResult(data=[], confidence=0.0, warnings=warnings)

        def is_header(s: str) -> bool:
            clean = re.sub(r'[^a-z]', '', s.lower())
            return clean in self._HEADERS

        # Pre-process: split merged language entries on the same line.
        # e.g. "Spanish: NativeEnglish: B2" -> "Spanish: Native\nEnglish: B2"
        # Use a lookahead so the capital letter is NOT consumed — it starts the next token.
        level_words = r'(?:Native|Fluent|Basic|Elementary|Intermediate|Advanced|Professional|Conversational|[A-C][12](?:[- ]\w+)?)'
        text = re.sub(r'(' + level_words + r')(?=[A-Z][a-z])', r'\1\n', text)

        lines = [line.strip() for line in text.split('\n') if line.strip()]
        languages_list = []
        seen = set()

        for line in lines:
            # Clean bullets and emojis at start
            line = re.sub(r'^[^a-zA-Z0-9]+', '', line).strip()
            if not line:
                continue

            # Check if line is just a section header
            if is_header(line):
                continue

            # Split on first : or – or — to get name and level
            parts = re.split(r'[-–—:]', line, maxsplit=1)
            lang_name = parts[0].strip()
            level = parts[1].strip() if len(parts) > 1 else None

            # Clean up level from extra decoration
            if level:
                level = re.sub(r'^[^a-zA-Z0-9]+', '', level).strip()
                level = re.sub(r'\s+', ' ', level)

            if not lang_name:
                continue

            # Dedup by (name, level) pair
            key = (lang_name.lower(), (level or "").lower())
            if key in seen:
                continue
            seen.add(key)

            languages_list.append(CVLanguage(name=lang_name, level=level or None))

        confidence = 80.0
        return BuildResult(data=languages_list, confidence=confidence, warnings=warnings)
