"""Bounded, metadata-only Sirach witness audit on parsed CATSS source."""

import pytest

from catss_tf.sirach_research import audit_sirach_witnesses
from catss_tf.parser import parse_parallel_text


def test_sirach_witness_audit_counts_markers_without_inventing_lexical_edges() -> None:
    document = parse_parallel_text(
        """Sir 2:13
HB 1\tGR
HB1 HB2 2\tGR
[..] 7\tGR
HB >8\tGR
HB 3 7\tGR
HB\tGR
""",
        source_name="27.Sirach.par",
    )

    audit = audit_sirach_witnesses(document)
    assert audit.source == "27.Sirach.par"
    assert audit.alignments == 6
    assert audit.witness_markers == 5
    assert audit.witness_groups == 4
    assert audit.multi_witness_groups == 1
    assert audit.witness_with_lacuna == 1
    assert audit.absence_markers == 1
    assert audit.absence_groups == 1
    assert dict(audit.witness_counts) == {
        "sirach_witness_geniza_a": 1,
        "sirach_witness_geniza_b": 1,
        "sirach_witness_geniza_c": 0,
        "sirach_witness_geniza_b_margin": 1,
        "sirach_witness_masada": 2,
    } | {
        "sirach_witness_geniza_d": 0,
        "sirach_witness_geniza_e": 0,
        "sirach_witness_masada_corrector": 0,
        "sirach_witness_11qpsa": 0,
        "sirach_witness_2q18": 0,
    }
    assert audit.witness_groups_with_multiple_mt >= 1
    assert audit.witness_groups_with_zero_mt >= 1
    assert audit.witness_groups_with_column_b == 0
    assert audit.witness_groups_with_continuations == 0
    assert all(len(identity) == 4 for _, identity in audit.examples)
    assert all(identity[0] == "Sir" for _, identity in audit.examples)
    assert "HB1" not in repr(audit)
    assert "LOGOS" not in repr(audit)


def test_sirach_audit_rejects_non_sirach_source() -> None:
    document = parse_parallel_text("Gen 1:1\nHB\tGR\n", source_name="01.Genesis.par")
    with pytest.raises(ValueError, match="Sirach"):
        audit_sirach_witnesses(document)
