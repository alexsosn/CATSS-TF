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


## R96-8 — real pinned 46-file overlap distribution (2026-10-11)

The initial GREEN exact-head [CI run 38125940495](https://github.com/alexsosn/CATSS-TF/actions/runs/38125940495) passed the full Python matrix (467 tests on each of 3.11, 3.12 and 3.13), release smoke, complete source/annotation checks, canonical Text-Fabric materialization and round-trip. The source was all 46 current CATSS parallel files; Greek parent was the exact `CenterBLC/LXX` revision `f32a98eddf7eb239aa73ab863d70381e416d5076`.

| Observed category | Count |
| --- | ---: |
| `scalar_references` | 6,218 |
| `exact_single` | 4,349 |
| `exact_single_with_overlap` | **232** |
| `exact_single_without_overlap` | **4,117** |
| `exact_multiple` | 455 |
| `no_surface_match` | 294 |
| `no_greek_tokens` | 453 |
| `catss_normalization_error` | 4 |
| `parent_normalization_error` | 0 |
| `parent_span_missing` | 641 |
| `unsupported_source` | 22 |
| `unknown_source` | 0 |

The exact single class partitions **232 + 4,117 = 4,349**. All 6,218 references are accounted for by unchanged outer outcome classes. The 232 potential competing placements are *existential overlaps*, not proof that all are impossible under a joint resolver; an ambiguous other alignment can select a different word interval. The 4,117 have no overlap **among explicitly referenced and successfully normalized candidate intervals in the same CATSS source and exact parent key**. That does not guarantee globally consistent placement or any meaning of the reference notation. In particular, the unreferenced Greek alignments in a parent verse are outside this screen. No `catss_reference_target` edges were generated.

This milestone narrows the next issue #96 research from the raw 4,349 local matches but does not close that issue or validate any semantic target.
