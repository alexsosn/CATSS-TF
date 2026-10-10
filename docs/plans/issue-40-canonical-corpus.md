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

## Gate 1b — typed contextual range integration (#88 / #91)

After merging the independently green `issue-88-contextual-reference-ranges`
branch into this canonical branch, commit a RED regression before production edits
requiring a `06.JoshB.par`, JoshB 9:2 `[[9.2a-2f]]` row to become
one standalone `reference_range` node connected through `oslots` to the
original alignment slot. The node must preserve its exact raw spelling and all
six typed start/end values (chapter, verse, subverse); it must not become two
scalar `reference` nodes, fabricate six parent LXX subverse nodes, invent a
`catss_reference_target` edge when the source target verse is ambiguous, or
create Hebrew/Greek lexical elements from the structural carrier.

Preserve exact alignment ID, source-line provenance and typed annotation.
Assert the `reference_range` node type occupies a contiguous node interval,
summary counts, audit invariants, and idempotent deterministic bundle output.
Check a mixed source containing both scalar reference and typed range, so
reference interval allocation remains correct.

The complete 46-file upstream snapshot must contain exactly one
`[[9.2a-2f]]` typed range and one canonical `reference_range` node.
Keep the original LXX projection's missing-parent failure: pinned
CenterBLC/LXX 1935 has one unlabeled Josh 9:2 subverse, not six a–f nodes.

This is a canonical-only representation of CATSS's own asserted semantics,
not a change to the LXX parent node topology.

## Canonical preservation vs. optional technique classification — real corpus gate

The complete 46-file snapshot failed at `12.2Sam.par`, physical line 7070:
`=;W/KL` ↔ `KAI\\ PA=S` (source-derived alignment
`catss:12.2Sam.par:971b19685ad28e2c3558`). This row contains MT-B
retroversion material but **no MT-A lexical material**; the Greek side
has lexical material. The standalone corpus must preserve this witnessed
alignment even though `derive_alignment_technique` correctly refuses
to guess whether the Greek is an addition, minus or transposition.

RED: on a synthetic `2Sam 7:19\n=;W/KL\tKAI\\ PA=S\n` require
successful canonical materialization, one alignment slot, its raw provenance
and MT-B retroversion annotation, zero fabricated MT elements, Greek
elements intact, `catss_tt_status=unclassified` plus explicit reason,
and **no** `catss_tt_addition_vs_mt`, `catss_tt_omission_vs_mt`, or
other guessed technique facts. The technique TSV should contain only
successfully classified rows; explicit failed count in the canonical summary
and node feature must make incompleteness discoverable. Add a mixed
success/failure regression and byte-determinism assertion.

This is a separation-of-concerns fix, not a relaxation of the strict
`derive_technique_state` API. Unknown technique must not block lossless
canonical TF preservation, but must never be converted into false binary
values or silently disappear. All parser/validation failures still fail
closed before publishing. Complete CI must assert a nonzero and bounded
unclassified count and the real 2 Samuel witness; discover and report the
count rather than guessing it.

Research → RED commit → implementation → full real-data gates → independent review.

## Gate 1c — scoped Jonah annotation target from #85 / PR #90

Evidence: the exact 32.Jonah.par, Jonah 4:3 source row
`--- YHWH\tDE/SPOTA KU/RIE` and pinned LXX parent 495520–495521
are researched in #85 / PR #90. The marker is physically in MT column A,
but its *target* is the first Greek lexical element only. The `YHWH`
lexical MT element corresponds to Greek element 2. No such target can
be guessed from a generic (1,2) alignment.

RED-before-implementation: materialize the exact mixed Jonah row, assert
one `catss_annotation_target` edge from the `apparent_minus`
annotation node to the `lxx_element` node with `catss_index=1`
and text `DE/SPOTA`, never to Greek `KU/RIE` or an MT element;
assert query-native `catss_target_side=lxx` and
`catss_target_index=1` on the annotation node. A pure apparent-minus
marker has no target edge. The RED must fail on current #47 production
before the implementation.

After #85's typed `Annotation.target_side/target_index` merges to main,
build only edges for **explicit** scoped targets, not inferred count
ratios. Reject invalid/missing targets; audit same-alignment slot membership,
index and target type. Preserve global contiguous TF node-type intervals.
Complete 46-file audit must yield exactly one scoped Jonah annotation edge,
with no new slots and no fabricated Greek/MT nodes. Run final-head matrix,
pinned-parent smoke and logically independent adversarial review.
