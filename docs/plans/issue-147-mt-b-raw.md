# Issue #147 plan — exact raw MT-column-B search

Research: [issue-147-mt-b-raw.md](../research/issue-147-mt-b-raw.md). No changed node/feature/schema identities.

## Public contract

Add `CanonicalMtBRawHit` containing `group: CanonicalAlignedGroup`, exact `mt_b_raw: str`, exact `retro_kind: str`. Export `find_mt_b_raw_matches(api, raw_substring: str, *, source: str | None = None, retro_kind: str | None = None)`. Input strings are **case-sensitive**, and the search uses Python literal substring (`raw_substring in mt_b_raw`), **not** token, regex, wildcard or word-boundary search. Source and kind filters compare exact strings. Results are yielded in alignment-slot order, with no positions/word-level or parent-node edges.

Validate standalone warp `api.F.otype.slotType == "alignment"`, nonempty non-whitespace query (no bare bytes/number), and optional nonempty string filters. Missing `catss_mt_col_b` feature returns an empty iterator. The optional `catss_retro_kind` feature is required if the source contains B values; fail explicitly on missing metadata for matching B evidence. Iterate `api.F.catss_mt_col_b.items()` only once. For each matched slot, fetch ordered existing MT-A and LXX elements via `_ordered_elements`; avoid new indexes, special carrier limitations, and branch or source mutations.

## TDD and safety gates

1. Commit this research then plan, before tests.
2. Commit RED synthetic native-TF tests in `tests/test_query_mt_b_raw.py`, exercising six source shapes (B-only context, B-only plain, nonlexical A with B, MT-A with no B, LXX-plus with B, vocalization) and source boundaries. Use a separate exhaustive-slot oracle, substring exactness, kind/metadata and invalid input cases; check the public symbol is initially missing.
3. **Observe** the RED (missing public symbol), e.g. a test-first one-off GitHub Actions job/isolated RED-only branch. Preserve workflow restoration and never merge RED-only artifacts.
4. Implement in `query.py`, export from `__init__.py`, and document an executable example and its limitations in `docs/libronix-coverage.md`.
5. Append independent real 46-file TF scan oracle after the current group query smoke, select a real nontrivial raw B seed and source in memory, compare ordered IDs/raw/kind against all native alignment slots; output only count. Include known source-line IDs or opaque source labels, never copyrighted B text in job log.
6. Pass exact-head Python 3.11/3.12/3.13 Ruff/mypy/pytest, release wheel, compiled Context-Fabric fixture and 46-file canonical TF/Agora. Perform independent adversarial review on final diff and real successful checks, then squash merge at expected head and close #147. Keep #126 open for true reconstructed lexical search and Libronix behavior.
