# Plan — issue #45 GitHub parent install

1. Commit RED metadata-contract tests verifying `[tf]` installs
   `text-fabric[github]>=13.1,<14` and dev likewise.
2. Add a clean installation smoke to release CI that builds a wheel,
   creates an isolated venv, installs the wheel with `[tf]` (dependencies
   **enabled**) and verifies that the `github` module and
   Text-Fabric's Github backend `Capable` initialize successfully.
   Use a fresh venv; no real corpus download on every PR.
3. Confirm tests fail on the existing metadata.
4. Update only the dependency spec and relevant researcher installation docs.
5. Run Python 3.11/3.12/3.13 pytest, ruff, mypy, release smoke and complete
   audit on exact final head.
6. Independent adversarial review against source package metadata, resolved
   installed wheel, optional/base install separation, documentation and
   Python-version compatibility before merge.
