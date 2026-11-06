# Plan — issue #103 PR-only CI supersession

1. Confirm existing real-run waste and review official Actions
   `concurrency` context/event syntax.
2. RED-first pytest contract: CI workflow must use a PR-number group
   with `github.run_id` for non-PR events, and only cancel PR events;
   retain both `push main` and `pull_request` triggers and all jobs.
3. GREEN one-scoped top-level workflow concurrency block. No
   changes to the actual 46-file CATSS audit or TLS transport.
4. Prove actual GitHub Actions supersession with two quick PR commits
   and inspect statuses; verify no main run canceled by the PR.
5. Run final exact-head Ruff/format/mypy/pytest on 3.11–3.13,
   release smoke, 46-file corpus materialization + TF readback.
6. Logically independent adversarial review of PR collision,
   main isolation, mergeability gates, and actual Action histories.
   Resolve any concern via RED/GREEN before merge. Close #103
   only if the observed Action behavior matches the intent.
