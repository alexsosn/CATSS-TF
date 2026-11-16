# #160 — research → RED → implementation → review

1. Read `docs/research/issue-160-reference-scope.md` and lock the exact native CATSS source-reference contract before implementation.
2. Add `tests/test_query_reference_scope.py` **first**. On a tiny synthetic two-document native TF corpus, compare four public searches with independently scanned alignment slots for source/book/chapter/verse and MT-A vs raw-B evidence. Exercise false positives, document-identity mismatches, invalid tuple shape, boolean/floating chapter/verse and negative values.
3. Commit test-only branch state and observe **RED** from exact-head CI (unexpected `reference` keyword arguments).
4. Implement a small shared validation/matching predicate in `src/catss_tf/query.py`, threaded through the four existing APIs. Preserve default results and their separate query semantics. No new schema, parser, variant inference, index, or dependency.
5. Document one exact reference-scoped researcher example in `docs/researcher-cookbook.md` and status/limits in `docs/libronix-coverage.md`.
6. Verify exact-head Python CI, release smoke, full 46-file standalone canonical/Agora and Context-Fabric acceptance. Independently re-read final implementation, compare against native feature semantics and deliberately try bad inputs and cross-source verse coincidences before merge.
7. Update #160 with evidence and close only after merge; #126, #149, #151 and pinned-parent #41 remain independently gated.
