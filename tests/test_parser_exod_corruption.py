"""RED-first tests for exact Exodus 35:19 corrupted header repair."""

from __future__ import annotations

import pytest

from catss_tf.parser import ParallelDocument, alignment_id_for, parse_parallel_text
from catss_tf.validation import validate_document

HEAD = "^ ^^^ =L/$RT {...?H/&RD} #\t{+} E)N AI(=S LEITOURGH/SOUSIN"
TAIL = "--+\tE)N AU)TAI=S"
CORRUPTION = (HEAD, "", "Exod 1:10", "    #", "", "Exod 35:19", TAIL)


def _parse(
    lines: tuple[str, ...] = CORRUPTION,
    *,
    source: str = "02.Exodus.par",
    verse: str = "Exod 35:19",
) -> ParallelDocument:
    return parse_parallel_text(
        verse + "\n" + "\n".join(lines) + "\n",
        source_name=source,
    )


def test_exod_35_19_corrupt_header_rejoins_one_row_with_all_physical_provenance() -> None:
    doc = _parse()

    assert len(doc.verses) == 1
    assert (doc.verses[0].book, doc.verses[0].chapter, doc.verses[0].verse) == ("Exod", 35, 19)
    assert len(doc.verses[0].alignments) == 1
    alignment = doc.verses[0].alignments[0]

    # All seven source lines remain queryable, including blanks and false headers.
    assert alignment.source_lines == tuple(range(2, 9))
    assert alignment.raw_lines == CORRUPTION
    assert doc.data_line_numbers == tuple(range(2, 9))
    assert alignment.alignment_id == alignment_id_for(
        source_name="02.Exodus.par",
        header_raw="Exod 35:19",
        source_lines=tuple(range(2, 9)),
        raw_lines=CORRUPTION,
    )
    assert alignment.mt_raw == "^ ^^^ =L/$RT {...?H/&RD} --+"
    assert alignment.lxx_raw == "{+} E)N AI(=S LEITOURGH/SOUSIN E)N AU)TAI=S"
    assert not [d for d in doc.diagnostics if d.code == "malformed_continuation"]

    report = validate_document(doc)
    assert report.summary.source_data_lines == 7
    assert report.summary.unaccounted_lines == 0
    assert report.summary.invalid_alignment_ids == 0


@pytest.mark.parametrize(
    ("source", "verse", "lines"),
    [
        ("01.Genesis.par", "Exod 35:19", CORRUPTION),
        ("02.Exodus.par", "Exod 35:18", CORRUPTION),
        (
            "02.Exodus.par",
            "Exod 35:19",
            (HEAD.replace("LEITOURGH/SOUSIN", "LEITOURGH/SOUSINX"), *CORRUPTION[1:]),
        ),
        ("02.Exodus.par", "Exod 35:19", (*CORRUPTION[:-1], "--+\tE)N AU)TAI=S X")),
    ],
)
def test_exodus_corruption_repair_does_not_generalize(
    source: str, verse: str, lines: tuple[str, ...]
) -> None:
    doc = _parse(lines, source=source, verse=verse)

    # A near-miss retains the old hard-boundary behavior; no silent guessed repairs.
    assert any((v.chapter, v.verse) == (1, 10) for v in doc.verses)
    assert len(doc.verses) > 1
    assert any(d.code == "malformed_continuation" for d in doc.diagnostics)


def test_exodus_repair_is_stable_under_source_line_offset() -> None:
    doc = parse_parallel_text(
        "Exod 35:18\nAB\tCD\n\nExod 35:19\n" + "\n".join(CORRUPTION) + "\n",
        source_name="02.Exodus.par",
    )
    assert len(doc.verses) == 2
    repaired = doc.verses[1].alignments[0]
    assert repaired.raw_lines == CORRUPTION
    assert repaired.source_lines == tuple(range(5, 12))
    assert not any(d.code == "malformed_continuation" for d in doc.diagnostics)
