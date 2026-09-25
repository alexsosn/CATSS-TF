# CATSS-TF Agent Instructions

This repository is designed for autonomous, issue-driven development. Coding agents must treat this file as the mandatory entry point.

## Read first

Before changing code, read in order:

1. `README.md`
2. `research.md`
3. `design.md`
4. `plan.md`
5. `LICENSE_SCOPE.md`
6. `docs/agentic-dev-loop.md`
7. the active GitHub issue and all linked PR/review discussion

Re-check relevant upstream contracts when a task depends on CATSS, Text-Fabric, BHSA, CenterBLC/LXX, or Agora behavior. Record changed evidence in `research.md` or a focused task research artifact.

## Non-negotiable rules

- Work from a GitHub issue with explicit acceptance criteria.
- Before implementation, check for an overlapping open issue or PR. Do not create concurrent duplicate implementations.
- Follow **research → design/plan → RED-first TDD → implementation → exact-head tests → logically independent adversarial review**.
- For behavior changes, preserve a deterministic failing test before the production fix.
- Review fixes follow the same RED → fix → GREEN → re-review discipline when behavior changes.
- A PR is mergeable only after review of the final head; any production change after review invalidates that approval.
- Keep research, design, tests, implementation, and review evidence proportional to the risk, but do not skip the gates.
- Keep unrelated cleanup out of implementation PRs.

## Data and licensing boundary

- Do not commit raw CATSS data, CATSS-derived databases, generated CATSS TF modules, BHSA data, or LXX data.
- Do not vendor snapshots of parent corpora.
- Tests use tiny synthetic fixtures or the minimum legally safe fragment required to reproduce parser behavior.
- CATSS acquisition must be explicit and user-initiated. Do not silently mirror, crawl, or prefetch the CATSS archive.
- Generated artifacts must carry provenance and upstream-license metadata.
- The MIT license covers CATSS-TF software only. See `LICENSE_SCOPE.md`.

## Text-Fabric architecture

- `catss-bhsa` and `catss-lxx` are **modules around existing parent warps**.
- A normal TF module must not introduce new slots or a new `alignment` node type.
- Parent corpus nodes remain authoritative; never renumber, replace, or silently synthesize parent word nodes.
- Use one canonical alignment model and two projections. Do not implement two independent CATSS parsers.
- The shared stable `catss_alignment_id` is the cross-projection join key.
- Cross-corpus node numbers must not be treated as globally meaningful identifiers.
- Mapping failures, ambiguities, versification mismatches, and tokenization mismatches must be explicit. Never shift an alignment to a neighboring token merely to make counts match.

## Upstream responsibility

- CATSS-TF owns parsing/materialization/mapping logic required to build its modules.
- It does not redefine CATSS textual judgments.
- It does not improve BHSA or LXX morphology by local correction.
- Upstream data anomalies must be preserved or reported, not silently normalized into a preferred reading.
- Agora registration is downstream distribution/integration metadata. Domain behavior belongs here.

## Definition of done

A behavior PR is complete only when:

- issue acceptance criteria are met;
- research assumptions are recorded;
- design/plan is updated for material architectural changes;
- a deterministic RED exists for the changed behavior;
- focused tests and the relevant full offline suite are green at the exact final head;
- failure/ambiguity cases are tested where relevant;
- no prohibited data artifact has been committed;
- docs and feature contracts are synchronized;
- a logically independent adversarial review has approved the exact final head.

## Review posture

Independent review is skeptical. In particular, inspect for:

- accidental CATSS/BHSA/LXX data redistribution;
- mapping by positional guess rather than verified token identity;
- hidden assumptions about Psalms or other versification differences;
- loss of CATSS column-B retroversions, plus/minus, transposition, or provenance;
- coupling of the two projections through unstable parent node numbers;
- module output that changes the parent warp;
- tests that prove only the fixture generator rather than production parsing/mapping;
- silent partial success.

When uncertain, fail explicitly and open a focused issue rather than hiding uncertainty in generated data.
