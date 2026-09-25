import dataclasses

from catss_tf.parser import parse_parallel_text
from catss_tf.validation import validate_document, validate_documents


def test_clean_document_has_zero_unresolved_and_complete_accounting() -> None:
    doc = parse_parallel_text(
        """Test 1:1
HB1\tGR1
HB2\tGR2
""",
        source_name="99.Test.par",
    )

    report = validate_document(doc)

    assert report.ok is True
    assert report.summary.source_files == 1
    assert report.summary.verses == 1
    assert report.summary.alignments == 2
    assert report.summary.source_data_lines == 2
    assert report.summary.accounted_lines == 2
    assert report.summary.unaccounted_lines == 0
    assert report.summary.parser_diagnostics == 0
    assert report.summary.unknown_annotations == 0
    assert report.summary.invalid_alignment_ids == 0
    assert report.summary.duplicate_alignment_ids == 0
    assert report.summary.error_count == 0
    assert report.summary.unresolved_count == 0
    assert report.summary.ignored_count == 0
    assert report.findings == ()


def test_parser_diagnostics_become_typed_unresolved_findings() -> None:
    doc = parse_parallel_text(
        """ORPHAN
Test 1:1
UNSPLIT
""",
        source_name="99.Test.par",
    )

    report = validate_document(doc)

    assert report.ok is False
    assert report.summary.parser_diagnostics == 2
    assert [finding.code for finding in report.findings] == [
        "orphan_line",
        "unsplit_row",
    ]
    assert all(finding.severity == "unresolved" for finding in report.findings)


def test_unknown_annotations_are_preserved_and_unresolved() -> None:
    doc = parse_parallel_text(
        """Test 1:1
HB .xx {zzUNKNOWN}\tGR
""",
        source_name="99.Test.par",
    )

    report = validate_document(doc)

    assert report.summary.unknown_annotations == 2
    assert [(finding.code, finding.side, finding.raw) for finding in report.findings] == [
        ("unknown_annotation", "mt_a", "{zzUNKNOWN}"),
        ("unknown_mt_strategy_siglum", "mt_a", ".xx"),
    ]
    assert report.summary.unresolved_count == 2


def test_allow_list_keeps_finding_but_marks_it_ignored() -> None:
    doc = parse_parallel_text(
        """Test 1:1
HB {zzUNKNOWN}\tGR
""",
        source_name="99.Test.par",
    )

    report = validate_document(doc, allowed_codes={"unknown_annotation"})

    assert report.ok is True
    assert report.summary.unresolved_count == 0
    assert report.summary.ignored_count == 1
    assert report.findings[0].severity == "ignored"
    assert report.findings[0].code == "unknown_annotation"


def test_alignment_id_mismatch_is_a_hard_error() -> None:
    doc = parse_parallel_text(
        """Test 1:1
HB\tGR
""",
        source_name="99.Test.par",
    )
    verse = doc.verses[0]
    bad_row = dataclasses.replace(verse.alignments[0], alignment_id="catss:tampered")
    bad_doc = dataclasses.replace(
        doc,
        verses=(dataclasses.replace(verse, alignments=(bad_row,)),),
    )

    report = validate_document(bad_doc)

    assert report.ok is False
    assert report.summary.invalid_alignment_ids == 1
    assert report.summary.error_count == 1
    finding = report.findings[0]
    assert finding.code == "alignment_id_mismatch"
    assert finding.alignment_id == "catss:tampered"


def test_duplicate_alignment_id_and_line_ownership_are_hard_errors() -> None:
    doc = parse_parallel_text(
        """Test 1:1
HB\tGR
""",
        source_name="99.Test.par",
    )
    verse = doc.verses[0]
    duplicated = dataclasses.replace(
        doc,
        verses=(
            dataclasses.replace(
                verse,
                alignments=(verse.alignments[0], verse.alignments[0]),
            ),
        ),
    )

    report = validate_document(duplicated)

    codes = [finding.code for finding in report.findings]
    assert "duplicate_alignment_id" in codes
    assert "duplicate_source_line_ownership" in codes
    assert report.summary.duplicate_alignment_ids == 1
    assert report.summary.error_count == 2


def test_unaccounted_source_line_is_a_hard_error() -> None:
    doc = parse_parallel_text(
        """Test 1:1
HB\tGR
""",
        source_name="99.Test.par",
    )
    bad_doc = dataclasses.replace(doc, data_line_numbers=(2, 99))

    report = validate_document(bad_doc)

    assert report.summary.source_data_lines == 2
    assert report.summary.accounted_lines == 1
    assert report.summary.unaccounted_lines == 1
    finding = next(f for f in report.findings if f.code == "unaccounted_source_line")
    assert finding.line_no == 99
    assert finding.severity == "error"


def test_validate_documents_detects_duplicate_ids_across_documents() -> None:
    first = parse_parallel_text(
        """Test 1:1
HB\tGR
""",
        source_name="99.Test.par",
    )
    second = parse_parallel_text(
        """Test 1:1
HB\tGR
""",
        source_name="99.Test.par",
    )

    report = validate_documents((first, second))

    assert report.summary.source_files == 2
    assert report.summary.duplicate_alignment_ids == 1
    assert any(f.code == "duplicate_alignment_id" for f in report.findings)
