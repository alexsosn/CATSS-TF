# Plan — issue #85 mixed apparent-minus scope at Jonah 4:3

Research basis: [issue-85-mixed-apparent-minus-jonah.md](../research/issue-85-mixed-apparent-minus-jonah.md).

## Research gate still required before RED

Verify against the exact configured parent `CenterBLC/LXX@f32a98eddf7eb239aa73ab863d70381e416d5076`:

1. `Jonah 4:3` contains adjacent parent words corresponding uniquely to CATSS `DE/SPOTA KU/RIE`;
2. `DE/SPOTA` maps to the first of those nodes and `KU/RIE` to the second;
3. record the current production resolver's behavior, including its mapping gap when
   the parent contains a unique matching pair.

**Research result:** the parent uniquely supplies nodes 495520–495521, but the
current resolver produces no mappings for this alignment. The implementation
must begin with RED tests for this mapping gap, not assume it is already solved.

## Intended IR design if parent grounding succeeds

Extend `Annotation` with optional element-target scope rather than weakening the alignment-wide apparent-minus rule. The scope must be explicit and index-based, e.g. a target side plus 1-based element index.

For the exact Jonah 4:3 mixed row, the leading MT-side apparent-minus annotation is expected to target Greek element 1 (`DE/SPOTA`).

Pure apparent-minus rows remain alignment-level/empty-MT events and retain their existing behavior.

## Canonical TF representation

The canonical corpus already has separate `annotation` and `lxx_element` nodes.

Add a query-native edge from a scoped annotation node to its target lexical element, with no JSON/blob encoding. The edge must be absent for annotations without a deterministic target.

## Projection behavior

For a scoped mixed apparent-minus annotation:

- LXX projection exposes `catss_sem_apparent_minus` and `catss_sem_apparent_minus_mt_a` only on the targeted Greek word membership;
- it must not smear the semantic onto other Greek words in the alignment;
- BHSA projection must not attach that Greek-targeted missing-MT semantic to the surviving lexical `YHWH` word.

The lexical `YHWH -> KU/RIE` mapping remains ordinary.

## Technique-v1

Introduce explicit scoped-mixed evidence to admit the `(1,2)` row while preserving:

- cardinality `one_many`;
- token balance `lxx_more`;
- `addition_vs_mt=False`;
- `omission_vs_mt=False`.

The existing pure apparent-minus validation remains strict: an unscoped `apparent_mt_minus=True` still requires zero MT lexical material.

## RED-first test gates

After parent grounding, commit tests before implementation for:

1. exact parser scope on Jonah 4:3;
2. no target scope on ordinary pure apparent-minus rows;
3. technique accepts only the scoped mixed form and rejects an unscoped `(1,2)` apparent-minus contradiction;
4. canonical annotation→`lxx_element[1]` target edge;
5. LXX projection semantic present on `DE/SPOTA` parent node only, absent on `KU/RIE`;
6. BHSA projection does not smear apparent-minus onto `YHWH`;
7. parent-grounded exact mapping remains unique;
8. complete snapshot contains exactly the researched mixed scoped form unless new cases are explicitly classified.

## Final gate

Run Python 3.11/3.12/3.13, ruff, format, mypy, release smoke, full 46-file audit, canonical materialization, both projections, and pinned-parent Jonah verification on the exact final SHA.

Then perform a logically independent adversarial review grounded in the raw Jonah row, parent nodes, parser IR, canonical edge, both projection modules and technique state.
