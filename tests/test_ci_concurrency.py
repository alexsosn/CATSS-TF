"""CI must cancel obsolete PR work without canceling main or other PRs."""

from pathlib import Path

WORKFLOW = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "ci.yml"


def test_ci_supersession_is_scoped_to_pr_not_main_or_other_prs() -> None:
    source = WORKFLOW.read_text(encoding="utf-8")
    assert "on:\n  push:\n    branches: [main]\n  pull_request:" in source

    # PR number remains fixed over all commits on one PR.
    # Main instead uses the unique run ID, and must not be canceled.
    assert (
        "concurrency:\n"
        "  group: catss-ci-${{ github.workflow }}-"
        "${{ github.event.pull_request.number || github.run_id }}\n"
        "  cancel-in-progress: ${{ github.event_name == 'pull_request' }}\n"
    ) in source

    # Keep the mandatory per-head Python matrix, release and full-source gates.
    for job in ("  test:\n", "  release-smoke:\n", "  complete-catss-audit:\n"):
        assert job in source
