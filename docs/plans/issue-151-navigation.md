# #151 — Researcher landing page plan

1. RED first: add `tests/test_researcher_navigation.py` asserting a README-linked landing page, relative local links that resolve (including anchor fragments), named entrypoints for synthetic canonical, annotation and unclassified scripts, and explicit separation of standalone/parent artifacts and Libronix limitations. Run test on unchanged docs, observe expected failure in GitHub CI pytest (not lint).
2. GREEN: write `docs/index.md` with a small decision table and task-oriented route from clean synthetic demo to authorized 46-file materialization, provenance, notation/schema lookup, browser and Agora, then pinned-parent constraints. Update README with one link, preserving existing user instructions.
3. Exact-head Python 3.11–3.13, release, 46-file canonical/Agora and Context-Fabric CI. Log a fresh-reader route using only the new page and independently audit broken links, wrong commands, conflated corpus scopes, unsupported E2E claims.
4. Review final diff adversarially, merge with expected SHA only after all gates green. Keep #151/#149/#126 open.
