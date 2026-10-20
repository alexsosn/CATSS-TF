# #136 — Audit source context of 71 newly unresolved Sirach alignments

## Research evidence

Merged #135 removed 7,868 source manuscript numerals from Sirach MT-A lexical tokens without changing typed manuscript annotations. The pinned 46-file CCAT test then established that **7,396** Sirach groups changed MT lexical cardinality: 7,324 derived→derived, **43** derived→unclassified Hebrew-empty/Greek-present, **28** derived→unclassified `CATSS LXX-minus` with no surviving Hebrew lexical material, and 1 unclassified witness-lacuna unchanged. Merged #142 found 85 Sirach unclassified records and 102 corpus-wide. Those are **mechanical classification changes**, not independent textual-critical adjudication. Prior research issue #132 explains why typed witness marker(s) on an alignment do not prove attribution to an individual word.

## What remains unknown

- Of these 71 newly unclassified groups, how many are standalone witness labels, multiple witness labels, `>n` absence markers, MT-B retroversions, lacuna/reconstruction-marked records, or Greek-minus rows?
- How many are neighboring other alignments within the *same verse* with Hebrew lexical material, and how many are isolated? Neighbor co-occurrence is only an editorial-context lead, never a source-grounded link.
- Which precise source chapter/verse/physical line identities should be independently inspected by a scholar? Licensed CCAT text may be locally inspected, but should **not** be committed to git or printed into CI output.

## Plan → RED-first tests → implementation → source test → skeptical review

1. Define a small **metadata-only** `audit_sirach_unclassified_context(document)` function over already-parsed `ParallelDocument`. Compare historical reader `_mt_lexical_readings(mt_col_a)` (with existing `is_lxx_plus` handling) to current `mt_count`, replay `derive_alignment_technique` with `dataclasses.replace`; count only transitions **derived→unclassified**. Record exact reason-string categories, witness and absence presence and source sides, MT-B presence, annotations, lexical counts, adjacent alignment **presence** on either side within that verse, and first 3 physical source identifiers per category.
2. RED-first synthetic source fixtures deliberately contain a Hebrew-empty/Greek-present witness-only record, a minus-marked witness-only record, neighboring genuine MT+Greek lexical alignments, MT-B witness, and derived witness-bearing cases. Assert transition categories and neighbor counts; assert the result's `repr` never contains MT/LXX lexical source tokens. Include non-Sirach source rejection, exclusion of pre-existing unclassified and current derived rows, and ambiguous >12 non-marker.
3. Implement **only a research audit**, no writer, parser, reference resolution, annotation semantics, runtime dependency, schema feature or separate state. Keep report bounded to numeric metadata, marker kind names and line coordinates; do not encode or infer manuscript→word edges or conjectural Greek additions/omissions.
4. In existing ephemeral 46-file CI, run the new audit after the existing Sirach parse, pin total **43+28=71** and independently compare identities/reasons to loaded native TF `find_unclassified_alignments()` when possible. Print only aggregate metadata, at most 3 chapter/verse/line identities in each category. Update this research document with actual counts, not guesses.
5. Exact-head Python 3.11–3.13, release, native Context-Fabric, full 46-file canonical TF readback and Agora E2E; separate critical code/data review anchored to exact head before merge. Do not close #136 unless actual philological interpretation is proven.

## Explicit limits

Historical lexical cardinality is reconstructed via the old _generic lexical reader_ as before #135, not a complete checkout of the former parser. The audit establishes causal parser-status transitions, **not** original manuscript witness scope, reading reconstruction, or actual Greek/Hebrew omission. A neighboring word in the same verse cannot be imputed as the target of an otherwise unbound manuscript number. Issue #132 and broader Libronix #126 stay open.
