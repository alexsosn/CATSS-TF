# Initial implementation plan

**Plan date:** 2026-09-25

The backlog is issue-driven. Each implementation issue follows the repository gates in `AGENTS.md`. GitHub issue numbers are recorded only after the issue actually exists; this plan uses stable task labels for sequencing.

## Phase 0 — Bootstrap

### BOOTSTRAP — Repository for autonomous development

Tracked by issue #1.

Deliver:

- agent policy;
- research/design/plan;
- software/data license boundary;
- Python package skeleton;
- offline lint/type/test CI;
- issue and PR templates.

## Phase 1 — Prove the source model before TF output

### SOURCE — CATSS acquisition and parser decision

Research and decide the v0.1 input contract:

- direct raw `.par` files with an in-project parser;
- reuse/adapt MIT-compatible parser logic;
- optional integration with an external CATSS package.

Acceptance must include license analysis, deterministic fixtures, and no CATSS data redistribution.

### IR — Canonical alignment IR and parallel-file parser

TDD against minimal synthetic fixtures for:

- 1:1;
- 1:n / n:1 / n:m;
- LXX plus/minus;
- Hebrew column-B retroversion;
- local and non-local transposition;
- Ketiv/Qere;
- discontinuous/continued rows;
- source provenance and deterministic IDs.

Do not implement TF serialization yet.

### VALIDATE — Alignment validation/reporting

Build diagnostics and invariants around the IR:

- every consumed source element accounted for;
- deterministic group IDs;
- no silent dropped rows;
- explicit unknown sigla;
- reproducible summaries.

## Phase 2 — Parent-corpus mapping

### BHSA-SCHEMA — Select and characterize first supported BHSA warp

Pin the first supported BHSA version and document:

- book/reference conventions;
- word tokenization;
- Ketiv/Qere representation;
- relevant surface/normalized features;
- node-version compatibility contract.

### BHSA-MAP — BHSA resolver

RED-first mapping tests, then implementation.

The resolver returns parent node IDs plus diagnostics; it does not write TF yet.

### LXX-SCHEMA — Characterize CenterBLC/LXX 1935 mapping

Audit CATSS ancestry versus actual TF token boundaries and references across representative hard cases.

### LXX-MAP — LXX resolver

RED-first mapping tests followed by implementation and drift diagnostics.

## Phase 3 — Text-Fabric modules

### TF-SCHEMA — TF feature schema

Freeze names/types/metadata for shared CATSS features and projection-specific diagnostics.

Verify that output is a true module around the parent warp and contains no new nodes.

### BHSA-MATERIALIZE — `catss-bhsa` materializer

Generate a module against the supported BHSA version; validate loadability together with the parent corpus.

### LXX-MATERIALIZE — `catss-lxx` materializer

Generate the corresponding module against CenterBLC/LXX 1935.

### CONSISTENCY — Cross-projection consistency

Given the same CATSS source, prove that shared `catss_alignment_id` values and normalized CATSS semantics agree between BHSA and LXX materializations.

## Phase 4 — Research ergonomics and release

### TECHNIQUE — Translation-technique derived features

Only after source-preserving modules are stable, define reproducible derived features such as token ratios, lexical/morphological comparison, plus/minus, and word-order relations. Keep derived analysis distinct from CATSS editorial annotation.

### RELEASE — Standalone v0.1 release

- clean install;
- deterministic offline tests;
- bounded opt-in integration fixtures using user-acquired data;
- documentation and limitations;
- no bundled corpus/data artifacts.

### AGORA — Agora registration

Register the released materializers with Agora without moving CATSS-specific behavior into Agora.

## Release principle

A fast path to “some TF files” is not the goal. The release gate is a mapping whose failures are measurable and whose provenance can be reproduced.
