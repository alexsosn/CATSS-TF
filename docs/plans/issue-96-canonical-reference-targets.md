# Plan — #96 fail-closed canonical scalar-reference edges

Research: [issue-96-canonical-reference-targets.md](../research/issue-96-canonical-reference-targets.md).
Scope: **only PR #47's canonical writer**, not the BHSA/LXX projection
reference resolvers.

## RED

1. Reproduce on the existing Genesis synthetic case: `[2]` is preserved as
   a structured `reference` node, but must have no speculative
   `catss_reference_target` edge to MT-derived `Gen 1:2`.
2. Reproduce with a Joshua B same-numeric-label reference `[9:2a]`
   and `JoshB 9:2` header. Require lossless Greek chapter/verse/subverse,
   no inferred target edge, no invented subverse/Greek lexical nodes.
3. An absent target such as `[99]` remains queryable without an edge.
4. Prove initial failure on exact preimplementation branch head via
   `pytest tests/test_canonical_materializer.py` in CI.

## GREEN

Remove only the ungrounded `catss_reference_target` inference from
the standalone materializer. Retain all structural verse nodes and scalar
reference nodes and counts. Update researcher documentation to state the
absence of verified target edges. No changes to projections or parent warp.

## Full gates

Python 3.11/3.12/3.13, ruff, mypy, release-smoke, 46-file materialization,
full Text-Fabric load and exact JoshB range preservation. Assert absence
of the unsupported edge in the full corpus. Compare derived and unclassified
technique counts with prior run (349,670 alignments; 4,306 unclassified).

Obtain logically independent exact-head adversarial review. Revisit #96
separately for full real-source 6,218-reference destination audit and any
future grounded relation.
