# R96-5 — pinned Greek-parent span availability (research)

## Evidence and boundary

The independently reviewed source-only inventory, merged as PR #98, reports
6,218 scalar Greek references across 46 CATSS parallel sources. There are 1,749
with no numeric MT-header candidate, 4,433 with exactly one, and 36 with
several. These figures **cannot** validate LXX destinations.

The existing LXX resolver already exposes `LxxVerseProvider.get_span(book,
chapter, verse, subverse)` and `default_lxx_reference()` with pinned
CenterBLC/LXX 1935 v1.0.1 source profiles. The provider returns a span only
when actual parent words with the requested exact subverse label exist.
For JoshB 9:2a–f the pinned parent has an unlabeled Josh 9:2 subverse, so an
explicit 9:2a lookup must return *absent*, not fall back to 9:2. The
`19.Neh.par` default reference is remapped to 2Esdr with chapter + 10,
but an explicitly specified Greek chapter uses its explicit value (existing
`_alignment_reference` semantics).

## What the new report can and cannot establish

Implement a **read-only, parent-validated existence audit** of scalar
Greek-reference span keys. For each reference, use the existing canonical
source classification and Greek default reference policy, preserving explicit
reference chapter/subverse. Distinguish:

- `parent_span_present`: an exact requested CenterBLC/LXX verse or labeled
  subverse exists and contains Greek words, *without claiming the CATSS row
  aligns textually to those words*.
- `parent_span_missing`: supported source, but the exact parent span has no
  words/is absent. Never fall back from explicit `a` to an unlabeled verse.
- `unsupported_source`: source explicitly listed as unsupported (e.g.
  Joshua A); no parent lookup is attempted.
- `unknown_source`: no pinned source profile; no parent lookup is attempted.

An invalid parent probe aborts before any audit; a provider returning an
inconsistent book/chapter/verse/subverse also aborts rather than counting
an alias as present. Do not publish parent nodes into the canonical TF warp,
infer Greek translation-technique facts, or use MT-header numeric coincidence.

The output is a compact deterministic count report (no transcribed source,
raw Greek words, or parent node IDs). The CI check must acquire the exact
pinned LXX Git revision through the existing research step, and the source
snapshot through the already opt-in 46-file audit; neither is distributed.

## Distinct future gate

Even an existing parent span is **not** a verified CATSS/LXX alignment;
textual normalization/unique sequence matching and the reference's
relationship to the current alignment must be investigated separately
before generating any canonical semantic target edge. Keep issue #96 open.
