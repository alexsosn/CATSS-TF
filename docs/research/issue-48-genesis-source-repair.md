# Research — issue #48 Genesis 6:19 known CATSS source repair

## Scope

The complete-CATSS audit for issue #40 exposed one Genesis row that contradicts
CATSS-TF's strict translation-technique invariant:

```
--= '' =H/BHMH	TW=N KTHNW=N
```

This research determines whether the invariant is wrong or the upstream row is a known
source anomaly.

## Evidence

### Current CCAT source

The current upstream `01.Genesis.par` contains the row under Gen 6:19. Nearby rows use
the normal CATSS LXX-plus notation `--+`, including rows that also carry reconstructed
Hebrew in column B.

Upstream:
https://ccat.sas.upenn.edu/gopher/text/religion/biblical/parallel/01.Genesis.par

### CATSS model

CATSS documentation distinguishes:

- Hebrew column A: formal MT↔LXX equivalents;
- Hebrew column B: selected presumed/reconstructed Hebrew equivalents retroverted from
  the Greek when the LXX appears to reflect a different Vorlage.

See Emanuel Tov, “A Computerized Database for Septuagint Research” and the published
description of the parallel-aligned Hebrew/Greek database.

### Existing parser prior art

`codykingham/CATSS_parsers/patch_catss.py` contains an explicit repair for this same
Genesis source row. The patch replaces the malformed semantic form `--=` with:

```
--+ '' =H/BHMH	TW=N KTHNW=N
```

That evidence is specific enough to treat the current source row as a known upstream
typo rather than as a new general CATSS notation.

## Decision R48-1 — keep technique-v1 strict

Do not weaken `derive_technique_state()`. A Hebrew-empty Greek alignment still needs
explicit LXX-plus or transposition evidence. Accepting arbitrary zero↔Greek rows would
hide genuinely malformed input.

## Decision R48-2 — exact-match repair only

The parser may repair this anomaly only when all of the following match:

- source basename: `01.Genesis.par`;
- original MT cell: `--= '' =H/BHMH`;
- original LXX cell: `TW=N KTHNW=N`.

Lookalike rows remain untouched and therefore continue to fail closed if they violate
downstream invariants.

## Decision R48-3 — preserve source provenance

The repair changes semantic interpretation, not the source record.

The IR must keep:

- the original physical `raw_lines`;
- original `mt_raw` / `lxx_raw`;
- the original bytes as the basis of `catss_alignment_id`.

Parsed column-A/column-B state, plus/minus classification and lexical counts may use the
corrected semantic form.

## Decision R48-4 — make the repair queryable

Silent normalization violates the repository's upstream-anomaly rule. The repaired
alignment therefore gets a typed `source_repair` annotation with provenance family,
original MT cell as `raw`, and corrected semantic MT cell as `payload`.

Projection schema must recognize `source_repair` as a query-native semantic kind so
BHSA/LXX modules do not lose the fact that the input required a known repair. The
canonical corpus already preserves typed annotations as first-class nodes.

## Decision R48-5 — no generalized patch table in this ticket

Cody Kingham's historical patch file contains other source-specific repairs. They have
not been independently revalidated against the current CCAT snapshot here. This issue
fixes only the empirically blocking Genesis row. Additional repairs require their own
evidence and tests.
