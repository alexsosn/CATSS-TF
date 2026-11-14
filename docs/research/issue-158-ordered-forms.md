# Issue #158 — source-position semantics for ordered CATSS lexical forms

Baseline `56783cdd589fe2adbe9d0d11a730e4764488058f` (2026-11-15). Parent user-facing parity #126, documentation #151.

## Evidence from real implementation and tests

- `src/catss_tf/query.py::find_groups_with_all_forms` searches exact source spellings in `catss_text` on `mt_element` and `lxx_element` and intersects canonical `alignment` slot ID sets. Query repeats intentionally collapse to set-membership. It does **not** provide source-order or positional meaning; `tests/test_query_all_forms.py` confirms that distinction.
- The native canonical materializer gives each lexical `mt_element` or `lxx_element` a 1-based `catss_index` *inside the same alignment slot*. `_ordered_elements(api, slot, element_type)` returns an exact tuple of original source element spellings in index order. `CanonicalAlignedGroup.mt_elements/lxx_elements` already expose this without new TF schema or raw data.
- Underlining in the existing Libronix crosswalk: same alignment MT↔Greek `ANDEQUALS` and multiword co-membership are partly modeled; actual phrase/running-text search across alignment boundaries and Libronix keyboard/search indexing are not. A deliberate narrow helper can support **ordered subsequence** and **consecutive elements within one editorial alignment**, but must not call either an attested word-level translation or an indexed phrase search.
- Required negative cases: the same words in reverse order, same verse but different alignment groups, repeated words with only one source occurrence, and one-sided order independently of the opposite side. Source identity remains filename-specific; no MT-B reconstructed text or BHSA/LXX parent indices.
- The existing full 46-file canonical CI reload has 349,670 alignment slots and an independent source-grounded `find_groups_with_all_forms` oracle. Select a real 2-element Greek sequence in one source group and compare the new public ordered query to an independent exhaustive native-TF sequence scan without logging licensed text.

## Bounded solution

Add `find_groups_with_ordered_forms(api, *, mt_forms=(), lxx_forms=(), adjacent=False, source=None)` in `query.py`, leveraging `find_groups_with_all_forms` as a **candidate reducer**, then applying a positional check to the ordered tuple(s) returned in each canonical group. Repeated requested spellings must consume distinct element positions; with `adjacent=True` they must consume consecutive positions. Exact source forms/case only; no new parser/materializer code, index, parent mapping or manuscript claims.

Update public exports, generated-schema-checked API reference, crosswalk and cookbook with an explicitly **within-one-group-only** example. Research → plan → pytest RED before code → implementation → exact-head Python matrix+full TF/Agora and independent adversarial review.
