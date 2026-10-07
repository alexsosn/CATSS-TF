# Research plan — issue #86 isolated marker-only CATSS row

Research record: [issue-86-marker-only-1esdr.md](../research/issue-86-marker-only-1esdr.md).

## Gate 1 — documentary/source comparison

1. Inspect Tov 1986 and the 1991 CCAT notation guide specifically for
   `---`, `--+`, and column-wide `''`.
2. Confirm the exact physical source row in the current 46-file snapshot,
   including its verse boundary and preceding addition lines.
3. Compare current and older CATSS exports and prior parser transforms, if available.
4. Determine whether the marker-only line adds independent interpretable semantics
   or is an export/column-state artifact.
5. Record positive and negative evidence; do not infer semantics from cardinality.

## Gate 2 — decision

If a documented state is found, define its scope precisely and an explicit typed
IR/canonical TF contract. If evidence remains insufficient, retain the unresolved
row and preserve provenance, without modifying technique-v1.

## Gate 3 — conditional RED → implementation

Only after Gate 2 yields a defensible rule:

- add RED tests for exact source identity and negative lookalikes;
- implement the narrowest typed representation;
- audit all 46 source files to prove no unintended interpretation;
- run the exact-head CI and researcher-facing query test;
- perform a logically independent adversarial review before merging.

No production changes are authorized by this research-only plan.
