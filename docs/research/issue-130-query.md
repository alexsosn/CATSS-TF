# #130 — Canonical alignment-group lexical lookup

## Evidence
The current canonical warp has `alignment` slots, word-like `mt_element`/`lxx_element` nodes and `catss_text`, `catss_index`, `catss_alignment_id`, `catss_source` features (see `canonical_materializer.py` and TF readback tests). Element nodes each cover their alignment slot via `oslots`. Reconstructed MT-B is a separate raw column and cannot be treated as a lexical MT-A element without a grounded tokenization decision. The existing Libronix crosswalk example loops across every slot, retrieving all elements for every one of ~349,670 groups for each candidate query.

## Design
Use Text-Fabric's standard feature-value lookup `F.catss_text.s(value)` to find lexical element candidates and `F.otype.v(element)` to discriminate MT vs Greek even when the spellings collide. Convert element node to its alignment slot through `L.d(element, otype="alignment")`. Intersect the slot sets and use source filename filter **after** matching; return records carrying the entire ordered group, not a fabricated 1:1 word pair. Check the warp slot type explicitly to avoid running against a BHSA/LXX projection. Keep the function side-effect-free and independent of the upstream .par inputs.

No second index, sidecars, new TF features, dependency or parent-warp mutation. Source filtering is literal filename equality (A/B and OG/Theodotion remain distinct); empty forms are invalid rather than wildcard-all queries.

## RED and gates
Commit `bac51b5` added a test that imports missing `find_aligned_groups` and compares it to an independently written exhaustive TF slot scan. CI initially identified formatting differences rather than reaching pytest. Formatting-only RED commit `fcf8181` corrects them, leaving the missing exported helper as the expected behavioral failure before production code. The acceptance gate is exact-head Python 3.11–3.13, release smoke, 46-file CI, Context-Fabric fixture acceptance, and a skeptical final-head review with a loaded TF API smoke.
