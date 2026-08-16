"""Independent text extraction strategies for valid DOCX packages."""

from __future__ import annotations

from abc import ABC, abstractmethod

from docx import Document

from backend.modules.cv.loader.extraction_models import ExtractionChunk
from backend.modules.cv.loader.openxml_package import (
    NS,
    WORD_NS,
    WPS_NS,
    VML_NS,
    OpenXMLPackage,
    element_identity,
    is_inside,
    text_from_element,
)


TEXTBOX_TAGS = {
    f"{{{WORD_NS}}}txbxContent",
    f"{{{WPS_NS}}}txbx",
    f"{{{VML_NS}}}textbox",
}


class DOCXExtractionStrategy(ABC):
    """Strategy interface; implementations do not coordinate with one another."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the unique strategy name."""
        raise NotImplementedError

    @abstractmethod
    def extract(self, package: OpenXMLPackage) -> list[ExtractionChunk]:
        """Extract text chunks from the DOCX package."""
        raise NotImplementedError


class HeaderStrategy(DOCXExtractionStrategy):
    """Extract textual content from Word document headers.

    Word CVs commonly place the candidate's name and contact information
    inside the document header instead of the main document body.

    This strategy runs before body-oriented strategies so header content
    becomes the first logical block in the merged extraction stream.
    """

    @property
    def name(self) -> str:
        return "word_headers"

    def extract(self, package: OpenXMLPackage) -> list[ExtractionChunk]:
        chunks: list[ExtractionChunk] = []
        ordinal = 0

        header_parts = sorted(
            part_name
            for part_name in package.xml_parts
            if part_name.startswith("word/header")
            and part_name.endswith(".xml")
        )

        for part_name in header_parts:
            root = package.root(part_name)

            for paragraph in root.xpath(".//w:p", namespaces=NS):
                text = text_from_element(paragraph)

                if not text:
                    continue

                chunks.append(
                    ExtractionChunk(
                        text=text,
                        source=self.name,
                        part_name=part_name,
                        ordinal=ordinal,
                        identity=element_identity(root, paragraph),
                    )
                )
                ordinal += 1

        return chunks


class StandardParagraphStrategy(DOCXExtractionStrategy):
    """Extract standard paragraphs and table-cell paragraphs."""

    @property
    def name(self) -> str:
        return "standard_paragraphs"

    def extract(self, package: OpenXMLPackage) -> list[ExtractionChunk]:
        document = Document(package.path)
        chunks: list[ExtractionChunk] = []
        ordinal = 0

        def append_paragraph(paragraph) -> None:
            nonlocal ordinal

            text = paragraph.text.strip()

            if text:
                chunks.append(
                    ExtractionChunk(
                        text=text,
                        source=self.name,
                        part_name="word/document.xml",
                        ordinal=ordinal,
                        identity=paragraph._p.getroottree().getpath(
                            paragraph._p
                        ),
                    )
                )
                ordinal += 1

        for paragraph in document.paragraphs:
            append_paragraph(paragraph)

        for table in document.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        append_paragraph(paragraph)

        return chunks


class TextBoxStrategy(DOCXExtractionStrategy):
    """Extract text contained inside Word text boxes."""

    @property
    def name(self) -> str:
        return "word_textboxes"

    def extract(self, package: OpenXMLPackage) -> list[ExtractionChunk]:
        chunks: list[ExtractionChunk] = []
        ordinal = 0

        for part_name in package.story_parts():
            root = package.root(part_name)

            for tag_name in TEXTBOX_TAGS:
                # We extract the tag prefix and local name to build the xpath
                # Or we can just use lxml iter()
                for textbox in root.iter(tag_name):
                    # For wps:txbx we need to iterate over w:t and a:t, 
                    # but it could also contain w:p. The safest is to extract all text directly
                    # from the textbox if it doesn't contain w:p, or use text_from_element.
                    
                    # Some textboxes have w:p, others just have w:t or a:t scattered.
                    # We can iterate over w:p and then gather any orphans?
                    # Let's extract text by looking for paragraphs first.
                    paragraphs = textbox.xpath(".//w:p", namespaces=NS)
                    
                    if paragraphs:
                        for paragraph in paragraphs:
                            text = text_from_element(paragraph)
                            if text:
                                chunks.append(
                                    ExtractionChunk(
                                        text=text,
                                        source=self.name,
                                        part_name=part_name,
                                        ordinal=ordinal,
                                        identity=element_identity(root, paragraph),
                                    )
                                )
                                ordinal += 1
                    else:
                        # Fallback for textboxes without w:p
                        text = text_from_element(textbox)
                        if text:
                            chunks.append(
                                ExtractionChunk(
                                    text=text,
                                    source=self.name,
                                    part_name=part_name,
                                    ordinal=ordinal,
                                    identity=element_identity(root, textbox),
                                )
                            )
                            ordinal += 1

        return chunks


class DrawingMLStrategy(DOCXExtractionStrategy):
    """Extract text from DrawingML text bodies outside text boxes."""

    @property
    def name(self) -> str:
        return "drawingml"

    def extract(self, package: OpenXMLPackage) -> list[ExtractionChunk]:
        chunks: list[ExtractionChunk] = []
        ordinal = 0

        for part_name in package.story_parts():
            root = package.root(part_name)

            for text_body in root.xpath(
                ".//a:txBody",
                namespaces=NS,
            ):
                if is_inside(text_body, TEXTBOX_TAGS):
                    continue

                for paragraph in text_body.xpath(
                    ".//a:p",
                    namespaces=NS,
                ):
                    text = text_from_element(paragraph)

                    if text:
                        chunks.append(
                            ExtractionChunk(
                                text=text,
                                source=self.name,
                                part_name=part_name,
                                ordinal=ordinal,
                                identity=element_identity(
                                    root,
                                    paragraph,
                                ),
                            )
                        )
                        ordinal += 1

        return chunks


class OpenXMLStrategy(DOCXExtractionStrategy):
    """Package-level recovery of Word paragraphs not inside textboxes."""

    @property
    def name(self) -> str:
        return "openxml_recovery"

    def extract(self, package: OpenXMLPackage) -> list[ExtractionChunk]:
        chunks: list[ExtractionChunk] = []
        ordinal = 0

        for part_name in package.story_parts():
            root = package.root(part_name)

            for paragraph in root.xpath(
                ".//w:p",
                namespaces=NS,
            ):
                if is_inside(paragraph, TEXTBOX_TAGS):
                    continue

                text = text_from_element(paragraph)

                if text:
                    chunks.append(
                        ExtractionChunk(
                            text=text,
                            source=self.name,
                            part_name=part_name,
                            ordinal=ordinal,
                            identity=element_identity(
                                root,
                                paragraph,
                            ),
                        )
                    )
                    ordinal += 1

            # Recover orphan text nodes (not in w:p and not in textboxes)
            # This is a last resort to catch everything
            orphan_texts = []
            for tag_type in ["w:t", "a:t"]:
                for t in root.xpath(f".//{tag_type}", namespaces=NS):
                    if not is_inside(t, {"{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p"} | TEXTBOX_TAGS):
                        if t.text and t.text.strip():
                            orphan_texts.append(t.text.strip())
                            
            if orphan_texts:
                chunks.append(
                    ExtractionChunk(
                        text=" ".join(orphan_texts),
                        source=self.name,
                        part_name=part_name,
                        ordinal=ordinal,
                        identity=element_identity(root, root),
                    )
                )
                ordinal += 1

        return chunks