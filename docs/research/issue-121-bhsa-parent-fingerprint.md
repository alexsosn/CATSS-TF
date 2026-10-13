# Issue 121 — research: verifying BHSA parent feature bytes before a CATSS projection

## Actual contracts inspected (2026-10-12)
- The upstream BHSA materializer is `materialize_bhsa(source, absent_output, *, provider: BhsaVerseProvider, parent_probe: BhsaParentProbe)` in `src/catss_tf/bhsa_materializer.py`. It calls `validate_bhsa_parent(parent_probe)` and fails before publication on profile mismatch.
- `src/catss_tf/bhsa_schema.py` pins `ETCBC/bhsa`, TF version `2021`, checkout tag `v1.8.1`, commit `b112c161cfd21eae403d51a2733740d8743460e7`, slotType `word`, maxSlot 426590, maxNode 1446831 and section types `book/chapter/verse`. Critically `BHSA_FEATURE_BLOB_SHAS` already lists eight **Git blob** hashes for the exact mapping-critical raw features: `otype`, `oslots`, `book`, `chapter`, `verse`, `g_cons_utf8`, `g_word_utf8`, `qere_utf8`. `BhsaParentProbe.feature_blob_shas` is optional: normal `validate_bhsa_parent` does not **require** fingerprints unless `require_blob_hashes=True`. Therefore a hypothetical Agora CLI that constructs a probe out of hardcoded checked-out version constants could pass without verifying any source data.
- Agora `scripts/agora_materialize.py` now has `ParentBinding(path,resource_id,version,source_revision,trusted,relative_path)` and manifest `parent_input` plus `{parent}`, `{parent_version}`, `{parent_revision}` placeholders; **the registered host**, not the CATSS plugin, authenticates trusted provenance/immutable resource identity and mounts the parent read-only when `--sandbox required`. A directory path by itself must never constitute trust. The future BHSA adapter must verify that the mounted raw mapping-critical feature contents are the **pinned** ones, then load TF from the same mount, construct `TextFabricBhsaProvider`, and materialize only features without copying the parent warp.
- The current Agora catalog has BHSA resource `bhsa`, repository `ETCBC/bhsa` and data license CC BY-NC 4.0. Parent may be a prepared TF version directory, not the root of the Git repository; use exactly the directory supplied in the trusted mount, do not follow arbitrary relative paths, and do not attempt to fetch GitHub inside the no-network sandbox.
- Git blob ID (historical Git SHA-1) of a raw file is SHA1(`b"blob " + decimal_file_size + b"\\0" + complete_file_bytes`). It differs from ordinary SHA1(content). This is a compatibility/content identity check against pinned known blobs, not a replacement for Agora's trusted source revision or license verification. Compute via streaming `os.open` file descriptors with `O_NOFOLLOW` if supported, `fstat` before/after and bounded chunks; do not read enormous parent TF features all at once.

## Implementation boundary
This ticket creates a reusable, **read-only** exact-feature-content preflight function. It has NO right to declare arbitrary source paths `trusted`, NO new registered `catss-bhsa` materializer ID, no BHSA data download, no duplicate warp. Test with an injected tiny set of expected fixture blob hashes for a positive streaming roundtrip; also test production constants are selected by default and that a synthetic 8-file parent cannot fool them. A real immutable BHSA 2021 mount, exact node/count readback, and full managed host integration still must be tested before enabling an executable producer on the manifest.

## Grounded immutable upstream Git object verification (2026-10-12)

Used the GitHub Git Trees API on `ETCBC/bhsa` to follow exact pinned commit
`b112c161cfd21eae403d51a2733740d8743460e7` → `tf/` tree
`0070f11a59187cc60d581ffe03bd50585459b0c0` → `tf/2021/` tree
`572fd11e9f11a1488ee94191e64b57e654e4e037`. Compared all **eight**
mapping-critical feature blob object IDs (not merely the five entries without
numeric digits in their names) against `BHSA_FEATURE_BLOB_SHAS`:

| feature | Git blob ID from pinned tree | expected pinned ID match |
| --- | --- | --- |
| otype | ecc4d0ecd388bd673d0aebfa8ab2a81508bec23c | yes |
| oslots | b389833f7624bb252dd2cf25cf798d4a6a82cc1b | yes |
| book | 70407385b60568eaeb44dbeb45f3a7dfafd2a6af | yes |
| chapter | 7834c771c0a42fe81b21a8284e95e4226a448108 | yes |
| verse | 06046e58967de2a46b6e976584bd29c98fe2fdab | yes |
| g_cons_utf8 | 8b1b0513cb7ae061ba180c8d6cdbfdb496aa4d44 | yes |
| g_word_utf8 | f78cce06300190ed5c8ef9ca1fa72b16cdfca5eb | yes |
| qere_utf8 | c4540df6d0068776ac4bb4475a28c7a403a8904e | yes |

Reference: `https://api.github.com/repos/ETCBC/bhsa/git/trees/572fd11e9f11a1488ee94191e64b57e654e4e037`.
This is direct **Git object metadata**, not a download of licensed BHSA
content or a positive run of this verifier on a local 2021 Text-Fabric parent.
Actual consumer-facing loading still requires Agora's trusted immutable
read-only source snapshot and a separate real parent-run test.

## Independent security correction after initial implementation

The first candidate exposed `expected_blob_shas` as a public keyword argument,
which would let an integration caller accidentally substitute its own hashes
and thereby defeat the reason for a **pinned** parent. A RED-first regression
in `tests/test_bhsa_parent_files.py` now inspects the public signature and
asserts it cannot accept this override. Only unit fixtures patch the module's
constant in an isolated test process; the production entrypoint always
compares against the module-imported pinned `BHSA_FEATURE_BLOB_SHAS`.
This does not turn arbitrary parent directories into trusted sources:
provenance is separately authenticated by Agora's `ParentBinding`.
