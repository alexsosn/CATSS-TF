"""Independent clean-process smoke for source-typed researcher annotation recipes."""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "examples/annotation_evidence_walkthrough.py"
COOKBOOK = ROOT / "docs/researcher-cookbook.md"

EXPECTED = {
    "alignment_groups": 3,
    "source_documents": 2,
    "mt_ketiv_nodes": 1,
    "mt_qere_nodes": 1,
    "mt_primary_hbk_nodes": 1,
    "same_mt_word_for_ketiv_qere": 1,
    "sirach_3_marked": 1,
    "sirach_3_independent_oracle": 1,
    "sirach_7_lacking_mt_a": 1,
    "sirach_7_lacking_independent_oracle": 1,
    "sirach_7_lacking_mt_b": 0,
    "sirach_8_marked": 0,
    "sirach_lacuna_annotations": 1,
    "sirach_fragmentary_letters": 1,
    "invented_annotation_targets": 0,
}


def test_evidence_walkthrough_clean_process(tmp_path: Path) -> None:
    assert SCRIPT.is_file(), "missing annotation evidence researcher example"
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
    assert not list(tmp_path.iterdir()), "walkthrough must leave user CWD unchanged"


def test_annotation_research_recipe_is_documented() -> None:
    body = COOKBOOK.read_text(encoding="utf-8")
    for required in (
        "## 6. Qere/Ketiv and Sirach annotation evidence",
        "examples/annotation_evidence_walkthrough.py",
        "find_sirach_witness_annotations",
        "`catss_ketiv_text`",
        "`catss_qere_text`",
        "Sirach",
        "reading-lacking",
        "not a manuscript-to-word",
        "not a pairwise",
        "tf-feature-reference.md",
    ):
        assert required in body, required
