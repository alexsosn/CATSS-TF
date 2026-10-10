"""Fail-closed source-only inventory of Greek-reference numeric coincidences."""

from catss_tf.reference_audit import audit_greek_references

from catss_tf.parser import parse_parallel_text


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
