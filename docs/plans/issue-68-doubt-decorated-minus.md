# Plan — issue #68 doubt-decorated Greek `---?`

Research basis: [issue-68-doubt-decorated-minus.md](../research/issue-68-doubt-decorated-minus.md).

## Gate 1 — RED tests

Before production changes:

1. parse `HB\t---?` as `is_lxx_minus=True`;
2. retain exactly the normal independent `doubt` annotation;
3. preserve raw `---?`, physical provenance and source-derived alignment id;
4. technique-v1 derives `omission_vs_mt=True` and not addition;
5. decorated contextual reference (Ps shape) remains queryable;
6. ordinary `---` behavior is unchanged;
7. unrelated tokens ending in `?` do not become LXX-minus.

## Gate 2 — implementation

Introduce the smallest explicit marker predicate needed for Greek-side minus detection:
accept the documented base minus markers plus exact `---?`. Do not perform generic
punctuation stripping and do not alter lexical token/cardinality rules.

## Gate 3 — snapshot guard

Across all 46 files require exactly seven first-token `---?` rows, all:
- MT lexical count > 0;
- Greek lexical count == 0;
- `is_lxx_minus=True`;
- independent `doubt` annotation present;
- technique omission true.

## Gate 4 — exact-head GREEN + independent review

Require Python 3.11/3.12/3.13, ruff, format, mypy, release smoke and complete CATSS
audit on the exact head. Review independently for over-broad punctuation stripping,
double-counted doubt semantics, raw-provenance drift, and regression of plain minus
markers.
