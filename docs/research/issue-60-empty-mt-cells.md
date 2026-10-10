# Research — issue #60 two physically empty MT cells

## Current source-grounded baseline

Issue #53's complete 46-file scan isolated **exactly two** rows with an
*empty physical Hebrew column A*, no column-B reconstruction and nonempty
Greek lexical material, without a continuation diagnostic:

- `17.1Esdras.par`, 1 Esdr 4:25: empty MT cell against `GUNAI=KA`.
  This follows other explicit long Greek-plus material.
- `27.Sirach.par`, Sir 19:14: empty MT cell against `E)/LEGCON`.
  This precedes other rows marked with the explicit Hebrew-witness
  lacuna `[..]` siglum.

There is **no typed LXX-plus or manuscript-lacuna marker in the empty cell**.
Issue #52, now merged, deliberately admits Sirach witness lacuna only
when **the first token of MT column A is `[..]`**, with a typed MT-A
annotation. This physically empty Sirach row does not satisfy it. Source
shape is not sufficient to assign either translation-addition or
manuscript-absence semantics.

## Additional actual-source audit, pending

Use the opt-in complete CCAT snapshot already downloaded for
`complete-catss-audit` in GitHub CI; print only a small structural
neighborhood of the two rows. Capture exact alignment IDs, source line
numbers, physical logical row count, adjacent source-side siglum classes,
typed annotations, plus/minus flags, and relation to surrounding verse
grouping. The `1Esdr` and `Sirach` cases must be evaluated separately,
including whether the empty row is a misplaced continuation or
source/export omission.

Do not commit upstream source texts, add inferred replacement Hebrew
readings, introduce generic empty-MT acceptance or assert fabricated
word mappings. This research PR does not change parser or technique
semantics. Any behavior change requires follow-up RED-first tests and
an exact-head 46-file audit / independent adversarial review.
