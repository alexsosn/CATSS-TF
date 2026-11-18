# Issue #168 — install command regression plan

1. No overlapping open PR: the only open CATSS-TF PR #42 is a pinned-parent case-study draft. Scope #168 under documentation/onboarding #151.
2. RED: commit `tests/test_docs_install_commands.py` before altering either document. Parse each `sh` fence whose first line begins `pip install`, then execute verbatim via POSIX `sh` with an injected `pip()` function that prints its arguments. Assert exactly two installer fences per document and exactly one `pip install TARGET` per fence. This checks the documented **shell execution**, not a hard-coded count of slashes, with zero network calls.
3. Record an observed pytest failure on the test-only head. Confirm the failure is at the intended command, not test collection, linting, package import or a dependency.
4. GREEN: change precisely four doubled backslash line continuations to single backslashes in README and RELEASE_NOTES. No code behavior, dependency or URLs change.
5. Verify focused test in a fresh environment plus exact-head Python 3.11/3.12/3.13, release smoke, Context-Fabric, full 46-file canonical source and Agora integration gates. Review diff independently with negative cases (escaped backslash, whitespace, quotation of optional extras). Do not merge on queued/partial CI.
6. Update #168 with evidence; merge after final-head independent review and all required checks. Keep #151/#149/#126 open.
