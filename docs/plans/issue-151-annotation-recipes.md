# #151 phase 2 — evidence/annotation recipes with a clean-user subprocess gate

1. Research `docs/research/issue-151-annotation-recipes.md` and record this plan before test/code.
2. Add RED-only `tests/test_researcher_annotations.py`: it must fail on missing `examples/annotation_evidence_walkthrough.py` and missing a documented section in `docs/researcher-cookbook.md`; invoke script via subprocess in a different temp CWD. Expect source-safe deterministic JSON counts for MT-A primary vs Qere/Ketiv (one word node), Sirach witness 3 marked, reading lacking witness 7, lacuna raw mark; verify negative witness 8 and absence of invented target edges. Don't handwave expected counts: test final oracle from built TF.
3. Observe actual behavior RED after pytest, with CI Ruff/mypy clean.
4. Implement the short synthetic CLI using `TemporaryDirectory` and public `materialize_corpus`/`find_sirach_witness_annotations`; inspect typed TF features/annotations without manuscript-to-token inference. Add exact user-readable recipe and expected output to cookbook; no outside data.
5. Run Python 3.11/3.12/3.13, release/Context-Fabric, full source 46-file canonical TF/Agora and independent exact-head adversarial review. Merge only if all green.
6. Keep #151/#149/#126 open for remaining textual-variation/phrase/order/Libronix capabilities and independently validated pinned parent E2E. Nothing in this mini-project certifies actual historical Sirach manuscript readings.
