# Research — issue #82 missing Greek lexical counterpart at 1 Esdras 6:4

## Trigger

The #70 contextual-reference audit isolated one remaining MT-nonempty / Greek-empty row
that is **not** an omission:

- source: `17.1Esdras.par`;
- reference: 1 Esdras 6:4;
- MT raw: `L/KM`;
- Greek raw: `[e5.3]`;
- current lexical cardinality: `(1,0)`.

The CATSS contextual reference points into the parallel Greek tradition, but the row
currently contains no Greek lexical surface for the resolver to map.

## Prior CATSS evidence

Cody Kingham's CATSS parser documentation gives the explicit alignment example

`L/KM    U(MI=N`

while discussing non-adjacent stylistic transposition. This establishes `U(MI=N` as
a CATSS Beta Code surface used for the Greek counterpart of Hebrew `L/KM`.

The #70 source audit also found that the referenced 1 Esdras text contains the second
person plural dative pronoun in this clause. Therefore this row should not be modeled
as an LXX-minus or as a neutral zero-token carrier.

## Parent-grounding requirement

CATSS-TF projects onto the pinned parent:

- repository: `CenterBLC/LXX`;
- version: `1935`;
- release: `v1.0.1`;
- commit: `f32a98eddf7eb239aa73ab863d70381e416d5076`.

Before changing production semantics, a temporary CI research gate must clone exactly
that commit, load `tf/1935` through Text-Fabric, inspect `1Esdr 6:4`, and prove:

1. `U(MI=N` normalizes to exactly one parent word in that verse;
2. the exact parent word/node can be reported;
3. a synthetic CATSS row `L/KM -> U(MI=N [e5.3]` resolves through the production
   `TextFabricLxxProvider` / resolver to that node;
4. the resolver does not need to fabricate an anchor or parent node.

## Repair hypothesis

If the parent-grounding gate succeeds, the narrow candidate repair is the exact identity

`("17.1Esdras.par", 6, 4, "L/KM", "[e5.3]")`

with semantic Greek cell

`U(MI=N [e5.3]`.

Raw source bytes, `lxx_raw == "[e5.3]"`, physical source lines, contextual-reference
annotation and source-derived alignment id must remain unchanged.

No generic contextual-reference-only carrier rule and no generic lexical restoration
from Hebrew morphology is permitted.
