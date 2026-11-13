# #151 phase 1 — executable first-researcher canonical TF walkthrough

Baseline `d59eb34480b70b25ba0d6ea3b5a410718536a882` after the notation and feature-schema reference PRs #152/#153 (2026-11-13). Parent docs task #149, Libronix feature parity #126.

## Verified user-facing code/data contracts

- `catss_tf.materialize_corpus(source_dir, output_dir)` writes a standalone canonical Text-Fabric module; `Fabric(locations=str(tmp_root), modules=("catss",), silent="deep").loadAll(silent="deep")` is the **working fixture and CI recipe** from tests `test_query_mt_b_raw.py`, `test_query_all_forms.py` and `test_canonical_materializer.py`. No BHSA/LXX parent is needed for this entry point.
- `find_aligned_groups(api, "MLK", "BASILEU/S")` tests exact MT-A and Greek **co-membership in one editorial alignment**, not a word-to-word edge, contextual phrase search or morphological transliteration.
- `find_groups_with_all_forms(api, mt_forms=("MLK", "DBR"), lxx_forms=("BASILEU/S", "LOGOS"))` uses AND/set semantics inside one alignment; tests already use exactly this style of fully synthetic example.
- `find_mt_b_raw_matches(api, "W/KL", retro_kind="context")` searches *parsed reconstructed MT-B*, including physically MT-A-empty rows, not an attested Hebrew lexical word, normalization, or Libronix `Reconst:` index.
- Other public functions `find_sirach_witness_annotations`, `find_unclassified_alignments` have explicit schema constraints (see `query.py`); do not invent user results for a tiny synthetic fixture and do not claim witness-to-word attribution.
- Existing docs are divided among `integration.md`, `browser.md`, `canonical-corpus.md`, `libronix-coverage.md`; the new dictionaries now cover source glyph names and actual feature types, but there is no single **document-first, clean-environment, runnable first study** with deterministic expected results and a subprocess E2E acceptance.

## Scoped delivery

A new, user-readable `docs/researcher-cookbook.md` containing onboarding and a short live canonical query walkthrough, backed by `examples/canonical_research_walkthrough.py`: purely synthetic MT-A+LXX + MT-B data created in a TemporaryDirectory; canonical TF materialized, loaded, and queried with public APIs; JSON counts printed on stdout; no external download, licensed data, parent TF overlays or repository-output modifications. A separate subprocess unit test invokes the CLI as a fresh user would, validates summary and nontrivial oracle/source boundaries, and fails RED before the script/page exist.

Doc sections can additionally explain how to extend queries to source verse, Qere/Ketiv, punctuation and manuscript caveats, linking full dictionaries and current known blockers. The user's real authorized 46-file corpus and pinned BHSA/LXX overlays remain a **separate** opt-in E2E; full tutorial completion of #151 must not be asserted by this first synthetic vertical slice alone. This has no new backend feature/index or schema change.
