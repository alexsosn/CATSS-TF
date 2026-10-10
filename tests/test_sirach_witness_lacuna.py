"""Sirach manuscript lacunae are not Greek additions against MT."""

import dataclasses
from typing import Any

import pytest

from catss_tf.lxx_materializer import _semantic_kinds
from catss_tf.parser import AlignmentRecord, parse_parallel_text
from catss_tf.technique import TechniqueError, derive_alignment_technique, derive_technique_state


def _alignment(row: str, *, source: str = "27.Sirach.par") -> AlignmentRecord:
    header = "Sir 2:13" if source == "27.Sirach.par" else "Gen 2:13"
    doc = parse_parallel_text(f"{header}\n{row}\n", source_name=source)
    return doc.verses[0].alignments[0]


def test_sirach_witness_lacuna_derives_without_translation_addition() -> None:
    alignment = _alignment("[..]\tOU)AI\\")
    assert (alignment.mt_count, alignment.lxx_count) == (0, 1)
    assert any(
        a.side == "mt_a" and a.kind == "sirach_lacuna_or_illegible" for a in alignment.annotations
    )
    technique = derive_alignment_technique("27.Sirach.par", alignment)
    assert technique.cardinality_mt_lxx == "zero_one"
    assert technique.token_balance_mt_lxx == "not_applicable"
    assert not technique.addition_vs_mt
    assert not technique.omission_vs_mt


def test_sirach_lacuna_is_not_allowed_on_wrong_source_or_annotation_scope() -> None:
    base = _alignment("[..]\tOU)AI\\")
    wrong_source = dataclasses.replace(
        base,
        alignment_id=base.alignment_id.replace("27.Sirach.par", "01.Genesis.par"),
    )
    wrong_side = dataclasses.replace(
        base,
        annotations=tuple(dataclasses.replace(a, side="lxx") for a in base.annotations),
    )
    for alignment, source in (
        (wrong_source, "01.Genesis.par"),
        (wrong_side, "27.Sirach.par"),
        (dataclasses.replace(base, mt_col_a="[BN] 3"), "27.Sirach.par"),
        (dataclasses.replace(base, mt_col_a="3 [..]"), "27.Sirach.par"),
        (_alignment("\t[..] OU)AI\\"), "27.Sirach.par"),
    ):
        assert alignment.mt_count == 0 and alignment.lxx_count > 0
        with pytest.raises(TechniqueError, match="Hebrew-empty"):
            derive_alignment_technique(source, alignment)


def test_typed_witness_lacuna_has_no_plus_and_rejects_contradictions() -> None:
    base: dict[str, Any] = dict(
        mt_n=0,
        lxx_n=1,
        is_lxx_plus=False,
        is_lxx_minus=False,
        trans_local=False,
        trans_remote=False,
        trans_style=False,
        sirach_witness_lacuna=True,
    )
    derived = derive_technique_state(**base)
    assert not derived.addition_vs_mt
    assert not derived.omission_vs_mt
    for extra in (
        {"mt_n": 1},
        {"lxx_n": 0},
        {"is_lxx_plus": True},
        {"apparent_mt_minus": True},
    ):
        with pytest.raises(TechniqueError):
            derive_technique_state(**(base | extra))


def test_lxx_word_inherits_scoped_sirach_mt_witness_evidence() -> None:
    alignment = _alignment("[..]\tOU)AI\\")
    semantics = _semantic_kinds(alignment, side="lxx", element_index=1)
    assert "sirach_lacuna_or_illegible" in semantics
