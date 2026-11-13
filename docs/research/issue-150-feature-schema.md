# #150 phase 2 — schema/public-API reference research

Baseline main: `ae00495ddfbf9dcaf9a23df353dbf97a9b0015e8` (2026-11-13). Phase 1 notation glossary was merged as PR #152; #150/#149/#151 remain open.

## Actual feature sources (no licensed CATSS rows)

- `src/catss_tf/tf_schema.py` declares **12** lane core fields, **5** translation-technique fields, **27** boolean membership flags, **5** payload convenience fields, **5** structural-event counters, **11** reference-range fields, a global `catss_alignment_n`, and 27 flag aggregate counters. Every lane-scoped declaration has base and `_2` feature names.
- `documented_semantic_specs()` supplies the book-aware source catalogue semantic kinds (including distinct general/Sirach collisions and the Samaritan pattern). `_RAW_SEMANTIC_KINDS` supplies additional raw parser-related semantic kinds not in that glossary. Their **union** produces the declared semantic feature names; each semantic kind expands into 16 feature names: base boolean, optional payload, source scopes `mt_a`/`mt_b`/`lxx` with their optional payloads, and a second membership lane `_2`. Do not list thousands of near-duplicate names without documenting the construction and user-facing meaning.
- An initial source-structure audit finds ~2,286 declared parent feature names (verify the exact runtime `FEATURE_SPECS` count under CI; never treat declarations as observed populated values).
- `src/catss_tf/canonical_materializer.py` emits canonical slot type `alignment`, structural `document/chapter/verse`, and detail `mt_element/mt_b_carrier/lxx_element/annotation/reference/reference_range/source_line`, plus one `catss_annotation_target` scoped edge. Canonical `catss_kind`/raw/payload features differ from parent `catss_sem_*` values. Some features and node types are present only on corpus-specific evidence.
- `src/catss_tf/__init__.py` exports a fixed public API `__all__`, now including `find_mt_b_raw_matches` after PR #148. The README lists only a subset of these names; public feature docs must distinguish importable API from internal schema definitions.
- No backend query/UI parity with Libronix follows from feature declarations; keep #126 open. E.g. `catss_reference_target` is candidate textual target evidence, not guaranteed parent MT verse identity (#96); Sirach witness markers are not word-level attestation (#132).

## Scoped phase 2

Deliver `docs/tf-feature-reference.md`: a concise complete public vocabulary of canonical node/edge types and feature names, parent base family kinds/types with rules for all semantic/scoped/second-lane combinations, concrete access examples, a public API inventory, caveats and pointers to notation glossary/cookbook. Automated code-driven audit must flag any undocumented non-semantic parent base, semantic kind, canonical otype and public import. No new library API, normalization/index, or corpus data.

Test RED before docs: source-audited table coverage contract fails on missing page. Execute on CI. Then write the page, link it from README and canonical docs, run exact-head Python+release+Context-Fabric+46-file TF/Agora checks and independent review. Keep #150 open only if implementation actually lacks full feature-name/meaning coverage or user-facing comprehension; #151 independently covers runnable cookbook and new-user smoke.
