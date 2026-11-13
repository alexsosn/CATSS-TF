# #150 phase 2 — compact lossless TF feature/otype dictionary

Research: [issue-150-feature-schema.md](../research/issue-150-feature-schema.md).

1. RED-first test `tests/test_docs_tf_feature_reference.py` verifies a missing `docs/tf-feature-reference.md` fails. Derive expected **parent base names and types** from `tf_schema` dictionaries, expected semantic kinds from `documented_semantic_specs()` plus `_RAW_SEMANTIC_KINDS`, global aggregate names from `_AGGREGATE_BY_FLAG`, canonical otypes from `canonical_materializer` source, and exported names from `catss_tf.__all__`. Require exact code-audited table coverage, not merely a one-time fixed number. Verify the documented lane/scope expansion rule accounts for exactly `FEATURE_SPECS`—this catches future schema drift.
2. Observe actual failing RED in GitHub Actions before adding the missing page. Keep tests source-code driven and no corpus data.
3. Create an accessible **compact** reference with parent core/type/meaning and semantic kind tables (all base names + all kind names), explicit expansion rule for 2 lanes × 4 scopes × (flag + payload), structural/aggregate counters, canonical TF node and feature surfaces, and public API list. Do not print 2,000 repetitive feature strings. Link the fully explicit `docs/notation-reference.md` for literal markers.
4. Add researcher examples with standalone vs projection warp, `F.otype`, `F.catss_kind`, `F.catss_sem_...`, source alignment IDs; explain optional/empty semantics, reference uncertainty and source-license/TLS boundaries. Use synthetic source strings.
5. Link in README and existing canonical docs, preserve all links. Run all exact-head CI and full 46-file E2E smoke; independent failure-oriented review; merge with expected SHA, keep #151 and #126 open.
