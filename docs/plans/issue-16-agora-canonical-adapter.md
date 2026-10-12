# #16 stage 1 plan — standalone CATSS through Agora

1. Ground actual Agora v1 JSON schema and Burns adapter contract; document that this PR covers **only** `catss` standalone (not BHSA/LXX parent-dependent projections). Preserve issue #16 open.
2. **RED first:** add `tests/test_agora_adapter.py` and a source-only manifest test. Confirm via CI that import `catss_tf.agora_adapter` or manifest existence fails before implementation. Tests exercise tiny synthetic Genesis and real native materializer (no mocks for positive path), Text-Fabric reload with `alignment` slot type, source/provenance retention, symlink/occupied output, source/output overlap, negative native validation, synthetic malicious writer files, rollback and permission semantics.
3. **GREEN:** implement `src/catss_tf/agora_adapter.py` and `agora.materializer.json`: `catss-canonical` standalone via `{source}` and `{output}`, user-local only, network deny. Bridge Agora's precreated output to the native absent-output destination with a private child. Verify regular `.tf` and `.tsv` files, promote with `os.link` no-overwrite, cleanup on failure. Source inspection and native mapping/validation remain solely in CATSS-TF.
4. Run Ruff, mypy, pytest on Python 3.11–3.13, wheel/release smoke, pinned 46-source full CATSS audit / readback at **final head**. The plugin manifest must parse as valid JSON and match Agora schema shape and exact advertised callable. No CATSS source or generated corpus committed.
5. Researcher docs: usage for already-acquired local sources, Agora install approval and sandbox, current unsupported BHSA/LXX parent-dependency boundaries, user-licensing/provenance.
6. Independent adversarial exact-head review: force source/output overlap and symlink paths, staged partial failure, native success followed by forged invalid output, and absence of silent network/parent dependency; review actual CI synthetic TF readback. If defects, RED-fix-recheck-re-review.
7. Squash merge with expected-head guard only after all gates pass; link Agora#221 and keep #16 open until the other two profiles are supported and downstream registration is verified.

## R16-2 review-fix RED → GREEN (strict registered source policy)

The existing 46-file source reports **0 ignored validation findings**, so the
previous assumption that the manifest must acknowledge 3 diagnostic codes is
unsupported. Prevent fail-open user-local source processing:

1. **RED:** commit an explicit manifest-contract regression asserting that
   registered `catss-canonical` execution.args contains *no* `--allow`.
   The old manifest necessarily fails this assertion. Record failure before
   touching the manifest.
2. **GREEN:** remove the 3 unconditional `--allow` flags from the manifest;
   keep direct caller opt-in semantics for diagnosed local research input.
3. Exact pinned 46-file Agora integration must execute with *no exceptions*,
   retain byte-for-byte TF and provenance equivalence, and load 349,670
   alignment slots plus 6,218 scalar references.
4. Document that the production manifest is strictly fail-closed and that
   test-only/source-operator options are not default Agora behavior.
5. Re-run complete five-job CI on the final head and obtain a logically
   independent adversarial re-review before merge. Keep #16 open.
