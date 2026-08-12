# Root Cause: Post-Merge CVSectionSplitter Coverage Gap

## Input

The merger produces 90 canonical textbox chunks, 3,430 characters, and 89
explicit `\n\n` block separators. The separator-loss defect is resolved.

## Expected output

For this sprint’s end-to-end criterion, the splitter must populate
`personal_info`, `summary`, `experience`, `education`, `skills`, `languages`,
and `certifications`.

## Actual output

The splitter detects summary, experience, education, and languages at 0.95
confidence. It returns empty `personal_info`, `skills`, and `certifications`.

## Exact class and lines

| Item | Location |
| --- | --- |
| Failure stage | `CVSectionSplitter._match_header()` |
| File | `backend/modules/cv/parser/cv_section_splitter.py` |
| Vocabulary declaration | `_SECTION_HEADERS`, lines **57–130** |
| Skills vocabulary | lines **96–109** |

## Root cause

The source CV contains the header `CORE TECHNOLOGIES`; it is not one of the
allowed skills headers (`technical skills`, `core competencies`, `core skills`,
and related values). Consequently the splitter never creates a skills boundary.

The canonical source chunks begin with `EXPERIENCIA DESTACADA`; no personal
contact block is present in the extracted canonical sequence. The source also
contains no `CERTIFICACIONES`/`CERTIFICATIONS` block. A merger must preserve
source content and boundaries; it cannot truthfully invent a contact or
certification section.

## Decision required

This is no longer an `ExtractionChunkMerger` defect. Under the approved scope,
the merger cannot add splitter vocabulary or synthesize absent candidate data.
The next sprint must decide whether to:

1. extend the splitter vocabulary to include `CORE TECHNOLOGIES`; and
2. use a CV that actually contains contact and certification data for the
   full-profile acceptance test.

No such change was made here because modifying `CVSectionSplitter` is
explicitly prohibited in this sprint.
