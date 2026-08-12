# DOCX-to-Dashboard Pipeline Audit

**Input:** `data/uploads/1a1a995a18f24a9ba5ebb4eff5ced934_CV_Miguel_Tovar_Full_Stack.docx`  
**Date:** 2026-08-07  
**Status:** **HALTED at first information-loss boundary**

## Trace

| Stage | Input | Output | Objects / confidence | Result |
| --- | ---: | ---: | --- | --- |
| DOCXLoader | DOCX package | 6,624 chars | 174 text nodes; 90 textbox chunks; `success` | Pass |
| ExtractionService handoff | 6,624 chars | 6,624 chars | no character loss | Pass |
| CVSectionSplitter | 6,624 chars | 1 text block; 8 section keys | only `experience`: 6,344 chars, confidence 0.95 | **Fail** |
| CVDocumentBuilder | invalid section map | 1 experience; 0 education/skills/languages/certifications | personal-info confidence 0.0; experience 80.0 | Diagnostic only |
| ProfessionalProfileMapper | — | — | — | Halted |
| ProfileRepository | — | — | — | Halted |
| Mission / GET / Flutter | — | — | — | Halted |

## DOCXLoader evidence

| Strategy | Chunks | Characters |
| --- | ---: | ---: |
| `standard_paragraphs` | 0 | 0 |
| `word_textboxes` | 90 | 3,252 |
| `drawingml` | 0 | 0 |
| `openxml_recovery` | 1 | 3,282 |

The loader report is `success`, with 174 text nodes and the `embedded_images` and `word_textbox` signals.

## CVSectionSplitter evidence

After splitter normalization, the input is 6,344 characters. `_split_blocks()` returns one block and `_detect_boundaries()` detects that block as `experience` at confidence 0.95.

| Section | Length | Confidence | Detection |
| --- | ---: | ---: | --- |
| personal_info | 0 | 0.00 | none |
| summary | 0 | 0.00 | none |
| experience | 6,344 | 0.95 | header |
| education | 0 | 0.00 | none |
| skills | 0 | 0.00 | none |
| languages | 0 | 0.00 | none |
| certifications | 0 | 0.00 | none |
| projects | 0 | 0.00 | none |

## Builder diagnostics

| Builder | Input | Objects | Confidence | Warnings |
| --- | ---: | ---: | --- |
| PersonalInfoBuilder | 0 | default contact | 0.0 | empty personal-info text |
| ExperienceBuilder | 6,344 | 1 `CVExperience` | 80.0 | role/company inference; deterministic normalization |
| EducationBuilder | 0 | 0 | 0.0 | empty education section |
| SkillsBuilder | 0 | 0 | 0.0 | empty skills section |
| LanguagesBuilder | 0 | 0 | 0.0 | empty languages section |
| CertificationsBuilder | 0 | 0 | 0.0 | empty certification section |

`CVDocument` contains 6,624 raw characters, one experience, zero education, zero skills, zero languages, zero certifications, and a default contact. This is the expected downstream consequence of the invalid section map, not a later data-loss point.

No profile was saved and no API, mission, or Flutter call was made. Continuing would serialize already-empty collections and violate the stop condition. See `ROOT_CAUSE_STAGE_DOCX_LOADER.md`.
