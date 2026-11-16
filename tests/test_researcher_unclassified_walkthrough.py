"""New-reader source-uncertainty example must be genuinely executable."""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "examples/unclassified_evidence_walkthrough.py"
COOKBOOK = ROOT / "docs/researcher-cookbook.md"

EXPECTED = {
    "alignment_groups": 5,
    "source_documents": 2,
    "unclassified_groups": 2,
    "unclassified_slots_direct_scan": 2,
    "original_reasons_and_ids_verified": True,
    "sirach_source_hits": 2,
    "genesis_false_hits": 0,
    "hebrew_empty_greek_hits": 1,
    "lxx_minus_without_mt_hits": 1,
    "unclassified_mt_lexical_elements": 0,
    "unclassified_source_lines": [[3, 3], [4, 4]],
    "first_unclassified_greek_forms": ["QEOS"],
}


def test_clean_user_can_run_unclassified_workflow(tmp_path: Path) -> None:
    assert SCRIPT.is_file(), "missing executable source-uncertainty case study"
    child = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
        timeout=120,
    )
    assert child.stderr == ""
    assert json.loads(child.stdout) == EXPECTED
    assert tuple(tmp_path.iterdir()) == (), "no CATSS/TF files may leak into user CWD"


def test_unclassified_cookbook_interpretation_is_explicit() -> None:
    body = COOKBOOK.read_text(encoding="utf-8")
    for expected in (
        "## 9. Explore unclassified CATSS alignment evidence",
        "examples/unclassified_evidence_walkthrough.py",
        "find_unclassified_alignments",
        "catss_tt_unclassified_reason",
        "catss_tt_status",
        "source_line_first",
        "reason_contains",
        "not a translation addition",
        "not a manuscript-to-word",
        "102",
        "46-file",
        "tf-feature-reference.md",
    ):
        assert expected in body, expected
