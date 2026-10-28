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

## Empirical 46-file source and native TF acceptance (2026-10-20)

CI run [39464002549](https://github.com/alexsosn/CATSS-TF/actions/runs/39464002549)
on branch head `ecd9b5f` completed **complete-catss-audit**, including
the full 46-file source scan, canonical TF materialization and readback,
Agora E2E adapter smoke, and exact identity/reason parity between the
**71** newly unresolved source rows and canonical TF. The Python 3.13
unit job failed on a missing *test fixture return annotation* at mypy,
so that run is **not** an all-green release gate; the fixture was typed
on the subsequent branch commit and awaits exact-head CI.

The source-side audit counted **7,396** changed lexical cardinalities and
**71** newly unresolved alignments, of which **43** are currently
Hebrew-empty/Greek-present and **28** carry LXX-minus notation without
surviving Hebrew lexical material.

| Evidence among 71 newly unresolved alignment groups | Groups |
| --- | ---: |
| MT-A witness annotation present | 70 |
| MT-B source column present | 5 |
| MT-B witness annotation present | 0 |
| More than one MT-A witness annotation | 1 |
| Any Sirach lacuna/illegibility annotation | 61 |
| Reconstructed letters annotation | 8 |
| Exact >n reading-absence annotation | 1 |
| LXX-minus status | 28 |
| Greek lexical elements present | 43 |
| One Greek lexical element | 28 |
| Two Greek lexical elements | 7 |
| Three Greek lexical elements | 7 |
| More than three Greek lexical elements | 1 |
| Prior immediate same-verse group has MT words | 21 |
| Following immediate same-verse group has MT words | 37 |
| Both immediate same-verse groups have MT words | 14 |
| Neither immediate same-verse group has MT words | 27 |

Counts are **overlapping groups**, not mutually exclusive readings or word
attestations. They are parser-observed evidence from CCAT source, not
claims that a manuscript contains or omits a specific Hebrew word.
The neighboring-group signal may assist manual source inspection, but
must **never** create a word-specific connection in TF.

Source witnesses among these alignments (counts of *annotations*, not groups):
Geniza B **42**, Geniza C **13**, Geniza E **6**, Geniza A **5**,
Masada **4**, and 11QPs(a) **1**. This totals 71 annotations over 70
MT-A-marker-bearing groups, owing to one group with multiple markers.
A source witness annotation must not be interpreted as a lexical
reading or an absence in a different manuscript.

The first three source-only identities in each unresolved-technique
category, suitable for licensed-source follow-up, are:
- LXX-minus without MT: Sir 3:20, physical line 856; Sir 9:3, line 2606;
  Sir 10:25, line 3085.
- Hebrew-empty/Greek-present: Sir 6:26, line 1814; Sir 9:13, line 2736;
  Sir 10:25, line 3072.

The new research audit deliberately **does not** resolve the 71 cases.
Before any representation of Sirach manuscript-specific readings is added
to the corpus, a separate source-grounded study must determine the syntax,
scope, and provenance of manuscript variants on real examples (#132).
