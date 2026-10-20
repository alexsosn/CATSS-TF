"""Inspect source-preserved, explicitly unresolved canonical CATSS alignments."""

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from tf.fabric import Fabric  # type: ignore[import-untyped]

from catss_tf import find_unclassified_alignments, materialize_corpus


def _loaded(tmp_path: Path, *, unresolved: bool = True) -> Any:
    source = tmp_path / "source"
    source.mkdir()
    if unresolved:
        (source / "27.Sirach.par").write_text(
            """Sir 2:13
HB 7\tLOGOS
3 7\tQEOS
7\t---
[..] 7\tLOGOS
""",
            encoding="utf-8",
        )
    else:
        (source / "27.Sirach.par").write_text("Sir 2:13\nHB\tLOGOS\n", encoding="utf-8")
    (source / "01.Genesis.par").write_text("Gen 1:1\nHB\tLOGOS\n", encoding="utf-8")
    materialize_corpus(source, tmp_path / "catss")
    return Fabric(locations=str(tmp_path), modules=("catss",), silent="deep").loadAll(silent="deep")


def _oracle(api: Any) -> tuple[tuple[int, str, str, tuple[str, ...]], ...]:
    """Independent exhaustive alignment-slot scan, not feature-item lookup."""
    rows: list[tuple[int, str, str, tuple[str, ...]]] = []
    for slot in api.F.otype.s("alignment"):
        if api.F.catss_tt_status.v(slot) != "unclassified":
            continue
        annotations = tuple(api.F.catss_kind.v(node) for node in api.L.u(slot, otype="annotation"))
        rows.append(
            (
                slot,
                api.F.catss_alignment_id.v(slot),
                api.F.catss_tt_unclassified_reason.v(slot),
                annotations,
            )
        )
    return tuple(rows)


def test_unclassified_query_matches_loaded_tf_independent_oracle(tmp_path: Path) -> None:
    api = _loaded(tmp_path)
    hits = tuple(find_unclassified_alignments(api))
    assert len(hits) == 2
    assert tuple(
        (hit.alignment_slot, hit.alignment_id, hit.reason, tuple(a.kind for a in hit.annotations))
        for hit in hits
    ) == _oracle(api)
    assert all(hit.source == "27.Sirach.par" and hit.book == "Sir" for hit in hits)
    assert [hit.source_line_first for hit in hits] == [3, 4]
    assert [hit.source_line_last for hit in hits] == [3, 4]
    assert all(hit.mt_elements == () and hit.mt_count == 0 for hit in hits)
    assert hits[0].lxx_elements == ("QEOS",)
    assert hits[0].lxx_count == 1
    assert "Hebrew-empty Greek alignment" in hits[0].reason
    assert "LXX-minus requires MT lexical material" in hits[1].reason
    assert hits[1].lxx_elements == ()
    assert any(a.kind == "sirach_witness_masada" and a.side == "mt_a" for a in hits[0].annotations)
    assert any(a.raw == "7" for a in hits[1].annotations)
    assert all(hit.alignment_id.startswith(f"catss:{hit.source}:") for hit in hits)


def test_filters_keep_original_reasons_without_new_status_labels(tmp_path: Path) -> None:
    api = _loaded(tmp_path)
    assert len(tuple(find_unclassified_alignments(api, source="27.Sirach.par"))) == 2
    assert tuple(find_unclassified_alignments(api, source="01.Genesis.par")) == ()
    minus = tuple(find_unclassified_alignments(api, reason_contains="LXX-minus"))
    assert len(minus) == 1
    assert minus[0].source_line_first == 4
    assert len(tuple(find_unclassified_alignments(api, reason_contains="Hebrew-empty"))) == 1
    assert tuple(find_unclassified_alignments(api, reason_contains="not a real error")) == ()


def test_sparse_derived_only_corpus_returns_nothing(tmp_path: Path) -> None:
    api = _loaded(tmp_path, unresolved=False)
    assert "catss_tt_unclassified_reason" not in api.Fall()
    assert tuple(find_unclassified_alignments(api)) == ()


def test_unclassified_query_rejects_wrong_slot_warp() -> None:
    fake: Any = SimpleNamespace(F=SimpleNamespace(otype=SimpleNamespace(slotType="word")))
    with pytest.raises(ValueError, match="alignment"):
        tuple(find_unclassified_alignments(fake))


def test_partially_loaded_tf_cannot_silently_claim_no_unclassified_alignments(
    tmp_path: Path,
) -> None:
    _loaded(tmp_path)
    fabric = Fabric(locations=str(tmp_path), modules=("catss",), silent="deep")
    partial: Any = fabric.load("catss_alignment_id", silent="deep")
    assert partial is not None
    assert partial.F.otype.slotType == "alignment"
    assert "catss_tt_status" not in partial.Fall()
    with pytest.raises(ValueError, match="catss_tt_status"):
        tuple(find_unclassified_alignments(partial))
