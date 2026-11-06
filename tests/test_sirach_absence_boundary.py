"""Regression: Sirach >n is a complete manuscript number, not a prefix."""

from pathlib import Path
from typing import Any

import pytest
from tf.fabric import Fabric  # type: ignore[import-untyped]

from catss_tf import find_sirach_witness_annotations, materialize_corpus
from catss_tf.parser import parse_parallel_text


@pytest.mark.parametrize(
    ("cell", "expected"),
    (
        ("HB >1", (">1",)),
        ("HB >7", (">7",)),
        ("HB >10", (">10",)),
        ("HB >12", ()),
        ("HB >11", ()),
        ("HB >101", ()),
        ("HB >21", ()),
        ("HB >12 >7 >101 >1 >10", (">7", ">1", ">10")),
        ("HBx>7tail", (">7",)),
    ),
)
def test_sirach_absence_annotations_do_not_accept_numeric_prefixes(
    cell: str, expected: tuple[str, ...]
) -> None:
    document = parse_parallel_text(f"Sir 2:13\n{cell}\tLOGOS\n", source_name="27.Sirach.par")
    row = document.verses[0].alignments[0]
    markers = tuple(a for a in row.annotations if a.kind == "sirach_reading_lacking_in_witness")
    assert tuple(a.raw for a in markers) == expected
    assert tuple(a.payload for a in markers) == tuple(raw[1:] for raw in expected)


def test_witness_absence_detection_keeps_mt_b_scope_and_non_sirach_negative() -> None:
    sirach = parse_parallel_text(
        "Sir 2:13\nHB =;RETRO >8 >12\tLOGOS\n",
        source_name="27.Sirach.par",
    )
    annotations = [
        a
        for a in sirach.verses[0].alignments[0].annotations
        if a.kind == "sirach_reading_lacking_in_witness"
    ]
    assert [(a.raw, a.side, a.payload) for a in annotations] == [(">8", "mt_b", "8")]

    genesis = parse_parallel_text(
        "Gen 2:13\nHB >7\tLOGOS\n",
        source_name="01.Genesis.par",
    )
    assert all(
        a.kind != "sirach_reading_lacking_in_witness"
        for a in genesis.verses[0].alignments[0].annotations
    )


def test_invalid_number_prefix_creates_no_canonical_witness_lacking_hit(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "27.Sirach.par").write_text(
        "Sir 2:13\nHB >12\tLOGOS\nHB >101\tLOGOS\nHB >7\tQEOS\n",
        encoding="utf-8",
    )
    result = materialize_corpus(source, tmp_path / "catss")
    assert result.summary.alignments == 3
    api: Any = Fabric(locations=str(tmp_path), modules=("catss",), silent="deep").loadAll(
        silent="deep"
    )
    assert tuple(find_sirach_witness_annotations(api, 1, mode="lacking")) == ()
    assert tuple(find_sirach_witness_annotations(api, 10, mode="lacking")) == ()
    hits = tuple(find_sirach_witness_annotations(api, 7, mode="lacking"))
    assert len(hits) == 1
    assert (hits[0].raw, hits[0].payload, hits[0].source_side) == (">7", "7", "mt_a")
    assert tuple(api.F.catss_mt_col_a.v(slot) for slot in (1, 2)) == ("HB >12", "HB >101")
