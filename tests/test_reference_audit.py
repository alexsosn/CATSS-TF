"""Fail-closed source-only inventory of Greek-reference numeric coincidences."""

from catss_tf.parser import parse_parallel_text
from catss_tf.reference_audit import audit_greek_references


def test_scalar_reference_audit_never_calls_numeric_candidates_verified_targets() -> None:
    genesis = parse_parallel_text(
        "Gen 1:1\nHB\tLOGOS [2] [99]\nGen 1:2\nHB\tQEOS\n",
        source_name="01.Genesis.par",
    )
    josh = parse_parallel_text(
        "JoshB 9:2\nHB\tLOGOS [9:2a]\nJoshB 9:2\nHB\tKAI\n",
        source_name="06.JoshB.par",
    )

    audit = audit_greek_references((genesis, josh))
    assert audit.source_files == 2
    assert audit.scalar_references == 3
    assert audit.explicit_chapters == 1
    assert audit.subverse_suffixes == 1
    assert audit.numeric_candidates_zero == 1  # [99] has no MT-header candidate
    assert audit.numeric_candidates_one == 1  # [2] has one *numeric* coincidence
    assert audit.numeric_candidates_multiple == 1  # [9:2a] has two MT 9:2 headers
    assert audit.by_source == (("01.Genesis.par", 2), ("06.JoshB.par", 1))


def test_scalar_reference_audit_keeps_nonmatching_verses_unmapped() -> None:
    one = parse_parallel_text("Gen 1:1\nHB\tLOGOS [2]\n", source_name="01.Genesis.par")
    audit = audit_greek_references((one,))
    assert audit.scalar_references == 1
    assert audit.numeric_candidates_zero == 1
    assert audit.numeric_candidates_one == 0
    assert audit.numeric_candidates_multiple == 0


def test_source_header_relative_greek_reference_classes_do_not_forge_targets() -> None:
    # Kingham's documented Gen 23:5 / [6] case marks a Greek verse
    # numerically different from the containing CATSS (MT) source header.
    genesis = parse_parallel_text(
        "Gen 23:5\nHB\tMH/ [6]\nGen 1:1\nHB\tLOGOS [1] [2:1] [2:2]\n",
        source_name="01.Genesis.par",
    )
    josh = parse_parallel_text(
        "JoshB 9:2\nHB\tLOGOS [9:2a]\nHB\tLOGOS [[9.2a-2f]]\n",
        source_name="06.JoshB.par",
    )

    audit = audit_greek_references((genesis, josh))
    assert audit.scalar_references == 5  # the contextual range is not a scalar
    assert audit.explicit_chapters == 3
    assert audit.subverse_suffixes == 1
    assert audit.same_header_numeric == 2  # [1] and [9:2a], still not Greek targets
    assert audit.different_verse_same_chapter == 1  # [6] under Gen 23:5
    assert audit.different_chapter == 2  # both [2:1] and [2:2]
    assert (
        audit.same_header_numeric
        + audit.different_verse_same_chapter
        + audit.different_chapter
    ) == audit.scalar_references


def test_source_header_relative_counts_each_tag_not_one_per_alignment() -> None:
    doc = parse_parallel_text(
        "Gen 1:1\nHB\tLOGOS [2] [2]\n",
        source_name="01.Genesis.par",
    )
    audit = audit_greek_references((doc,))
    assert audit.scalar_references == 2
    assert audit.same_header_numeric == 0
    assert audit.different_verse_same_chapter == 2
    assert audit.different_chapter == 0


def test_source_header_relative_explicit_zero_chapter_is_not_defaulted() -> None:
    # The parser accepts numeric zero as notation. An audit must preserve
    # its explicit chapter instead of silently treating it as absent.
    doc = parse_parallel_text(
        "Gen 1:1\nHB\tLOGOS [0:1]\n",
        source_name="01.Genesis.par",
    )
    audit = audit_greek_references((doc,))
    assert audit.scalar_references == 1
    assert audit.same_header_numeric == 0
    assert audit.different_verse_same_chapter == 0
    assert audit.different_chapter == 1
