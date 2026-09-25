# ADR-0001 — CATSS source is a local raw parallel directory

**Status:** accepted  
**Date:** 2026-09-25  
**Issue:** #3

## Context

CATSS-TF needs the Hebrew–Greek CATSS alignment to generate two TF enrichment modules. The raw CATSS parallel files remain publicly reachable from CCAT, but the accompanying user declaration imposes conditions beyond ordinary open-source licensing, including non-commercial restrictions and downstream-access/registration obligations.

Two public parser projects establish useful prior art:

- `codykingham/CATSS_parsers`: MIT, raw-file parser/downloader toolkit;
- `curran-gehring/catss`: CC BY-NC 4.0 source, convenient SQLite/query layer.

CATSS-TF itself is MIT licensed and should remain usable without importing a non-commercial software dependency. It also does not need CATSS LXX morphology because the target LXX TF corpus supplies its own text/morphology.

## Decision

For v0.1:

1. CATSS-TF operates on an explicit local directory containing CATSS parallel `*.par` files.
2. The user may supply an existing directory or explicitly invoke a CATSS-TF downloader that retrieves the files directly from the upstream CCAT host.
3. CATSS-TF does not redistribute CATSS files and does not decide or enforce the user's compliance with upstream terms; that remains the user's responsibility.
4. Only direct-child `*.par` files are parser inputs; discovery is non-recursive.
5. Before parsing, CATSS-TF computes a deterministic source manifest containing filename, byte size, and SHA-256 for every input file.
6. The production parser will be implemented in CATSS-TF against the raw `.par` format. MIT-compatible prior art may be reused with attribution when appropriate; CC BY-NC implementation code is not copied into CATSS-TF.
7. CATSS LXX morphology is not required for v0.1.
8. Real CATSS data are not committed as fixtures. Parser/downloader tests use synthetic data and fake network transports.

## Consequences

### Positive

- the repository and its CI remain independent of CATSS corpus data;
- users retain responsibility for upstream CATSS/CCAT terms;
- first-time setup can be automated without CATSS-TF redistributing a corpus snapshot;
- the parser receives the smallest dataset actually required;
- materialization is reproducible against exact source bytes;
- Agora can invoke the downloader/materializer while files still flow directly from CCAT to the user's environment.

### Costs

- downloader behavior depends on the continued availability/layout of the upstream CCAT host;
- documentation must distinguish CATSS-TF's MIT software license from CATSS data terms;
- integration tests against the real corpus remain opt-in and must not publish downloaded artifacts.

## Reconsideration trigger

Revisit this ADR if CCAT changes its distribution host/layout, publishes new machine-readable acquisition metadata, or the required source set expands beyond the parallel files.
