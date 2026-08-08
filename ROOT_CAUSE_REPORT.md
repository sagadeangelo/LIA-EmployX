# DOCX Extraction Root-Cause Report

## Scope reviewed

The production CV ingestion path is `CVParserAgent -> ExtractionService -> LoaderFactory -> DOCXLoader -> CVSectionSplitter -> CVDocumentBuilder -> ProfessionalProfileMapper -> ProfileRepository`. The mission runtime invokes `CVParserAgent` after the upload persists the file; it does not extract document text itself. A separate legacy `modules/cv/engine` reader stack also has a paragraph-only DOCX reader, but it is not the path used by the mission.

The review intentionally excludes the already-validated mission, profile, builder, Flutter, and agent-runtime layers. Their observed empty outputs are the correct consequence of receiving empty source text.

## Current architecture and failure boundary

`DOCXLoader.load()` opens a package with `python-docx.Document` and combines only `document.paragraphs` and `document.tables`. It returns a `str`. `ExtractionService` passes that string directly to language detection, section splitting, and the document builder. There is no document-level extraction result, no source-aware diagnostics, and no guard against successful-but-empty DOCX extraction.

The failure boundary is therefore the conversion from the DOCX package to raw text, before `CVDocumentBuilder` is called.

## Evidence

The stored upload corpus was audited on 2026-08-07. Representative affected files have the following properties:

| Evidence | Observed value |
| --- | --- |
| `python-docx` document paragraphs | 4 or 10 |
| non-empty paragraph text | 0 |
| extracted paragraph/table text | 0 characters |
| `/word/document.xml` `w:t` nodes | 174-176 |
| `/word/document.xml` `w:txbxContent` nodes | 16 |

For example, `data/uploads/1a1a995a18f24a9ba5ebb4eff5ced934_CV_Miguel_Tovar_Full_Stack.docx` has four exposed paragraphs with no text, but 174 Word text nodes, all in textbox content. Multiple `Asesor - Hotelero` uploads exhibit the same pattern. In contrast, conventional documents in the same corpus have 31-34 non-empty paragraphs and are extracted by the current loader.

`python-docx` deliberately presents the main document body through its object model; it does not make every WordprocessingML text container (notably text inside shapes/text boxes) available as `document.paragraphs`. This is a representation limitation, not a data-loss or profile-mapping problem.

## Root cause

The single extraction mechanism assumes all textual DOCX content is represented as ordinary paragraphs or tables. Modern layout-oriented CV generators place candidate content in DrawingML/VML shapes and `w:txbxContent`; that content is stored in the OpenXML package but omitted by the current API traversal. The loader converts this recoverable state into an indistinguishable empty string.

## Why downstream fixes could not solve it

At the first downstream boundary, the language detector, section splitter, and builders receive `""`. They cannot infer contact details, experience, skills, or sections that were never delivered. The mapper and repository then correctly persist empty/default model fields, and the dashboard correctly renders them. Runtime retries, prompt changes, builder changes, or Flutter changes cannot recover unextracted XML and would violate separation of responsibilities.

## Design implications

The fix is a permanent extraction-layer redesign, not OCR or a one-off XPath. DOCX must be parsed as an OpenXML package using independent, observable strategies. The public legacy `load() -> str` contract must remain available, while a richer extraction result supplies diagnostics and prevents silent empty success for image-only, malformed, or unsupported packages.
