from __future__ import annotations

import pytest

from catss_tf.parser import alignment_id_for, parse_parallel_text
from catss_tf.tf_schema import FEATURE_SPECS


def test_known_genesis_6_19_source_repair_is_explicit_and_semantic_only() -> None:
    raw = "--= '' =H/BHMH\tTW=N KTHNW=N"
    document = parse_parallel_text(
        f"Gen 6:19\n{raw}\n",
        source_name="01.Genesis.par",
    )
    alignment = document.verses[0].alignments[0]

    assert alignment.raw_lines == (raw,)
    assert alignment.mt_raw == "--= '' =H/BHMH"
    assert alignment.lxx_raw == "TW=N KTHNW=N"
    assert alignment.alignment_id == alignment_id_for(
        source_name="01.Genesis.par",
        header_raw="Gen 6:19",
        source_lines=(2,),
        raw_lines=(raw,),
    )

    assert alignment.mt_col_a == "--+ ''"
    assert alignment.mt_col_b == "H/BHMH"
    assert alignment.is_lxx_plus is True
    assert alignment.mt_count == 0
    assert alignment.lxx_count == 2
    assert alignment.has_retroversion is True
    assert alignment.retroversion_kind == "plain"

    repairs = tuple(
        annotation for annotation in alignment.annotations if annotation.kind == "source_repair"
    )
    assert len(repairs) == 1
    repair = repairs[0]
    assert repair.side == "mt_a"
    assert repair.family == "provenance"
    assert repair.contextual is True
    assert repair.raw == "--= '' =H/BHMH"
    assert repair.payload == "--+ '' =H/BHMH"

    assert "catss_sem_source_repair" in FEATURE_SPECS


@pytest.mark.parametrize(
    ("source_name", "mt_cell"),
    (
        ("02.Exodus.par", "--= '' =H/BHMH"),
        ("01.Genesis.par", "--= '' =H/XYH"),
    ),
)
def test_known_source_repair_does_not_generalize_to_lookalikes(
    source_name: str,
    mt_cell: str,
) -> None:
    document = parse_parallel_text(
        f"Gen 6:19\n{mt_cell}\tTW=N KTHNW=N\n",
        source_name=source_name,
    )
    alignment = document.verses[0].alignments[0]

    assert alignment.mt_raw == mt_cell
    assert alignment.is_lxx_plus is False
    assert alignment.mt_col_a == "--"
    assert not any(annotation.kind == "source_repair" for annotation in alignment.annotations)
