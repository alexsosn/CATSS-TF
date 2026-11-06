# #41 — Restore and validate scholarly notebook against current CATSS-TF

## Research / reconciliation (2026-11-07)

The September draft PR #42 `1f859c3` was based on a pre-release parser and contained two added GitHub workflows which downloaded the licensed CATSS files with `curl --insecure`. Their historical jobs 36243959640 and 36243881350 failed while building the BHSA projection; they did **not** execute the notebook. In current `main`, `docs/case-studies/magic-terminology.md` already publishes cautiously scoped, verified-looking source counts (e.g. Greek `μάγος` is 2 in Daniel OG and 8 in Theodotion in CenterBLC/LXX 1935), but these are not evidence that the old notebook has run.

The notebook has 9 unexecuted code cells, default module paths relative to the launch CWD, `nodes_for_alignment()` calling `F.catss_alignment_id.s()` on each Greek token (a linear feature scan per token), and a BHSA join by alignment ID alone. It must not imply equal corpora or manuscript-specific lexical links.

Merge resolution `d4bd121` uses the current main tree, retaining only the notebook and research notes from the historical branch; all obsolete insecure CI jobs have been dropped. The PR is a draft and must not merge until user-facing E2E results are observed.

## Scoped next step — research → plan → RED → code → test/review

1. Notebook configuration must require **explicit absolute**, existing local projection directories in `CATSS_LXX_MODULE` and `CATSS_BHSA_MODULE`, matching `catss-lxx` / `catss-bhsa`. Never infer relative paths from the process CWD. This avoids silently loading an unrelated project or parent.
2. Reuse a single per-notebook Hebrew index keyed by **(CATSS source, stable alignment ID)**, scanning TF word nodes and both membership lanes only once. Missing/wrong-source matches stay unmapped; no positional fallback or new library-level indexing infrastructure.
3. Set literal claims/notes to the currently scoped full-parent versus OG-only counts, and keep Daniel OG / Theodotion separate. Do not invent notebook execution output.
4. Deterministic RED-first tests using stdlib JSON/AST load the notebook, compile every code cell, exercise configuration resolution across different CWDs with temporary module directories and missing/malformed env vars, and exercise an extracted pure alignment-index function with a fake two-lane Text-Fabric API. The original notebook must fail these tests for meaningful behavioral reasons.
5. Bring these notebook-only fixes to GREEN in the existing Python matrix. No licensed CATSS/parent data, no generated corpus or notebook outputs checked into git.
6. E2E still required before final merge: execute notebook on independently acquired user-local CATSS and pinned BHSA/LXX (with exact versions and disclosed source provenance), audit summary counts and missing projections, then independent adversarial final-head review. The existing full CATSS *canonical* CI cannot substitute for a **BHSA/LXX projection** notebook E2E, and the default CCAT TLS issue #44 must not be bypassed.

## Definition of done and non-goals

This narrow repair episode does not close #41 or finalize PR #42 by itself. It fixes deterministic reproducibility/performance in the notebook, without new TF feature model, downloader behavior or speculative lexicon alignment. Full-source projection may remain blocked on pinned JoshB subverse constraints. Keep the broader #126 open.

## Preflight extension — existing projection consistency API

A separate implementation review found that the documented same-snapshot requirement was not mechanically enforced. The library already has `compare_projection_bundles(bhsa_directory, lxx_directory)` in `consistency.py`. Its production code independently reads both `catss-sources.tsv` tables, rejects mismatched size/SHA-256 fingerprints, and compares canonical alignment/annotation/technique sidecars for supported shared sources. This is the existing cross-projection contract; do **not** reinvent a manifest or run positional joins.

RED-first tests of a small notebook `require_matching_projections` function must assert the exact two paths reach the comparator and that `ok=False` raises with bounded diagnostic *codes* instead of permitting silently inconsistent corpora. GREEN: call the existing comparator before loading either pinned parent, report only a successful numeric source count and keep the notebook source/output-free. Re-run the focused and full offline CI and obtain fresh failure-oriented review. This verifies **internal bundle agreement**, not independent authentication of the upstream CATSS bytes or an E2E parent-corpus run.
