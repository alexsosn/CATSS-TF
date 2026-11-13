"""User-facing offline CATSS canonical quickstart smoke via a fresh process."""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "examples/canonical_research_walkthrough.py"
COOKBOOK = ROOT / "docs/researcher-cookbook.md"
README = ROOT / "README.md"

EXPECTED = {
    "alignment_groups": 5,
    "source_documents": 2,
    "mt_greek_groups": 2,
    "source_scoped_groups": 1,
    "multi_form_groups": 1,
    "false_cross_group_matches": 0,
    "mt_b_context_hits": 1,
    "mt_b_as_mt_a_hits": 0,
}


def test_researcher_walkthrough_from_clean_working_directory(tmp_path: Path) -> None:
    assert SCRIPT.is_file(), "missing runnable canonical user-facing walkthrough"
    process = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
        timeout=120,
    )
    assert process.stderr == ""
    result = json.loads(process.stdout)
    assert result == EXPECTED
    assert not list(tmp_path.iterdir()), "demo must not leave TF data in user CWD"


def test_cookbook_provides_reproducible_user_instructions() -> None:
    assert COOKBOOK.is_file(), "missing researcher cookbook"
    content = COOKBOOK.read_text(encoding="utf-8")
    for expected in (
        "examples/canonical_research_walkthrough.py",
        "find_aligned_groups",
        "find_groups_with_all_forms",
        "find_mt_b_raw_matches",
        "catss-bhsa",
        "catss-lxx",
        "not a word-to-word",
        "not a manuscript attestation",
        "46-file",
        "authenticated",
        "notation-reference.md",
        "tf-feature-reference.md",
        "after the `api = Fabric(...).loadAll(...)` line",
        "before the `return` statement",
    ):
        assert expected in content, expected
    assert "docs/researcher-cookbook.md" in README.read_text(encoding="utf-8")
