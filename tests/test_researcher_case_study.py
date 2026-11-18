"""A compact scholarly case study must be reproducible from the public demo."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASE_STUDY = ROOT / "docs/researcher-case-study.md"
INDEX = ROOT / "docs/index.md"


def test_case_study_is_linked_and_cites_executable_oracle() -> None:
    assert "[Worked case study](researcher-case-study.md)" in INDEX.read_text(encoding="utf-8")
    content = CASE_STUDY.read_text(encoding="utf-8")
    for expected in (
        "python examples/canonical_research_walkthrough.py",
        "alignment_groups",
        "source_documents",
        "mt_greek_groups",
        "source_scoped_groups",
        "false_cross_group_matches",
        "mt_b_as_mt_a_hits",
        "reference_wrong_source_book_groups",
        "reversed_greek_order_groups",
        "MLK",
        "BASILEU/S",
        "QEOS",
        "LOGOS",
        "W/KL",
        "01.Genesis.par",
        "06.JoshB.par",
        "synthetic",
        "not a word-to-word",
        "catss_source",
        "catss_alignment_id",
        "Libronix",
        "BHSA",
        "LXX",
    ):
        assert expected in content, expected
    for expected_line in (
        '"alignment_groups": 5',
        '"source_documents": 2',
        '"mt_greek_groups": 2',
        '"source_scoped_groups": 1',
        '"false_cross_group_matches": 0',
        '"mt_b_as_mt_a_hits": 0',
        '"reference_wrong_source_book_groups": 0',
        '"reversed_greek_order_groups": 0',
    ):
        assert expected_line in content, expected_line
