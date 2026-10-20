"""Sirach parser-status transitions are inspectable without publishing source words."""

import pytest

from catss_tf.parser import parse_parallel_text
from catss_tf.sirach_unclassified_research import audit_sirach_unclassified_context


def _sample():
    return parse_parallel_text(
        """Sir 2:13
HB\tLOGOS
7\tQEOS
7\t---
HB 3\tFWS
7 =;RETRO 3\tLOGOS
HB\tLOGOS
HB >12\tQEOS
""",
        source_name="27.Sirach.par",
    )


def test_sirach_newly_unclassified_groups_have_source_safe_context() -> None:
    report = audit_sirach_unclassified_context(_sample())

    assert report.source == "27.Sirach.par"
    assert report.newly_unclassified == 3
    hebrew_empty_reason = (
        "Hebrew-empty Greek alignment requires CATSS LXX-plus, apparent MT minus, "
        "or transposition evidence"
    )
    assert dict(report.transition_reasons) == {
        hebrew_empty_reason: 2,
        "CATSS LXX-minus requires MT lexical material": 1,
    }
    counts = dict(report.context_counts)
    assert counts["has_mt_a_witness_marker"] == 3
    assert counts["has_mt_b_column"] == 1
    assert counts["has_mt_b_witness_marker"] == 1
    assert counts["has_lxx_minus"] == 1
    assert counts["has_lxx_lexical"] == 2
    assert counts["neighbor_left_with_mt"] == 2
    assert counts["neighbor_right_with_mt"] == 2
    assert counts["neighbor_both_with_mt"] == 1
    assert counts.get("has_absence_marker", 0) == 0
    assert counts.get("has_lacuna", 0) == 0
    assert counts.get("has_continuation", 0) == 0
    assert all(
        len(positions) <= 3 and all(len(location) == 4 for location in positions)
        for _kind, positions in report.samples
    )
    assert all(
        location[0] == "Sir" for _kind, positions in report.samples for location in positions
    )
    assert "LOGOS" not in repr(report)
    assert "RETRO" not in repr(report)
    assert "QEOS" not in repr(report)


def test_newly_unclassified_audit_ignores_derived_and_ambiguous_digits() -> None:
    doc = parse_parallel_text(
        """Sir 2:13
HB 7\tLOGOS
HB >12\tQEOS
HB\tLOGOS
""",
        source_name="27.Sirach.par",
    )
    report = audit_sirach_unclassified_context(doc)
    assert report.newly_unclassified == 0
    assert report.changed_groups == 1
    assert report.transition_reasons == ()


def test_sirach_audit_rejects_other_source_and_preserves_empty_snapshot() -> None:
    doc = parse_parallel_text("Gen 1:1\nHB\tLOGOS\n", source_name="01.Genesis.par")
    with pytest.raises(ValueError, match="27.Sirach.par"):
        audit_sirach_unclassified_context(doc)

    empty = parse_parallel_text("Sir 2:13\nHB\tLOGOS\n", source_name="27.Sirach.par")
    report = audit_sirach_unclassified_context(empty)
    assert report.newly_unclassified == 0
    assert report.context_counts == ()
    assert report.samples == ()
