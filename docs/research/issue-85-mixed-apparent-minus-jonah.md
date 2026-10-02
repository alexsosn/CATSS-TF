# Research — issue #85 mixed apparent-MT-minus row at Jonah 4:3

## Exact source state

Current CATSS `32.Jonah.par`, Jonah 4:3 contains one logical row:

`--- YHWH\tDE/SPOTA KU/RIE`

Parser state on the current corpus is:

- one MT lexical element: `YHWH`;
- two Greek lexical elements: `DE/SPOTA`, `KU/RIE`;
- one leading MT-side `apparent_minus` annotation from `---`;
- no transposition evidence.

The physical source and complete-snapshot audit show that this is not a continuation,
column-splitting, or export-orphan defect.

## CATSS/formal-alignment evidence

CATSS is a formal element alignment. A marker occupies the formal counterpart position
when one side has no lexical counterpart. The prior CATSS parser recognizes the leading
`---` independently from the following lexical `YHWH`; it does not consume
`YHWH` as part of the marker.

Therefore this row encodes two element correspondences inside one physical alignment:

1. an apparent MT-minus element corresponding to Greek `DE/SPOTA`;
2. lexical MT `YHWH` corresponding to Greek `KU/RIE`.

Treating the entire row as a pure apparent-MT-minus alignment is wrong because lexical
MT material remains. Treating it as an ordinary one-to-two lexical alignment loses the
explicit apparent-minus evidence.

## Independent textual evidence

The actual verse has MT יהוה against Greek δέσποτα κύριε. Published discussion of the
divine-name rendering at Jonah 4:3 explicitly notes that MT has only the tetragram while
the Greek has δέσποτα κύριε and that a fuller Hebrew Vorlage would have to be
reconstructed to account for both Greek titles.

This supports CATSS's formal split: `KU/RIE` is the lexical rendering of `YHWH`,
while `DE/SPOTA` is the Greek element with no MT counterpart represented by the
leading `---`.

## Canonical-model implication

The standalone canonical corpus already creates independent `mt_element`,
`lxx_element`, and `annotation` nodes. Alignment-wide boolean technique flags are
therefore too coarse to preserve the scope of this marker.

The preferred representation is:

- retain the ordinary alignment slot and both Greek element nodes;
- retain the `apparent_minus` annotation node;
- add explicit element-level scope from that annotation to the first Greek element;
- retain the lexical `YHWH` / `KU/RIE` correspondence as the non-minus element pair.

No synthetic lexical node should be invented for the missing MT element.

## Parent-grounding gate

Before implementation, verify against the pinned
`CenterBLC/LXX@f32a98eddf7eb239aa73ab863d70381e416d5076` parent that Jonah 4:3 contains
the exact adjacent sequence `δέσποτα κύριε`, and that production normalization maps:

- `DE/SPOTA` uniquely to the δέσποτα node;
- `KU/RIE` uniquely to the following κύριε node.

This research ticket must not weaken the pure apparent-minus cardinality invariant for
the 61 homogeneous rows.
