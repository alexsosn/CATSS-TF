# Research — #106 predictable CATSS download staging path

## Grounding in current code

On `main@cddf57edba08e88120d2ba0cd53340f2eaf27e61`,
`src/catss_tf/source.py::download_parallel_source` handles one
validated HTTPS byte payload with a deterministic sibling filename
`<file>.par.part`, written by `pathlib.Path.write_bytes`, followed
by `Path.replace` and `unlink(missing_ok=True)`.

If a prior operator run, another concurrent download, or a local
actor has created that path as a symbolic link, Python opens the
linked destination for writing. The subsequent replacement can
complete while the symlink target's data has been overwritten.
A pre-existing regular `.part` is also overwritten/removed. This
risks an unrelated user's local files and breaks concurrent workers'
staging isolation; no speculative network threat is required.

This is distinct from #44's upstream incomplete HTTPS certificate
chain. Production already verifies TLS and prohibits origin-changing
and HTTPS-to-HTTP redirects. Do not weaken any existing checks.

## Alternatives

- Reuse deterministic `.part`, reject symlinks only: still loses on
  stale regular partial files, concurrent invocations, and TOCTOU.
- Use `open(..., 'xb')` on deterministic name: rejects collisions
  but prevents easy restart when stale files remain.
- **Chosen**: `tempfile.mkstemp(dir=target.parent, prefix=...)`
  creates a unique sibling with O_EXCL; write via its open file
  descriptor, `os.replace` to the requested name on the same FS,
  and unlink only that unique name in a `finally` block.

## Limits

Atomic replacement is **per-file**, not an atomic multi-file
transaction. A concurrent writer intentionally replacing the same
requested final target still has last-writer-wins semantics. This
hardening specifically prevents staging-path collision/symlink
clobber and leaves the user-visible acquisition contract unchanged.
No corpus data is committed to the Git repository.
