# ExtractionChunkMerger Implementation Validation

## Implemented scope

Only `ExtractionChunkMerger` was refactored. No extraction strategy, splitter,
builder, profile model, runtime, API, repository, or Flutter file was changed.

The merger now:

1. Treats source chunk text as opaque; it does not trim or collapse whitespace.
2. Emits `\n\n` between independent retained chunks.
3. Preserves same-strategy repetitions and order.
4. Reconciles semantic duplicates only across strategies.
5. Suppresses an OpenXML recovery chunk when at least 80% of the selected
   canonical chunks from the same document part are semantically covered.

## Real-CV evidence

Input: `CV_Miguel_Tovar_Full_Stack.docx`.

| Metric | Before merger refactor | After merger refactor |
| --- | ---: | ---: |
| retained chunks | 91 | 90 |
| raw text characters | 6,624 | 3,430 |
| block separators (`\n\n`) | 0 | 89 |
| OpenXML recovery duplication | retained | suppressed |
| same-strategy repeated layout blocks | flattened/at risk | preserved |

The lower post-merge character count is intentional: the 3,282-character
OpenXML recovery chunk is a concatenated duplicate representation of the
textbox content. The 90 textbox chunks remain in source order and their text
is not normalized by the merger.

## Splitter result

| Section | Characters | Confidence | Result |
| --- | ---: | ---: | --- |
| personal_info | 0 | 0.00 | Fail |
| summary | 760 | 0.95 | Pass |
| experience | 1,450 | 0.95 | Pass |
| education | 358 | 0.95 | Pass |
| skills | 0 | 0.00 | Fail |
| languages | 722 | 0.95 | Pass |
| certifications | 0 | 0.00 | Fail |
| projects | 0 | 0.00 | Not required by this CV |

## Validation decision

The merger now satisfies its approved structural-preservation scope: it emits
explicit document blocks and removes only cross-strategy fallback duplication.
The sprint success criterion is nevertheless **not met** for this particular
CV because three required sections remain empty. The pipeline validation stops
at `CVSectionSplitter`; no CVDocument/profile persistence/API/Flutter claim is
made from an incomplete section map.

The exact evidence and constrained next decision are in
`ROOT_CAUSE_STAGE_CVSECTION_SPLITTER_POST_MERGE.md`.
