"""
LIA EmployX — CV Section Splitter

Divide el texto plano de un CV en secciones semánticas.

Principios:

- Detecta encabezados reales, no palabras sueltas.
- Soporta encabezados visuales y decorativos.
- Soporta encabezados pegados al contenido:
      EDUCATIONIndustrial and Systems Engineering...
- Evita interpretar palabras como "Engineering", "Technologies"
  o "Portfolio" como secciones por sí mismas.
- Mantiene separadas las secciones principales.
- Deduplica bloques repetidos producidos por múltiples estrategias
  de extracción DOCX.
- No ejecuta OCR.
- No construye modelos de dominio.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Final, Literal


SectionKey = str

DetectionMethod = Literal[
    "header",
    "structural",
    "none",
]


@dataclass(slots=True)
class SectionResult:
    text: str
    confidence: float
    detection: DetectionMethod


SectionMap = dict[SectionKey, SectionResult]


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


# ============================================================================
# MAIN SECTION HEADERS
# ============================================================================
#
# IMPORTANTE:
#
# Estos son encabezados de SECCIÓN PRINCIPAL.
#
# No debemos poner aquí palabras como:
#
#   technologies
#   portfolio
#   frontend
#   backend
#   engineering
#
# porque pueden aparecer normalmente dentro del contenido.
#
# "AI TOOLKIT", "CORE TECHNOLOGIES" y "LIA ECOSYSTEM" sí son válidos
# como subencabezados de SKILLS.
#
# ============================================================================

_SECTION_HEADERS: Final[dict[SectionKey, list[str]]] = {
    "summary": [
        "perfil profesional",
        "professional profile",
        "professional summary",
        "resumen profesional",
        "career objective",
        "objetivo profesional",
        "about me",
        "about",
        "summary",
        "resumen",
        "perfil",
        "objetivo",
    ],
    "experience": [
        "experiencia laboral",
        "experiencia profesional",
        "professional experience",
        "work experience",
        "employment history",
        "career history",
        "featured experience",
        "experiencia",
        "empleo",
        "trayectoria profesional",
        "trayectoria",
    ],
    "education": [
        "formacion academica",
        "formacion",
        "educacion",
        "estudios",
        "academic background",
        "academic education",
        "education",
        "academic",
    ],
    "skills": [
        "habilidades tecnicas",
        "habilidades clave",
        "habilidades",
        "competencias clave",
        "competencias",
        "aptitudes",
        "technical skills",
        "core competencies",
        "core skills",
        "competencies",
        "strengths",
        "skills",
        "core technologies",
        "ai toolkit",
        "ai tools",
        "artificial intelligence toolkit",
        "technical toolkit",
        "technology stack",
        "tech stack",
        "lia ecosystem",
        "lia tech ecosystem",
        "ecosistema lia",
        "herramientas de ia",
        "herramientas ia",
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


# ============================================================================
# DECORATIVE PREFIXES
# ============================================================================

_DECORATIVE_PREFIX_RE = re.compile(
    r"^[^A-Za-z0-9ÁÉÍÓÚÜÑáéíóúüñ]+"
)


class CVSectionSplitter:
    """
    Divide un CV en secciones semánticas.

    Estrategia:

    1. Detectar encabezados completos.
    2. Detectar encabezados pegados al contenido únicamente cuando
       aparecen al PRINCIPIO de un bloque.
    3. Aplicar heurística estructural extremadamente conservadora.
    4. Deduplicar contenido repetido generado por distintas estrategias
       de extracción DOCX.
    """

    def __init__(self) -> None:
        self._patterns = self._compile_patterns()
        self._embedded_headers = self._compile_embedded_headers()

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    def split(self, text: str) -> SectionMap:
        normalized = self._normalize(text)

        if not normalized:
            return self._empty_result()

        blocks = self._split_blocks(normalized)

        blocks = self._expand_embedded_headers(blocks)

        return self._build_sections(blocks)

    def process(self, text: str) -> SectionMap:
        sections = self.split(text)
        self.print_summary(sections)
        return sections

    def print_summary(
        self,
        sections: SectionMap,
    ) -> None:
        separator = "=" * 70

        print()
        print(separator)
        print("CV Sections")
        print(separator)
        print()

        for key in _EMPTY_SECTIONS:
            result = sections.get(
                key,
                SectionResult("", 0.0, "none"),
            )

            print(
                f"  {key:<20}"
                f"{len(result.text):>6} caracteres "
                f"[{result.detection}]"
            )

        print()

    def debug(
        self,
        text: str,
    ) -> SectionMap:
        separator = "=" * 70

        print()
        print(separator)
        print("DEBUG — CV Section Splitter")
        print(separator)

        normalized = self._normalize(text)

        blocks = self._split_blocks(normalized)

        blocks = self._expand_embedded_headers(blocks)

        detected = self._detect_boundaries(blocks)

        sections = self._build_sections(blocks)

        print()
        print(
            f"  Bloques después de expansión: "
            f"{len(blocks)}"
        )

        print()
        print("  Límites detectados:")
        print()

        if not detected:
            print("    (ninguno)")

        for item in detected:
            header = item["text"].split(
                "\n",
                1,
            )[0]

            safe_header = (
                header.encode(
                    "ascii",
                    errors="replace",
                )
                .decode("ascii")
            )

            print(
                f"    bloque {item['index']:>4} "
                f"[{item['section']:<16}] "
                f"conf:{item['confidence']:.2f} "
                f"({item['detection']}) "
                f"{safe_header[:60]}"
            )

        print()
        print("  Contenido por sección:")
        print()

        for key in _EMPTY_SECTIONS:
            result = sections[key]

            print("-" * 70)

            print(
                f"{key.upper()} "
                f"[{result.confidence:.2f} | "
                f"{result.detection}]"
            )

            print("-" * 70)

            if not result.text:
                print("(vacío)")
                print()
                continue

            lines = result.text.splitlines()

            for line in lines[:8]:
                print(f"  {line}")

            if len(lines) > 8:
                print("  ...")

            print()

        return sections

    # =========================================================================
    # NORMALIZATION
    # =========================================================================

    def _normalize(
        self,
        text: str,
    ) -> str:
        if not text:
            return ""

        text = text.replace(
            "\r\n",
            "\n",
        )

        text = text.replace(
            "\r",
            "\n",
        )

        text = text.replace(
            "\t",
            " ",
        )

        text = re.sub(
            r"[ ]{2,}",
            " ",
            text,
        )

        text = re.sub(
            r"\n{3,}",
            "\n\n",
            text,
        )

        return text.strip()

    # =========================================================================
    # BLOCKS
    # =========================================================================

    def _split_blocks(
        self,
        text: str,
    ) -> list[str]:
        return [
            block.strip()
            for block in text.split("\n\n")
            if block.strip()
        ]

    # =========================================================================
    # ACCENT NORMALIZATION
    # =========================================================================

    @staticmethod
    def _normalize_for_matching(
        text: str,
    ) -> str:
        replacements = str.maketrans(
            "áéíóúüñÁÉÍÓÚÜÑàèìòùÀÈÌÒÙäëïöüÄËÏÖÜ",
            "aeiouunAEIOUUNaeiouAEIOUaeiouAEIOU",
        )

        return text.translate(replacements)

    # =========================================================================
    # SEMANTIC KEY
    # =========================================================================

    @staticmethod
    def _semantic_key(
        text: str,
    ) -> str:
        return "".join(
            character.casefold()
            for character in text
            if character.isalnum()
        )

    # =========================================================================
    # PATTERN COMPILATION
    # =========================================================================

    def _compile_patterns(
        self,
    ) -> dict[
        SectionKey,
        list[re.Pattern[str]],
    ]:
        compiled: dict[
            SectionKey,
            list[re.Pattern[str]],
        ] = {}

        for section, headers in _SECTION_HEADERS.items():
            patterns: list[re.Pattern[str]] = []

            for header in headers:
                normalized_header = (
                    self._normalize_for_matching(
                        header
                    )
                )

                escaped = r"\s+".join(
                    re.escape(word)
                    for word in normalized_header.split()
                )

                pattern = re.compile(
                    rf"^[^A-Za-z0-9]*"
                    rf"{escaped}"
                    rf"[^A-Za-z0-9]*$",
                    re.IGNORECASE,
                )

                patterns.append(pattern)

            compiled[section] = patterns

        return compiled

    # =========================================================================
    # EMBEDDED HEADER COMPILATION
    # =========================================================================

    def _compile_embedded_headers(
        self,
    ) -> list[
        tuple[
            str,
            SectionKey,
            re.Pattern[str],
        ]
    ]:
        """
        Prepara encabezados para detectar casos como:

            EDUCATIONIndustrial and Systems Engineering...

        IMPORTANTE:

        La detección posterior solo acepta estos encabezados cuando
        aparecen al PRINCIPIO del bloque.

        Esto evita:

            Prompt Engineering
                  ^

        convirtiéndose accidentalmente en EDUCATION.
        """

        result: list[
            tuple[
                str,
                SectionKey,
                re.Pattern[str],
            ]
        ] = []

        for section, headers in _SECTION_HEADERS.items():
            for header in headers:
                normalized_header = (
                    self._normalize_for_matching(
                        header
                    )
                )

                escaped = re.escape(
                    normalized_header
                )

                pattern = re.compile(
                    rf"^{escaped}",
                    re.IGNORECASE,
                )

                result.append(
                    (
                        header,
                        section,
                        pattern,
                    )
                )

        result.sort(
            key=lambda item: len(item[0]),
            reverse=True,
        )

        return result

    # =========================================================================
    # EMBEDDED HEADERS
    # =========================================================================

    def _expand_embedded_headers(
        self,
        blocks: list[str],
    ) -> list[str]:
        """
        Expande únicamente encabezados pegados al PRINCIPIO de un bloque.

        Ejemplo válido:

            🎓 EDUCATIONIndustrial and Systems Engineering...

        se convierte en:

            EDUCATION
            Industrial and Systems Engineering...

        NO se permite buscar encabezados arbitrariamente dentro del bloque.

        Por tanto:

            Prompt Engineering

        NO puede convertirse en:

            Prompt
            Engineering

        y:

            LIA ecosystem

        no se interpreta como encabezado si forma parte de contenido
        de una sección ya existente.
        """

        expanded: list[str] = []

        for block in blocks:
            pieces = self._split_leading_embedded_header(
                block
            )

            expanded.extend(pieces)

        return [
            piece.strip()
            for piece in expanded
            if piece.strip()
        ]

    def _split_leading_embedded_header(
        self,
        block: str,
    ) -> list[str]:
        """
        Detecta un único encabezado pegado al comienzo del bloque.

        Ejemplos:

            EDUCATIONIndustrial...

            🎓 EDUCATIONIndustrial...

            PROFESSIONAL SUMMARYFull Stack...

        """

        working = block.strip()

        if not working:
            return []

        # -------------------------------------------------------------
        # Eliminar decoración inicial solamente para detectar el header.
        # -------------------------------------------------------------

        match_prefix = _DECORATIVE_PREFIX_RE.match(
            working
        )

        content_start = (
            match_prefix.end()
            if match_prefix
            else 0
        )

        candidate = working[
            content_start:
        ]

        normalized_candidate = (
            self._normalize_for_matching(
                candidate
            )
        )

        # -------------------------------------------------------------
        # Buscar SOLO al principio.
        # -------------------------------------------------------------

        for (
            header,
            section,
            pattern,
        ) in self._embedded_headers:

            match = pattern.match(
                normalized_candidate
            )

            if not match:
                continue

            header_length = len(
                header
            )

            # ---------------------------------------------------------
            # Necesitamos que exista contenido después del header.
            # Si el bloque es simplemente "EDUCATION", el match normal
            # del encabezado completo se encargará.
            # ---------------------------------------------------------

            if len(candidate) <= header_length:
                continue

            actual_header = candidate[
                :header_length
            ].strip()

            remaining = candidate[
                header_length:
            ].strip()

            if not remaining:
                continue

            # ---------------------------------------------------------
            # Construir dos bloques:
            #
            #   HEADER
            #   CONTENT
            # ---------------------------------------------------------

            return [
                actual_header,
                remaining,
            ]

        return [working]

    # =========================================================================
    # HEADER MATCHING
    # =========================================================================

    def _match_header(
        self,
        block: str,
    ) -> SectionKey | None:
        first_line = block.split(
            "\n",
            1,
        )[0].strip()

        normalized_line = (
            self._normalize_for_matching(
                first_line
            )
        )

        best_section: SectionKey | None = None
        best_length = 0

        for section, patterns in self._patterns.items():
            for index, pattern in enumerate(patterns):

                if not pattern.fullmatch(
                    normalized_line
                ):
                    continue

                header_length = len(
                    _SECTION_HEADERS[
                        section
                    ][index]
                )

                if header_length > best_length:
                    best_length = header_length
                    best_section = section

        return best_section

    # =========================================================================
    # STRUCTURAL DETECTION
    # =========================================================================

    def _detect_structural_boundary(
        self,
        block: str,
    ) -> SectionKey | None:
        """
        Detección estructural conservadora.

        Solamente reconoce EXPERIENCE cuando existen simultáneamente:

        - un rol profesional;
        - una fecha/rango temporal.

        NO intenta inferir EDUCATION por palabras como:

            engineering
            university
            degree

        porque esas palabras aparecen frecuentemente dentro de títulos,
        cursos, certificados y descripciones.
        """

        normalized = (
            self._normalize_for_matching(
                block
            )
        )

        role_pattern = re.compile(
            r"\b("
            r"developer|"
            r"desarrollador|"
            r"engineer|"
            r"ingeniero|"
            r"manager|"
            r"gerente|"
            r"consultant|"
            r"consultor|"
            r"analyst|"
            r"analista|"
            r"architect|"
            r"arquitecto|"
            r"director|"
            r"coordinator|"
            r"coordinador|"
            r"designer|"
            r"diseñador|"
            r"specialist|"
            r"especialista|"
            r"lead|"
            r"lider|"
            r"founder"
            r")\b",
            re.IGNORECASE,
        )

        date_pattern = re.compile(
            r"\b(?:19|20)\d{2}\b"
            r"|"
            r"\bpresent\b"
            r"|"
            r"\bactualidad\b",
            re.IGNORECASE,
        )

        if (
            role_pattern.search(normalized)
            and date_pattern.search(normalized)
        ):
            return "experience"

        return None

    # =========================================================================
    # BOUNDARIES
    # =========================================================================

    def _detect_boundaries(
        self,
        blocks: list[str],
    ) -> list[dict[str, Any]]:
        found: list[
            dict[str, Any]
        ] = []

        for index, block in enumerate(blocks):

            section = self._match_header(
                block
            )

            if section is not None:
                found.append(
                    {
                        "index": index,
                        "section": section,
                        "confidence": 0.98,
                        "detection": "header",
                        "text": block,
                    }
                )

                continue

            structural = (
                self._detect_structural_boundary(
                    block
                )
            )

            if structural is not None:
                found.append(
                    {
                        "index": index,
                        "section": structural,
                        "confidence": 0.75,
                        "detection": "structural",
                        "text": block,
                    }
                )

        return found

    # =========================================================================
    # BUILD
    # =========================================================================

    def _build_sections(
        self,
        blocks: list[str],
    ) -> SectionMap:

        accumulator: dict[
            SectionKey,
            list[str],
        ] = {
            key: []
            for key in _EMPTY_SECTIONS
        }

        confidences: dict[
            SectionKey,
            float,
        ] = {}

        detections: dict[
            SectionKey,
            DetectionMethod,
        ] = {}

        detected = self._detect_boundaries(
            blocks
        )

        # ---------------------------------------------------------------------
        # Si no encontramos ningún encabezado:
        # ---------------------------------------------------------------------

        if not detected:
            accumulator[
                "personal_info"
            ] = blocks

            return self._join_sections(
                accumulator,
                confidences,
                detections,
            )

        # ---------------------------------------------------------------------
        # Personal info = contenido antes del primer encabezado.
        # ---------------------------------------------------------------------

        first_index = detected[
            0
        ]["index"]

        accumulator[
            "personal_info"
        ] = blocks[
            :first_index
        ]

        # ---------------------------------------------------------------------
        # Procesar cada límite.
        # ---------------------------------------------------------------------

        for index, boundary in enumerate(
            detected
        ):
            section = boundary[
                "section"
            ]

            start = boundary[
                "index"
            ]

            if index + 1 < len(
                detected
            ):
                end = detected[
                    index + 1
                ]["index"]
            else:
                end = len(blocks)

            content = blocks[
                start + 1:end
            ]

            accumulator[
                section
            ].extend(
                content
            )

            confidence = float(
                boundary[
                    "confidence"
                ]
            )

            if confidence >= confidences.get(
                section,
                0.0,
            ):
                confidences[
                    section
                ] = confidence

                detections[
                    section
                ] = boundary[
                    "detection"
                ]

        # ---------------------------------------------------------------------
        # Deduplicación final.
        # ---------------------------------------------------------------------

        for section in accumulator:
            accumulator[
                section
            ] = self._deduplicate_section_blocks(
                accumulator[section]
            )

        return self._join_sections(
            accumulator,
            confidences,
            detections,
        )

    # =========================================================================
    # SECTION DEDUPLICATION
    # =========================================================================

    def _deduplicate_section_blocks(
        self,
        blocks: list[str],
    ) -> list[str]:

        result: list[str] = []

        seen: set[str] = set()

        for block in blocks:

            key = self._semantic_key(
                block
            )

            if not key:
                continue

            if key in seen:
                continue

            seen.add(key)

            result.append(
                block
            )

        return result

    # =========================================================================
    # RESULT
    # =========================================================================

    def _join_sections(
        self,
        accumulator: dict[
            SectionKey,
            list[str],
        ],
        confidences: dict[
            SectionKey,
            float,
        ],
        detections: dict[
            SectionKey,
            DetectionMethod,
        ],
    ) -> SectionMap:

        result: SectionMap = {}

        for key in _EMPTY_SECTIONS:

            text = "\n\n".join(
                block.strip()
                for block in accumulator.get(
                    key,
                    [],
                )
                if block.strip()
            ).strip()

            result[key] = SectionResult(
                text=text,
                confidence=confidences.get(
                    key,
                    0.0,
                ),
                detection=detections.get(
                    key,
                    "none",
                ),
            )

        return result

    # =========================================================================
    # EMPTY
    # =========================================================================

    @staticmethod
    def _empty_result() -> SectionMap:
        return {
            key: SectionResult(
                text="",
                confidence=0.0,
                detection="none",
            )
            for key in _EMPTY_SECTIONS
        }