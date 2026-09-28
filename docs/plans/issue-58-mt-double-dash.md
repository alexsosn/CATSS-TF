# Plan — issue #58 MT-side double-dash apparent-minus variant

Research basis: [issue-58-mt-double-dash.md](../research/issue-58-mt-double-dash.md).

## Gate 1 — RED tests

Add focused tests before production changes for the composite legacy form:

1. parser: MT `--` + non-empty column B + non-empty Greek emits exactly one
   `Annotation(side="mt_a", kind="apparent_minus", raw="--")`;
2. parser: the Sirach `--\t---` zero/zero row does not emit MT apparent-minus;
3. technique-v1 accepts the target shape but keeps `addition_vs_mt=False` and
   `omission_vs_mt=False`;
4. BHSA projection uses the existing verse-level `apparent_mt_minus` anchor rather
   than fabricating a Hebrew word mapping;
5. LXX projection exposes the existing query-native
   `catss_sem_apparent_minus{,_mt_a}` features on Greek memberships;
6. cross-projection consistency accepts the same BHSA-anchor/LXX-word asymmetry;
7. complete-snapshot guard proves exactly four target `--` rows are typed and the
   Sirach zero/zero exception remains untyped/fail-closed.

The RED commit contains tests/guard changes only.

## Gate 2 — implementation

Reuse the existing `apparent_minus` semantic identity; do not add a synonym.

In parser construction, emit the semantic for first-token MT-column-A `--` only when
all of these are true:

- column B exists and is non-empty;
- MT lexical count is zero;
- Greek lexical count is positive.

Preserve annotation raw spelling `--`, source lines, raw lines and alignment id.
Do not set `is_lxx_plus`.

The existing technique, TF schema, BHSA/LXX projection and consistency logic should be
reused unchanged unless RED tests expose a real integration gap.

## Gate 3 — exact-head verification

Run on the exact implementation head:

- ruff check / format;
- mypy;
- pytest on Python 3.11/3.12/3.13;
- release smoke;
- complete 46-file notation audit;
- composite `--` population guard.

## Gate 4 — independent adversarial review

Review the exact green head independently, trying to falsify:

- marker-only overgeneralization;
- accidental classification of Sirach 1:19;
- collapse into LXX-plus/addition semantics;
- column-B loss or lexical fabrication;
- projection asymmetry drift;
- source provenance/alignment-id changes;
- regressions to ordinary Greek-side `--` LXX-minus handling.

Any blocker returns to RED → implementation → full exact-head test.
