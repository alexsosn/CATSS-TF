# Initial research

**Date:** 2026-09-25  
**Scope:** feasibility and architecture for CATSS → Text-Fabric materializers.

This document records the initial evidence behind the bootstrap design. It is not a claim that unresolved mapping questions are already solved.

## R-001 — CATSS contains a scholarly Hebrew–Greek alignment, not only parallel verse text

The CATSS parallel files align elements of MT/BHS with the Greek Old Testament and encode more than simple word pairs. CATSS documentation and later descriptions distinguish formal MT↔LXX equivalents from additional information about the presumed Hebrew Vorlage and translation technique.

Relevant CATSS markup includes plus/minus relations, transpositions, Hebrew column-B retroversions, Ketiv/Qere context, and more specialized translation-technique/textual sigla. Cody Kingham's parser documentation is especially useful because it reconstructs differences between the historical documentation and the currently downloadable files.

Sources:

- Emanuel Tov, “The Use of a Computerized Database for Septuagint Research: The Greek-Hebrew Parallel Alignment,” BIOSCS 17 (1984), 36–47: https://ccat.sas.upenn.edu/ioscs/journal/volumes/bioscs17.pdf
- CATSS/CCAT historical and distribution context: https://ccat.sas.upenn.edu/~jtreat/rs/rscpuhx.html
- codykingham/CATSS_parsers: https://github.com/codykingham/CATSS_parsers
- parser notes on the parallel format: https://github.com/codykingham/CATSS_parsers/blob/master/parallel_readme.md

**Implication:** the canonical intermediate representation must preserve CATSS judgments and source markup, not collapse the dataset to one Hebrew token ↔ one Greek token.

## R-002 — Existing open tooling offers two different upstream integration choices

`codykingham/CATSS_parsers` is MIT-licensed parsing/download tooling. It is primarily a parser toolkit and documents the complicated `.par` format. It does not package CATSS data because of the CATSS data license.

`curran-gehring/catss` is a newer Python package that downloads CATSS data, builds SQLite, exposes a CLI and query API, decodes Unicode, and preserves alignment flags. It is therefore easier to consume operationally, but its source code is CC BY-NC 4.0 and CATSS data remain separately restricted.

Sources:

- https://github.com/codykingham/CATSS_parsers
- https://github.com/curran-gehring/catss

**Implication:** CATSS-TF must not copy CC BY-NC implementation code into the MIT project. The first implementation issue must make an explicit dependency/adaptation decision. A clean parser built from documented CATSS format, reuse of MIT-compatible code, or an optional runtime dependency are all possibilities; none is selected merely by convenience.

## R-003 — CATSS data must stay outside this repository

The CATSS ecosystem has historically distributed its files for non-commercial research/educational use under separate terms. Both modern parser projects explicitly avoid treating the data as permissively licensed source code.

Sources:

- https://github.com/codykingham/CATSS_parsers
- https://github.com/curran-gehring/catss
- https://ccat.sas.upenn.edu/~jtreat/rs/rscpuhx.html

**Implication:** CATSS-TF is materializer-only. CI cannot depend on downloading CATSS. Tests must be synthetic/minimal and ordinary repository releases contain software only.

## R-004 — Text-Fabric modules cannot supply their own independent node universe

Text-Fabric defines a dataset as a warp (`otype`, `oslots`) plus other features. A module contains only additional features (“wefts”) constructed around the warp of the dataset with which it is loaded.

Text-Fabric's dataset modification API can create new node types only by writing a new derived dataset. That is a different artifact from a normal attachable module.

Sources:

- https://annotation.github.io/text-fabric/tf/about/datamodel.html
- https://annotation.github.io/text-fabric/tf/dataset/modify.html
- https://annotation.github.io/text-fabric/tf/core/fabric.html

**Implication:** `catss-bhsa` and `catss-lxx` must not create `alignment` nodes. Alignment identity is represented as features attached to existing parent nodes. If a future use case genuinely requires alignment nodes, it requires a separate derived-dataset design and ADR.

## R-005 — BHSA is a suitable Hebrew parent but version identity matters

ETCBC/BHSA is already distributed in Text-Fabric and contains multiple immutable/fixed dataset versions. Its repository explicitly describes versioned TF data and a family of attachable enrichment modules.

Source:

- https://github.com/ETCBC/bhsa

The BHSA README currently lists CC BY-NC 4.0 for the data.

**Implication:** the materializer must resolve CATSS Hebrew against a specific supported BHSA warp/version. Generated module files are valid only for the parent warp against which they were materialized. The initial implementation should target one explicit BHSA version before claiming broader compatibility.

## R-006 — CenterBLC/LXX is a natural Greek parent

CenterBLC/LXX provides Rahlfs 1935 in Text-Fabric and states that its direct source descends from CATSS LXX material. It exposes version `1935` and decomposes CATSS-style morphology into TF features.

Source:

- https://github.com/CenterBLC/LXX

**Implication:** Greek-side mapping may be substantially easier than Hebrew-side mapping because the parent corpus and CATSS share ancestry. This must still be verified token-by-token; common ancestry is not proof of identical token boundaries, verse numbering, or ordering.

## R-007 — Parent node numbers cannot be the cross-corpus identifier

BHSA node numbers are meaningful only in the BHSA warp. LXX node numbers are meaningful only in the LXX warp. A feature in one module that stores a naked node number from the other corpus would create an unstable hidden dependency.

**Implication:** both projections use a stable CATSS-derived alignment identifier such as a normalized source reference plus deterministic row/group identity. Parent node numbers are local outputs of materialization, not canonical identifiers.

## R-008 — The mapping problem is the central correctness risk

CATSS and the target corpora may differ in:

- tokenization and handling of inseparable Hebrew elements;
- Beta-code/Unicode normalization;
- Ketiv/Qere representation;
- punctuation and morphological separators;
- additions/omissions represented as placeholders rather than tokens;
- local and non-local transpositions;
- Psalms MT/LXX versification divergence;
- Greek subverses and superscriptions;
- reconstructed Hebrew column-B material that is not an MT token.

A naive “same verse + same position” mapping can silently produce false scholarly alignments.

**Implication:** mapping is validation-first. Each source token/span must be explained by an exact or explicitly classified mapping rule. Unresolved rows are reported, not coerced.

## R-009 — One canonical IR should feed both modules

Maintaining separate Hebrew and Greek CATSS parsers would create drift: a change in transposition, plus/minus, or source-row interpretation could yield incompatible modules.

**Implication:** parsing creates a single canonical alignment IR retaining both sides, flags, raw source provenance, and deterministic IDs. Two resolvers then map that same IR onto BHSA and LXX.

## Initial unknowns requiring focused issues

1. Which CATSS acquisition/parser path is legally and technically preferable for v0.1?
2. Which exact BHSA version should be the first supported parent?
3. Does CenterBLC/LXX 1935 preserve CATSS word boundaries closely enough for deterministic mapping across all covered books?
4. What is the complete CATSS alignment-group model for discontinuous/transposed rows?
5. Can one parent token participate in more than one canonical alignment group, and if so, what TF feature encoding is most queryable?
6. Which CATSS sigla should become normalized structured features in v0.1 versus retained raw/provenance text?
7. How should generated modules record upstream license/provenance metadata without embedding prohibited source data?


## R-010 — Current CATSS distribution still exposes the raw parallel files together with a restrictive user declaration

**Rechecked:** 2026-09-25.

The current CCAT parallel directory still exposes the `.par` files and the files named `00.UserDec.txt` / `00.user-declaration.txt` alongside the format documentation:

- https://ccat.sas.upenn.edu/gopher/text/religion/biblical/parallel/

The declaration is reproduced by current CATSS-consuming projects/services. Its conditions include: no commercial use without written consent; observance of text-specific restrictions; control of downstream access; requiring recipients of supplied material to observe the same conditions and register a signed declaration; proper acknowledgment; and reporting discovered errors.

A current reproduction is available at:

- https://biblecrawler.org/index.php/user-licence/

The modern `curran-gehring/catss` README independently describes the CATSS data as governed by the CCAT user agreement, not for commercial use without written consent, and states that CCAT no longer has an active maintainer after Robert Kraft's death in 2023:

- https://github.com/curran-gehring/catss

**Implication:** public availability of the raw files is not equivalent to a permissive data license. CATSS-TF must not treat an HTTP GET as sufficient evidence that downstream redistribution or automated third-party acquisition is authorized.

## R-011 — v0.1 should not automate CATSS acquisition

Both examined parser projects can fetch CCAT files directly over HTTP. Cody Kingham's MIT-licensed downloader downloads the parallel and morphology collections; `curran-gehring/catss` similarly fetches CCAT documentation, parallel files, and morphology files.

However, an automated downloader in CATSS-TF cannot itself satisfy the declaration's recipient-registration requirement, and CATSS-TF cannot verify that a user has completed whatever registration/permission process applies to their copy. The lack of an active CCAT maintainer makes inventing a replacement click-through particularly inappropriate.

Sources:

- https://github.com/codykingham/CATSS_parsers/blob/master/download_catss.py
- https://github.com/curran-gehring/catss/blob/main/catss/download.py

**Decision:** v0.1 accepts only a **user-supplied local CATSS parallel directory**. CATSS-TF does not download CATSS data. Acquisition remains the user's responsibility under upstream terms. A downloader may be reconsidered only after a separate issue establishes a valid contemporary acquisition/acceptance mechanism.

## R-012 — v0.1 needs only the CATSS parallel files, not the LXX morphology collection

The project goal is to project the Hebrew–Greek alignment and CATSS-specific alignment annotations onto BHSA and CenterBLC/LXX. The parent LXX corpus already supplies its own TF text/morphology layer, and BHSA supplies the Hebrew linguistic layer.

The CATSS `lxxmorph` collection would therefore duplicate parent-corpus information while expanding the acquisition and licensing surface.

**Decision:** the v0.1 source contract consumes `*.par` files from the CATSS **parallel** collection only. Morphology may later be consulted as a validation oracle if a focused issue demonstrates a need, but it is not part of the materializer's required source contract.

## R-013 — Parser implementation stays inside CATSS-TF and must remain MIT-compatible

`codykingham/CATSS_parsers` is MIT licensed and is valid prior art/reference material. `curran-gehring/catss` has a convenient package/API but its original source is CC BY-NC 4.0, which is a poor implementation dependency for an MIT materializer intended for general Agora distribution.

The newer package remains useful as an external behavioral/reference oracle during research, but CATSS-TF must not copy its CC BY-NC implementation into this repository.

Sources:

- https://github.com/codykingham/CATSS_parsers/blob/master/LICENSE
- https://github.com/curran-gehring/catss/blob/main/LICENSE

**Decision:** issue #4 will implement CATSS-TF's own parser at the raw `.par` boundary. It may use the published CATSS documentation and MIT-compatible prior art, with attribution where code is actually reused. The production package has no runtime dependency on `curran-gehring/catss`.

## R-014 — Source provenance starts with deterministic per-file fingerprints

The CCAT directory does not expose a versioned release identifier for the parallel corpus as a whole. File modification dates also vary by book and are not sufficient as immutable identifiers.

**Decision:** the minimum source provenance recorded by CATSS-TF is:

- source kind: `catss-parallel`;
- each direct-child `*.par` filename;
- byte size;
- SHA-256 digest.

Absolute local paths are operational input and are not part of canonical provenance. Materialization time belongs to the later generated-module metadata, not the source fingerprint.

The source inspector is intentionally non-recursive so that an accidentally selected broad directory cannot silently mix unrelated CATSS collections into the source set.
