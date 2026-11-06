# Plan — issue #58 MT-column `--` exact repairs

Research basis: [issue-58-mt-double-dash-repairs.md](../research/issue-58-mt-double-dash-repairs.md).

## Gate 1 — RED

Add parser regressions for all four researched rows requiring:

- raw source/provenance unchanged;
- stable source-derived alignment id;
- semantic `mt_col_a` starts with `--+`;
- original column-B payload retained;
- `is_lxx_plus=True`;
- exactly one typed `source_repair` annotation with original and corrected MT cells.

Add a lookalike regression proving the same `--` shape at another verse is not
normalized.

Add a complete-snapshot assertion that exactly four current alignments carry these
specific source repairs and no unrepaired Hebrew-empty/nonempty-Greek first-token
`--` row remains.

## Gate 2 — implementation

Extend `_KNOWN_SOURCE_ROW_REPAIRS` only. Do not alter:

- the generic plus/minus marker sets;
- technique-v1 rules;
- column-B parsing;
- alignment identity construction.

## Gate 3 — GREEN

Run focused parser/technique tests, then exact-head Python 3.11/3.12/3.13, ruff,
formatting, mypy, release smoke and complete-CATSS audit.

## Gate 4 — independent adversarial review

Review the exact final green head for:

- accidental generalization of bare `--`;
- wrong source/header identity;
- mutation of raw provenance or alignment IDs;
- dropped column-B reconstruction;
- false LXX-plus on lookalikes;
- mismatch between repair annotation and corrected semantic cell.

Merge only if the exact final head is green and review has no blockers.

## Downstream acceptance

Merge main into canonical PR #47. Its full materializer must pass these four rows and
advance to the next independently researched residual class.
