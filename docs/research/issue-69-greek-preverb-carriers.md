# Research — issue #69 zero-token Greek-preverb carriers

## Trigger

Issue #64 isolated three MT-nonempty / Greek-empty residual alignments carrying the
already-typed Greek-preverb notation:

- Prov 28:18: `B/)XT -> {p} ---`;
- Sir 5:2: `)XRY 3 -> {p} ---`;
- Sir 23:17: `B/W 3 -> {p}`.

They currently fail technique-v1 because Greek lexical cardinality is zero but no
recognized LXX-minus or transposition evidence is present.

## Documentary/prior-parser evidence

The open CATSS parser reconstruction in
`codykingham/CATSS_parsers@dd89b38981bd3f199f7ac3f8b2b026ccb19b0a35`
defines `{p}` / `{p}+` as **“Greek preverb representing Hebrew preposition”**.

CATSS-TF already preserves this as the typed `greek_preverb` annotation. The notation
therefore carries positive translational/morphological evidence even when no standalone
Greek lexical token remains in the alignment cell.

This evidence is not, by itself, evidence of omission. In particular, a bare `{p}`
carrier must not become LXX-minus merely because its lexical Greek count is zero.

## Research questions

1. What is the complete current `{p}` population across all 46 CATSS files?
2. Which Greek lexical cardinalities and surface shapes occur?
3. Are `{p} ---` rows compositionally “preverb rendering + LXX-minus”, or does the
   following `---` belong to another scope?
4. Is bare `{p}` a legitimate zero-token semantic carrier that technique-v1 should
   admit without addition/omission?
5. Do the three residuals form one model or two distinct classes?
6. Can the behavior be recognized by explicit typed evidence rather than a generic
   zero-Greek exception?

## Snapshot research gate

A temporary complete-snapshot audit will enumerate every alignment with a
`greek_preverb` annotation, including source/reference, raw MT/LXX cells, lexical
cardinality, first Greek token, annotations, and neighboring alignments. It will also
summarize surface-shape and cardinality distributions.

No production semantics change during this gate.


## Complete-snapshot result

The current 46-file snapshot contains **290** alignments with a typed Greek-side
`greek_preverb` annotation.

Cardinality distribution is overwhelmingly ordinary lexical alignment. Only three
rows have lexical MT material with zero standalone Greek lexical tokens:

- Prov 28:18: `B/)XT -> {p} ---`, cardinality `(1,0)`;
- Sir 5:2: `)XRY 3 -> {p} ---`, cardinality `(2,0)`;
- Sir 23:17: `B/W 3 -> {p}`, cardinality `(2,0)`.

No other current Greek-preverb row has this zero-Greek shape.

The wider population is important evidence against treating `{p}` as an omission
marker: the same typed notation occurs routinely alongside one or more Greek lexical
tokens. Its meaning is the rendering relation supplied by the preverb annotation, not
absence of translation.

## Interpretation of `{p} ---`

The prior CATSS parser describes `{p}` / `{p}+` as “Greek preverb representing
Hebrew preposition”. That is positive translation evidence for the Hebrew material.

For the two `{p} ---` rows, the trailing dashes therefore cannot safely be promoted
to an alignment-level omission claim for the whole Hebrew carrier: doing so would say
that the Hebrew material is untranslated while the same source row explicitly says it
is represented by a Greek preverb. The conservative model is:

- `greek_preverb` supplies explicit non-lexical rendering evidence;
- zero standalone Greek lexical tokens remain a descriptive cardinality fact;
- neither `addition_vs_mt` nor `omission_vs_mt` is inferred.

This also covers the bare `{p}` Sirach row without inventing a separate exception.

## Decision R69-1 — typed carrier evidence admits zero-Greek cardinality

Technique-v1 may admit an MT-nonempty / Greek-empty alignment without LXX-minus or
transposition evidence when the alignment carries a typed Greek-side
`greek_preverb` annotation.

This is a closed semantic exception based on explicit CATSS evidence, not a generic
zero-Greek relaxation.

## Decision R69-2 — no omission inference

For such carriers:

- preserve `cardinality_mt_lxx` as `one_zero` or `many_zero`;
- preserve `token_balance_mt_lxx=not_applicable`;
- require `addition_vs_mt=False`;
- require `omission_vs_mt=False`;
- do not set `is_lxx_minus` from the presence of a later `---` token.

The existing query-native `greek_preverb` semantic feature remains the positive
evidence researchers use to distinguish these rows from true omissions.

## Decision R69-3 — closed current population

A permanent complete-snapshot guard should require exactly the three rows above to be
MT-nonempty / Greek-empty Greek-preverb carriers, all accepted by technique-v1 with no
addition/omission semantics. Any new member of the class must be surfaced by the guard.
