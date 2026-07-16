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
from typing import Final


# ---------------------------------------------------------------------------
# Tipos
# ---------------------------------------------------------------------------

SectionKey = str
SectionMap = dict[SectionKey, str]

# Estructura de retorno garantizada (orden reproducible en Python 3.7+).
_EMPTY_SECTIONS: Final[SectionMap] = {
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
# \W en Python es Unicode-aware por defecto, por lo que cubre emojis (🎓💡🧠),
# símbolos tipográficos (•►▪◆★), puntuación, espacios y todo lo demás
# sin necesidad de enumerar cada carácter.
_DECORATIVE_PATTERN: Final[str] = r"\W"


class CVSectionSplitter:
    """Divide el texto plano de un CV en secciones nombradas.

    No realiza ninguna interpretación semántica. No llama servicios externos.
    No crea objetos de dominio. Su única responsabilidad es segmentar texto.

    Example:
        >>> splitter = CVSectionSplitter()
        >>> sections = splitter.split(raw_text)
        >>> splitter.print_summary(sections)
    """

    # ------------------------------------------------------------------
    # Construcción
    # ------------------------------------------------------------------

    def __init__(self) -> None:
        # Compilar el mapa de patrones una sola vez para toda la vida del
        # objeto. Clave: sección; valor: lista de re.Pattern compilados.
        self._patterns: dict[SectionKey, list[re.Pattern[str]]] = (
            self._compile_patterns()
        )

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def split(self, text: str) -> SectionMap:
        """Divide el texto del CV en secciones.

        Args:
            text: Texto completo del CV en formato plano.

        Returns:
            Diccionario con exactamente ocho claves:
            personal_info, summary, experience, education,
            skills, languages, certifications, projects.
            Todos los valores son str.
        """
        normalized = self._normalize(text)
        lines = self._split_lines(normalized)
        return self._build_sections(lines)

    def process(self, text: str) -> SectionMap:
        """Punto de entrada principal del splitter.

        Equivalente a split(). Conservado para compatibilidad con la
        API pública existente.

        Args:
            text: Texto completo del CV en formato plano.

        Returns:
            Diccionario de secciones. Ver split().
        """
        sections = self.split(text)
        self.print_summary(sections)
        return sections

    def print_summary(self, sections: SectionMap) -> None:
        """Imprime un resumen con el nombre y tamaño de cada sección.

        Args:
            sections: Diccionario devuelto por split().
        """
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
        """Ejecuta el splitter en modo diagnóstico.

        Imprime información detallada sobre líneas, encabezados detectados
        y contenido de cada sección.

        Args:
            text: Texto completo del CV en formato plano.

        Returns:
            Diccionario de secciones. Ver split().
        """
        separator = "=" * 70
        print()
        print(separator)
        print("DEBUG — CV Section Splitter")
        print(separator)

        normalized = self._normalize(text)
        lines = self._split_lines(normalized)
        detected = self._detect_headers(lines)
        sections = self._build_sections(lines)

        # Líneas
        print()
        print(f"  Líneas totales : {len(lines)}")
        print()

        # Encabezados
        print("  Encabezados detectados:")
        print()
        if detected:
            for item in detected:
                # Encode safely: replace characters unsupported by the
                # current console codec with '?' instead of crashing.
                header_text: str = item["text"]  # type: ignore[assignment]
                safe_text = header_text.encode(
                    "ascii", errors="replace"
                ).decode("ascii")
                print(
                    f"    linea {item['index']:>4}  "
                    f"[{item['section']:<16}]  "
                    f"{safe_text}"
                )
        else:
            print("    (ninguno)")
        print()

        # Contenido de secciones
        print("  Contenido por sección:")
        print()
        for key in _EMPTY_SECTIONS:
            value = sections.get(key, "")
            print(f"  {'-' * 66}")
            print(f"  {key.upper()}")
            print(f"  {'-' * 66}")
            if value:
                for line in value.splitlines():
                    print(f"    {line}")
            else:
                print("    (vacío)")
            print()

        return sections

    # ------------------------------------------------------------------
    # Métodos privados — normalización
    # ------------------------------------------------------------------

    def _normalize(self, text: str) -> str:
        """Normaliza saltos de línea, tabulaciones y espacios múltiples.

        Args:
            text: Texto crudo del CV.

        Returns:
            Texto normalizado listo para segmentación.
        """
        if not text:
            return ""

        # Unificar saltos de línea (CRLF → LF, CR → LF)
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        # Reemplazar tabulaciones por un espacio
        text = text.replace("\t", " ")

        # Colapsar espacios múltiples en uno solo
        text = re.sub(r" {2,}", " ", text)

        # Reducir más de dos saltos de línea consecutivos a exactamente dos
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()

    def _split_lines(self, text: str) -> list[str]:
        """Divide el texto normalizado en líneas, eliminando las vacías.

        Args:
            text: Texto normalizado.

        Returns:
            Lista de líneas no vacías con espacios perimetrales eliminados.
        """
        return [line.strip() for line in text.split("\n") if line.strip()]

    # ------------------------------------------------------------------
    # Métodos privados — detección de encabezados
    # ------------------------------------------------------------------

    def _compile_patterns(self) -> dict[SectionKey, list[re.Pattern[str]]]:
        """Compila los patrones de encabezado una sola vez.

        Cada encabezado conocido se convierte en un patrón que tolera:
        - Mayúsculas o minúsculas.
        - Prefijos/sufijos decorativos: emojis (🎓💡🧠), símbolos tipográficos
          (•►▪◆★⭐✓✔—), puntuación, espacios, dos puntos, etc.
        - Espacios múltiples entre palabras.
        - Variantes con o sin tilde (la comparación normaliza antes de match).

        El prefijo/sufijo decorativo se modela como ``\\W*`` (non-word) — cualquier
        carácter que no sea letra, dígito o guion bajo — lo que cubre
        todos los símbolos anteriores sin enumerar cada uno.

        Returns:
            Mapa sección → lista de patrones compilados.
        """
        compiled: dict[SectionKey, list[re.Pattern[str]]] = {}
        deco = f"(?:{_DECORATIVE_PATTERN})*"

        for section, headers in _SECTION_HEADERS.items():
            patterns: list[re.Pattern[str]] = []
            for header in headers:
                # Palabras del encabezado separadas por uno o más espacios.
                escaped = r"\s+".join(re.escape(word) for word in header.split())
                pattern = re.compile(
                    rf"^{deco}{escaped}{deco}$",
                    re.IGNORECASE,
                )
                patterns.append(pattern)
            compiled[section] = patterns

        return compiled

    def _normalize_for_matching(self, line: str) -> str:
        """Elimina tildes y normaliza una línea para la comparación de patrones.

        Args:
            line: Línea original.

        Returns:
            Línea sin tildes, lista para comparar contra patrones.
        """
        replacements = str.maketrans(
            "áéíóúÁÉÍÓÚàèìòùÀÈÌÒÙäëïöüÄËÏÖÜâêîôûÂÊÎÔÛ",
            "aeiouAEIOUaeiouAEIOUaeiouAEIOUaeiouAEIOU",
        )
        return line.translate(replacements)

    def _match_header(self, line: str) -> SectionKey | None:
        """Determina si una línea es un encabezado de sección conocido.

        La detección ignora mayúsculas, símbolos decorativos, espacios
        múltiples y tildes. Ante ambigüedad, el encabezado más largo gana.

        Args:
            line: Línea de texto ya normalizada.

        Returns:
            Clave de sección si la línea es un encabezado, None en caso contrario.
        """
        normalized_line = self._normalize_for_matching(line)
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

    def _detect_headers(
        self, lines: list[str]
    ) -> list[dict[str, int | str]]:
        """Detecta todos los encabezados en la lista de líneas.

        Args:
            lines: Lista de líneas del CV (normalizadas y sin vacías).

        Returns:
            Lista de diccionarios con index, section y text,
            ordenados por posición ascendente.
        """
        found: list[dict[str, int | str]] = []

        for index, line in enumerate(lines):
            section = self._match_header(line)
            if section is not None:
                found.append(
                    {
                        "index": index,
                        "section": section,
                        "text": line,
                    }
                )

        return found

    # ------------------------------------------------------------------
    # Métodos privados — construcción de secciones
    # ------------------------------------------------------------------

    def _build_sections(self, lines: list[str]) -> SectionMap:
        """Construye el diccionario de secciones a partir de las líneas.

        Todo el texto anterior al primer encabezado pertenece a
        personal_info. Cada bloque entre encabezados pertenece a la sección
        correspondiente. Los encabezados repetidos se concatenan.

        Args:
            lines: Lista de líneas del CV (normalizadas y sin vacías).

        Returns:
            Diccionario de secciones con valores str.
        """
        accumulator: dict[SectionKey, list[str]] = {
            key: [] for key in _EMPTY_SECTIONS
        }

        detected = self._detect_headers(lines)

        if not detected:
            accumulator["personal_info"] = lines
            return self._join_sections(accumulator)

        first_index: int = detected[0]["index"]  # type: ignore[assignment]

        # Líneas anteriores al primer encabezado → personal_info
        accumulator["personal_info"] = lines[:first_index]

        # Distribuir bloques entre encabezados consecutivos
        for i, header in enumerate(detected):
            section: SectionKey = header["section"]  # type: ignore[assignment]
            start: int = header["index"] + 1  # type: ignore[operator]
            end: int = (
                detected[i + 1]["index"]  # type: ignore[index]
                if i + 1 < len(detected)
                else len(lines)
            )
            # Encabezado repetido: concatenar en lugar de sobrescribir.
            accumulator[section].extend(lines[start:end])

        return self._join_sections(accumulator)

    @staticmethod
    def _join_sections(
        accumulator: dict[SectionKey, list[str]],
    ) -> SectionMap:
        """Convierte listas de líneas en cadenas de texto.

        Args:
            accumulator: Mapa sección → lista de líneas.

        Returns:
            Mapa sección → str (texto unido y sin espacios perimetrales).
        """
        return {
            key: "\n".join(accumulator.get(key, [])).strip()
            for key in _EMPTY_SECTIONS
        }


# ---------------------------------------------------------------------------
# Prueba local
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    _SAMPLE_CV = """
Miguel Tovar
miguel@example.com | +52 55 1234 5678
Ciudad de México, México

► Perfil Profesional

Ingeniero de Software con más de 8 años de experiencia en desarrollo
de aplicaciones móviles y backend.

★ EXPERIENCIA LABORAL

Empresa Alpha — Senior Flutter Developer (2021 – presente)
- Desarrollo de apps multiplataforma con Flutter y Dart.

Empresa Beta — Python Backend Developer (2018 – 2021)
- APIs REST con FastAPI y Django.

• EDUCACIÓN

Universidad Nacional Autónoma
Licenciatura en Ingeniería en Sistemas Computacionales — 2017

◆ HABILIDADES CLAVE

Flutter · Dart · Python · FastAPI · Docker · AWS · PostgreSQL

IDIOMAS

Español — Nativo
Inglés — C1 (TOEFL 110)

Certificaciones

AWS Certified Developer – Associate (2023)
Google Cloud Professional Data Engineer (2022)

Proyectos

LIA EmployX — Plataforma de reclutamiento con IA
OpenResume — Generador de CVs de código abierto
"""

    import sys
    # Reconfigure stdout to UTF-8 so all Unicode in the sample prints
    # correctly regardless of the Windows console default encoding.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    _splitter = CVSectionSplitter()
    _splitter.debug(_SAMPLE_CV)
