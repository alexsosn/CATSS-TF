# R96-7 — textual-surface candidate evidence for scalar CATSS Greek references

## Baseline: actual pinned data, not numeric MT coincidences

Issue #96 rejects `catss_reference_target` links inferred solely from
CATSS MT-header numeric equality. The merged R96-5 parent inventory
(counted over all 46 upstream files against pinned CenterBLC/LXX commit
`f32a98eddf7eb239aa73ab863d70381e416d5076`) found 6,218 scalar
Greek references: 5,555 existing nonempty exact parent spans, 641
missing spans, 22 explicitly unsupported sources, zero unknown sources.
All 424 explicit Greek lettered subverses lacked an exact labeled span.
These numbers make it worthwhile to assess **textual evidence** before
considering any typed destination edge.

The existing `lxx_resolver.py` implements non-lemma surface-only
`normalize_catss_greek` and `normalize_lxx_greek` and counts exact
contiguous source-token sequences in pinned parent verse spans
(`_find_candidates`). Its actual mapping requires a unique
**nonoverlapping joint placement of all tasks**, not simply a match for
one reference. This diagnostic must preserve that distinction.

## Research question and constrained approach

For each explicit CATSS `GreekReference`, look up its exact book /
chapter / verse / subverse with existing `default_lxx_reference` source
policy. Validate the LXX provider probe, returned location metadata,
word subverse scope, and nonempty span. Reuse the existing two surface
normalizers, count *exact contiguous candidate occurrences* for the
alignment's Greek tokens within the referenced parent span. Aggregate:

- existing parent + exactly one surface candidate;
- existing parent + multiple surface candidates (ambiguous);
- existing parent + no surface candidate;
- existing parent + no CATSS Greek lexical tokens;
- invalid CATSS token / invalid parent normalization (separately);
- missing exact parent span / unsupported source / unknown source.

Numbers in the report must exhaust scalar refs; no raw corpus content or
parent word IDs are exported. Cache repeated parent span queries; never
fuzzy match, silently drop unsupported punctuation, fall back a labeled
subverse to an unlabeled verse, infer MT verse equalities, or label a
single candidate a verified alignment.

## Critical distinction

Even **exactly one contiguous sequence** is only local evidence in one
candidate parent verse. CATSS scalar references may be contextual
rather than relocation instructions, the same CATSS alignment may carry
multiple scalar refs, and other CATSS alignments in that parent section
may compete for overlapping spans. The current strict LXX resolver
performs a different joint-placement procedure. This R96-7 report is
a conservative **candidate triage**, not evidence sufficient to create
canonical reference-target edges. Keep #96 open.
