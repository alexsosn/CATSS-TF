# R96-8 — Cross-alignment surface overlap within exact Greek references

## Grounding in pinned real corpus and code

Current `src/catss_tf/reference_surface_audit.py` counts `exact_single` whenever one alignment's Greek token sequence occurs once in the pinned parent verse. It assesses each scalar reference *independently*, despite the strict `lxx_resolver._solve_unique_placement` requiring a joint, non-overlapping assignment. It therefore cannot distinguish a locally unique candidate that is already claimed as a candidate by another CATSS alignment (possibly with several alternatives).

In the complete 46-file audit against pinned CenterBLC/LXX `f32a98eddf7eb239aa73ab863d70381e416d5076`, run [38124330799](https://github.com/alexsosn/CATSS-TF/actions/runs/38124330799), 6,218 scalar references partition as: 4,349 exact-single local spans, 455 exact-multiple, 294 no match, 453 alignments without Greek tokens, 4 CATSS normalization errors, 0 parent errors, 641 missing parent spans, 22 unsupported, 0 unknown. These results are actual source-and-parent observations, not proven reference destinations.

## Decision

Add read-only **candidate-overlap triage** to the same audit. For each exact parent key within a CATSS source document, retain normalized candidate intervals as zero-based half-open word-offset ranges. For each *locally unique* reference, classify whether **any** interval proposed by a *different alignment* in the same CATSS source and exact parent book/chapter/verse/subverse overlaps its interval. Include intervals from other alignments with multiple candidates; an ambiguous alternative can still compete. Same alignment's repeated references are not competitors. An identical parent key in a different CATSS source must not be treated as proof of joint-placement conflict across unrelated textual traditions. Preserve two new disjoint counts `exact_single_with_overlap` and `exact_single_without_overlap`, summing to the existing `exact_single`.

This is an *existential overlap screen*, **not** a proof of resolvability. Even a unique, non-overlapping local candidate is not a verified target: scalar CATSS references may convey contextual information, and non-reference CATSS tasks competing for the same parent section are beyond this audit. No canonical edges, source-text excerpts, parent word-node IDs, or source/parent corpus copies are produced.

## Performance and failure boundary

Reuse the existing exact source classification, version pin, parent-span metadata integrity checks, text normalization, and cached parent tokens. Store only sparse candidate offsets for references which normalize and have exact parent spans (at most 6,218 reference instances in the current corpus). Preserve existing counts and fail-closed behavior. Report counts only. No fuzzy matching, MT-header numeric equivalence, subverse fallback, or changes to LXX projection semantics.

## RED-first fixtures

Test a single candidate overlapped by (a) another alignment's unique candidate and (b) another alignment's *multiple* candidates; a non-overlapping pair; duplicate scalar references on the same alignment; and a different source document with the same parent key. Run the fixed tests before implementation and capture intended assertion RED. Validate final behavior against all 46 user-acquired CCAT files and pinned LXX; record observed counts in this research file once measured.
