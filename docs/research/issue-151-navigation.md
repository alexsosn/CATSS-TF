# #151 — Researcher navigation and first-session entrypoint (2026-11-18)

Snapshot: main `f7e3057155c7de245307e02a0e52824aac7f591b`.

## Research

The README links a quickstart and then lists ten heterogeneous technical, project and contributor files. There is no `docs/index.md` user-first landing page. The cookbook has nine synthetic-tested sections; the schema and notation inventories already exist, with source-catalog-driven tests. The crosswalk distinguishes two Libronix resources, and #126 remains open. A new reader must infer which of `catss`, `catss-bhsa`, `catss-lxx` to use, which operations need licensed inputs, and what is E2E-verified.

This is a documentation navigation defect, not a reason to build a new query API. Existing examples are tested by `tests/test_researcher_quickstart.py` and other standalone synthetic smokes. The latest exact-head 46-file canonical CI and Agora adapter passed on #169; this does not establish pinned-parent full E2E.

## Scope

Add a single `docs/index.md` that provides a task-to-recipe map, precise artifact/feature boundaries, safe installation and verification steps, error triage and an explicit current release gate. Put a prominent link in README. Test all local Markdown links in the landing page and its actual commands/targets, and ensure the README points to it. Do not rewrite the exhaustive catalogs, invent Libronix parity, add adapters or bundle proprietary source. Parent #151 remains open.
