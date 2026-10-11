# Plan — issue #44 verified CCAT acquisition UX milestone

1. **Research** existing download/CLI implementation, clean Ubuntu
   certificate-failure logs, source URL redirects, and evidence for mirror/CA.
   Document that neither a trusted replacement chain nor live mirror has
   been proved.
2. **RED-first**: failing tests for explicit PEM CA bundle loading,
   HTTPS-only `base_url`, HTTPS-to-HTTP redirect rejection, actionable
   certificate-chain failure, CLI argument forwarding, and no change to
   default single-argument downloader mocks/local fingerprints.
3. **Implement** optional strict verified TLS context, audited redirect
   handler, CLI `--ca-bundle` and `--base-url`, narrow fail-closed
   messages. No unsafe fallback or auto-trust.
4. **GREEN** Ruff, format, mypy, pytest Python 3.11–3.13, release
   smoke, full 46-source semantic audit, and exact-head check statuses.
   This complete-source audit is NOT TLS verification.
5. **Independent adversarial review** of exact committed diff:
   challenge HTTP credential/prefix tricks, redirect downgrade,
   escaped/traversal filenames, invalid CA, spoofed trust assumptions,
   and source overwrite integrity; rerun RED/GREEN for findings.
6. Merge only if independent review is nonblocking. Keep #44 open until
   actual verified clean-Ubuntu acquisition is demonstrated against a
   clearly authenticated origin.
