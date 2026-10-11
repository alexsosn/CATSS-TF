# #16 research — executable standalone CATSS Agora contract (stage 1)

2026-10-11; main at merged R96-15 `05e95b011053c5607a3f89b3b6ae6a7fbcc27dc1`.

## Actual downstream contract

Read Agora `registry/schema/materializer-plugin.schema.json` at `main`: a root `agora.materializer.json` can advertise independently runnable materializer IDs with `user-local` acquisition, `input.type=directory`, `required_globs`, `allow_symlinks=false`, `execution.type=python-module`, literal `{source}` and `{output}` placeholders, and `execution.network=deny`. `output.format=text-fabric` can assert `otype.tf`, `oslots.tf`, `otext.tf`. A standalone native corpus MUST NOT specify an output `composition.kind=feature-module` or `parent_input`. The executable `python-module` must exist inside the installed package; the current `catss-tf` CLI offers only `fetch/validate/browse` and cannot produce a module in one command.

Agora's `_create_staging_output` (existing Burns acceptance case in `alexsosn/CTC-TF`, `agora.materializer.json` and `ugarit_context_parsing.agora_adapter`) pre-creates an **empty staging directory**, whereas `catss_tf.canonical_materializer.materialize_corpus(source, destination)` **requires destination absent** and publishes atomically as a new sibling. Passing Agora's `{output}` directly would fail. The adapter must invoke native materialization in a **private absent child** under the pre-created output, validate native corpus files, and publish only those files into Agora's staging root, preserving native fail-closed behavior.

## Boundaries from code and real pinned source checks

Native `materialize_corpus` writes a real standalone Text-Fabric warp with `alignment` slots and source/provenance sidecars. The existing `tests/test_canonical_materializer.py` proves a tiny Genesis fixture yields loadable Text-Fabric `otype/oslots/otext` and stable `catss_alignment_id`. The full pinned 46-file audit at CATSS-TF PR #117 proves 349,670 canonical alignment slots and 6,218 reference nodes. The adapter must not parse/reinterpret CATSS itself, include licensed corpus files, or download automatically; it should simply invoke the existing native method.

Agora issue #135 and #221 are still OPEN for managed parent-dependent feature-module installation/publication. The current `catss-bhsa` writer requires `BhsaParentProbe` and a parent-specific provider; `catss-lxx` requires `TextFabricLxxProvider` with exact pinned release identity. The pinned complete CCAT snapshot currently cannot always materialize full LXX due to JoshB 9:2 absent lettered subverse spans. **Do not declare or register these profiles yet**: declaring feature modules without tested trusted read-only parent bindings would be a false capability claim. The upstream #16 and downstream Agora#221 remain open until all profiles are executable.

## Security and provenance risks

- Reject absent, occupied, symlink output and source/output overlap **before invoking** native code. Reject non-directory/symlink source path; native source inspection independently rejects direct-child symlink `.par` files.
- Validate every native output entry is a regular file (no symlinks, directories, hard-coded parent warp from another corpus or foreign files) and include `otype.tf`, `oslots.tf`, `otext.tf` plus at least one `catss_alignment_id.tf` feature. Reject unexpected file extensions (allow native `.tf` and `.tsv` files only), no fake missing files.
- Publish with no-replace hard links into Agora-owned staging. If validation/copy fails, do not retain partial files, and remove private native child. Never write outside staging or into source/parent. Agora is responsible for transactional final promotion.
- Do not run `catss-tf fetch` or any network action; the manifest acquisition is `user-local` only, and Agora execution network policy is `deny`.
- An **empty staging root** is required; no overwriting even when foreign contents appear during execution.
- This is one standalone artifact; do not bundle a BHSA or LXX parent warp or claim such compatibility.

## Sources

- https://github.com/alexsosn/Agora/blob/main/registry/schema/materializer-plugin.schema.json
- https://github.com/alexsosn/CTC-TF/blob/master/agora.materializer.json
- https://github.com/alexsosn/CTC-TF/blob/master/src/ugarit_context_parsing/agora_adapter.py
- https://github.com/alexsosn/Agora/issues/135
- https://github.com/alexsosn/Agora/issues/221
- CATSS-TF `src/catss_tf/canonical_materializer.py`, `tests/test_canonical_materializer.py`, `LICENSE_SCOPE.md`.

## Review finding — full real CATSS requires explicit diagnostic allowance

After implementing the first adapter, an independent cross-check of `.github/workflows/ci.yml`, step **Materialize complete canonical corpus**, found that the *actual pinned 46-file source* is only accepted with the explicit reviewed native option:

```python
allowed_validation_codes = {
    "invalid_lxx_reference",
    "malformed_continuation",
    "unsplit_row",
}
```

Native `materialize_corpus` defaults to allowing **none**. A v1 Agora manifest with no such flags therefore could only materialize diagnostic-clean subsets, and would **fail on the full real snapshot**, despite claiming general CATSS corpus materialization. This was not documented in the initial plan and is a blocking user-facing defect discovered before merge.

Decision: preserve the **strict default** for direct `python -m catss_tf.agora_adapter ...`; expose explicit repeatable `--allow CODE`, forward exactly the selected code strings into native `materialize_corpus(..., allowed_validation_codes=...)`. Agora's immutable reviewed root manifest must list each of these three known source diagnostics **literally in its `execution.args`**; describe them as explicit acknowledged source anomalies, not trust bypasses, and never allow `unknown_annotation`, `unknown_mt_strategy_siglum` or mapping/parent drift by default. The native materializer retains per-finding ignored-diagnostic provenance in `catss-diagnostics.tsv` and continues to validate all source rows. The wildcard `*.par` still accepts user-local subsets; no exact source hash is asserted beyond native manifest SHA-256 fingerprints.

Add a **real pinned 46-file adapter invocation** to existing opt-in complete-catss-audit after canonical reload: precreate an empty stage, execute `agora_adapter.main([... --allow CODE ...])`, then reload as a standalone Text-Fabric corpus with exactly 349,670 alignment slots, 6,218 reference nodes, intact `catss-diagnostics.tsv` and absence of the private child. Preserve the existing full native audit; this is deliberate additional coverage of the public Agora path. Never publish/upload generated corpus artifacts.
