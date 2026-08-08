"""Read-only, shared OpenXML package support for DOCX extraction strategies."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from zipfile import BadZipFile, ZipFile, is_zipfile

from lxml import etree


WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
DRAWING_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
NS = {"w": WORD_NS, "a": DRAWING_NS}
W_TEXT = f"{{{WORD_NS}}}t"
A_TEXT = f"{{{DRAWING_NS}}}t"


class InvalidOpenXMLPackage(ValueError):
    """A file that cannot be processed as a Word DOCX package."""


@dataclass(frozen=True)
class OpenXMLPackage:
    path: Path
    xml_parts: dict[str, bytes]
    image_count: int

    @classmethod
    def open(cls, file_path: str | Path) -> "OpenXMLPackage":
        path = Path(file_path)
        if path.suffix.lower() != ".docx":
            raise InvalidOpenXMLPackage(f"Unsupported DOCX extension: {path.suffix or '<none>'}")
        if not path.is_file():
            raise InvalidOpenXMLPackage(f"File does not exist: {path}")
        if not is_zipfile(path):
            raise InvalidOpenXMLPackage("The file is not a valid OpenXML ZIP package.")

        try:
            with ZipFile(path) as archive:
                names = set(archive.namelist())
                required = {"[Content_Types].xml", "word/document.xml"}
                missing = required - names
                if missing:
                    raise InvalidOpenXMLPackage(
                        f"The DOCX package is missing required parts: {', '.join(sorted(missing))}."
                    )
                xml_parts = {
                    name: archive.read(name)
                    for name in names
                    if name.startswith("word/") and name.endswith(".xml")
                }
                image_count = sum(name.startswith("word/media/") for name in names)
        except BadZipFile as error:
            raise InvalidOpenXMLPackage("The DOCX ZIP package is corrupted.") from error

        return cls(path=path, xml_parts=xml_parts, image_count=image_count)

    def root(self, part_name: str) -> etree._Element:
        try:
            return etree.fromstring(self.xml_parts[part_name])
        except (KeyError, etree.XMLSyntaxError) as error:
            raise InvalidOpenXMLPackage(f"Cannot parse OpenXML part: {part_name}") from error

    def story_parts(self) -> tuple[str, ...]:
        headers_and_footers = sorted(
            part for part in self.xml_parts if part.startswith("word/header") or part.startswith("word/footer")
        )
        return ("word/document.xml", *headers_and_footers)

    def signal_summary(self) -> tuple[int, list[str]]:
        text_nodes = 0
        signals: set[str] = set()
        for part_name in self.story_parts():
            root = self.root(part_name)
            text_nodes += len(root.xpath(".//w:t | .//a:t", namespaces=NS))
            if root.xpath(".//w:txbxContent", namespaces=NS):
                signals.add("word_textbox")
            if root.xpath(".//a:txBody", namespaces=NS):
                signals.add("drawingml_text")
        if self.image_count:
            signals.add("embedded_images")
        return text_nodes, sorted(signals)


def element_identity(root: etree._Element, element: etree._Element) -> str:
    return root.getroottree().getpath(element)


def text_from_element(element: etree._Element) -> str:
    """Join run fragments without injecting spaces into split words."""
    return "".join(node.text or "" for node in element.iter() if node.tag in {W_TEXT, A_TEXT}).strip()


def is_inside(element: etree._Element, namespace_tag: str) -> bool:
    current = element.getparent()
    while current is not None:
        if current.tag == namespace_tag:
            return True
        current = current.getparent()
    return False
