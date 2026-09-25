# ADR-0001 — CATSS source is user-supplied raw parallel files

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

1. CATSS-TF accepts an explicit **local directory** supplied by the user.
2. The directory contains the CATSS parallel `*.par` files to be processed.
3. CATSS-TF performs **no network acquisition** of CATSS.
4. Only direct-child `*.par` files are source inputs; discovery is non-recursive.
5. Before parsing, CATSS-TF computes a deterministic source manifest containing filename, byte size, and SHA-256 for every input file.
6. The production parser will be implemented in CATSS-TF against the raw `.par` format. MIT-compatible prior art may be reused with attribution when appropriate; CC BY-NC implementation code is not copied into CATSS-TF.
7. Real CATSS data are not committed as fixtures. Parser tests use synthetic records designed to exercise format structures.

## Consequences

### Positive

- the repository and its CI remain independent of restricted corpus data;
- users retain responsibility for obtaining CATSS under upstream terms;
- the parser receives the smallest dataset actually required;
- materialization is reproducible against exact source bytes;
- Agora can invoke the materializer without becoming a CATSS data distributor.

### Costs

- first-time installation cannot automatically fetch CATSS;
- documentation must explain the required local source path;
- integration tests against the real corpus are opt-in and require user-acquired data.

## Reconsideration trigger

Revisit this ADR only if a contemporary CATSS rights holder/distributor provides a clear acquisition mechanism that CATSS-TF can legally and operationally implement, or if the project receives explicit permission covering automated distribution/acquisition.
