# Research — issue #40 canonical CATSS Text-Fabric corpus

## Scope

Issue #40 asks CATSS-TF to materialize a standalone canonical `catss` Text-Fabric
corpus from the same `ParallelDocument` / `AlignmentRecord` IR that feeds the BHSA
and LXX projection modules.

This research is grounded in the current parser, validation layer, projection schema,
and Text-Fabric warp contract. It does not change CATSS acquisition or upstream
licensing.

## Existing invariants

The parser already gives every logical alignment row a deterministic
`catss_alignment_id`, preserves its physical source lines and raw MT/LXX cells, and
normalizes:

- MT readings, including Ketiv/Qere and doubt/Aramaic state;
- LXX lexical elements;
- Greek-side reference overrides;
- plus/minus and transposition state;
- column-B retroversion kind;
- typed annotations with source side, semantic family, contextual flag, payload, and
  raw siglum.

`validate_documents()` already proves source-line ownership, deterministic identity,
duplicate identity rejection, source-book consistency, and explicit handling of
unknown notation/parser diagnostics. The canonical corpus should consume these facts,
not parse CATSS independently.

Text-Fabric requires one slot type and requires every non-slot node in `oslots` to be
anchored to at least one slot. A standalone corpus can therefore choose a slot model
that is independent of BHSA/LXX word nodes.

Relevant implementation/specification references:

- `src/catss_tf/parser.py`
- `src/catss_tf/validation.py`
- `src/catss_tf/tf_schema.py`
- Text-Fabric warp reader/writer:
  https://github.com/annotation/text-fabric/blob/master/tf/core/data.py

## R40-1 — one CATSS alignment record is one TF slot

**Decision:** the standalone corpus uses slot type `alignment`. Every
`AlignmentRecord` becomes exactly one slot node.

Reasons:

1. An alignment group is the smallest entity that always exists in CATSS. Either lexical
   side may be empty.
2. A lexical-element slot model cannot represent a group with no element on one side
   without inventing a surrogate lexical item; a completely non-lexical service row
   would have no slot at all.
3. Alignment slots preserve source order naturally and make arbitrary numbers of
   Hebrew-empty or Greek-empty groups independently queryable.
4. The stable `catss_alignment_id` becomes a feature on the slot itself and is the
   canonical join key used by `catss-bhsa` and `catss-lxx`.

The slot is the alignment entity; there is no redundant second `alignment` node.

## R40-2 — lexical and provenance details are child nodes, not packed strings

Non-slot node types attached to one alignment slot:

- `mt_element`: one per parsed `MtReading`, with 1-based index, primary text,
  optional Ketiv/Qere, doubt and Aramaic flags;
- `lxx_element`: one per parsed Greek lexical element, with 1-based index and text;
- `annotation`: one per typed source annotation, preserving side, kind, family,
  contextual flag, payload and raw siglum;
- `reference`: one per structured Greek reference override;
- `source_line`: one per physical source line owned by the alignment.

This keeps independently meaningful repeated facts as independently queryable nodes.
No JSON, comma-separated node lists, numbered lanes, or delimiter-packed pseudo-records
are required for normal queries.

The alignment slot itself carries scalar group-level facts: source, book/chapter/verse,
raw cells, counts, plus/minus, transposition flags, retroversion kind and derived
technique-v1 state.

## R40-3 — document/chapter/verse are structural nodes

The corpus also contains `document`, `chapter`, and `verse` nodes, each spanning
the alignment slots in its scope.

The Text-Fabric section contract is:

- section types: `document,chapter,verse`;
- section features: `catss_source,chapter,verse`.

Using CATSS source filename as the top-level section identity keeps Joshua A/B and
Daniel OG/Theodotion distinct even when their normalized book/chapter/verse labels
overlap. A separate `book` feature records the CATSS header book.

## R40-4 — relational semantics are edges only when the IR has an actual target

A structured `GreekReference` is represented as a `reference` node. If its
chapter/verse target resolves unambiguously to a verse node in the same CATSS source,
a valueless edge `catss_reference_target` connects the reference node to that verse.

If the target is absent or not uniquely resolvable, the raw/structured reference node
is preserved without fabricating an edge.

Current local/remote transposition flags do not identify a target alignment in the
parser IR. The canonical corpus must not invent such a target. A future parser change
may add a transposition edge when CATSS semantics supply a deterministic target.

## R40-5 — canonical schema version is independent of projection schema v1

Projection schema v1 is a weft-only, parent-node contract and remains unchanged.

The standalone corpus introduces `CANONICAL_SCHEMA_VERSION = "1"`. Its feature
metadata uses `@catssCanonicalSchema=1` and `@catssArtifact=catss`.

Changing the canonical node model later requires an explicit canonical schema bump; it
must not silently reinterpret projection feature schema v1.

## R40-6 — numbering and output are deterministic

Slot numbering follows deterministic source/document order, then verse order, then
alignment order. Source order is the configured `CATSS_PARALLEL_FILENAMES` order.

All non-slot nodes are allocated after the slot range and every such node has a non-empty
`oslots` mapping. Structural and child-node creation order is deterministic.

The writer emits explicit Text-Fabric node/edge rows rather than depending on
Text-Fabric at runtime. Text-Fabric remains an optional integration dependency.

## R40-7 — fail closed before publication

Canonical materialization:

1. snapshots each input file once and parses those exact bytes;
2. rejects source names outside the configured CATSS parallel contract;
3. runs `validate_documents()`;
4. derives technique-v1 state for every alignment;
5. compiles the canonical graph in memory;
6. runs a preservation audit over every supplied document;
7. writes into a temporary directory and atomically publishes only after all checks pass.

Allowed validation codes remain explicit caller input. Unknown notation is never
silently accepted.

## R40-8 — preservation audit is an executable invariant

The canonical build audit checks, for all supplied documents:

- one alignment slot per IR `AlignmentRecord`;
- exact one-to-one `catss_alignment_id` preservation;
- one MT element node per `MtReading`;
- one LXX element node per `lxx_tokens` item;
- one annotation/reference/source-line node per IR item;
- no lexical node on an actually empty side;
- all non-slot nodes anchored to at least one alignment slot;
- source fingerprints and provenance rows agree with the snapshotted input.

This audit runs as part of every canonical materialization. On a complete 46-file user
snapshot it is therefore a corpus-wide preservation audit; tests exercise the same
logic on synthetic/minimal inputs.

## R40-9 — distribution boundary does not change

CATSS-TF continues to distribute software only. The generated standalone `catss`
corpus is a local derivative of user-acquired CATSS data and is not committed or
attached to releases.

Agora should eventually expose three separate materializers:

- `catss-corpus`;
- `catss-bhsa-module`;
- `catss-lxx-module`.

The standalone corpus requires no parent TF resource. Projection modules keep exact
parent validation and join to the canonical corpus through `catss_alignment_id`.


## R40-10 — Text-Fabric node types are contiguous intervals

A real Text-Fabric load exposed a warp-format invariant that the in-memory preservation
audit did not previously encode. `otype` is stored by Text-Fabric in an optimized
representation where each node type has one contiguous node-id interval; the API's
`F.otype.s(type)` uses that interval. It is therefore insufficient for
`node_types[node] == type` to be locally correct if nodes of the same type are
interleaved with other types.

The initial canonical compiler allocated detail nodes per alignment:

`mt_element -> lxx_element -> annotation -> reference -> source_line`

and repeated that sequence for every alignment. The resulting `otype.tf` loaded, but
Text-Fabric treated the full min/max interval as belonging to a type, so
`F.otype.s("mt_element")` returned nodes of intervening types as well.

The canonical graph must allocate every non-slot type in one global block. The
preservation audit must reject any graph where a node type occurs in more than one
interval. The executable TF-load regression remains the user-visible acceptance test.
