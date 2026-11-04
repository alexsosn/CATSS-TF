# #144 — Source-exact multi-form co-membership in canonical TF

## Research evidence and user workflow

`docs/libronix-coverage.md` explicitly leaves same-alignment article+noun group search to ad hoc researcher code. The public `find_aligned_groups(api, mt_form, lxx_form)` (merged #131) checks one MT-A and one LXX spelling by a single pass over `api.F.catss_text.items()`, discriminates `mt_element` from `lxx_element` through `api.F.otype.v()`, converts each matching lexical node to the containing alignment slot with `L.d(..., otype="alignment")` and intersects. Its `CanonicalAlignedGroup` already has stable source ID, source book/chapter/verse and ordered lexical members.

This is grounded in the actual writer and loaded native-TF tests, not in a new inferred alignment relation. The canonical slot is an editorial *alignment group*, potentially many-to-many; the presence of two Greek elements on the same alignment does **not** imply adjacency, running-text phrase order, a syntactic dependency or one-to-one Hebrew lexical counterparts. MT-B tentative retroversion is **not** an MT-A lexical element. Hebrew and Greek surface spellings must be matched on their own sides even if identical.

## Plan

1. Add `find_groups_with_all_forms(api, *, mt_forms=(), lxx_forms=(), source=None)` using the same existing `CanonicalAlignedGroup` output. A set of **distinct** exact forms on each side means an AND condition within one alignment slot; duplicate requested spellings carry no token-count requirement. At least one source form is required. Fail explicitly for accidentally bare strings, blank/non-string values or a wrong warp.
2. Implement a single scan over `F.catss_text.items()` populating per-(element-side, exact-form) matching alignment-slot sets; intersect, sort slots, filter exact source filename and emit ordered groups. Empty intersections must not join adjacent alignments, and no secondary index/data/schema is introduced. Query time remains linear in populated lexical features and matching descendants.
3. RED-first tests: existing tiny native-TF `Genesis/JoshB` fixture, an independently written exhaustive `otype.s('alignment')` oracle, Greek-only article+noun, MT-only, cross-side, same-verse/different-row, source differences, repeated-query-form semantics, invalid arguments and wrong-warp rejection.
4. Add source-safe, full 46-file TF acceptance: choose an actual alignment with two distinct Greek lexical elements and an MT lexical element; derive its exact forms **in memory** and compare new query membership against a separate full alignment-slot scan (with source bound), printing only aggregate counts. Do not hard-code or log copyrighted lexical data.
5. Document a researcher-facing example and explicit Libronix/phrase/MT-B limitations. Run Python 3.11–3.13, release, Context-Fabric and real 46-file canonical+Agora CI on final head; separate adversarial review before merge.

## Security, provenance and performance

No upstream data or generated corpus files in git, no parent node cross-warp access, no normalization, no inferred manuscript links, and no semantic alteration of canonical materialization. The new query is read-only and does not persist caches. Issue #126 remains open for wider Libronix parity.
