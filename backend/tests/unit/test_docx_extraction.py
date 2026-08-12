from pathlib import Path

import pytest

from backend.modules.cv.loader.docx_loader import DOCXLoader
from backend.modules.cv.loader.extraction_models import (
    DocumentExtractionError,
    ExtractionStatus,
)
from backend.modules.cv.loader.docx_strategies import DrawingMLStrategy
from backend.modules.cv.loader.openxml_package import OpenXMLPackage


ROOT = Path(__file__).resolve().parents[3]
TEXTBOX_CV = ROOT / "data" / "uploads" / "1a1a995a18f24a9ba5ebb4eff5ced934_CV_Miguel_Tovar_Full_Stack.docx"
STANDARD_CV = ROOT / "data" / "uploads" / "4125e26c60694020acbfea823269ee5b_CV_Miguel_Tovar_Asesor_atencion.docx"
IMAGE_ONLY_CV = ROOT / "backend" / "storage" / "uploads" / "docx" / "00733c50-6041-4a33-b7bf-e562e9ed7b2a.docx"


def test_extracts_textbox_content_from_real_upload() -> None:
    result = DOCXLoader().extract(TEXTBOX_CV)

    assert result.report.status is ExtractionStatus.SUCCESS
    assert result.report.text_node_count >= 174
    assert "word_textbox" in result.report.signals
    assert result.raw_text
    assert any(chunk.source == "word_textboxes" for chunk in result.chunks)
    assert DOCXLoader().load(TEXTBOX_CV) == result.raw_text


def test_extracts_standard_docx_without_regression() -> None:
    result = DOCXLoader().extract(STANDARD_CV)

    assert result.report.status is ExtractionStatus.SUCCESS
    assert result.raw_text
    standard_run = next(run for run in result.report.strategies if run.strategy == "standard_paragraphs")
    assert standard_run.chunk_count > 0


def test_image_only_docx_returns_actionable_report() -> None:
    result = DOCXLoader().extract(IMAGE_ONLY_CV)

    assert result.report.status is ExtractionStatus.IMAGE_ONLY
    assert result.report.image_count > 0
    assert result.report.warnings
    with pytest.raises(DocumentExtractionError) as error:
        DOCXLoader().load(IMAGE_ONLY_CV)
    assert error.value.report is result.report or error.value.report.status is ExtractionStatus.IMAGE_ONLY


def test_invalid_docx_returns_unsupported_report(tmp_path: Path) -> None:
    invalid_file = tmp_path / "not-a-docx.docx"
    invalid_file.write_text("not a zip package", encoding="utf-8")

    result = DOCXLoader().extract(invalid_file)

    assert result.report.status is ExtractionStatus.UNSUPPORTED
    assert result.report.errors


def test_extracts_drawingml_text_independently() -> None:
    package = OpenXMLPackage(
        path=Path("drawingml-fixture.docx"),
        image_count=0,
        xml_parts={
            "word/document.xml": b'''<?xml version="1.0" encoding="UTF-8"?>
                <w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
                    xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
                  <w:body><a:txBody><a:p><a:r><a:t>DrawingML resume text</a:t></a:r></a:p></a:txBody></w:body>
                </w:document>'''
        },
    )

    chunks = DrawingMLStrategy().extract(package)

    assert [chunk.text for chunk in chunks] == ["DrawingML resume text"]
