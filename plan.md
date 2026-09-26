# Initial implementation plan

**Plan date:** 2026-09-25

The backlog is issue-driven. Each implementation issue follows the repository gates in `AGENTS.md`.

## Phase 0 — Bootstrap

### BOOTSTRAP — Repository for autonomous development (#1)

Deliver:

- agent policy;
- research/design/plan;
- software/data license boundary;
- Python package skeleton;
- offline lint/type/test CI;
- issue and PR templates.

## Phase 1 — Prove the source model before TF output

### SOURCE — CATSS acquisition and parser decision (#3)

Research and decide the v0.1 input contract:

- direct raw `.par` files with an in-project parser;
- reuse/adapt MIT-compatible parser logic;
- optional integration with an external CATSS package.

Acceptance must include license analysis, deterministic fixtures, and no CATSS data redistribution.

### IR — Canonical alignment IR and parallel-file parser (#4)

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

### VALIDATE — Alignment validation/reporting (#5)

Build diagnostics and invariants around the IR:

- every consumed source element accounted for;
- deterministic group IDs;
- no silent dropped rows;
- explicit unknown sigla;
- reproducible summaries.

## Phase 2 — Parent-corpus mapping

### BHSA-SCHEMA — Select and characterize first supported BHSA warp (#6)

Pin the first supported BHSA version and document:

- book/reference conventions;
- word tokenization;
- Ketiv/Qere representation;
- relevant surface/normalized features;
- node-version compatibility contract.

### BHSA-MAP — BHSA resolver (#7)

RED-first mapping tests, then implementation.

The resolver returns parent node IDs plus diagnostics; it does not write TF yet.

### LXX-SCHEMA — Characterize CenterBLC/LXX 1935 mapping (#8)

Audit CATSS ancestry versus actual TF token boundaries and references across representative hard cases.

### LXX-MAP — LXX resolver (#9)

RED-first mapping tests followed by implementation and drift diagnostics.

## Phase 3 — Text-Fabric modules

### TF-SCHEMA — TF feature schema (#10)

Freeze names/types/metadata for shared CATSS features and projection-specific diagnostics.

Verify that output is a true module around the parent warp and contains no new nodes.

### BHSA-MATERIALIZE — `catss-bhsa` materializer (#11)

Generate a module against the supported BHSA version; validate loadability together with the parent corpus.

### LXX-MATERIALIZE — `catss-lxx` materializer (#12)

Generate the corresponding module against CenterBLC/LXX 1935.

### CONSISTENCY — Cross-projection consistency (#13)

Given the same CATSS source, prove that shared `catss_alignment_id` values and normalized CATSS semantics agree between BHSA and LXX materializations.

## Phase 4 — Research ergonomics and release

### TECHNIQUE — Translation-technique derived features (#14)

Only after source-preserving modules are stable, define reproducible derived features such as token ratios, lexical/morphological comparison, plus/minus, and word-order relations. Keep derived analysis distinct from CATSS editorial annotation.

### TF-WEBAPP — Standard Text-Fabric browser integration (#35)

Use the native BHSA/LXX Text-Fabric apps with the generated CATSS modules through
Text-Fabric's standard local module mechanism. CATSS-TF does not define a third corpus
app and Agora is not part of browser startup.

### RELEASE — Standalone v0.1 release (#15)

- clean install;
- deterministic offline tests;
- bounded opt-in integration fixtures using user-acquired data;
- standard Text-Fabric browser workflow;
- documentation and limitations;
- no bundled corpus/data artifacts.

### AGORA — Agora registration (#16)

Register the released materializers with Agora without moving CATSS-specific behavior into Agora.

## Dependency summary

```text
#3 SOURCE ──> #4 IR ──> #5 VALIDATE
                 │          │
#6 BHSA-SCHEMA ──┴──────> #7 BHSA-MAP ──┐
                                           ├─> #10 TF-SCHEMA ─> #11 BHSA-MATERIALIZE ─┐
#8 LXX-SCHEMA ─────────> #9 LXX-MAP ─────┘                                             ├─> #13 CONSISTENCY
                                                         #12 LXX-MATERIALIZE <───────────┘
                                                                                          │
                                                                                          ├─> #14 TECHNIQUE
                                                                                          └─> #35 TF-WEBAPP ─> #15 RELEASE ─> #16 AGORA
```

Issue bodies contain the authoritative acceptance criteria and dependencies.

## Release principle

A fast path to “some TF files” is not the goal. The release gate is a mapping whose failures are measurable and whose provenance can be reproduced.
