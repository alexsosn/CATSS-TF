# Issue #168 — broken copy-paste shell installers

Research snapshot: `main` at `737bdead6da9dc883eb35bbcac1f50e4b04d0926` (2026-11-18).

## User-visible evidence

Both `README.md` and `RELEASE_NOTES.md` contain two ```sh``` code fences that begin with `pip install` followed by **two literal backslash characters** at end of that line. They are on README lines 23/30 and release notes lines 58/65. The two lines read, literally, `pip install \\`` (two backslashes before newline). The next line is a URL or quoted install target. A single trailing backslash is required for POSIX shell line continuation, as already correctly used in `docs/integration.md`.

Two literal backslashes escape each other. Thus a copy-pasted example first invokes `pip` with a literal backslash package argument and then attempts to execute the URL as a separate command. The v0.1.0 release assets exist, but copy-paste commands are broken before dependency installation. No upstream corpus data, new package, or parent-Text-Fabric integration is involved.

## Boundary

Fix only the shell continuation in the four affected examples. Preserve existing install targets and descriptions, including differences between already-published v0.1.0 and current-source code. No release, public API, package metadata, corpus, TLS trust or data licensing change. This issue is a bounded onboarding slice of #151/#149; it cannot close either parent or Libronix parity #126.

## Test evidence to obtain

Extract the **actual fenced commands**, run each against a shell-local `pip()` stub to capture arguments (no network or packages). Before the fix, the command should fail/produce more than one command. After the fix, each must invoke `pip` once with exactly `install` and the single target string. Inspect shell behavior separately from test implementation; run exact-head CI and independent adversarial review.
