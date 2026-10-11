# R96-14 — research → plan → RED/TDD → real corpus → adversarial review

1. **Reconcile:** issue #96 OPEN, main after merged #115, no overlapping PR; inspect `lxx_resolver._placements_conflict`, `_mapping_kind`, existing real parsed transposition test, reference audit and pinned 46-file counts.
2. **Research/design:** preserve the two prior strict non-overlap partitions, model exactly the production resolver's *identity-equal* alignment/carrier exception as a third read-only classification, not a generic overlap allowance or verified CATSS target.
3. **RED:** commit parametrized helper and parser-level failing tests for one eligible pair, partial-overlap nonexception, unmarked pair conflict, three-task conflict, ambiguity and budget. Capture intended pytest failure (not format/lint errors).
4. **GREEN:** derive role map using real parser annotations, pass it into lazy DFS only for `role_context` classification, keep other solver invocations and existing summaries untouched. Add a compact role-count output and CI partition invariants.
5. **Pinned real data:** compare 46 CATSS sources and pinned LXX, all old 6,218 and 671-category counters, count role-eligible and classification-changing scopes. Preserve full TF build/readback, Python 3.11/3.12/3.13, Ruff/format/mypy and release smoke.
6. **Adversarial exact-head review:** independently challenge role provenance, transposition misuse, partial/identical overlap, duplicate alignments, unexpected changes to strict counts, solver cutoff and omissions of implicit contenders. Post precise GitHub review and re-review after any changes.
7. **Merge:** only reviewed exact head + all five CI jobs success, preserve #96 OPEN, no corpus redistribution or speculative semantic target edges.
