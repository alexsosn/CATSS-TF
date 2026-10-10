# Plan R96-5 — parent span availability audit

Research: [issue-96-parent-span-audit.md](../research/issue-96-parent-span-audit.md).

## Research → RED

Commit deterministic tests on synthetic CATSS documents and a strict fake
`LxxVerseProvider`, before implementing the audit:
- `Gen 1:1` references `[2]` (exact parent Gen 1:2 exists) and `[99]`
  (missing): one present, one missing, not a verified textual mapping.
- `JoshB 9:2` with `[9:2a]`, provider offers only unlabeled Josh 9:2:
  explicit subverse is **missing**, never promoted to the parent verse.
- `Neh 1:1` with `[2]`, parent `2Esdr 11:2`: inherited source policy.
- `JoshA` and an unprofiled source are counted unsupported/unknown without
  making a provider call.
- A parent with a wrong release SHA and one that aliases the requested
  subverse to another returned span must fail closed.
Use an initial `NotImplementedError` stub to make the tests RED on CI;
do not treat format/type failures as TDD proof.

## GREEN

Implement read-only `audit_lxx_parent_span_availability(documents, provider)`
in `reference_audit.py`. Validate `provider.parent_probe` once with the
existing `validate_lxx_parent()`, enforce exact returned span identity, use
local cache keyed by pinned parent book/chapter/verse/subverse, and keep
deterministic integer counters; no node IDs or text in result. Input documents
are already parsed; no new CLI network paths.

## Full source and review gates

Extend the existing pinned Jonah-parent integration step **after** its
`TextFabricLxxProvider` is created. Audit all 46 already-downloaded CATSS
source files, require exactly 6,218 references and exhaustive disjoint
partition of present/missing/unsupported/unknown. Report actual counts and
explicit subverse-present/missing; compare against the source-only 424 suffixes.
Do not assert a guessed expected present count; ground it in the run first.

Run ruff, format, mypy, pytest on Python 3.11–3.13, release smoke, existing
46-file canonical round trip. Conduct a logically independent adversarial
review of all source/probe/reference-key paths and actual pinned results.
Merge the research milestone only when every check is green; leave #96 open.
