# Research — issue #103 superseded CI runs

## Observed real runner waste

PR #102 demonstrated queued/running obsolete whole-corpus Actions runs:
38098813077, 38098885885, 38099043529, 38099103565,
38099256110, 38099264539, and follow-up runs, even when source
changes were already superseded. The CATSS-TF CI workflow
`.github/workflows/ci.yml` enables `push: main` and
`pull_request` but has no workflow-level `concurrency`. The
expensive 46-file real-data audit ran repeatedly on older PR heads.
Each audit uses runner minutes and delays exact-head validation.

## Official GitHub Actions concurrency contract

GitHub's workflow syntax documentation
https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax
confirms workflow-level `concurrency` allows the `github`
context; `cancel-in-progress` accepts a conditional expression.
A stable group may use `github.workflow`, and a null event-specific
value can use `||` fallback. Group membership/cancellation operates
across the whole workflow, including the full-source job.

## Proposed strict behavior

Use a PR-number namespace for PR workflow runs and unique run-ID
namespace for main / non-PR runs:

```yaml
concurrency:
  group: catss-ci-${{ github.workflow }}-${{ github.event.pull_request.number || github.run_id }}
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}
```

One PR's changed head cancels the old head, including old whole-corpus
jobs. A different PR number does not collide. Every push to main has
a different run ID and must **not** be canceled by PR work or another
main push. The schema syntax is documented and no source data is
changed.

The exact latest PR head must still run the complete audit to green.
A simple workflow-source assertion is necessary but insufficient:
after implementation, collect Actions run IDs on two rapid commits
and observe the superseded PR run cancel with the newer head's jobs
still scheduled. Do not merge if YAML expressions fail GitHub validation.
