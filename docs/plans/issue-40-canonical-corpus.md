# Plan — issue #40 canonical CATSS Text-Fabric corpus

Research basis: [issue-40-canonical-corpus.md](../research/issue-40-canonical-corpus.md).

## Gate 1 — RED tests

Add focused tests before implementation for:

1. standalone TF warp contains `alignment` slots and loads without BHSA/LXX;
2. one slot is emitted for every alignment, including multiple independent LXX-plus and
   LXX-minus groups in the same verse;
3. MT/LXX element nodes preserve element counts/order and empty sides create no fake
   lexical node;
4. annotation, Greek-reference, and physical-source-line nodes preserve repeated facts
   independently;
5. resolvable structured Greek references create `catss_reference_target` edges and
   unresolved references do not get fabricated targets;
6. validation failure and unknown source names leave no output directory;
7. deterministic materialization produces byte-identical output for the same source;
8. canonical alignment ids match the parser identities used by projection sidecars;
9. public package API exports the canonical materializer;
10. every node type occupies exactly one contiguous node-id interval after TF load, so
    `F.otype.s(type)` returns exactly the nodes assigned that type.

The RED commit must contain no production implementation.

## Gate 2 — implementation

Introduce a small canonical-corpus module with:

- `CANONICAL_SCHEMA_VERSION = "1"`;
- graph dataclasses/compiler separated from filesystem publication;
- explicit TF warp/node/edge writers;
- type-block node allocation compatible with Text-Fabric's optimized `otype` interval model;
- an in-memory audit that rejects split/interleaved node-type intervals;
- atomic `materialize_corpus(...)`;
- preservation audit executed before publication;
- canonical sidecars for sources, alignments, technique, annotations, source lines and
  diagnostics;
- package-root API export.

Reuse parser, validation and technique code. Do not add a second parser or reuse
BHSA/LXX resolver logic.

## Gate 3 — tests and static checks

Run repository CI on the exact PR head:

- pytest on Python 3.11/3.12/3.13;
- ruff;
- mypy;
- release smoke.

The focused canonical test must load the generated warp with Text-Fabric and execute at
least one graph/search query.

## Gate 4 — independent adversarial review

Review the exact green head from scratch, explicitly trying to break:

- empty-side and zero-lexeme alignment identity;
- duplicate/lost alignments;
- slot/non-slot numbering and `oslots` completeness;
- repeated annotations/source lines;
- reference-edge target ambiguity;
- alternate traditions sharing references;
- accidental cross-warp node ids;
- delimiter-packed structures or fixed-width lane leakage;
- atomic publication on failures;
- divergence of canonical and projection `catss_alignment_id`.

Any substantive finding returns to RED-test → implementation → full-test. Re-review the
new exact head before merge.

## Gate 5 — merge and follow-up

Merge only after exact-head green CI and no blocking adversarial findings. Close #40
through the PR. Do not fold #44, #45, or Agora #16 into this PR; continue those as
independent tickets after #40.
