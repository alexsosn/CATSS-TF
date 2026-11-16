# #160 — CATSS source-reference scoped queries

Baseline main `f6390bd6` (2026-11-14). Linked workflow requirements: #126 and #151.

## Evidence

- `src/catss_tf/query.py` exports `find_aligned_groups`, `find_groups_with_all_forms`, `find_groups_with_ordered_forms`, `find_mt_b_raw_matches`. Each exposes only optional exact `source` matching (and method-specific filters), yet already constructs returned `CanonicalAlignedGroup` from native `api.F.book`, `api.F.chapter`, `api.F.verse` on **alignment slots**.
- `tests/test_query.py`, `test_query_all_forms.py`, `test_query_ordered_forms.py` build tiny native TF modules covering at least two books and several verses. Filtering results by source-reference after lookup should agree with a direct exhaustive native TF alignment-slot oracle.
- Source-header book identities can distinguish different textual traditions. Canonical `book`/`chapter`/`verse` are not a guaranteed Greek versification mapping, and neither `catss_reference_target` nor BHSA/LXX parent IDs can safely substitute.
- Editorial reconstructed MT-B evidence lives in `catss_mt_col_b` on the same alignment slot, never in an attested MT-A word. Query should therefore share the reference filter while preserving that distinction.

## Boundaries

Introduce optional `reference=(book, chapter, verse)` exact matching for these four queries, with source header spelling and integer values. A source `verse=0` should not be rejected merely for being zero. Validation occurs even when queries would return no hits. No verse ranges, aliases, Greek target inference, cross-alignment phrase search, parent mapping, new index, or undocumented tokenization. Keep `source` filename filtering independent and conjunctive.

Synthetic fixture: Genesis 1:1, 1:2, 2:1 with repeated lexical forms and reconstructed `=;W/KL` at two references, plus JoshB 1:1. Independent native TF oracles exercise positive/negative combinations, wrong books/sources, and malformed references. Full-corpus CI should verify materialization and native-TF reload without committing corpus data.
