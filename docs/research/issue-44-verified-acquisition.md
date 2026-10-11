# Research — issue #44 CCAT TLS acquisition fail closed

## Observed failure and boundaries

On clean GitHub-hosted Ubuntu 24.04 / Python 3.11, current production
`catss-tf fetch` raises `ssl.SSLCertVerificationError` on
`https://ccat.sas.upenn.edu/gopher/text/religion/biblical/parallel/01.Genesis.par`.
Explicit `certifi==2026.7.22` did **not** repair the local issuer failure
(issue #44, actual Actions runs 36242341730 and 36242428596).
A full 46-file source audit currently runs using a research-only unverified
SSL context, which proves source-format behavior but **is not** a validated
production acquisition path. Do not copy its transport into production.

`src/catss_tf/source.py` delegates directly to `urllib.request.urlopen`
with the default TLS context. The Python API supports `base_url` but the
`catss-tf fetch` CLI does not expose a base-url override or a custom
trust anchor. Python's standard redirect processing may accept an HTTPS
response redirecting to HTTP; that would defeat the intended TLS boundary.
Normal tests mock the downloader; they do not exercise TLS validation.

The CCAT upstream still publishes the 46 CATSS parallel filenames under
its HTTPS directory index. A successful browser proxy fetch does not prove
that clean client OpenSSL trust accepts the supplied chain. No verified
independent complete mirror or independently authenticated intermediate CA
was established in this research pass. Therefore claiming a live fix to the
default HTTPS endpoint would be scientifically and operationally unsound.

## Narrow milestone and security invariant

Give users a **verified-only acquisition path** they can configure, while
retaining the existing SHA-256/byte-size source manifest and non-empty
overwrite behavior:

- `--ca-bundle PATH` / `ca_bundle=...`: explicitly chosen PEM CA
  bundle, loaded with `ssl.create_default_context(cafile=...)`. No
  `CERT_NONE`, `check_hostname=False`, or unverified context.
- `--base-url HTTPS_URL`: explicit *HTTPS-only* operator-supplied
  authoritative mirror/base host. Reject HTTP and credentials in source URL,
  including redirect targets. No implicit change of origin.
- On certificate failure, surface actionable guidance to use a verified
  chain/mirror or an already-local source directory. Do not provide a
  helper that downloads or trusts an unverified certificate itself.
- Preserve already-supported exact bytes, per-file fingerprints, source
  names, and the two-argument public API.
- All new tests stub networking and prove TLS context/redirect restrictions
  without relying on the live CCAT server.

The default endpoint remains potentially unavailable until a genuine live
verified OpenSSL check succeeds. **Keep issue #44 open** after merging
this opt-in acquisition milestone unless an opt-in live verified check
demonstrates actual default or operator-configured successful acquisition.
Do not mistake CI's unverified source-format audit for TLS remediation.

## Future live-validation gate

On a trustworthy client with a verified organization-approved CA
intermediate or an independently authenticated HTTPS alternative:
`catss-tf fetch --ca-bundle /path/to/verified-ccat-ca.pem
--base-url https://validated.host/path /tmp/catss-test`.
Inspect the successful certificate chain and source manifest, then
document origin/chain fingerprint and upstream data/license equivalence.
Do not embed third-party source bytes or a private CA in this repo.
