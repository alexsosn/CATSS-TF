# Issue #147 research — raw MT-B evidence query

Date: 2026-11-10. Parent issue: #126. Baseline main `fc36e25c2388ffdc41f14eab5896e0602e152f65`.

## Actual code and source semantics

- `src/catss_tf/parser.py::_split_mt_columns` splits semantic MT source at its **first** `=` into `mt_col_a` and the stripped, possibly empty `mt_col_b`; no `=` means B is `None`. The value is **reconstructed/editorial CATSS source**, not a second MT word stream.
- `_retroversion_kind` classifies the **raw B prefix**: `;` = context, `v` = vocalization, `vs` = shin/sin vocalization, `:` = proper noun, `@` = etymology, `%p` = preposition variants, etc.; otherwise plain. It never asserts a lexical equivalent or manuscript witness.
- `src/catss_tf/canonical_materializer.py` preserves `catss_mt_col_a`, `catss_mt_col_b` and `catss_retro_kind` **on every alignment slot**. Special `mt_b_carrier` nodes are deliberately limited to physically empty A, Greek lexical and non-LXX-plus contexts, six nodes in the current complete corpus. Restricting B search to those nodes would lose ordinary A/B rows and marked additions.
- `tests/test_canonical_materializer.py` already loaded actual native TF for `--+ =;W/KL\tLOGOS`, `^^^ ^ =W/KL\tLOGOS`, and B-only `=;W/KL` source shapes. `docs/canonical-corpus.md` grounds `=;W/KL` in 2 Samuel and `=W/M/BNY` in 1 Esdras. These are test-shape anchors, not a license to assume textual witness attestations.
- `src/catss_tf/query.py` already publishes `CanonicalAlignedGroup`, `_ordered_elements`, and `find_groups_with_all_forms` using native `alignment` slots; B is intentionally excluded from those lexical queries. `__init__.py` explicitly exports the public query types/functions.
- `.github/workflows/ci.yml` builds a 46-file canonical TF snapshot, and a Text-Fabric `api` is available inside the `Reload complete canonical CATSS corpus with Text-Fabric` job step. The step already checks scalar reference nodes and the `find_groups_with_all_forms` full-scan oracle; add a *bounded* raw-B oracle there, not another download/materialization.

## Risk and unresolved equivalences

An exact substring of raw B matches editorial notation, partial words, or nonlexical signs. It must be named **raw source containment**, not Libronix `Reconst:` lexical search or transliteration normalization. This is deliberate partial coverage of #126. Materialized Text-Fabric can omit a wholly unpopulated `catss_mt_col_b` feature, so a valid no-B corpus must yield no hits, not a fabricated error; a matched nonempty B with missing `catss_retro_kind` should fail closed because the writer emits both.

Regression traps: same source verse with multiple alignment groups, MT-A term equal to query but B absent, LXX-plus rows that nevertheless carry column B, A marked-only rows, B-only plain vs context and vocalization, exact source filename scope, two separate CATSS sources, match ordering by alignment slot, raw string untouched and source-license-safe CI logs.
