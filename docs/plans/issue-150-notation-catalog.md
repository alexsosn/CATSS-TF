# #150 phase 1 — complete catalogue table and executable inspection

Research: [issue-150-notation-audit.md](../research/issue-150-notation-audit.md).

1. Add `tests/test_docs_notation_catalog.py` with **RED** test requiring `docs/notation-reference.md`. Parse a simple Markdown 7-column table, require exactly the 86 general and 16 Sirach source entries (keyed by **profile+literal**), plus a distinct `<sp…>` pattern row. Require each row's semantic kind, family, contextual indicator and `catss_sem_<kind>` to agree with `notation._GENERAL`/`_SIRACH` and `FEATURE_SPECS`. Reject duplicate profile+raw rows, missing collisions, wrong 16 `I:` count, and invented semantics. Preserve code provenance explicitly.
2. Observe the focused test failing because the documentation page has not been created. Execute first in Python GitHub CI before inherited lint for reliable behavioral evidence; restore standard CI afterward.
3. Add a public, readable `docs/notation-reference.md` containing exact table and an introduction for scholars: source glyph vs semantic kind vs canonical annotation vs parent feature, contextual payloads and two membership lanes. Include book-sensitive collision/16-inf-abs explanations and a safe synthetic, executable TF lookup snippet. Keep missing manuscript links honest.
4. Add `README.md` and `docs/special-notation.md` crosslinks to the dictionary; no new library APIs or schema.
5. Run pytest and full exact-head gates. Review adversarially *as a separate thought process*: check real source-code contracts, collisions, dubious semantic equivalence and actual CI oracle; merge only if green and exact head guarded.
6. Keep #150 open for complete **public canonical/overlay feature inventory** and #151 for full executable research cookbook and independent new-reader smoke. Both are needed before #149 closure.
