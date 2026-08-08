"""
===============================================================================
LIA EmployX — CV Section Splitter
===============================================================================

Responsabilidad única: dividir el texto plano de un CV en secciones
nombradas. No interpreta información, no llama servicios externos, no
crea modelos de dominio.

Autor : LIA EmployX Team
Python: 3.12+
===============================================================================
"""

from __future__ import annotations

import re
from typing import Final, Any, Literal
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Tipos
# ---------------------------------------------------------------------------

SectionKey = str

DetectionMethod = Literal["header", "structural", "none"]

@dataclass(slots=True)
class SectionResult:
    """
    Contiene el texto extraído y metadatos sobre cómo fue detectada la sección.
    """
    text: str
    confidence: float
    detection: DetectionMethod

SectionMap = dict[SectionKey, SectionResult]

# Estructura de retorno garantizada.
_EMPTY_SECTIONS: Final[dict[SectionKey, str]] = {
    "personal_info": "",
    "summary": "",
    "experience": "",
    "education": "",
    "skills": "",
    "languages": "",
    "certifications": "",
    "projects": "",
}

# ---------------------------------------------------------------------------
# Encabezados reconocidos por sección
# ---------------------------------------------------------------------------

_SECTION_HEADERS: Final[dict[SectionKey, list[str]]] = {
    "summary": [
        "perfil profesional",
        "perfil",
        "professional profile",
        "professional summary",
        "summary",
        "about me",
        "about",
        "objetivo profesional",
        "objetivo",
        "career objective",
        "objective",
        "resumen profesional",
        "resumen",
    ],
    "experience": [
        "experiencia laboral",
        "experiencia profesional",
        "experiencia",
        "historial laboral",
        "trayectoria profesional",
        "trayectoria",
        "professional experience",
        "work experience",
        "employment history",
        "employment",
        "career history",
        "featured experience",
    ],
    "education": [
        "formacion academica",
        "formacion",
        "educacion",
        "estudios",
        "academic background",
        "academic education",
        "academic",
        "education",
    ],
    "skills": [
        "habilidades tecnicas",
        "habilidades clave",
        "habilidades",
        "competencias clave",
        "competencias",
        "aptitudes",
        "valor diferencial",
        "technical skills",
        "core competencies",
        "core skills",
        "competencies",
        "strengths",
        "skills",
        "core technologies",
        "technologies",
    ],
    "languages": [
        "idiomas",
        "languages",
        "language",
    ],
    "certifications": [
        "certificaciones",
        "certificados",
        "certifications",
        "certification",
        "licenses",
        "licencias",
    ],
    "projects": [
        "proyectos personales",
        "proyectos",
        "projects",
        "project",
        "open source",
        "portafolio",
        "portfolio",
    ],
}

# Patrón decorativo: cualquier carácter que NO sea letra, dígito o guion bajo.
_DECORATIVE_PATTERN: Final[str] = r"\W"


class CVSectionSplitter:
    """Divide el texto plano de un CV en secciones nombradas."""

    def __init__(self) -> None:
        self._patterns: dict[SectionKey, list[re.Pattern[str]]] = (
            self._compile_patterns()
        )

    def split(self, text: str) -> SectionMap:
        """Divide el texto del CV en secciones."""
        normalized = self._normalize(text)
        blocks = self._split_blocks(normalized)
        return self._build_sections(blocks)

    def process(self, text: str) -> SectionMap:
        sections = self.split(text)
        self.print_summary(sections)
        return sections

    def print_summary(self, sections: SectionMap) -> None:
        separator = "=" * 70
        print()
        print(separator)
        print("CV Sections")
        print(separator)
        print()
        for key in _EMPTY_SECTIONS:
            value = sections.get(key, "")
            print(f"  {key:<20} {len(value):>6} caracteres")
        print()

    def debug(self, text: str) -> SectionMap:
        separator = "=" * 70
        print()
        print(separator)
        print("DEBUG — CV Section Splitter")
        print(separator)

        normalized = self._normalize(text)
        blocks = self._split_blocks(normalized)
        detected = self._detect_boundaries(blocks)
        sections = self._build_sections(blocks)

        print()
        print(f"  Bloques totales : {len(blocks)}")
        print()

        print("  Límites detectados:")
        print()
        if detected:
            for item in detected:
                header_text: str = item["text"].split("\n")[0]
                safe_text = header_text.encode(
                    "ascii", errors="replace"
                ).decode("ascii")
                print(
                    f"    bloque {item['index']:>4}  "
                    f"[{item['section']:<16}]  "
                    f"conf:{item['confidence']:.2f} ({item['detection']})  "
                    f"{safe_text[:40]}"
                )
        else:
            print("    (ninguno)")

        print()
        print("  Contenido por sección:")
        print()
        for key in _EMPTY_SECTIONS:
            value = sections.get(key, "")
            print(f"  {'-' * 66}")
            if hasattr(value, 'confidence'):
                print(f"  {key.upper()} [Conf: {value.confidence:.2f} | Method: {value.detection}]")
            else:
                print(f"  {key.upper()}")
            print(f"  {'-' * 66}")
            if value:
                for line in value.splitlines()[:5]:
                    print(f"    {line}")
                if len(value.splitlines()) > 5:
                    print("    ...")
            else:
                print("    (vacío)")
            print()

        return sections

    def _normalize(self, text: str) -> str:
        if not text:
            return ""
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = text.replace("\t", " ")
        text = re.sub(r" {2,}", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def _split_blocks(self, text: str) -> list[str]:
        """Divide el texto normalizado en bloques (párrafos)."""
        return [block.strip() for block in text.split("\n\n") if block.strip()]

    def _compile_patterns(self) -> dict[SectionKey, list[re.Pattern[str]]]:
        compiled: dict[SectionKey, list[re.Pattern[str]]] = {}
        deco = f"(?:{_DECORATIVE_PATTERN})*"

        for section, headers in _SECTION_HEADERS.items():
            patterns: list[re.Pattern[str]] = []
            for header in headers:
                escaped = r"\s+".join(re.escape(word) for word in header.split())
                pattern = re.compile(
                    rf"^{deco}{escaped}(?:\b|{deco})",
                    re.IGNORECASE,
                )
                patterns.append(pattern)
            compiled[section] = patterns

        return compiled

    def _normalize_for_matching(self, line: str) -> str:
        replacements = str.maketrans(
            "áéíóúÁÉÍÓÚàèìòùÀÈÌÒÙäëïöüÄËÏÖÜâêîôûÂÊÎÔÛ",
            "aeiouAEIOUaeiouAEIOUaeiouAEIOUaeiouAEIOU",
        )
        return line.translate(replacements)

    def _match_header(self, block: str) -> SectionKey | None:
        first_line = block.split("\n")[0]
        normalized_line = self._normalize_for_matching(first_line)
        best_section: SectionKey | None = None
        best_length: int = 0

        for section, patterns in self._patterns.items():
            for i, pattern in enumerate(patterns):
                if pattern.match(normalized_line):
                    header_length = len(_SECTION_HEADERS[section][i])
                    if header_length > best_length:
                        best_length = header_length
                        best_section = section

        return best_section

    def _detect_structural_boundary(self, block: str) -> SectionKey | None:
        """Heurística para detectar límites de secciones por estructura del bloque."""
        # Detectar rangos de fechas o años sueltos (muy comunes en educación)
        date_pattern = r"\b(?:19|20)\d{2}\b|[Pp]resente|[Aa]ctualidad"
        role_pattern = r"\b(desarrollador|developer|ingeniero|engineer|manager|líder|leader|director|consultor|consultant|analista|analyst|jefe|coordinador|arquitecto|architect)\b"
        edu_pattern = r"\b(universidad|university|licenciatura|bachelor|master|maestría|phd|instituto|degree|ingeniería|tecnológico)\b"
        
        has_date = bool(re.search(date_pattern, block, re.IGNORECASE))
        if has_date:
            if re.search(role_pattern, block, re.IGNORECASE):
                # Evitar falsos positivos con certificaciones que incluyen el rol (ej. AWS Developer)
                if not re.search(r"\b(certified|certificación|certificate|curso|course)\b", block, re.IGNORECASE):
                    return "experience"
            if re.search(edu_pattern, block, re.IGNORECASE):
                return "education"
        return None

    def _detect_boundaries(self, blocks: list[str]) -> list[dict[str, Any]]:
        found = []
        for index, block in enumerate(blocks):
            # 1. Intentar match explícito de encabezado
            section = self._match_header(block)
            if section is not None:
                found.append({
                    "index": index,
                    "section": section,
                    "confidence": 0.95,
                    "detection": "header",
                    "text": block,
                })
                continue
                
            # 2. Intentar match estructural si no hubo header explícito
            section = self._detect_structural_boundary(block)
            if section is not None:
                found.append({
                    "index": index,
                    "section": section,
                    "confidence": 0.80,
                    "detection": "structural",
                    "text": block,
                })
        return found

    def _build_sections(self, blocks: list[str]) -> SectionMap:
        accumulator: dict[SectionKey, list[str]] = {key: [] for key in _EMPTY_SECTIONS}
        confidences: dict[SectionKey, float] = {}
        detections: dict[SectionKey, str] = {}

        detected = self._detect_boundaries(blocks)

        if not detected:
            accumulator["personal_info"] = blocks
            return self._join_sections(accumulator, confidences, detections)

        filtered_detected = []
        last_section = None
        for d in detected:
            if d["section"] != last_section:
                filtered_detected.append(d)
                last_section = d["section"]

        first_index: int = filtered_detected[0]["index"]
        accumulator["personal_info"] = blocks[:first_index]

        for i, boundary in enumerate(filtered_detected):
            section: SectionKey = boundary["section"]
            
            if section not in confidences or boundary["confidence"] > confidences[section]:
                confidences[section] = boundary["confidence"]
                detections[section] = boundary["detection"]

            start: int = boundary["index"]
            end: int = (
                filtered_detected[i + 1]["index"]
                if i + 1 < len(filtered_detected)
                else len(blocks)
            )
            accumulator[section].extend(blocks[start:end])

        return self._join_sections(accumulator, confidences, detections)

    def _join_sections(
        self,
        accumulator: dict[SectionKey, list[str]],
        confidences: dict[SectionKey, float],
        detections: dict[SectionKey, str],
    ) -> SectionMap:
        result = {}
        for key in _EMPTY_SECTIONS:
            text = "\n\n".join(accumulator.get(key, [])).strip()
            conf = confidences.get(key, 0.0)
            det = detections.get(key, "none")
            result[key] = SectionResult(text=text, confidence=conf, detection=det) # type: ignore
        return result


if __name__ == "__main__":

    _SAMPLE_CV = """
Miguel Tovar
miguel@example.com | +52 55 1234 5678
Ciudad de México, México

► Perfil Profesional

Ingeniero de Software con más de 8 años de experiencia en desarrollo
de aplicaciones móviles y backend.

Empresa Alpha — Senior Flutter Developer (2021 – presente)
- Desarrollo de apps multiplataforma con Flutter y Dart.

Empresa Beta — Python Backend Developer (2018 – 2021)
- APIs REST con FastAPI y Django.

Universidad Nacional Autónoma
Licenciatura en Ingeniería en Sistemas Computacionales — 2017

◆ HABILIDADES CLAVE

Flutter · Dart · Python · FastAPI · Docker · AWS · PostgreSQL

IDIOMAS

Español — Nativo
Inglés — C1 (TOEFL 110)

Certificaciones (2023)

AWS Certified Developer – Associate (2023)
Google Cloud Professional Data Engineer (2022)

Proyectos Personales

LIA EmployX — Plataforma de reclutamiento con IA
OpenResume — Generador de CVs de código abierto
"""

    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    _splitter = CVSectionSplitter()
    _splitter.debug(_SAMPLE_CV)
