# R96-12 — research / plan / RED-first / independent review

1. Confirm baseline in current code, read existing bounded search tests, verify complete 46-file CI and the open issue #96. Commit research and plan first.
2. Commit RED budgeted memory regression on 80,000 synthetic alternatives, small-tree parity fixtures for cutoff and overlap, and long-branch (>1,000 tasks) behavior. Obtain actual intended RED failure from the GitHub CI pytest matrix with Ruff/format/mypy green.
3. Replace `pending` eager cloned assignments with stack of active candidate iterators and selected intervals. Preserve exact DFS order, entered-node visit counts, fail-closed budget semantics, and distinction of 0, 1, 2 solutions. Avoid recursion and modifying production result dataclass.
4. Run focused/full tests, exact pinned 46-source CATSS+LXX audits, Python 3.11/3.12/3.13, lint+format+mypy, release smoke, full TF build/readback. Researcher-facing docs should distinguish bounded search frontier from input candidate memory.
5. Logically independent adversarial exact-final-head review: challenge missed final sibling, off-by-one budgets, false `unique` after early cutoff, 2-solutions cap, adjacency, duplicate intervals, generators/large width, traceback/memory footprint across Pythons, changed production parent probe or reference counts. Post review on PR.
6. Merge only reviewed exact head after all five required jobs green; verify main and leave umbrella #96 open.
