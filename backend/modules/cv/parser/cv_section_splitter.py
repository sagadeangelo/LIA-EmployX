"""
LIA EmployX
CV Section Splitter
============================================================

Divide el texto plano de un CV en secciones semánticas.

Responsabilidades
-----------------
- Detectar encabezados reales.
- Soportar encabezados visuales/decorativos.
- Soportar encabezados pegados al contenido.
- Evitar falsos positivos por palabras sueltas.
- Mantener separadas las secciones principales.
- Deduplicar bloques repetidos.
- Limpiar artefactos pequeños de extracción DOCX.
- Recuperar información personal desplazada.
- Recuperar información personal fragmentada.
- Recuperar cabeceras personales contaminando otras secciones.
- Manejar encabezados duplicados.
- Separar LIA Ecosystem como proyectos.
- Evitar "Technologies" como falso encabezado dentro de Experience.
- No ejecutar OCR.
- No construir modelos de dominio.

La salida de este módulo es deliberadamente simple:

    dict[str, SectionResult]

Los Builders son responsables de transformar posteriormente
cada sección en modelos de dominio.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Final, Literal


# ============================================================================
# TYPES
# ============================================================================

SectionKey = str

DetectionMethod = Literal[
    "header",
    "structural",
    "recovery",
    "none",
]

ContactRegion = tuple[int, int]


@dataclass(slots=True)
class SectionResult:
    """
    Resultado de una sección detectada.
    """

    text: str
    confidence: float
    detection: DetectionMethod


SectionMap = dict[SectionKey, SectionResult]


# ============================================================================
# EMPTY SECTION CONTRACT
# ============================================================================

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

_SECTION_HEADERS: Final[
    dict[SectionKey, list[str]]
] = {
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
        "lia ecosystem",
        "lia tech ecosystem",
        "ecosistema lia",
    ],
}


# ============================================================================
# DECORATIVE PREFIXES
# ============================================================================

_DECORATIVE_PREFIX_RE = re.compile(
    r"^[^A-Za-z0-9À-ÖØ-öø-ÿ]+"
)


# ============================================================================
# CONTACT SIGNALS
# ============================================================================

_EMAIL_RE = re.compile(
    r"\b[A-Z0-9._%+\-]+"
    r"@"
    r"[A-Z0-9.\-]+"
    r"\.[A-Z]{2,}\b",
    re.IGNORECASE,
)


_PHONE_RE = re.compile(
    r"(?<!\d)"
    r"(?:\+\d{1,3}[\s.-]?)?"
    r"(?:\(?\d{2,4}\)?[\s.-]?)?"
    r"\d{3}[\s.-]?"
    r"\d{3,4}"
    r"(?:[\s.-]?\d{2,4})?"
    r"(?!\d)"
)


_LINKEDIN_RE = re.compile(
    r"\blinkedin\b",
    re.IGNORECASE,
)


_GITHUB_RE = re.compile(
    r"\bgithub\b",
    re.IGNORECASE,
)


_CONTACT_MARKERS: Final[tuple[str, ...]] = (
    "linkedin",
    "github",
    "portfolio",
    "email",
    "gmail",
    "hotmail",
    "outlook",
    "phone",
    "mobile",
    "tel",
    "telefono",
    "teléfono",
)


_PROFILE_TITLE_MARKERS: Final[tuple[str, ...]] = (
    "developer",
    "engineer",
    "designer",
    "architect",
    "manager",
    "analyst",
    "consultant",
    "specialist",
    "founder",
    "director",
    "lead",
    "desarrollador",
    "ingeniero",
    "diseñador",
    "arquitecto",
    "gerente",
    "analista",
    "consultor",
    "especialista",
    "fundador",
    "lider",
    "líder",
)


_LOCATION_MARKERS: Final[tuple[str, ...]] = (
    "mexico",
    "méxico",
    "coahuila",
    "piedras negras",
    "monterrey",
    "guadalajara",
    "saltillo",
    "usa",
    "united states",
    "united states of america",
    "texas",
    "utah",
)


_FRAGMENTED_PROFILE_MARKERS: Final[tuple[str, ...]] = (
    "linkedin",
    "github",
    "portfolio",
    "git",
)


# ============================================================================
# CLASS
# ============================================================================


class CVSectionSplitter:
    """
    Divide un CV en secciones semánticas.

    Estrategia:

    1. Normalizar texto.
    2. Dividir en bloques.
    3. Expandir encabezados pegados.
    4. Detectar fronteras semánticas.
    5. Construir secciones.
    6. Deduplicar bloques repetidos.
    7. Resolver headers duplicados.
    8. Recuperar contaminación de cabecera personal.
    9. Recuperar información personal desplazada.
    10. Limpiar idiomas.
    """

    def __init__(self) -> None:
        self._patterns = self._compile_patterns()
        self._embedded_headers = (
            self._compile_embedded_headers()
        )

    # ========================================================================
    # PUBLIC API
    # ========================================================================

    def split(
        self,
        text: str,
    ) -> SectionMap:
        """
        Divide el texto del CV en secciones.
        """

        normalized = self._normalize(text)

        if not normalized:
            return self._empty_result()

        blocks = self._split_blocks(normalized)

        blocks = self._expand_embedded_headers(blocks)

        return self._build_sections(blocks)

    def process(
        self,
        text: str,
    ) -> SectionMap:
        """
        Ejecuta split() e imprime un resumen.
        """

        sections = self.split(text)

        self.print_summary(sections)

        return sections

    def print_summary(
        self,
        sections: SectionMap,
    ) -> None:
        """
        Imprime métricas básicas de las secciones.
        """

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
        """
        Ejecuta el splitter mostrando información diagnóstica.
        """

        separator = "=" * 70

        print()
        print(separator)
        print("DEBUG — CV Section Splitter")
        print(separator)

        normalized = self._normalize(text)

        blocks = self._split_blocks(normalized)

        expanded = self._expand_embedded_headers(blocks)

        detected = self._detect_boundaries(expanded)

        sections = self._build_sections(expanded)

        print()
        print(
            f"  Bloques originales: {len(blocks)}"
        )

        print(
            f"  Bloques después de expansión: {len(expanded)}"
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

            print(
                f"    bloque {item['index']:>4} "
                f"[{item['section']:<16}] "
                f"conf:{item['confidence']:.2f} "
                f"({item['detection']}) "
                f"{header[:60]}"
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

            for line in lines[:10]:
                print(f"  {line}")

            if len(lines) > 10:
                print("  ...")

            print()

        return sections

    # ========================================================================
    # NORMALIZATION
    # ========================================================================

    def _normalize(
        self,
        text: str,
    ) -> str:
        """
        Normaliza saltos de línea y espacios sin destruir estructura.
        """

        if not text:
            return ""

        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")
        text = text.replace("\t", " ")

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

    # ========================================================================
    # BLOCKS
    # ========================================================================

    def _split_blocks(
        self,
        text: str,
    ) -> list[str]:
        """
        Divide el documento en bloques usando fronteras explícitas.
        """

        return [
            block.strip()
            for block in text.split("\n\n")
            if block.strip()
        ]

    # ========================================================================
    # MATCHING NORMALIZATION
    # ========================================================================

    @staticmethod
    def _normalize_for_matching(
        text: str,
    ) -> str:
        """
        Normaliza acentos para comparación semántica.
        """

        replacements = str.maketrans(
            {
                "á": "a",
                "é": "e",
                "í": "i",
                "ó": "o",
                "ú": "u",
                "ü": "u",
                "ñ": "n",
                "Á": "A",
                "É": "E",
                "Í": "I",
                "Ó": "O",
                "Ú": "U",
                "Ü": "U",
                "Ñ": "N",
                "à": "a",
                "è": "e",
                "ì": "i",
                "ò": "o",
                "ù": "u",
                "À": "A",
                "È": "E",
                "Ì": "I",
                "Ò": "O",
                "Ù": "U",
                "ä": "a",
                "ë": "e",
                "ï": "i",
                "ö": "o",
                "Ä": "A",
                "Ë": "E",
                "Ï": "I",
                "Ö": "O",
            }
        )

        return text.translate(replacements)

    @staticmethod
    def _semantic_key(
        text: str,
    ) -> str:
        """
        Produce una clave estable para deduplicación.
        """

        return "".join(
            character.casefold()
            for character in text
            if character.isalnum()
        )

    # ========================================================================
    # PATTERN COMPILATION
    # ========================================================================

    def _compile_patterns(
        self,
    ) -> dict[
        SectionKey,
        list[re.Pattern[str]],
    ]:
        """
        Compila encabezados completos.
        """

        compiled: dict[
            SectionKey,
            list[re.Pattern[str]],
        ] = {}

        for section, headers in _SECTION_HEADERS.items():
            patterns: list[re.Pattern[str]] = []

            for header in headers:
                normalized_header = (
                    self._normalize_for_matching(header)
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
        Compila encabezados que pueden aparecer pegados al contenido.
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
                    self._normalize_for_matching(header)
                )

                pattern = re.compile(
                    rf"^{re.escape(normalized_header)}",
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

    # ========================================================================
    # EMBEDDED HEADERS
    # ========================================================================

    def _expand_embedded_headers(
        self,
        blocks: list[str],
    ) -> list[str]:
        """
        Convierte:

            EDUCATIONIndustrial Engineering...

        en:

            EDUCATION
            Industrial Engineering...
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
        Detecta un encabezado pegado al comienzo de un bloque.
        """

        working = block.strip()

        if not working:
            return []

        prefix_match = _DECORATIVE_PREFIX_RE.match(working)

        content_start = (
            prefix_match.end()
            if prefix_match
            else 0
        )

        candidate = working[content_start:]

        normalized_candidate = (
            self._normalize_for_matching(candidate)
        )

        for (
            header,
            _section,
            pattern,
        ) in self._embedded_headers:

            match = pattern.match(
                normalized_candidate
            )

            if not match:
                continue

            header_length = len(header)

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

            return [
                actual_header,
                remaining,
            ]

        return [working]

    # ========================================================================
    # HEADER MATCHING
    # ========================================================================

    def _match_header(
        self,
        block: str,
    ) -> SectionKey | None:
        """
        Detecta un encabezado completo.
        """

        first_line = block.split(
            "\n",
            1,
        )[0].strip()

        normalized_line = (
            self._normalize_for_matching(first_line)
        )

        best_section: SectionKey | None = None
        best_length = 0

        for section, patterns in self._patterns.items():
            for index, pattern in enumerate(patterns):
                if not pattern.fullmatch(normalized_line):
                    continue

                header_length = len(
                    _SECTION_HEADERS[section][index]
                )

                if header_length > best_length:
                    best_length = header_length
                    best_section = section

        return best_section

    # ========================================================================
    # CONTEXTUAL HEADER RULES
    # ========================================================================

    def _is_ignored_contextual_header(
        self,
        section: SectionKey,
        block_index: int,
        blocks: list[str],
    ) -> bool:
        """
        Evita falsos encabezados creados por elementos internos del CV.

        Caso principal:

            Experience
            ...
            Technologies
            : Flutter · Python · ...

        "Technologies" pertenece a la experiencia y no debe
        abrir una nueva sección Skills.
        """

        normalized = (
            self._normalize_for_matching(
                blocks[block_index]
            ).casefold()
        )

        if normalized != "technologies":
            return False

        previous_sections = self._detect_previous_real_sections(
            block_index,
            blocks,
        )

        return "experience" in previous_sections

    def _detect_previous_real_sections(
        self,
        block_index: int,
        blocks: list[str],
    ) -> set[SectionKey]:
        """
        Detecta las secciones explícitas anteriores al bloque actual.

        Se utiliza solamente para decisiones contextuales.
        """

        sections: set[SectionKey] = set()

        for index in range(block_index):
            section = self._match_header(blocks[index])

            if section is not None:
                sections.add(section)

        return sections

    # ========================================================================
    # STRUCTURAL DETECTION
    # ========================================================================

    def _detect_structural_boundary(
        self,
        block: str,
    ) -> SectionKey | None:
        """
        Detección estructural conservadora.

        Recupera EXPERIENCE cuando existen simultáneamente
        rol profesional y fecha.
        """

        normalized = (
            self._normalize_for_matching(block)
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
            r"líder|"
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

    # ========================================================================
    # BOUNDARIES
    # ========================================================================

    def _detect_boundaries(
        self,
        blocks: list[str],
    ) -> list[dict[str, Any]]:
        """
        Detecta todos los límites de sección.

        Las detecciones son contextuales para evitar:

        - Technologies dentro de Experience.
        - Headers duplicados que realmente representan
          una cabecera/contacto.
        """

        found: list[dict[str, Any]] = []

        for index, block in enumerate(blocks):
            section = self._match_header(block)

            if section is not None:
                if self._is_ignored_contextual_header(
                    section,
                    index,
                    blocks,
                ):
                    continue

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

            structural = self._detect_structural_boundary(
                block
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

    # ========================================================================
    # BUILD SECTIONS
    # ========================================================================

    def _build_sections(
        self,
        blocks: list[str],
    ) -> SectionMap:
        """
        Construye el mapa final de secciones.

        Maneja especialmente:

        - Summary duplicado.
        - Contacto posterior al segundo Summary.
        - Cabecera personal contaminando Education.
        - LIA Ecosystem como Projects.
        - Technologies interno de Experience.
        """

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

        detected = self._detect_boundaries(blocks)

        if not detected:
            accumulator["personal_info"] = list(blocks)

            return self._join_sections(
                accumulator,
                confidences,
                detections,
            )

        first_index = detected[0]["index"]

        accumulator["personal_info"] = blocks[:first_index]

        for index, boundary in enumerate(detected):
            section = boundary["section"]
            start = boundary["index"]

            if index + 1 < len(detected):
                end = detected[index + 1]["index"]
            else:
                end = len(blocks)

            content = blocks[start + 1:end]

            # ---------------------------------------------------------------
            # SUMMARY DUPLICADO
            # ---------------------------------------------------------------

            if section == "summary" and self._is_duplicate_summary(
                detected,
                index,
            ):
                self._split_duplicate_summary_region(
                    content=content,
                    accumulator=accumulator,
                )

            else:
                accumulator[section].extend(content)

            confidence = float(boundary["confidence"])

            if confidence >= confidences.get(section, 0.0):
                confidences[section] = confidence
                detections[section] = boundary["detection"]

        # --------------------------------------------------------------------
        # Deduplication
        # --------------------------------------------------------------------

        for section in accumulator:
            accumulator[section] = (
                self._deduplicate_section_blocks(
                    accumulator[section]
                )
            )

        # --------------------------------------------------------------------
        # Section contamination recovery
        # --------------------------------------------------------------------
        #
        # Important for DOCX layouts where visual columns are flattened
        # sequentially. In the current CV, the education section can be
        # followed by the visual personal header:
        #
        #   MIGUEL
        #   TOVAR AMARAL
        #   Full Stack Developer
        #   ...
        #   linkedin...
        #   github...
        #
        # That region is not education and must be removed before the
        # EducationBuilder receives the text.
        # --------------------------------------------------------------------

        self._remove_personal_profile_from_education(
            accumulator=accumulator,
            confidences=confidences,
            detections=detections,
        )

        # --------------------------------------------------------------------
        # Personal information recovery
        # --------------------------------------------------------------------

        self._recover_personal_info(
            accumulator=accumulator,
            confidences=confidences,
            detections=detections,
        )

        # --------------------------------------------------------------------
        # Language cleanup
        # --------------------------------------------------------------------

        accumulator["languages"] = (
            self._clean_languages_blocks(
                accumulator["languages"]
            )
        )

        return self._join_sections(
            accumulator,
            confidences,
            detections,
        )

    # ========================================================================
    # SECTION CONTAMINATION RECOVERY
    # ========================================================================

    def _remove_personal_profile_from_education(
        self,
        accumulator: dict[SectionKey, list[str]],
        confidences: dict[SectionKey, float],
        detections: dict[SectionKey, DetectionMethod],
    ) -> None:
        """
        Evita que una cabecera personal/profesional termine dentro
        de EDUCATION debido a la pérdida de estructura visual del DOCX.

        Ejemplo:

            Ingeniería Industrial y de Sistemas
            Universidad del Valle de México
            Google Data Analytics (Coursera)
            continua en IA,
            Flutter y Arquitectura de Software
            MIGUEL
            TOVAR AMARAL
            Full Stack Developer
            ...
            linkedin
            github
            ...

        La recuperación requiere evidencia semántica suficiente:

        - nombre;
        - título profesional;
        - múltiples señales de contacto.

        No depende del nombre concreto del candidato.
        """

        education_blocks = accumulator.get(
            "education",
            [],
        )

        if not education_blocks:
            return

        contact_start = self._find_profile_contamination_start(
            education_blocks
        )

        if contact_start is None:
            return

        contaminated = education_blocks[
            contact_start:
        ]

        if not contaminated:
            return

        recovered = self._recover_fragmented_contact(
            contaminated
        )

        # No modificar EDUCATION si no podemos reconstruir una cabecera
        # personal suficientemente confiable.
        if recovered is None:
            return

        personal_text, _remaining_blocks = recovered

        if not personal_text:
            return

        accumulator["education"] = (
            education_blocks[:contact_start]
        )

        accumulator["personal_info"].append(
            personal_text
        )

        confidences["personal_info"] = max(
            confidences.get("personal_info", 0.0),
            0.95,
        )

        detections["personal_info"] = "recovery"

    def _find_profile_contamination_start(
        self,
        blocks: list[str],
    ) -> int | None:
        """
        Encuentra el comienzo de una cabecera personal/profesional
        contaminando una sección estructurada.

        Requiere:

        1. una línea que parezca nombre;
        2. un título profesional cercano;
        3. múltiples señales de contacto posteriormente.

        Esto evita cortar educación legítima por encontrar una palabra
        como "Developer" o "Engineer".
        """

        if not blocks:
            return None

        # --------------------------------------------------------------------
        # Caso 1:
        #
        # Nombre + título profesional + señales de contacto
        # --------------------------------------------------------------------

        for start_index, candidate in enumerate(blocks):
            if not self._looks_like_name_line(candidate):
                continue

            window_end = min(
                len(blocks),
                start_index + 25,
            )

            window = blocks[
                start_index:window_end
            ]

            has_profile_title = any(
                self._looks_like_profile_title(
                    value
                )
                for value in window
            )

            if not has_profile_title:
                continue

            contact_signals = sum(
                1
                for value in window
                if self._is_contact_fragment(value)
            )

            if contact_signals < 2:
                continue

            return start_index

        # --------------------------------------------------------------------
        # Caso 2:
        #
        # Nombre dividido en dos bloques:
        #
        # MIGUEL
        # TOVAR AMARAL
        # Full Stack Developer
        # ...
        # --------------------------------------------------------------------

        for start_index in range(
            len(blocks) - 1
        ):
            first = blocks[start_index].strip()
            second = blocks[start_index + 1].strip()

            if not self._looks_like_name_line(first):
                continue

            if not self._looks_like_name_line(second):
                continue

            window_end = min(
                len(blocks),
                start_index + 25,
            )

            window = blocks[
                start_index:window_end
            ]

            has_profile_title = any(
                self._looks_like_profile_title(
                    value
                )
                for value in window
            )

            if not has_profile_title:
                continue

            contact_signals = sum(
                1
                for value in window
                if self._is_contact_fragment(value)
            )

            if contact_signals >= 2:
                return start_index

        return None

    # ========================================================================
    # DUPLICATE SUMMARY
    # ========================================================================

    def _is_duplicate_summary(
        self,
        detected: list[dict[str, Any]],
        boundary_index: int,
    ) -> bool:
        """
        Determina si el boundary actual es un Summary duplicado.

        Ejemplo:

            PROFESSIONAL SUMMARY
            ...
            PROFESSIONAL SUMMARY
            ...

        El segundo Summary puede ser en realidad el punto donde
        empieza la cabecera visual/contacto del CV.
        """

        current = detected[boundary_index]

        if current["section"] != "summary":
            return False

        previous_same_summary = any(
            item["section"] == "summary"
            for item in detected[:boundary_index]
        )

        return previous_same_summary

    def _split_duplicate_summary_region(
        self,
        content: list[str],
        accumulator: dict[
            SectionKey,
            list[str],
        ],
    ) -> None:
        """
        Separa el contenido posterior a un Summary duplicado.

        El CV de prueba produce:

            MIGUEL
            TOVAR AMARAL
            Full Stack Developer
            Building AI-powered products...
            linkedin...
            ...

        Esta región pertenece a personal_info.
        """

        if not content:
            return

        contact_start = self._find_contact_block_start(
            content
        )

        if contact_start is None:
            accumulator["summary"].extend(content)
            return

        summary_part = content[:contact_start]
        contact_part = content[contact_start:]

        if summary_part:
            accumulator["summary"].extend(summary_part)

        if not contact_part:
            return

        recovered = self._recover_fragmented_contact(
            contact_part
        )

        if recovered is not None:
            personal_text, _remaining_blocks = recovered

            if personal_text:
                accumulator["personal_info"].append(
                    personal_text
                )

            # Los bloques visuales restantes, como FRONTEND/BACKEND,
            # no se clasifican automáticamente como personal_info.
            return

        contact_end = self._find_contact_region_end(
            contact_part
        )

        if contact_end is None:
            accumulator["personal_info"].extend(
                contact_part
            )
            return

        accumulator["personal_info"].extend(
            contact_part[:contact_end]
        )

        if contact_part[contact_end:]:
            accumulator["summary"].extend(
                contact_part[contact_end:]
            )

    def _find_contact_region_end(
        self,
        blocks: list[str],
    ) -> int | None:
        """
        Encuentra el final de una región de contacto fragmentada.

        La región termina cuando aparecen elementos visuales que ya no son
        datos personales, por ejemplo:

            GitHub Portfolio
            FRONTEND
            BACKEND
            Building modern, responsive
            ...

        El resultado es el índice exclusivo del último bloque de contacto.
        """

        if not blocks:
            return None

        last_contact = -1

        for index, block in enumerate(blocks):
            value = block.strip()

            if self._is_contact_fragment(value):
                last_contact = index
                continue

            if self._looks_like_contact_continuation(value):
                if last_contact >= 0:
                    last_contact = index
                continue

            if last_contact < 0:
                continue

            normalized = (
                self._normalize_for_matching(value)
                .casefold()
            )

            if normalized in {
                "frontend",
                "backend",
                "front end",
                "back end",
            }:
                break

            break

        if last_contact < 0:
            return None

        return last_contact + 1

    def _find_contact_block_start(
        self,
        blocks: list[str],
    ) -> int | None:
        """
        Encuentra el primer bloque que inicia la cabecera personal.

        Prioridad:

        1. Dos líneas consecutivas con apariencia de nombre.
        2. Una línea de nombre seguida por varias señales de contacto.
        3. Un título profesional corto con un nombre inmediatamente
           anterior.

        Los párrafos largos nunca se consideran cabecera por contener
        palabras como "Founder", "Developer", etc.
        """

        if not blocks:
            return None

        # --------------------------------------------------------------------
        # 1. Nombre + apellido + señales de contacto
        # --------------------------------------------------------------------

        for index in range(len(blocks) - 1):
            if not self._looks_like_name_line(blocks[index]):
                continue

            if not self._looks_like_name_line(
                blocks[index + 1]
            ):
                continue

            window = blocks[
                index:min(len(blocks), index + 20)
            ]

            signal_count = sum(
                1
                for candidate in window
                if self._is_contact_fragment(candidate)
            )

            if signal_count >= 2:
                return index

        # --------------------------------------------------------------------
        # 2. Una sola línea de nombre + señales
        # --------------------------------------------------------------------

        for index, block in enumerate(blocks):
            if not self._looks_like_name_line(block):
                continue

            window = blocks[
                index:min(len(blocks), index + 20)
            ]

            signal_count = sum(
                1
                for candidate in window
                if self._is_contact_fragment(candidate)
            )

            if signal_count >= 2:
                return index

        # --------------------------------------------------------------------
        # 3. Título profesional corto con nombre anterior
        # --------------------------------------------------------------------

        for index, block in enumerate(blocks):
            if not self._looks_like_contact_header_block(block):
                continue

            if self._looks_like_profile_title(block):
                name_start = self._find_name_before(
                    lines=blocks,
                    title_index=index,
                )

                if name_start is not None:
                    return name_start

        return None

    def _looks_like_contact_header_block(
        self,
        block: str,
    ) -> bool:
        """
        Determina si un bloque puede iniciar la cabecera personal.

        Un resumen profesional puede contener palabras como "Founder",
        "Developer" o "Engineer". Por eso los bloques largos de prosa
        nunca se consideran cabecera únicamente por contener un título.
        """

        value = block.strip()

        if not value:
            return False

        if len(value) > 100:
            return False

        if self._looks_like_profile_title(value):
            if (
                len(value.split()) <= 8
                and not re.search(
                    r"[.!?]",
                    value,
                )
            ):
                return True

        if self._looks_like_name_line(value):
            return True

        if self._is_contact_fragment(value):
            return True

        return False

    # ========================================================================
    # PERSONAL INFORMATION RECOVERY
    # ========================================================================

    def _recover_personal_info(
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
    ) -> None:
        """
        Recupera información personal desplazada dentro de summary.

        Si ya fue recuperada durante el tratamiento de Summary duplicado,
        no vuelve a moverla.
        """

        if accumulator["personal_info"]:
            confidences.setdefault(
                "personal_info",
                0.95,
            )

            detections.setdefault(
                "personal_info",
                "recovery",
            )

        blocks = accumulator["summary"]

        if not blocks:
            return

        recovered = self._recover_fragmented_contact(
            blocks
        )

        if recovered is not None:
            personal_text, remaining_blocks = recovered

            accumulator["personal_info"].append(
                personal_text
            )

            accumulator["summary"] = remaining_blocks

            confidences["personal_info"] = 0.95
            detections["personal_info"] = "recovery"

            return

        for index, block in enumerate(blocks):
            if not self._looks_like_personal_info(block):
                continue

            if not self._is_meaningful_contact_block(block):
                continue

            personal_block = blocks.pop(index)

            accumulator["personal_info"].append(
                personal_block
            )

            confidences["personal_info"] = 0.90
            detections["personal_info"] = "recovery"

            return

    # ========================================================================
    # FRAGMENTED CONTACT RECOVERY
    # ========================================================================

    def _recover_fragmented_contact(
        self,
        blocks: list[str],
    ) -> tuple[str, list[str]] | None:
        """
        Reconstruye una cabecera personal fragmentada por la extracción DOCX.

        Soporta dos escenarios:

        1. Un bloque contiene múltiples líneas.
        2. Cada elemento visual fue extraído como un bloque independiente.
        """

        # --------------------------------------------------------------------
        # Caso 1: un bloque multilinea
        # --------------------------------------------------------------------

        for block_index, block in enumerate(blocks):
            lines = [
                line.strip()
                for line in block.splitlines()
                if line.strip()
            ]

            if len(lines) < 2:
                continue

            signal_indexes = [
                index
                for index, line in enumerate(lines)
                if self._is_contact_fragment(line)
            ]

            if len(signal_indexes) < 2:
                continue

            first_signal = min(signal_indexes)
            last_signal = max(signal_indexes)

            start = self._find_contact_region_start(
                lines=lines,
                first_signal=first_signal,
            )

            end = last_signal + 1

            while (
                end < len(lines)
                and end <= last_signal + 6
            ):
                candidate = lines[end]

                if self._is_contact_fragment(candidate):
                    end += 1
                    continue

                if self._looks_like_contact_continuation(
                    candidate
                ):
                    end += 1
                    continue

                break

            region = lines[start:end]

            if not self._region_has_enough_contact_signals(
                region
            ):
                continue

            personal_text = "\n".join(
                region
            ).strip()

            if not personal_text:
                continue

            remaining_lines = (
                lines[:start]
                + lines[end:]
            )

            remaining_text = "\n".join(
                remaining_lines
            ).strip()

            updated_blocks = list(blocks)

            if remaining_text:
                updated_blocks[block_index] = (
                    remaining_text
                )
            else:
                updated_blocks.pop(block_index)

            return (
                personal_text,
                updated_blocks,
            )

        # --------------------------------------------------------------------
        # Caso 2: bloques independientes
        #
        # MIGUEL
        # TOVAR AMARAL
        # Full Stack Developer
        # ...
        # linkedin
        # ...
        # github
        # ...
        # +52...
        # --------------------------------------------------------------------

        for start_index, candidate in enumerate(blocks):
            if not self._looks_like_name_line(candidate):
                continue

            window_end = min(
                len(blocks),
                start_index + 30,
            )

            window = blocks[
                start_index:window_end
            ]

            signal_positions = [
                relative_index
                for relative_index, value in enumerate(window)
                if self._is_contact_fragment(value)
            ]

            if len(signal_positions) < 2:
                continue

            last_signal_relative = max(
                signal_positions
            )

            end_index = (
                start_index
                + last_signal_relative
                + 1
            )

            # Incluir fragmentos de URL/email.
            while end_index < window_end:
                value = blocks[end_index]

                if self._is_contact_fragment(value):
                    end_index += 1
                    continue

                if self._looks_like_contact_continuation(
                    value
                ):
                    end_index += 1
                    continue

                # El título profesional y un tagline corto pueden estar
                # entre el nombre y las señales de contacto.
                if end_index <= start_index + 4:
                    if self._looks_like_profile_title(
                        value
                    ):
                        end_index += 1
                        continue

                break

            region = blocks[
                start_index:end_index
            ]

            if not self._region_has_enough_contact_signals(
                region
            ):
                continue

            personal_text = "\n".join(
                value.strip()
                for value in region
                if value.strip()
            ).strip()

            if not personal_text:
                continue

            updated_blocks = (
                blocks[:start_index]
                + blocks[end_index:]
            )

            return (
                personal_text,
                updated_blocks,
            )

        return None

    def _find_contact_region_start(
        self,
        lines: list[str],
        first_signal: int,
    ) -> int:
        """
        Busca hacia atrás el inicio del encabezado personal.
        """

        if first_signal <= 0:
            return first_signal

        search_start = max(
            0,
            first_signal - 8,
        )

        title_index: int | None = None

        for index in range(
            first_signal - 1,
            search_start - 1,
            -1,
        ):
            if self._looks_like_profile_title(
                lines[index]
            ):
                title_index = index
                break

        if title_index is not None:
            name_start = self._find_name_before(
                lines=lines,
                title_index=title_index,
            )

            if name_start is not None:
                return name_start

            return title_index

        for index in range(
            first_signal - 2,
            search_start - 1,
            -1,
        ):
            if index < 0:
                continue

            if (
                self._looks_like_name_line(
                    lines[index]
                )
                and self._looks_like_name_line(
                    lines[index + 1]
                )
            ):
                return index

        return first_signal

    def _find_name_before(
        self,
        lines: list[str],
        title_index: int,
    ) -> int | None:
        """
        Busca un nombre inmediatamente antes del título profesional.
        """

        if title_index <= 0:
            return None

        previous = title_index - 1

        if self._looks_like_name_line(
            lines[previous]
        ):
            if (
                previous > 0
                and self._looks_like_name_line(
                    lines[previous - 1]
                )
            ):
                return previous - 1

            return previous

        return None

    # ========================================================================
    # NAME / PROFILE DETECTION
    # ========================================================================

    def _looks_like_name_line(
        self,
        line: str,
    ) -> bool:
        """
        Detecta una línea que parece parte de un nombre humano.
        """

        value = line.strip()

        if not value:
            return False

        if len(value) > 40:
            return False

        if any(
            character.isdigit()
            for character in value
        ):
            return False

        if any(
            character in value
            for character in (
                "@",
                "/",
                ":",
                ".",
                "+",
                "·",
            )
        ):
            return False

        words = value.split()

        if not 1 <= len(words) <= 4:
            return False

        normalized = (
            self._normalize_for_matching(value)
        )

        excluded_markers = (
            "building",
            "designed",
            "experienced",
            "specializing",
            "powered",
            "services",
            "applications",
            "platform",
        )

        if any(
            marker in normalized.casefold()
            for marker in excluded_markers
        ):
            return False

        return all(
            re.fullmatch(
                r"[A-Za-zÀ-ÖØ-öø-ÿ'-]+",
                word,
            )
            is not None
            for word in words
        )

    def _looks_like_profile_title(
        self,
        line: str,
    ) -> bool:
        """
        Detecta títulos profesionales.
        """

        normalized = (
            self._normalize_for_matching(line)
        )

        return any(
            re.search(
                rf"\b{re.escape(marker)}\b",
                normalized,
                re.IGNORECASE,
            )
            for marker in _PROFILE_TITLE_MARKERS
        )

    # ========================================================================
    # CONTACT DETECTION
    # ========================================================================

    def _is_contact_fragment(
        self,
        line: str,
    ) -> bool:
        """
        Determina si una línea puede formar parte de información personal.

        Esta función es una señal, no una decisión final.
        """

        value = line.strip()

        if not value:
            return False

        normalized = (
            self._normalize_for_matching(value)
        )

        lower = normalized.casefold()

        if _EMAIL_RE.search(value):
            return True

        if self._looks_like_phone(value):
            return True

        if _LINKEDIN_RE.search(value):
            return True

        if _GITHUB_RE.search(value):
            return True

        if any(
            marker in lower
            for marker in _LOCATION_MARKERS
        ):
            return True

        if any(
            marker in lower
            for marker in (
                "@gmail",
                "@hotmail",
                "@outlook",
                "@gmailcom",
                "@hotmailcom",
                "@outlookcom",
            )
        ):
            return True

        if any(
            marker in lower
            for marker in (
                "linkedin",
                "github",
                "portfolio",
            )
        ):
            return True

        if lower in {
            "in",
            "com",
            "comv",
            "com/",
            "in/",
            ".com",
            "gmailcom",
            "@gmailcom",
        }:
            return True

        return False

    def _looks_like_phone(
        self,
        text: str,
    ) -> bool:
        """
        Determina si el texto contiene un teléfono razonable.
        """

        if not text:
            return False

        digits = re.sub(
            r"\D",
            "",
            text,
        )

        if len(digits) < 7:
            return False

        return bool(
            _PHONE_RE.search(text)
        )

    def _region_has_enough_contact_signals(
        self,
        lines: list[str],
    ) -> bool:
        """
        Exige múltiples señales antes de extraer una región.
        """

        if not lines:
            return False

        strong = 0
        weak = 0

        joined = "\n".join(lines)

        if _EMAIL_RE.search(joined):
            strong += 2

        if self._looks_like_phone(joined):
            strong += 2

        if _LINKEDIN_RE.search(joined):
            strong += 1

        if _GITHUB_RE.search(joined):
            strong += 1

        for line in lines:
            normalized = (
                self._normalize_for_matching(line)
                .casefold()
            )

            if any(
                marker in normalized
                for marker in _LOCATION_MARKERS
            ):
                weak += 1

            if any(
                marker in normalized
                for marker in _CONTACT_MARKERS
            ):
                weak += 1

            if any(
                marker in normalized
                for marker in (
                    "@gmail",
                    "@hotmail",
                    "@outlook",
                    "@gmailcom",
                    "@hotmailcom",
                    "@outlookcom",
                )
            ):
                weak += 1

            if any(
                marker in normalized
                for marker in _FRAGMENTED_PROFILE_MARKERS
            ):
                weak += 1

            if self._looks_like_phone(line):
                weak += 2

        if strong >= 2:
            return True

        return weak >= 3

    def _looks_like_contact_continuation(
        self,
        line: str,
    ) -> bool:
        """
        Detecta fragmentos de URL/email separados por DOCX.
        """

        normalized = (
            self._normalize_for_matching(line)
            .casefold()
        )

        if normalized in {
            "in",
            "com",
            "comv",
            "com/",
            "in/",
            ".com",
            "gmailcom",
            "@gmailcom",
            "hotmailcom",
            "@hotmailcom",
            "outlookcom",
            "@outlookcom",
        }:
            return True

        if normalized.endswith(
            ("com", "com/", "in/", "comv")
        ):
            return True

        if normalized.startswith(
            ("@", ".", "/", "-")
        ):
            return True

        return False

    # ========================================================================
    # PERSONAL INFO BLOCK DETECTION
    # ========================================================================

    def _looks_like_personal_info(
        self,
        block: str,
    ) -> bool:
        """
        Determina si un bloque completo parece información personal.
        """

        if not block.strip():
            return False

        normalized = (
            self._normalize_for_matching(block)
        )

        lower = normalized.casefold()

        strong_signals = 0

        if _EMAIL_RE.search(block):
            strong_signals += 2

        if self._looks_like_phone(block):
            strong_signals += 2

        if _LINKEDIN_RE.search(block):
            strong_signals += 1

        if _GITHUB_RE.search(block):
            strong_signals += 1

        marker_hits = sum(
            1
            for marker in _CONTACT_MARKERS
            if marker in lower
        )

        strong_signals += min(
            marker_hits,
            2,
        )

        if strong_signals >= 2:
            return True

        has_phone = self._looks_like_phone(block)

        has_profile_title = any(
            re.search(
                rf"\b{re.escape(marker)}\b",
                normalized,
                re.IGNORECASE,
            )
            for marker in _PROFILE_TITLE_MARKERS
        )

        return has_phone and has_profile_title

    def _is_meaningful_contact_block(
        self,
        block: str,
    ) -> bool:
        """
        Evita considerar contacto un bloque diminuto.
        """

        lines = [
            line.strip()
            for line in block.splitlines()
            if line.strip()
        ]

        if not lines:
            return False

        if len(lines) == 1:
            value = lines[0].casefold()

            if value in {
                "linkedin",
                "linkedin comin/",
                "github",
                "github.",
                "com",
                "com/",
                "in",
                "in/",
                "gmailcom",
                "@gmailcom",
            }:
                return False

        signals = 0

        if _EMAIL_RE.search(block):
            signals += 1

        if self._looks_like_phone(block):
            signals += 1

        if _LINKEDIN_RE.search(block):
            signals += 1

        if _GITHUB_RE.search(block):
            signals += 1

        return signals >= 2

    # ========================================================================
    # LANGUAGE CLEANUP
    # ========================================================================

    def _clean_languages_blocks(
        self,
        blocks: list[str],
    ) -> list[str]:
        """
        Elimina artefactos mínimos y duplicados.
        """

        if not blocks:
            return []

        cleaned: list[str] = []
        seen: set[str] = set()

        for block in blocks:
            value = block.strip()

            if not value:
                continue

            semantic = self._semantic_key(value)

            if (
                len(semantic) == 1
                and semantic.isalpha()
            ):
                continue

            if semantic in seen:
                continue

            seen.add(semantic)

            cleaned.append(value)

        return cleaned

    # ========================================================================
    # DEDUPLICATION
    # ========================================================================

    def _deduplicate_section_blocks(
        self,
        blocks: list[str],
    ) -> list[str]:
        """
        Deduplica preservando el orden.
        """

        result: list[str] = []
        seen: set[str] = set()

        for block in blocks:
            key = self._semantic_key(block)

            if not key:
                continue

            if key in seen:
                continue

            seen.add(key)
            result.append(block)

        return result

    # ========================================================================
    # JOIN RESULTS
    # ========================================================================

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
        """
        Convierte acumuladores en SectionResult.
        """

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

    # ========================================================================
    # EMPTY RESULT
    # ========================================================================

    @staticmethod
    def _empty_result() -> SectionMap:
        """
        Devuelve el contrato vacío completo.
        """

        return {
            key: SectionResult(
                text="",
                confidence=0.0,
                detection="none",
            )
            for key in _EMPTY_SECTIONS
        }