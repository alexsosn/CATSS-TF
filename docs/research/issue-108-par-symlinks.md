# Research — #108 direct-child CATSS .par symlinks bypass source provenance

## Reproduced by code inspection of main@9b26a61

`inspect_parallel_source()` filters `root.iterdir()` by `path.is_file() and path.suffix == ".par"`, then `_manifest_for_paths()` computes `path.stat().st_size` and `_sha256(path)`, both following a link. It therefore accepts `source/01.Genesis.par -> /outside/unrelated-file` as source data. A dangling `.par` link is excluded instead of diagnosed.

`download_parallel_source()` skips `target` if `target.is_file() and target.stat().st_size > 0 and not overwrite`. An existing link to unrelated nonempty bytes is regarded as a successfully acquired CATSS file and fingerprinted. #106 hardened only the *temporary* staging name; no protection was added for the final on-disk file being *read*.

This problem requires no hostile network, invalid TLS certificate, or insecure URL. The trust boundary is the local source directory, including accidental operator-managed links. CATSS source data are user-acquired and fingerprinted, so provenance should not silently refer to an external target.

## Design options and choice

- Following links with a warning still admits ambiguous identity and broken-link omission.
- Checking link targets stay below root with `resolve()` still allows link swaps and ordinary legitimate source files do not need links. More complex than warranted.
- Chosen: reject all direct-child `.par` symlink entries (including dangling) at inspection time, and reject requested target symlinks before network/write in download. Parent *directory* may itself be a deliberate symlink.
- Preflight all requested names before network so later unsafe names do not leave partial acquisition of preceding names. Do not alter the allowlisted names or verified HTTPS transport.
- Only the on-disk snapshot at check time is guarded; no claim of protection against hostile concurrent filesystem changes/TOCTOU in a writable directory.

## Regression contract

Ordinary files, non-recursive filtering, and normal downloader staging remain unchanged. Symlinks pointing inside or outside the source, and dangling `.par` symlinks, fail with a typed exception and without reading target bytes. For a two-name download with the second name symlinked, the first must not be fetched. Dataset operators needing symlinked upstream files can copy them into an owned directory (or resolve the real directory as the source root). No CATSS files enter git.
