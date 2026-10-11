# Plan — #106 secure temporary CATSS acquisition

1. Commit RED tests for a pre-existing sibling `.part` symlink
   pointing at an unrelated file and a stale regular `.part` file.
   The downloaded target must contain the right bytes, victim and
   stale files must remain unchanged, and the source manifest must
   fingerprint only the requested target. Confirm intentional pytest
   failure in CI after ruff and mypy.
2. Implement exclusive unique temporary sibling via `mkstemp`.
   Close the file descriptor with `os.fdopen`, write bytes,
   replace via `os.replace`, clean up only this invocation's
   newly allocated path. Avoid a fixed suffix, `follow_symlinks`,
   deleting any pre-existing `.part`, disabling HTTPS validation,
   or HTTP downgrade.
3. Add a failure-injection regression ensuring a failed final
   replacement preserves an existing destination and cleans up
   the allocated temporary file.
4. GREEN: ruff check+format, mypy, pytest 3.11/3.12/3.13,
   release smoke, complete 46-file source+canonical TF readback.
5. Independent adversarial review of exact final green commit:
   race boundaries, wrong unlink target, symlink behavior, resource
   descriptors, download exceptions, manifest correctness. If
   defects found, RED → fix → GREEN → re-review. Merge then close
   #106, leaving #44 open.
