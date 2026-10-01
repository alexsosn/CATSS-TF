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
