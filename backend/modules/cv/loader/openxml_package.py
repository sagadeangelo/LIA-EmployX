"""Read-only, shared OpenXML package support for DOCX extraction strategies."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from zipfile import BadZipFile, ZipFile, is_zipfile

from lxml import etree


WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
DRAWING_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
WPS_NS = "http://schemas.microsoft.com/office/word/2010/wordprocessingShape"
VML_NS = "urn:schemas-microsoft-com:vml"

NS = {
    "w": WORD_NS,
    "a": DRAWING_NS,
    "wps": WPS_NS,
    "v": VML_NS,
}

W_TEXT = f"{{{WORD_NS}}}t"
A_TEXT = f"{{{DRAWING_NS}}}t"


class InvalidOpenXMLPackage(ValueError):
    """A file that cannot be processed as a Word DOCX package."""


@dataclass(frozen=True)
class OpenXMLPackage:
    """
    Read-only representation of a DOCX OpenXML package.

    The package exposes:
    - XML parts used by text extraction strategies.
    - Embedded media parts used by OCR/image strategies.
    """

    path: Path
    xml_parts: dict[str, bytes]
    media_parts_data: dict[str, bytes]
    image_count: int

    @classmethod
    def open(cls, file_path: str | Path) -> "OpenXMLPackage":
        """
        Open and validate a DOCX package.

        XML parts and embedded media are loaded into memory so extraction
        strategies can operate independently of the ZIP archive lifecycle.
        """
        path = Path(file_path)

        if path.suffix.lower() != ".docx":
            raise InvalidOpenXMLPackage(
                f"Unsupported DOCX extension: {path.suffix or '<none>'}"
            )

        if not path.is_file():
            raise InvalidOpenXMLPackage(
                f"File does not exist: {path}"
            )

        if not is_zipfile(path):
            raise InvalidOpenXMLPackage(
                "The file is not a valid OpenXML ZIP package."
            )

        try:
            with ZipFile(path) as archive:
                names = set(archive.namelist())

                required = {
                    "[Content_Types].xml",
                    "word/document.xml",
                }

                missing = required - names

                if missing:
                    raise InvalidOpenXMLPackage(
                        "The DOCX package is missing required parts: "
                        f"{', '.join(sorted(missing))}."
                    )

                xml_parts = {
                    name: archive.read(name)
                    for name in names
                    if name.startswith("word/")
                    and name.endswith(".xml")
                }

                media_parts_data = {
                    name: archive.read(name)
                    for name in names
                    if name.startswith("word/media/")
                    and not name.endswith("/")
                }

                image_count = len(media_parts_data)

        except BadZipFile as error:
            raise InvalidOpenXMLPackage(
                "The DOCX ZIP package is corrupted."
            ) from error

        return cls(
            path=path,
            xml_parts=xml_parts,
            media_parts_data=media_parts_data,
            image_count=image_count,
        )

    def root(self, part_name: str) -> etree._Element:
        """
        Parse and return an XML part as an lxml root element.
        """
        try:
            return etree.fromstring(self.xml_parts[part_name])
        except (KeyError, etree.XMLSyntaxError) as error:
            raise InvalidOpenXMLPackage(
                f"Cannot parse OpenXML part: {part_name}"
            ) from error

    def story_parts(self) -> tuple[str, ...]:
        """
        Return the document and all available header/footer story parts.
        """
        headers_and_footers = sorted(
            part
            for part in self.xml_parts
            if part.startswith("word/header")
            or part.startswith("word/footer")
        )

        return (
            "word/document.xml",
            *headers_and_footers,
        )

    def media_parts(self) -> tuple[str, ...]:
        """
        Return embedded media part names in deterministic order.

        Example:
            (
                "word/media/image1.png",
                "word/media/image2.jpeg",
                ...
            )
        """
        return tuple(sorted(self.media_parts_data))

    def read_media(self, part_name: str) -> bytes:
        """
        Return the raw bytes of an embedded media part.
        """
        try:
            return self.media_parts_data[part_name]
        except KeyError as error:
            raise InvalidOpenXMLPackage(
                f"Media part does not exist: {part_name}"
            ) from error

    def signal_summary(self) -> tuple[int, list[str]]:
        """
        Return basic structural signals discovered in the package.
        """
        text_nodes = 0
        signals: set[str] = set()

        for part_name in self.story_parts():
            root = self.root(part_name)

            text_nodes += len(
                root.xpath(
                    ".//w:t | .//a:t",
                    namespaces=NS,
                )
            )

            if root.xpath(
                ".//w:txbxContent",
                namespaces=NS,
            ):
                signals.add("word_textbox")

            if root.xpath(
                ".//a:txBody",
                namespaces=NS,
            ):
                signals.add("drawingml_text")

        if self.image_count:
            signals.add("embedded_images")

        return text_nodes, sorted(signals)


def element_identity(
    root: etree._Element,
    element: etree._Element,
) -> str:
    """Return a stable XPath identity for an XML element."""
    return root.getroottree().getpath(element)


def text_from_element(
    element: etree._Element,
) -> str:
    """
    Join text fragments without injecting spaces into split words.
    """
    return "".join(
        node.text or ""
        for node in element.iter()
        if node.tag in {W_TEXT, A_TEXT}
    ).strip()


def is_inside(
    element: etree._Element,
    namespace_tags: set[str] | tuple[str, ...],
) -> bool:
    """
    Determine whether an element is nested inside any given XML tags.
    """
    if isinstance(namespace_tags, str):
        namespace_tags = {namespace_tags}
    else:
        namespace_tags = set(namespace_tags)

    current = element.getparent()

    while current is not None:
        if current.tag in namespace_tags:
            return True

        current = current.getparent()

    return False