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

**Implication:** public availability of the raw files is not equivalent to a permissive data license. CATSS-TF must not redistribute the CATSS corpus as if it were MIT-licensed; users remain responsible for the upstream terms that apply to their own acquisition and use.

## R-011 — v0.1 may automate direct user acquisition from CCAT

Both examined parser projects fetch CCAT files directly over HTTP. Cody Kingham's MIT-licensed downloader downloads the CATSS collections; `curran-gehring/catss` likewise downloads raw CCAT files at build time while keeping the data out of its own repository.

Sources:

- https://github.com/codykingham/CATSS_parsers/blob/master/download_catss.py
- https://github.com/curran-gehring/catss/blob/main/catss/download.py

The important distribution boundary is between **CATSS-TF redistributing CATSS data** and **software run by the user downloading data directly from the upstream CCAT host**. CATSS-TF does not need to police or simulate the user's compliance workflow.

**Decision:** v0.1 supports both:
- an already existing local CATSS parallel directory; and
- an explicit user-invoked downloader that retrieves the parallel `.par` files directly from CCAT into a local directory.

CATSS-TF documents the upstream terms and leaves compliance to the user. It does not bundle CATSS data, cache them in releases, or relicense downloaded files.

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


## R-015 — Preserve both CATSS Daniel parallel editions

The current `curran-gehring/catss` book registry describes 45 parallel files and deliberately gives `DanOG` no `par_file`, because that package chooses Theodotion as its canonical Daniel for its own application model. Its source comments nevertheless note that CCAT ships MT↔LXX parallel data in both Daniel editions.

Direct checks against the CCAT host on 2026-09-25 confirm that both files are available:

- `45.DanielOG.par`
- `46.DanielTh.par`

Sources:

- https://github.com/curran-gehring/catss/blob/main/catss/books.py
- https://ccat.sas.upenn.edu/gopher/text/religion/biblical/parallel/45.DanielOG.par
- https://ccat.sas.upenn.edu/gopher/text/religion/biblical/parallel/46.DanielTh.par

**Decision:** CATSS-TF's default acquisition set contains **46 parallel files**, including both Daniel OG and Theodotion. CATSS-TF is source-preserving and must not inherit an application-specific canonical-Daniel choice from another consumer.


## R-016 — Verse headers are authoritative boundaries; blank lines are not reliable enough

CATSS parallel files normally separate verses with blank lines, but the raw corpus has known corruptions in which blank lines and even stray verse-like strings appear inside data. The MIT `CATSS_parsers` patcher documents concrete cases in Exodus and Psalms where relying on blank-line structure would split a verse incorrectly.

The current `curran-gehring/catss` parser recognizes headers with a book token that may contain digits and slashes and an optional chapter component. Its comments record a previous silent-loss bug when Samuel/Kings headers such as `1Sam/K`, `1/3Kgs`, and `Ps151` were not accepted.

Sources:

- https://github.com/codykingham/CATSS_parsers/blob/master/patch_catss.py
- https://github.com/curran-gehring/catss/blob/main/catss/parse_parallel.py

**Decision:** CATSS-TF treats a recognized verse header as the authoritative verse boundary. Blank lines are ignored as layout. Nonblank content before the first header is not silently discarded; it becomes a parser diagnostic.

## R-017 — A CATSS row may contain MT column A, reconstructed column B, and LXX

CATSS rows are column-oriented. The MT side may split into:

- column A: the MT/BHS element used as the formal alignment base;
- column B: a selected retroversion or other Hebrew reconstruction, introduced by `=`.

The CATSS transcription alphabet for Hebrew does not use `=` as a letter, while CATSS annotation forms deliberately use it to introduce column-B material (including forms such as `=:`, `=%p`, and `=@...`).

Sources:

- Cody Kingham, `parallel_readme.md`: https://github.com/codykingham/CATSS_parsers/blob/master/parallel_readme.md
- MIT parser/normalization prior art: https://github.com/codykingham/CATSS_parsers
- independent current implementation notes: https://github.com/curran-gehring/catss/blob/main/catss/parse_parallel.py

**Decision:** the first `=` on the MT side begins column B. The raw MT cell is always retained, so later research can revise this interpretation without source loss.

## R-018 — Physical lines and logical alignment rows are not the same thing

CATSS uses `#` to continue rows that exceeded historical line-length/export constraints. The continuation may extend either the Hebrew or Greek column. A logical alignment therefore needs provenance over **one or more physical source lines**.

The raw corpus also contains orphan/corrupt physical lines documented by `CATSS_parsers/patch_catss.py`. Those manual patches mix genuine typo repair, normalization, and interpretive repair.

**Decision:** issue #4 performs only conservative `#` continuation joining. It does not import the large historical patch/normalization table. Each logical alignment stores all contributing physical line numbers and raw lines. Other malformed lines remain represented and receive diagnostics rather than being silently rewritten.

## R-019 — Transposition markup has several distinct observable forms

Current raw CATSS differs from older documentation. Cody Kingham documents that ordinary transpositions are predominantly marked with `^` / `^^^` in the downloadable corpus, with legacy `~` still occurring in Joel and Jonah. Other forms include:

- single `^`: local/order transposition indication;
- `^^^`: counterpart occurs elsewhere/non-local link;
- `{...}` or `{...TEXT}`: equivalent reflected elsewhere;
- `{..^TEXT}`: stylistic or grammatical transposition.

Source:

- https://github.com/codykingham/CATSS_parsers/blob/master/parallel_readme.md

**Decision:** the initial IR does not reorder either language. It records normalized transposition kinds while preserving the raw sigla. Legacy `~` is recognized as a local transposition marker rather than globally rewriting source bytes.

## R-020 — Alignment ratios are descriptive token counts, not textual-critical judgments

One CATSS logical row can contain multiple whitespace-separated Hebrew and/or Greek lexical elements. A shallow `m:n` ratio is useful downstream, but CATSS inline annotations can wrap lexical text and can also supply placeholders.

**Decision:** issue #4 exposes conservative lexical-candidate token tuples and a derived count ratio for straightforward rows. Raw cells remain authoritative. Translation-technique interpretation of ratios is deferred to issue #14.

## R-021 — Unknown markup must remain first-class evidence

The CATSS format contains documented unknown or ambiguous symbols, and the MIT parser research explicitly lists several. Treating an unrecognized `{...}` block as ignorable would destroy evidence.

**Decision:** every brace-delimited markup block is emitted as an annotation. Known forms receive a normalized kind; unrecognized forms receive `kind="unknown"` with the raw siglum unchanged. Other malformed/unsplit structures receive diagnostics. No nonblank source row is intentionally dropped.

## R-022 — Alignment IDs are source-derived content identities

The same CATSS logical alignment must receive the same identifier in both future TF projections, independent of BHSA/LXX node IDs and materialization order.

**Decision:** `alignment_id` is derived from:

- basename of the CATSS source file;
- raw verse header;
- contributing physical source line numbers;
- contributing raw source lines.

These components are hashed with SHA-256. The identifier changes when the relevant upstream source bytes or physical provenance change, which is desirable because generated modules must identify the exact source they were materialized from.


## R-023 — CATSS should be projected into native Text-Fabric feature shapes

BHSA and CenterBLC/LXX already expose linguistic information as ordinary per-node TF features, with word slots as the main lexical objects and `book/chapter/verse` as section features. A CATSS enrichment module is most useful if CATSS behaves the same way in TF queries.

**Decision:** the materializer schema is scalar-first:

- independent concepts become independent features;
- alignment cardinalities are integer features (`catss_mt_n`, `catss_lxx_n`) rather than a compound ratio string;
- stable yes/no concepts become boolean/presence-style integer features;
- stable closed classifications become short enum strings;
- same-parent relationships may use TF edge features where they genuinely model a relation;
- raw markup, arbitrary annotation collections, JSON, and delimited lists are not routine node features.

The parser IR remains lossless but also exposes these future TF atoms explicitly, so the later materializers do not need to deserialize or reinterpret parser blobs.


## R-024 — CATSS names the data; CCAT names the distribution host/infrastructure

The alignment dataset consumed by this project is part of **CATSS** (Computer Assisted Tools for Septuagint Studies), specifically the CATSS parallel Hebrew–Greek alignment. The University of Pennsylvania **CCAT** (Center for Computer Analysis of Texts) is the historical institutional infrastructure/host from which the CATSS files are currently distributed.

**Naming rule:**

- use **CATSS** for the project, dataset, parallel alignment, source files, parser, and generated annotations;
- use **CCAT** only for the upstream host/distribution location or institutional context.

Thus `source_kind="catss-parallel"` and the repository name `CATSS-TF` are correct, while constants such as `CCAT_PARALLEL_BASE_URL` correctly describe the network host rather than the dataset.

## R-025 — Validation must be independent of future TF serialization

Parser diagnostics and unknown CATSS structures must be measurable before any BHSA/LXX mapping or TF output exists. Otherwise a materializer could silently turn parser uncertainty into apparently authoritative node features.

**Decision:** validation operates on the canonical CATSS IR and produces typed findings plus scalar counts. It does not emit TF and does not require either parent corpus.

## R-026 — Source-line accounting requires the parser to expose its complete data-line set

Alignment rows already retain their contributing physical line numbers and parser diagnostics retain the line that caused them. That is not sufficient to prove absence of silent loss unless the parsed document also records the complete set of nonblank, non-header source data lines.

**Decision:** `ParallelDocument` records `data_line_numbers`. Validation compares that set against the union of alignment-owned lines and diagnostic lines. Any difference is a hard validation error.

## R-027 — Unknown markup remains preserved but unresolved

The parser deliberately preserves unrecognized brace markup as `Annotation(kind="unknown")` and unknown dot strategy sigla as `Annotation(kind="mt_strategy_siglum")`. Preservation prevents data loss, but it does not mean the structure is understood well enough for materialization.

**Decision:** validation emits typed unresolved findings for these annotations. Future explicit policy may allow selected finding codes, but the default validation policy requires zero unresolved findings.

## R-028 — Validation summaries must stay scalar and automation-friendly

Validation output should be directly usable by CLI/agents/CI and should not require parsing prose or a nested opaque blob.

**Decision:** summaries expose explicit integer fields including source files, verses, alignments, source data lines, accounted lines, unaccounted lines, parser diagnostics, unknown annotations, invalid IDs, duplicate IDs, errors, unresolved findings, and explicitly ignored/allowed findings.


## R-029 — v0.1 targets the immutable BHSA 2021 warp

The ETCBC/BHSA repository explicitly keeps historical data versions side by side and states that data in an existing version directory do not change; newer versions are stored separately.

For the `tf/2021` dataset:

- Git tag `v1.8.1` resolves to commit `b112c161cfd21eae403d51a2733740d8743460e7`;
- the v1.8.1 release notes state that the TF feature data are identical to the previous release and that the release adds NER specifications/tooling;
- the mapping-critical TF files at the v1.8.1 commit have the fingerprints recorded below;
- `otype.tf` declares `@version=2021`;
- nodes `1-426590` are the `word` slots;
- there are 39 `book` nodes, 929 `chapter` nodes, and 23,213 `verse` nodes;
- `otext.tf` declares section types/features `book,chapter,verse`.

Sources:

- https://github.com/ETCBC/bhsa
- https://github.com/ETCBC/bhsa/releases/tag/v1.8.1
- https://github.com/ETCBC/bhsa/tree/v1.8.1/tf/2021
- https://github.com/ETCBC/bhsa/blob/v1.8.1/tf/2021/otype.tf
- https://github.com/ETCBC/bhsa/blob/v1.8.1/tf/2021/otext.tf

A subtlety: the `__checkout__.txt` stored inside the tagged tree still names the preceding checkout, while the later repository marker names `v1.8.1 / b112...`. CATSS-TF therefore treats the Git tag/ref plus the actual TF feature fingerprints—not the embedded checkout marker alone—as the release identity.

**Decision:** the first `catss-bhsa` materializer supports **ETCBC/BHSA TF 2021 as published at release tag v1.8.1**. It does not resolve against an unversioned/latest BHSA warp.

## R-030 — Parent identity must be verified at the warp and mapping-feature level

A CATSS module is valid only for the exact parent node identities on which it was materialized. Checking the human-readable version string alone is weaker than checking the actual TF files.

GitHub currently reports the following Git blob IDs for the BHSA 2021 files used by CATSS-TF:

- `otype.tf`: `ecc4d0ecd388bd673d0aebfa8ab2a81508bec23c`
- `oslots.tf`: `b389833f7624bb252dd2cf25cf798d4a6a82cc1b`
- `book.tf`: `70407385b60568eaeb44dbeb45f3a7dfafd2a6af`
- `chapter.tf`: `7834c771c0a42fe81b21a8284e95e4226a448108`
- `verse.tf`: `06046e58967de2a46b6e976584bd29c98fe2fdab`
- `g_cons_utf8.tf`: `8b1b0513cb7ae061ba180c8d6cdbfdb496aa4d44`
- `g_word_utf8.tf`: `f78cce06300190ed5c8ef9ca1fa72b16cdfca5eb`
- `qere_utf8.tf`: `c4540df6d0068776ac4bb4475a28c7a403a8904e`

**Decision:** these files define the v0.1 mapping contract. Parent validation can compare their Git blob hashes when raw TF files are available; an adapter that cannot expose raw files must at minimum verify version, slot type/count, section contract, and feature presence before mapping.

## R-031 — BHSA represents Ketiv/Qere as alternative readings on one word slot

BHSA's default full-text format is:

`{qere_utf8/g_word_utf8}{qere_trailer_utf8/trailer_utf8}`

while the explicit ketiv format uses:

`{g_word_utf8}{trailer_utf8}`.

The sparse `qere_utf8` feature is described as a “word pointed-Hebrew masoretic reading correction”. Real values can contain embedded line breaks and multiple visual orthographic pieces while remaining attached to one BHSA word node.

Sources:

- https://github.com/ETCBC/bhsa/blob/master/tf/2021/otext.tf
- https://github.com/ETCBC/bhsa/blob/master/tf/2021/qere_utf8.tf

**Decision:** CATSS Ketiv/Qere alternatives resolve to the **same BHSA word slot**. A resolver must normalize a BHSA feature value as one slot value even when its display string contains whitespace/newlines; it must never manufacture additional BHSA token positions from qere display pieces.

## R-032 — Mapping identity uses text-bearing word features, not BHSA morphology

The BHSA parent offers rich morphology and syntax, but those annotations are not needed to establish CATSS token identity and could turn a textual mapping decision into a morphology-dependent heuristic.

**Decision:** v0.1 Hebrew resolution uses only structural location plus text-bearing word features:

- `book`, `chapter`, `verse`;
- `g_cons_utf8` as the primary consonantal word form;
- `g_word_utf8` as the pointed/accented ketiv form when needed;
- `qere_utf8` as the alternate masoretic reading when present.

Morphology may be used after mapping for research queries, but not to rescue a failed identity match.

## R-033 — CATSS-to-BHSA book identity must be explicit

BHSA book values are Latinized ETCBC names such as `Numeri`, `Josua`, `Samuel_I`, `Reges_I`, `Jesaia`, `Psalmi`, `Iob`, and `Chronica_I`. CATSS file stems and verse-header tokens use different conventions.

Some CATSS parallel sources are multiple Greek editions over the same MT book:

- `06.JoshB` and `07.JoshA` → BHSA `Josua`;
- `08.JudgesB` and `09.JudgesA` → BHSA `Judices`;
- `45.DanielOG` and `46.DanielTh` → BHSA `Daniel`.

Samuel/Kings CATSS headers may use Kingdoms notation (`1Sam/K`, `2Sam/K`, `1/3Kgs`, `2/4Kgs`), while BHSA uses `Samuel_I`, `Samuel_II`, `Reges_I`, `Reges_II`.

**Decision:** the CATSS source filename stem is mapped through a versioned explicit table to the BHSA `book` value. Book order, numeric position, and header spelling are never used as implicit identity.

## R-034 — Four CATSS parallel sources have no direct BHSA parent book in v0.1

BHSA 2021 contains the 39-book Hebrew canon. The 46 CATSS parallel sources also include:

- `17.1Esdras.par`
- `22.Ps151.par`
- `27.Sirach.par`
- `42.Baruch.par`

BHSA has no corresponding book nodes for these sources.

**Decision:** these four source files are explicitly `unsupported_for_bhsa` in v0.1. They remain available for the LXX projection. CATSS-TF does not try to map them transitively onto similar Hebrew passages.

## R-035 — Verse location narrows the search; it never proves word identity

BHSA 2021 has ordinary `book/chapter/verse` sections. CATSS MT-side references are the natural first filter for candidate BHSA words, but textual corpora can differ in tokenization and exceptional reference conventions.

**Decision:** the future BHSA resolver follows:

1. explicit CATSS source stem → BHSA book;
2. exact chapter/verse candidate section;
3. normalization and content agreement against BHSA word-slot forms;
4. only then assign BHSA node IDs.

“same verse + same ordinal word position” is forbidden as a successful mapping rule. Position may constrain or diagnose a match after textual agreement but cannot replace it.

## R-036 — BHSA licensing remains an upstream data concern

BHSA data are CC BY-NC 4.0 and require attribution; the repository README identifies DOI `10.17026/dans-z6y-skyh` and requires consent for commercial applications.

**Decision:** CATSS-TF's MIT license does not relicense BHSA. Generated `catss-bhsa` modules inherit whatever upstream restrictions apply to their BHSA-derived node association/data and are not bundled in this software repository.


## R-037 — LXX-plus alignments have no honest BHSA word target

A CATSS LXX-plus row has `mt_count=0`: the Greek contains material with no corresponding MT word. Therefore there is no BHSA word slot to which that alignment can be truthfully attached.

Assigning such a row to the previous/next/nearest BHSA word would create a synthetic textual claim and violate the project's no-positional-guessing rule.

BHSA does, however, provide existing `verse` nodes. A BHSA-side module can use the containing verse as the structural location for **verse-level aggregate/presence features** about Hebrew-empty CATSS alignments without inventing a word correspondence.

A further limitation follows from the no-new-node module model: multiple independent LXX-plus groups in one verse cannot each be represented as separate first-class BHSA-side alignment entities without packing IDs into a list/blob. That representation decision belongs to the TF feature-schema issue (#10), not to the parent resolver.

**Decision:**

- MT-bearing CATSS alignments target BHSA `word` slots after textual resolution;
- Hebrew-empty/LXX-plus alignments must never receive an invented word target;
- the BHSA projection may use the existing `verse` node for scalar aggregate/presence features about such rows;
- exact per-plus-group provenance may remain in the deterministic sidecar unless #10 finds a genuinely query-native representation;
- the LXX projection remains the natural word-level home for the Greek tokens themselves.


## R-038 — CATSS column A and BHSA share the BHS/MT reference sequence

The CATSS parallel alignment uses the Michigan–Claremont BHS text as the Hebrew reference. CATSS column A records MT elements as the formal alignment base, and CATSS verse references follow BHS versification even where the Greek verse numbering differs.

BHSA 2021 is likewise a BHS-derived corpus whose word slots expose consonantal word forms through `g_cons_utf8`.

Sources:

- https://ccat.sas.upenn.edu/~jtreat/rs/rscpuhx.html
- https://github.com/codykingham/CATSS_parsers/blob/master/parallel_readme.md
- https://etcbc.github.io/bhsa/features/g_cons_utf8/

**Decision:** the default Hebrew resolver does not use fuzzy sequence alignment. For each supported verse it first proves equality between the complete normalized CATSS MT-column-A word sequence and the complete normalized BHSA word-slot sequence. Node assignment by sequence position happens only **after** this content equality has succeeded.

## R-039 — CATSS morphological separators stay inside one BHSA word slot

The currently distributed CATSS parallel files use `/` as a morphological separator inside the Hebrew word (for example `B/R)$YT`). BHSA's `word` nodes are the slots; morphemes such as preformatives, suffixes, and endings are represented as features of a word slot, not as additional slots.

Sources:

- https://github.com/codykingham/CATSS_parsers/blob/master/parallel_readme.md
- https://etcbc.github.io/bhsa/features/0_home/
- https://etcbc.github.io/bhsa/features/otype/

**Decision:** `/` is removed for word identity. CATSS-TF never splits a CATSS word at `/` into multiple BHSA nodes.

Post-merge hardening (#26) extends the same intra-word treatment to backslash (`\\`), which the MIT CATSS converter also explicitly removes.

Examples:

```text
B/R)$YT  -> בראשׁית -> one BHSA word slot
W/H/)RC  -> והארץ   -> one BHSA word slot
```

## R-040 — Hebrew normalization is strict and consonantal

The Michigan–Claremont encoding gives a deterministic consonant map, including `$` for shin and `&` for sin. BHSA `g_cons_utf8` contains consonants and preserves the shin/sin dot distinction (for example `אשׁר`).

BHSA `g_word_utf8` and `qere_utf8` contain pointed forms; their diacritics are not stable identity material for this mapping. BHSA explicitly recommends consonantal features for robust searches.

Sources:

- CATSS BETA documentation distributed from the CCAT host;
- https://etcbc.github.io/bhsa/features/g_cons_utf8/
- https://etcbc.github.io/bhsa/features/g_word_utf8/
- https://etcbc.github.io/bhsa/features/qere_utf8/

**Decision:** CATSS-TF independently implements only the Hebrew normalization needed for MT identity:

- Michigan–Claremont consonants -> Unicode Hebrew;
- `/` removed;
- known vowel/dagesh/rafe/accent codes ignored for consonantal comparison;
- Hebrew final forms applied at orthographic word end;
- shin/sin dots preserved;
- Unicode input from BHSA is canonically decomposed and stripped of all combining marks **except** shin/sin dots;
- whitespace inside one BHSA feature value is ignored as display material, not converted to additional word slots.

Unknown CATSS characters fail explicitly. In particular, an unexpected lexical `#` is not guessed as shin/sin because current CATSS uses `#` for continuation.

Post-merge hardening (#26) recognizes ASCII `-` as the documented maqaf representation **when it actually occurs inside a CATSS MT element**. The resolver expands that element into multiple BHSA word positions; it does not infer boundaries from arbitrary punctuation.

## R-041 — Ketiv/Qere needs per-word alternatives, not row-level bags

CATSS marks Ketiv with `*` and Qere with `**`. BHSA stores the divergent Ketiv on the ordinary word slot and the Qere in the sparse `qere_utf8` feature on that same slot.

A row-level pair of tuples such as `mt_ketiv_tokens` and `mt_qere_tokens` loses association if more than one MT reading occurs in a logical CATSS row.

Sources:

- CATSS parser documentation / Michigan–Claremont conventions;
- https://etcbc.github.io/bhsa/features/g_word_utf8/
- https://etcbc.github.io/bhsa/features/qere_utf8/

**Decision:** the parser IR gains an immutable per-position `MtReading` structure. Each reading carries one primary CATSS form plus optional Ketiv and Qere alternatives. Existing `mt_tokens`, `mt_ketiv_tokens`, and `mt_qere_tokens` remain derived compatibility fields during this development stage.

For a `*KETIV **QERE` pair:

- primary identity against BHSA `g_cons_utf8` is the Ketiv;
- CATSS Qere must additionally agree with consonantalized BHSA `qere_utf8` on the **same word node**;
- missing or disagreeing BHSA Qere is a mapping finding, never silently ignored.

## R-042 — Known CATSS source sigla must not reach the Hebrew decoder as letters

Two source forms are especially relevant before Hebrew normalization:

- `,,a` marks a word in an Aramaic section;
- leading/trailing question marks mark doubt in the word or interpretation.

They are scholarly annotations, not Hebrew letters.

**Decision:** parser hardening under issue #7 structures these markers before resolution. `,,a` and doubt markers do not contribute to `mt_tokens`; their presence remains explicit in the IR. The Hebrew decoder itself remains strict and does not silently discard arbitrary punctuation.

## R-043 — Whole-verse equality is the mapping proof

A supported CATSS verse is resolved as follows:

1. map the CATSS source filename through the explicit BHSA book profile;
2. fetch exactly one BHSA verse node for `(book, chapter, verse)`;
3. flatten the CATSS MT readings in source order, excluding Hebrew-empty/LXX-plus rows and all column-B retroversions;
4. normalize CATSS primary readings;
5. normalize each BHSA word slot's `g_cons_utf8`;
6. require equal sequence lengths and equality at **every** position;
7. check CATSS Qere alternatives against `qere_utf8` on their already-proven same slot;
8. only then emit CATSS-token -> BHSA-node mappings.

This is not positional guessing: position is used as an identifier only after the full textual sequence has proven the positional correspondence.

**Decision:** v0.1 has no dynamic-programming, nearest-word, morphology-based, or edit-distance fallback. A mismatch yields a typed verse-level diagnostic with the first differing position and normalized values.

## R-044 — Hebrew-empty rows produce verse anchors, not word mappings

LXX-plus rows are omitted from the MT sequence and therefore do not affect whole-verse word cardinality. After the containing BHSA verse has been identified, the resolver records a `BhsaVerseAnchor` for each Hebrew-empty alignment.

This anchor is provenance for later materialization; it does not claim correspondence to any BHSA word.

**Decision:** resolver output distinguishes word mappings and verse anchors structurally. Issue #10 decides which scalar verse-level aggregates become TF features.

## R-045 — Resolver is pure behind a small BHSA verse-provider contract

Mapping correctness should be testable without downloading BHSA in normal CI.

**Decision:** issue #7 defines:

```text
BhsaWord
  node
  g_cons_utf8
  g_word_utf8?
  qere_utf8?

BhsaVerse
  node
  book
  chapter
  verse
  words[]

BhsaVerseProvider
  get_verse(book, chapter, verse) -> BhsaVerse?
```

The pure resolver consumes this interface. A thin `TextFabricBhsaProvider` adapts an already-loaded BHSA TF API using its section and locality APIs. The adapter has no authority to repair or reinterpret failed mappings.


## R-046 — BHSA has real empty-consonant slots in Ketiv/Qere processing

Reconciliation of superseded PR #21 exposed a parent-data case that the merged #7 resolver did not support. BHSA 2021's own `programs/ketivQere.py` explicitly does:

```python
gw = F.g_cons.v(w)
if gw == "":
    gw = "."
```

while constructing the Ketiv/Qere lookup. This is direct evidence that a BHSA word slot participating in the Masoretic reading machinery can have an empty written consonantal value.

Source:

- https://github.com/ETCBC/bhsa/blob/v1.8.1/programs/ketivQere.py

The alternative PR #21 also proposed treating CATSS `/` as an optional BHSA word boundary. That part is rejected: the documentation for the **current CATSS parallel dump** states that `/` is the morphological separator inside the Hebrew word, while maqqeph-separated words are represented with whitespace.

**Decision:**

- a CATSS Qere-only reading (`**QERE`, no paired Ketiv) establishes its textual proof against BHSA `qere_utf8` on that same word slot;
- this is valid whether the slot's written `g_cons_utf8` is empty or non-empty;
- ordinary and paired Ketiv/Qere positions continue to prove identity against written `g_cons_utf8` first;
- an empty written BHSA slot is never skipped to rescue an ordinary CATSS token;
- `/` remains intra-word normalization and is not a candidate BHSA slot boundary;
- successful Qere-only resolution is explicitly `mapping_kind=qere`.


## R-047 — CATSS conversion distinguishes internal segmentation from maqaf

The MIT CATSS conversion notebook explicitly maps:

- forward slash `/` as internal morphological segmentation documented by CATSS;
- backslash `\\` to the empty string in its Hebrew converter;
- hyphen `-` to U+05BE HEBREW PUNCTUATION MAQAF.

Its worked conversion example includes `B\\BYT-LXMM` and renders `בבית־לחמם`.

Source:

- https://github.com/codykingham/CATSS_parsers/blob/master/dev/generate_parallel.ipynb

This evidence does **not** imply that every current CATSS file uses internal hyphens; it establishes the semantics when such a form occurs.

**Decision:** for Hebrew identity, `/` and `\\` are removed inside one CATSS word segment. `-` is different: it is an orthographic word boundary (maqaf) and may expand one CATSS alignment element into multiple BHSA word-slot positions.

## R-048 — Maqaf expansion must preserve whole-verse proof

BHSA word identity lives on word slots, while maqaf is inter-word/trailer material. Treating a maqaf-containing CATSS element as one BHSA slot would create a false word-count mismatch; treating it as fuzzy alignment would weaken the resolver's proof.

**Decision:** before verse equality:

1. split each CATSS `MtReading.primary` at `-`;
2. normalize each non-empty segment independently;
3. preserve `alignment_id`, CATSS `mt_index`, and a zero-based `segment_index`;
4. compare the fully expanded CATSS sequence with all BHSA word slots;
5. emit mappings only if the complete expanded sequence matches.

Ketiv/Qere alternatives are expanded by the same maqaf rule. If paired primary/Qere readings have different segment counts, the verse fails with a typed `qere_segment_count_mismatch`; no positional rescue is attempted.

Empty maqaf segments (leading, trailing, or doubled `-`) are normalization errors and fail closed.


## R-049 — v0.1 targets CenterBLC/LXX release v1.0.1 exactly

CenterBLC/LXX publishes Rahlfs 1935 as Text-Fabric version `1935`. The repository README marks the corpus WIP, so CATSS-TF must not target floating `main`.

Release tag `v1.0.1` resolves to Git commit:

`f32a98eddf7eb239aa73ab863d70381e416d5076`

At that tag, `otype.tf` declares:

- slot type `word`;
- 623,693 word slots;
- 30,419 `subverse` nodes;
- 30,371 `verse` nodes;
- 1,192 `chapter` nodes;
- 57 `book` nodes;
- max node 685,732.

`otext.tf` declares the standard section hierarchy `book,chapter,verse`; `subverse` is an additional node/word feature, not a section level.

Sources:

- https://github.com/CenterBLC/LXX/releases/tag/v1.0.1
- https://github.com/CenterBLC/LXX/tree/v1.0.1/tf/1935
- https://github.com/CenterBLC/LXX/blob/v1.0.1/tf/1935/otype.tf
- https://github.com/CenterBLC/LXX/blob/v1.0.1/tf/1935/otext.tf

**Decision:** the first `catss-lxx` materializer supports **CenterBLC/LXX 1935 as published at v1.0.1 only**.

## R-050 — CenterBLC shares CATSS ancestry but not the parallel-file representation

CenterBLC's README says its source is Eliran Wong's `LXX-Rahlfs-1935`, itself built on CATSS LXX morphology. The CenterBLC converter does not consume CATSS parallel `.par` files directly: it reads a 26-column intermediate table and constructs TF word slots and sections.

The converter therefore proves lineage, not token/reference identity with CATSS parallel.

Sources:

- https://github.com/CenterBLC/LXX/blob/v1.0.1/README.md
- https://github.com/CenterBLC/LXX/blob/v1.0.1/programs/TF-converter_LXX.py
- https://github.com/eliranwong/LXX-Rahlfs-1935

**Decision:** #9 must validate Greek content against parent word slots. Common CATSS/Rahlfs ancestry is never itself a successful mapping rule.

## R-051 — `word`, not `g_cons_utf8`, is the Greek surface identity feature

Direct inspection of CenterBLC v1.0.1 shows:

```text
word:        ἐν  ἀρχῇ  ἐποίησεν  ὁ  θεὸς  τὸν  οὐρανὸν ...
lex_utf8:    ἐν  ἀρχή  ποιέω     ὁ  θεός  ὁ    οὐρανός ...
g_cons_utf8: εν  αρχη  ποιεω      ο  θεος  ο    ουρανος ...
```

Thus `g_cons_utf8` is normalized lexical/lemma material, not an unaccented inflected surface. Using it for identity would collapse morphology (`ἐποίησεν → ποιεω`, `τὸν → ο`).

**Decision:** Greek node identity is proven against the parent `word` surface after Unicode/diacritic normalization. Lemma and morphology features may be queried after mapping but cannot rescue a failed surface match.

## R-052 — Representative CATSS parallel Greek really matches CenterBLC surface

The MIT CATSS parser documentation reproduces raw `01.Genesis.par` data. For Genesis 1:1, the CATSS Greek running text is:

`E)N A)RXH=| E)POI/HSEN O( QEO\S TO\N OU)RANO\N KAI\ TH\N GH=N`

CenterBLC v1.0.1 `word` slots for Gen 1:1 are:

`ἐν ἀρχῇ ἐποίησεν ὁ θεὸς τὸν οὐρανὸν καὶ τὴν γῆν`

These agree after ordinary Greek accent/breathing normalization.

Source:

- https://github.com/codykingham/CATSS_parsers/blob/master/parallel_readme.md
- CenterBLC/LXX v1.0.1 TF `word.tf`, `book.tf`, `chapter.tf`, `verse.tf`

**Implication:** direct surface mapping is viable for ordinary passages; the remaining problem is reference/order reconstruction, not a fundamentally different Greek edition in ordinary text.

## R-053 — CATSS square-bracket Greek references are required location evidence

CATSS parallel verse headers follow BHS/MT versification. Documentation states that when Rahlfs LXX differs, the Greek line ends with a square-bracket reference.

The documented Gen 23:5 example ends:

`MH/ [6]`

Direct CenterBLC audit confirms:

- CenterBLC Gen 23:5 ends with `λέγοντες`;
- CenterBLC Gen 23:6 begins with `μή`.

Therefore `[6]` is not ancillary annotation: it moves that Greek token to the next parent verse.

The CATSS regex documentation recognizes both `[...]` and `[[...]]` as "(chapter &) verse difference from Hebrew". Examples elsewhere include chapter+verse and letter suffixes.

Sources:

- https://github.com/codykingham/CATSS_parsers/blob/master/parallel_readme.md
- https://github.com/codykingham/CATSS_parsers/blob/master/regex_patterns.py

**Decision:** #9 must use structured CATSS Greek reference evidence per alignment/token group. The MT verse header is only the default location. A raw `verse_reference` string is not sufficient as the final resolver contract.

## R-054 — CATSS Greek row order is not always printed LXX word order

CATSS documentation explicitly states that only the MT running text is reliably unaltered; LXX running text has been moved in cases of global differences. Local, adjacent, remote, and stylistic transposition sigla are documented.

**Decision:** unlike the BHSA resolver, #9 must not prove mapping by blindly flattening `AlignmentRecord.lxx_tokens` in CATSS row order. It must either reconstruct printed Greek order from structured transposition/reference evidence or solve exact parent placement with uniqueness checks. Duplicate-token ambiguity must fail closed.

## R-055 — CenterBLC v1.0.1 selects the B text of Joshua/Judges

Wong's source mapping distinguishes:

- `07.JoshB.mlxx` / `08.JoshA.mlxx`;
- `09.JudgesB.mlxx` / `10.JudgesA.mlxx`.

Its "main" book set explicitly uses `JoshB` and `JudgB`; A forms are alternate books. CenterBLC v1.0.1 has only one `Josh` and one `Judg` book, not separate A books.

Sources:

- https://github.com/eliranwong/LXX-Rahlfs-1935/blob/master/08_versification/book_maps.csv
- https://github.com/eliranwong/LXX-Rahlfs-1935/blob/master/11_end-users_files/MyBible/Bibles/books_main.csv
- https://github.com/eliranwong/LXX-Rahlfs-1935/blob/master/11_end-users_files/MyBible/Bibles/books_alternate.csv

**Decision:** CATSS `06.JoshB` → CenterBLC `Josh`; `08.JudgesB` → `Judg`. CATSS `07.JoshA` and `09.JudgesA` are explicitly unsupported by the v0.1 LXX projection. They must not be coerced onto the B parent books.

## R-056 — Daniel editions are separate and directly representable

Wong's source has separate `DanielOG.mlxx` and `DanielTh.mlxx`; CenterBLC preserves separate `Dan` and `DanTh` books. Direct TF audit also shows separate `Bel/BelTh` and `Sus/SusTh`.

Wong's main mapping names Old Greek Daniel `DanOG`; CenterBLC shortens that parent book value to `Dan`.

**Decision:**

- CATSS `45.DanielOG` → CenterBLC `Dan`;
- CATSS `46.DanielTh` → CenterBLC `DanTh`.

No cross-edition fallback is allowed.

## R-057 — Psalm 151 is inside CenterBLC `Ps`

Direct CenterBLC TF audit shows `Ps` has chapters 1 through 151. Chapter 151 contains verses 1–7.

CATSS parallel distributes Psalm 151 separately as `22.Ps151.par`.

The independent modern CATSS registry likewise records that CATSS LXX morphology Psalm 151 is packed at the end of the Psalms morphology source.

**Decision:** `22.Ps151` maps to CenterBLC `Ps`, fixed parent chapter 151. It is not unsupported and does not require a synthetic parent book.

## R-058 — CenterBLC `2Esdr` combines Ezra and Nehemiah

CenterBLC `2Esdr` contains 23 chapters. Independent CATSS morphology handling documents the source convention:

- 2 Esdras chapters 1–10 = Ezra;
- 2 Esdras chapters 11–23 = Nehemiah;
- Nehemiah 1 = 2 Esdras 11.

**Decision:**

- CATSS `18.Ezra` → parent `2Esdr`, same chapter;
- CATSS `19.Neh` → parent `2Esdr`, chapter + 10.

Any explicit Greek reference annotation takes precedence over this default transform once #9 has parsed it structurally.

## R-059 — Esther additions require the parent `subverse` feature

CenterBLC has one `Esth` book. Direct TF/source audit shows addition material represented through the same integer chapter/verse plus `subverse` values, e.g.:

`1:1a ... 1:1s`, `3:13a...`, `4:17a...`, `8:12a...`, `10:3a...`.

The standard TF section hierarchy remains only `book/chapter/verse`; `subverse` must therefore be read on words/nodes inside the verse.

**Decision:** `subverse` is mapping-critical for the LXX parent profile. #9 must preserve suffix-bearing Greek references and filter parent word candidates by subverse where CATSS supplies that evidence.

## R-060 — Parent feature fingerprints define the v0.1 LXX mapping contract

At CenterBLC/LXX tag v1.0.1, Git blob IDs of mapping-critical TF files are:

- `otype.tf`: `2e6480a9a4ee6abf5d13f66f3851766dfedb94e6`
- `oslots.tf`: `e95696fc14dbbf3c3738f062a5c8b237893e7fd9`
- `book.tf`: `0bfae94bb312cb7ecd33b102babb9400c554d8be`
- `chapter.tf`: `ec64b6bf72a6282e9da5064ca2e895171190208e`
- `verse.tf`: `ff8766352d7aff530c6eec4f66366adcc691740e`
- `subverse.tf`: `cecfaf2d1ddc4fd1e93958abd674a7e60e676ae5`
- `word.tf`: `f88e525991c3d09beac713a91ef8ed41e6308a03`
- `orig_order.tf`: `0d03394bec636957f48c0cf3ef44a2907a5d68af`

**Decision:** these files and counts define the exact v0.1 parent profile. `word` is the surface identity feature; `orig_order` is provenance/diagnostic support, not a substitute for textual agreement.

## R-061 — Full CATSS-vs-parent corpus diff could not be executed in this runtime

The public modern CATSS project publishes prebuilt SQLite assets containing both parallel alignment and LXX morphology, which would permit a full corpus-level differential audit. This execution environment cannot retrieve GitHub release binary assets, and the CCAT text endpoint timed out.

This limitation is explicit rather than replaced with an assumption.

Evidence actually checked for #8 includes:

- exact CenterBLC v1.0.1 TF structure and feature blobs;
- Wong/CCAT book and versification maps;
- modern independent CATSS parallel↔lxxmorph registry/remap logic;
- documented raw CATSS parallel samples and repair examples;
- positive Gen 1:1 surface equality;
- negative/reference-sensitive Gen 23:5→23:6 case;
- explicit CATSS documentation that Greek order may be moved.

**Decision:** #9 must include an opt-in full-corpus integration audit when user-acquired CATSS data are available. A release must report mapping coverage and divergence classes; synthetic/unit evidence alone is not enough for v0.1 release confidence.
