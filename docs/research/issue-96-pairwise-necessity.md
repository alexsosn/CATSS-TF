# R96-9 — distinguish unavoidable pairwise candidate collisions from optional alternatives

## Grounding (2026-10-11)

The merged R96-8 code in `src/catss_tf/reference_surface_audit.py` computes candidate intervals `[start, stop)` per exact parent key and CATSS source for *explicit scalar reference alignments only*. It classifies a locally unique reference as overlapping if **any** interval for any other alignment in the same scope intersects its single interval. The verified pinned [46-source CI run 38125940495](https://github.com/alexsosn/CATSS-TF/actions/runs/38125940495) reports 6,218 scalar references, 4,349 exact locally unique surface matches, of which 232 overlap and 4,117 do not. A candidate alternative may overlap even when an alternative at a different parent word offset does not.

The strict `lxx_resolver` attempts a *joint non-overlapping placement* of tasks; the current read-only audit is neither that solver nor evidence about the meaning of contextual reference notation. Before global reasoning, classify pairwise candidate collisions with no semantic upgrade and no parent word IDs.

## Proposed precise semantics

For each locally unique scalar reference with candidate interval U, inspect **different alignment IDs** in the same (CATSS source filename, exact parent book, chapter, verse, subverse) group. For each competitor C, its set of distinct candidate intervals is nonempty by construction.

* `exact_single_with_unavoidable_overlap`: there exists a competitor C for which **every** candidate interval of C intersects U. This is a locally unavoidable *pairwise word-position collision if both alignments are required to be placed*. The competitor may be locally unique or ambiguous; it is **not** a demonstrated semantic contradiction (some references are contextual and may not assert placements).
* `exact_single_with_avoidable_overlap_only`: there is at least one overlapping candidate from another alignment, but for **every** competing alignment at least one alternative interval is disjoint from U. This does not prove a globally non-overlapping assignment across all tasks; combinations of multiple competitors can remain impossible.
* The two new counters partition the **existing** `exact_single_with_overlap` (232 at the known baseline) and leave `exact_single_without_overlap`, `exact_single`, and all existing outer partitions untouched.

Duplicate references in the same `alignment_id` do not self-compete; they still count per scalar reference, as before. Different CATSS source traditions are isolated even with the same pinned Greek key. `None`/lettered subverse keys remain distinct, and parent-fingerprint/word-label checks fail closed. The only stored values remain offset intervals; no biblical texts or parent node IDs are exported.

## RED-first fixtures and hazards

Use synthetic pinned-provider tests:
1. Two distinct locally unique alignments on one word => both unavoidable.
2. One long unique candidate `LOGOS KAI` at [0,2) with another `LOGOS` at [0,1) and [2,3) => overlap **avoidable** by choosing the second alternative.
3. One long unique candidate `LOGOS KAI LOGOS` at [0,3) competing with `LOGOS` at positions 0 and 2 => unavoidable although competitor ambiguous.
4. Multiple competitors with an unavoidable and an avoidable overlap => unavoidable wins.
5. Adjacent nonintersecting candidates, repeated scalar refs of one alignment and two source traditions preserve the previous invariants.

The old two-counter overlap behavior stays the authoritative outer partition; no claim of resolved CATSS reference destinations or `catss_reference_target` edges. Count actual category frequencies only after the complete pinned 46-file CI probe; do not guess.


## R96-9 pinned 46-file result (2026-10-11)

The production-code head `3354115a902520ec82422c453064142f91dcf94f` passed the [CI run 38129496270](https://github.com/alexsosn/CATSS-TF/actions/runs/38129496270): 472 tests on Python 3.11, 3.12 and 3.13, Ruff/mypy, release smoke, complete CCAT-source notation checks, pinned CenterBLC/LXX reference diagnostics, canonical TF materialization and TF reload.

Observed output from all 46 CATSS files and exact pinned CenterBLC/LXX `f32a98eddf7eb239aa73ab863d70381e416d5076`:

| Field | Count |
| --- | ---: |
| `scalar_references` | 6,218 |
| `exact_single` | 4,349 |
| `exact_single_with_overlap` | 232 |
| `exact_single_with_unavoidable_overlap` | **108** |
| `exact_single_with_avoidable_overlap_only` | **124** |
| `exact_single_without_overlap` | 4,117 |
| `exact_multiple` | 455 |
| `no_surface_match` | 294 |
| `no_greek_tokens` | 453 |
| `catss_normalization_error` | 4 |
| `parent_normalization_error` | 0 |
| `parent_span_missing` | 641 |
| `unsupported_source` | 22 |
| `unknown_source` | 0 |

**Partition invariants:** 108 + 124 = 232; 232 + 4,117 = 4,349. All previous outcome counts remain identical to R96-8. The 108 references have an overlap with a competitor for which **every** local candidate intersects the unique interval. The 124 references have overlap possibilities but no such single inevitably intersecting competitor. These are counts of **scalar references**, not of distinct alignments, verses or proven translational events.

Next investigations for #96 must establish which CATSS scalar references actually entail placements, then incorporate implicit alignments and global constraints in a pinned-parent joint solver. Neither the 124 nor the 4,117 class can be interpreted as verified canonical LXX targets; the 108 class must not be interpreted as a demonstrable scribal error without source-specific investigation. No new edges or upstream corpora are distributed.
