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


## Parent-grounding result

The research gate cloned the exact configured parent commit
`f32a98eddf7eb239aa73ab863d70381e416d5076`, loaded
`CenterBLC/LXX/tf/1935` with Text-Fabric 13.1, and inspected `1Esdr 6:4`.

The parent verse contains the following opening slots:

- node 294470: `τίνος`;
- node **294471: `ὑμῖν`**;
- node 294472: `συντάξαντος`.

Across the complete parent verse, CATSS `U(MI=N` normalizes to exactly one word:
node **294471**, `ὑμῖν`, `orig_order=294471`.

A synthetic row using the proposed semantic cell

`L/KM -> U(MI=N [e5.3]`

was then passed through the production `TextFabricLxxProvider` and
`resolve_lxx_document()` against that pinned parent. The result was:

- one supported document;
- one reference group;
- one resolved reference group;
- exactly one word mapping;
- mapped parent node 294471;
- no reference anchor;
- no mapping finding;
- no normalization or parent failure.

Thus the proposed lexical restoration is parent-real, unique, and already compatible
with the strict resolver. No fabricated node, anchor, fuzzy placement or resolver
exception is required.

## Decision R82-1 — exact lexical source repair

Repair only the exact identity

`("17.1Esdras.par", 6, 4, "L/KM", "[e5.3]")`

to semantic Greek

`U(MI=N [e5.3]`.

Do not infer Greek lexemes from Hebrew morphology or from contextual references
generically.

## Decision R82-2 — preserve source provenance

The repair must keep unchanged:

- original physical raw line;
- `mt_raw == "L/KM"`;
- `lxx_raw == "[e5.3]"`;
- source line(s);
- source-derived alignment id;
- typed Greek-side `contextual_reference` annotation with payload `e5.3`.

Emit the existing LXX-side `source_repair` provenance annotation whose payload is
`U(MI=N [e5.3]`.

## Decision R82-3 — ordinary lexical mapping after repair

After repair the canonical state is lexical-to-lexical:

- MT count 1;
- Greek count 1;
- Greek token `U(MI=N`;
- neither LXX-plus nor LXX-minus;
- technique cardinality `one_one`;
- neither addition nor omission.

The LXX projection must resolve the restored token to CenterBLC node 294471 through the
ordinary exact word-mapping path.


## Adversarial finding — existing transposition carrier

Independent review of the exact upstream verse found that the proposed bare lexical
repair would duplicate a Greek token that CATSS already carries elsewhere in the same
verse. The current source sequence is:

```
1Esdr 6:4
MN      TI/NOS [e5.3]
{...}   U(MI=N [e5.3]
&M {...+(M}    SUNTA/CANTOS [e5.3]
L/KM    [e5.3]
+(M     {...} [e5.3]
```

CATSS documentation classifies `{...}` as the placeholder/carrier side of a
non-adjacent stylistic transposition, paired with a `{..^...}` alignment annotation.
CATSS-TF's resolver deliberately permits one parent word to be shared only by the pair
`transposition_alignment` + `transposition_carrier`; two unmarked/exact mappings to
the same parent word are rejected.

Therefore the earlier candidate semantic cell `U(MI=N [e5.3]` is too weak: it makes
the repaired `L/KM` row an ordinary exact mapping and conflicts with the already
present carrier `{...} -> U(MI=N [e5.3]`.

## Revised decision R82-1 — restore the missing transposition alignment

Repair only the exact source identity

`("17.1Esdras.par", 6, 4, "L/KM", "[e5.3]")`

to semantic Greek

`{..^U(MI=N} [e5.3]`.

This preserves one lexical Greek surface `U(MI=N` for the repaired row while restoring
its CATSS relationship to the existing `{...}` carrier. The resolver must map both
records to the same pinned parent word, with mapping kinds
`transposition_alignment` and `transposition_carrier`, respectively.

The complete regression must include both real rows. An isolated synthetic
`L/KM -> U(MI=N` test is insufficient because it cannot detect the duplicate-placement
conflict.
