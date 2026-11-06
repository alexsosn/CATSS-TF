# Plan — issue #48 Genesis 6:19 known CATSS source repair

Research basis: [issue-48-genesis-source-repair.md](../research/issue-48-genesis-source-repair.md).

## Gate 1 — RED tests

Before production changes, add tests proving that the current parser:

1. fails to recognize the exact current Genesis anomaly as LXX-plus;
2. must preserve original `mt_raw`, physical source line and stable alignment identity;
3. must expose normalized column A/B state from the documented corrected semantic form;
4. must attach an explicit `source_repair` annotation;
5. must not repair a lookalike row in another source or a different Genesis row.

Add a projection-schema regression requiring `catss_sem_source_repair` to be a valid
query-native feature.

## Gate 2 — implementation

Implement the smallest shared-parser repair:

- exact source/cell match before semantic parsing;
- preserve original raw cells and physical lines separately from semantic cells;
- derive `is_lxx_plus`, counts and retroversion state from the corrected semantic cells;
- append one typed provenance annotation;
- add `source_repair` to the projection semantic schema.

Do not change `derive_technique_state()`.

## Gate 3 — GREEN

Run focused parser/schema/materializer tests, then the full Python 3.11/3.12/3.13 CI,
ruff, formatting, mypy and release smoke.

The real complete-CATSS audit in PR #47 is the downstream acceptance test: after this
fix lands on main and #47 is updated, Genesis 6:19 must no longer fail technique
derivation.

## Gate 4 — independent adversarial review

Review the exact final head from scratch and challenge:

- accidental broad matching of `--=`;
- mutation/loss of exact raw provenance;
- changed alignment IDs;
- silent normalization without queryable repair provenance;
- weakening of technique invariants;
- projection schema omissions;
- new false repairs in other sources.

Merge only after the final head is green and the independent review has no blocking
findings.
