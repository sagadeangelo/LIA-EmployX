# DOCX Extraction Implementation Plan

## Phase 1 — Establish contracts

Create immutable extraction-domain models for chunks, result, report, strategy execution, and status. Define the strategy protocol and a document-extraction exception that carries an `ExtractionReport`. Preserve `BaseLoader.load()` and the public `DOCXLoader.load() -> str` API.

Acceptance: existing callers compile unchanged; direct DOCX callers can use `extract()` for diagnostics.

## Phase 2 — Implement OpenXML strategy layer

Create a package context that validates a DOCX ZIP package, enumerates main, header, and footer XML parts, and records document signals. Implement the four independent strategies and the deterministic chunk merger. Strategy failures are reported individually without discarding text supplied by another strategy.

Acceptance: standard paragraphs, Word text boxes, DrawingML text, and raw OpenXML fallback each produce attributable chunks with no duplicate final text.

## Phase 3 — Integrate without pipeline changes

Make `DOCXLoader` delegate to the resolver. Update only the extraction service to call `extract()` when supported, log report summary, and fail with a report-carrying exception for non-success statuses. Keep PDF loader and all existing pipeline outputs/contracts intact.

Acceptance: mission runtime and API receive the same `CVDocument` model for successful documents; unsupported/image-only DOCX errors explain the reason.

## Phase 4 — Test and verify

Add focused unit tests for every strategy, deduplication, malformed packages, image-only classification, and legacy `load()`. Add an extraction-service test using a stored textbox-based CV and retain a standard-DOCX regression test. Run the backend suite and compile all modified modules.

Acceptance: the textbox corpus yields non-empty raw text and populated downstream sections; PDF tests remain green; no runtime/UI/builder/profile files are changed.

## Rollout safeguards

The resolver has no network or OCR dependency. Structured reports provide the observability needed to measure real-world producer variants. New strategy registration is additive, so future formats can be introduced behind the loader boundary without rewriting the CV pipeline.
