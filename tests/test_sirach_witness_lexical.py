"""Sirach textual witnesses do not become Hebrew lexical elements."""

from pathlib import Path
from typing import Any

from tf.fabric import Fabric  # type: ignore[import-untyped]

from catss_tf.canonical_materializer import materialize_corpus
from catss_tf.parser import alignment_id_for, parse_parallel_text
from catss_tf.technique import derive_alignment_technique


def test_sirach_mt_a_witness_numbers_and_absence_labels_are_not_mt_words() -> None:
    document = parse_parallel_text(
        """Sir 2:13
HB 1\tGR
HB 3 7\tGR2
[..] 7\tGR3
HB >8\tGR4
HB =;ALT 3\tGR5
HB 10\tGR6
""",
        source_name="27.Sirach.par",
    )
    rows = document.verses[0].alignments
    assert tuple(row.mt_tokens for row in rows) == (
        ("HB",),
        ("HB",),
        (),
        ("HB",),
        ("HB",),
        ("HB",),
    )
    assert tuple(row.mt_count for row in rows) == (1, 1, 0, 1, 1, 1)
    assert rows[4].mt_col_b == ";ALT 3"
    assert any(a.side == "mt_b" and a.raw == "3" for a in rows[4].annotations)
    assert [a.raw for a in rows[1].annotations if a.kind.startswith("sirach_witness_")] == [
        "3",
        "7",
    ]
    assert any(
        a.kind == "sirach_reading_lacking_in_witness" and a.raw == ">8"
        for a in rows[3].annotations
    )

    lacuna = rows[2]
    technique = derive_alignment_technique(document.source_name, lacuna)
    assert technique.cardinality_mt_lxx == "zero_one"
    assert technique.token_balance_mt_lxx == "not_applicable"
    assert not technique.addition_vs_mt and not technique.omission_vs_mt
    for row in rows:
        assert row.raw_lines
        assert row.alignment_id == alignment_id_for(
            source_name=document.source_name,
            header_raw=document.verses[0].header_raw,
            source_lines=row.source_lines,
            raw_lines=row.raw_lines,
        )


def test_non_sirach_and_ambiguous_numeric_lexical_text_stays_intact() -> None:
    cases = (
        ("01.Genesis.par", "Gen 1:1", "HB 7", ("HB", "7")),
        ("99.Test.par", "Sir 1:1", "HB 7", ("HB", "7")),
        ("27.Sirach.par", "Sir 1:1", "HB7", ("HB7",)),
        ("27.Sirach.par", "Sir 1:1", "HB >12", ("HB", ">12")),
    )
    for source, header, mt, expected in cases:
        doc = parse_parallel_text(f"{header}\n{mt}\tLOGOS\n", source_name=source)
        assert doc.verses[0].alignments[0].mt_tokens == expected


def test_sirach_canonical_tf_excludes_witness_digit_word_nodes(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    rows = "Sir 2:13\nHB 1\tLOGOS\n[..] 7\tOU)AI\\\nHB >8\tQEOS\n"
    (source / "27.Sirach.par").write_text(rows, encoding="utf-8")
    result = materialize_corpus(source, tmp_path / "catss")
    assert result.summary.mt_elements == 2
    api: Any = Fabric(locations=str(tmp_path), modules=("catss",), silent="deep").loadAll(
        silent="deep"
    )
    assert tuple(api.F.catss_mt_n.v(slot) for slot in (1, 2, 3)) == (1, 0, 1)
    assert tuple(api.F.catss_text.v(n) for n in api.F.otype.s("mt_element")) == ("HB", "HB")
    for slot in (1, 2, 3):
        assert tuple(api.L.u(slot, otype="annotation"))
        assert tuple(api.L.u(slot, otype="source_line"))
    assert api.F.catss_tt_status.v(2) == "derived"
    assert api.F.catss_tt_cardinality_mt_lxx.v(2) == "zero_one"
