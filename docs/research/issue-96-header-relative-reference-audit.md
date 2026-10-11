# R96-15 research — source-header-relative Greek reference notation

## Reconcile and evidence (2026-10-11)

Umbrella issue [#96](https://github.com/alexsosn/CATSS-TF/issues/96) remains OPEN; PR #116 was merged to `main` as `e5ead111afb93749c8b470151a389828044df74c`. No other open PR implements this source-only audit. The only unrelated draft is the magic-terminology notebook PR #42.

### Source semantics actually supported

Kingham's [CATSS parallel format reconstruction](https://github.com/codykingham/CATSS_parsers/blob/master/parallel_readme.md), section *Layout → Verses*, explicitly says parallel-file headers follow BHS numbering when it differs from Rahlfs Greek, and illustrates a source header `Gen 23:5` with the end-of-Greek-column marker `[6]`, describing that line as Greek verse 6. The reconstruction cites the CATSS 1991 `00.ReadReParallel.txt` and Emanuel Tov (1986), but is **secondary**, and the direct CCAT primary document timed out during this pass. This example supports measuring a **header-relative numeric displacement**; it does **not** show that every Greek square bracket is a word-level destination, how long its scope persists, or what contextual/range notation means. No primary-authoritative definition has been verified in this task.

Existing parser `src/catss_tf/parser.py::_extract_greek_references` stores each scalar Greek bracket as `GreekReference(chapter|None, verse, subverse|None, raw)`, and stores `[[9.2a-2f]]` separately in `lxx_reference_ranges`; the latter must **never** be counted as a scalar override. `ParallelVerse.chapter/verse` describes the physical *CATSS source header*. Existing `reference_audit.audit_greek_references` checks **all MT-header labels in a file** for zero/one/many numeric coincidences; this answers a different question from agreement with the reference's **own** header. The pinned 46-file inventory has 6,218 scalar references, 6 with an explicit chapter and 424 with a subverse suffix. Of the 6,218, 1,749 have no numeric MT-header candidate, 4,433 have one and 36 multiple; none are verified Greek targets.

### Specific information gap and conservative policy

Measure the scalar label's **own source-header** relationship, with mutually exclusive numeric categories:

1. `same_header_numeric`: effective reference chapter equals containing CATSS header chapter AND reference verse equals the header verse. Keep lettered suffix in the suffix count only: a matching `JoshB 9:2` / `[9:2a]` is still *not* a proved Greek subverse.
2. `different_verse_same_chapter`: effective chapter equals header chapter, but reference verse differs; e.g. the documented `Gen 23:5` / `[6]`. This is *potential* changed Greek versification, not a target.
3. `different_chapter`: a supplied explicit chapter differs from header chapter, regardless of whether verse also differs. Count once, before verse comparison.
Use `reference.chapter if reference.chapter is not None else verse.chapter` (never `or`, so explicit zero is not swallowed). Count **each scalar occurrence**, including repeated tags on one alignment. Do not infer anything from nearby lines, lexical tokens, Greek parent spans, translational equivalence or source numerals outside scalar references. Existing MT-header numeric-coincidence distribution and all other reports remain unchanged. Do not create new TF nodes/edges or modify parent mappings; only aggregate counts, with no raw source bytes or node IDs in results.

## Risk-focused validation matrix

| Synthetic or documented shape | Own-header class | Caveat |
| --- | --- | --- |
| `Gen 23:5`, Greek `[6]` | different verse, same chapter | Kingham's concrete Greek-versification example |
| `Gen 1:1`, Greek `[1]` | same numeric | Numeric equality proves no lexical target |
| `Gen 1:1`, Greek `[2:1]` | different chapter | Explicit chapter precedence |
| `Gen 1:1`, Greek `[2:2]` | different chapter, **not** additionally verse-shift class | Mutual exclusivity |
| `JoshB 9:2`, Greek `[9:2a]` | same numeric, lettered suffix | No supported `2a` subverse node in pinned parent |
| `JoshB 9:2`, `[[9.2a-2f]]` | **not scalar** | Preserve typed contextual range separately |
| `Gen 1:1`, two `[2]` tags | two verse-shift occurrences | Audits physical scalar notation, not deduplicated lexical tasks |

On the pinned 46 files, record exact totals **after** source integration runs, and retain the existing 6,218 / 1,749 / 4,433 / 36 and 6 explicit / 424 suffix invariants. Do not claim anything about Psalms, Esther, JoshB *actual* frequencies until measured.

## Boundaries and next research

This is a source-label diagnostic, independent of CenterBLC/LXX and BHSA. Greek reference semantics, Greek parent subverses, sentence-level span/scope, contextual `[c.v]`, Greek edition variation and cross-verse transposition are **not** resolved by these counters. Before introducing `catss_reference_target`, inspect authoritative CCAT/Tov documentation and examine actual Psalms/Esther/JoshB source rows and matching pinned parent surfaces with ambiguity checks. Leave #96 OPEN.

## Actual 46-source pinned audit (R96-15, 2026-10-11)

Full CI [run 38164945447](https://github.com/alexsosn/CATSS-TF/actions/runs/38164945447) on code head `e88a76ab554b374e882df0cd91a651f861b5c2a7` succeeded (Python 3.11/3.12/3.13, release smoke, full real source/parent audit, 46-file Text-Fabric materialization and readback). The `complete-catss-audit` job recorded:

| Source-only numeric evidence | Count |
| --- | ---: |
| Source files / scalar Greek references | 46 / **6,218** |
| Own-header chapter + verse **numeric equality** | **24** |
| Own-header different verse, effective chapter equal | **6,188** |
| Explicitly different chapter | **6** |
| Original MT-header numeric matches: zero / one / multiple | **1,749 / 4,433 / 36** |
| Explicit chapter labels / lettered suffixes | **6 / 424** |

Exactly 24 + 6,188 + 6 = 6,218. All six explicit chapter labels differ from the containing source chapter on this pinned corpus. The *24 same-numeric* cases are not verified Greek verse identity, while the *6,188 same-chapter verse differences* are not evidence by themselves for the nature, scope, or even textual destination of the bracket notation. Real Greek parent checks remain separate: 5,555 references with nonempty exact labeled parent spans, 641 missing, 22 unsupported; all 424 explicit lettered subverses have no matching labeled parent span. The original 671 explicit group and 260/84/32/295/0 conditional role-aware group partitions remain unchanged. Canonical TF readback still reports 349,670 alignment slots and 6,218 reference nodes. These observed categories are diagnostic only and yield **zero new verified reference-target edges**.

The test-only RED attempt on `22db138` failed at Ruff format before pytest; the corrected test-only head `23584c0` passed Ruff/format but correctly failed mypy with twelve missing-attribute contract errors before pytest. A later temporary test-only workflow `b3cd139` deliberately runs the focused pytest before mypy to obtain a behavioral RED; its result must be recorded separately. No intentional failure of mypy/format is presented as pytest RED.
