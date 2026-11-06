"""Native TF Sirach witness annotation queries, never individual word attestations."""

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from tf.fabric import Fabric  # type: ignore[import-untyped]

from catss_tf import find_sirach_witness_annotations
from catss_tf.canonical_materializer import materialize_corpus


def _api(tmp_path: Path) -> Any:
    root = tmp_path / "source"
    root.mkdir()
    (root / "27.Sirach.par").write_text(
        """Sir 2:13
HB 7\tLOGOS
HB >7\tQEOS
HB 3 7\tLOGOS QEOS
HB =;RETRO 7\tLOGOS
[..] 7\tQEOS
HB 10\tLOGOS
""",
        encoding="utf-8",
    )
    (root / "01.Genesis.par").write_text("Gen 1:1\nHB 7\tQEOS\n", encoding="utf-8")
    materialize_corpus(root, tmp_path / "catss")
    return Fabric(locations=str(tmp_path), modules=("catss",), silent="deep").loadAll(silent="deep")


def _oracle(api: Any, witness: int, mode: str, side: str | None) -> tuple[tuple[int, int], ...]:
    """Independent exhaustive per-slot oracle (does not scan F.catss_kind.items())."""
    kinds = {
        1: "sirach_witness_geniza_b",
        3: "sirach_witness_geniza_a",
        7: "sirach_witness_masada",
        10: "sirach_witness_2q18",
    }
    target = kinds[witness] if mode == "marked" else "sirach_reading_lacking_in_witness"
    matches: list[tuple[int, int]] = []
    for slot in api.F.otype.s("alignment"):
        if api.F.catss_source.v(slot) != "27.Sirach.par":
            continue
        for node in api.L.u(slot, otype="annotation"):
            if api.F.catss_kind.v(node) != target:
                continue
            if mode == "lacking" and api.F.catss_payload.v(node) != str(witness):
                continue
            if side is not None and api.F.catss_side.v(node) != side:
                continue
            matches.append((slot, node))
    return tuple(sorted(matches))


def test_witness_query_returns_each_source_annotation_not_word_edges(tmp_path: Path) -> None:
    api = _api(tmp_path)
    all_hits = tuple(find_sirach_witness_annotations(api, 7))
    assert len(all_hits) == 4
    assert tuple((h.alignment_slot, h.annotation_node) for h in all_hits) == _oracle(
        api, 7, "marked", None
    )
    assert [h.source_side for h in all_hits] == ["mt_a", "mt_a", "mt_b", "mt_a"]
    assert [h.raw for h in all_hits] == ["7", "7", "7", "7"]
    assert all(h.source == "27.Sirach.par" and h.book == "Sir" for h in all_hits)
    assert len({h.alignment_id for h in all_hits}) == 4
    assert all(h.mode == "marked" and h.witness == 7 for h in all_hits)
    assert all_hits[1].mt_elements == ("HB",)
    assert all_hits[1].lxx_elements == ("LOGOS", "QEOS")
    assert all_hits[2].mt_elements == ("HB",)  # MT-B 7 is not an MT-A word


def test_lacking_marker_and_exact_source_column_are_distinct(tmp_path: Path) -> None:
    api = _api(tmp_path)
    lacks = tuple(find_sirach_witness_annotations(api, 7, mode="lacking"))
    assert tuple((h.alignment_slot, h.annotation_node) for h in lacks) == _oracle(
        api, 7, "lacking", None
    )
    assert len(lacks) == 1
    assert lacks[0].raw == ">7"
    assert lacks[0].source_side == "mt_a"
    assert lacks[0].mode == "lacking"
    assert tuple(find_sirach_witness_annotations(api, 7, mode="lacking", side="mt_b")) == ()
    mt_a = tuple(find_sirach_witness_annotations(api, 7, side="mt_a"))
    mt_b = tuple(find_sirach_witness_annotations(api, 7, side="mt_b"))
    assert len(mt_a) == 3 and len(mt_b) == 1
    assert tuple((h.alignment_slot, h.annotation_node) for h in mt_b) == _oracle(
        api, 7, "marked", "mt_b"
    )
    assert len(tuple(find_sirach_witness_annotations(api, 3))) == 1
    assert len(tuple(find_sirach_witness_annotations(api, 10))) == 1
    assert tuple(find_sirach_witness_annotations(api, 1)) == ()


@pytest.mark.parametrize("witness", (0, 11, 12, -1, True, "7"))
def test_unknown_witness_fails_closed(tmp_path: Path, witness: Any) -> None:
    api = _api(tmp_path)
    with pytest.raises(ValueError, match="witness"):
        tuple(find_sirach_witness_annotations(api, witness))


@pytest.mark.parametrize(("mode", "side"), (("negative", None), ("marked", "lxx")))
def test_unknown_query_mode_or_side_fails_closed(tmp_path: Path, mode: Any, side: Any) -> None:
    api = _api(tmp_path)
    with pytest.raises(ValueError):
        tuple(find_sirach_witness_annotations(api, 7, mode=mode, side=side))


def test_incompatible_word_slot_warp_fails_before_scanning(tmp_path: Path) -> None:
    _api(tmp_path)
    fake: Any = SimpleNamespace(F=SimpleNamespace(otype=SimpleNamespace(slotType="word")))
    with pytest.raises(ValueError, match="alignment"):
        tuple(find_sirach_witness_annotations(fake, 7))


@pytest.mark.parametrize(
    ("row", "expected"),
    (
        ("HB 7\tLOGOS", 1),
        ("HB\tLOGOS", 0),
        ("HB\t7 QEOS", 0),
    ),
)
def test_sparse_canonical_features_and_greek_column_do_not_create_false_witnesses(
    tmp_path: Path, row: str, expected: int
) -> None:
    root = tmp_path / "source"
    root.mkdir()
    (root / "27.Sirach.par").write_text(f"Sir 2:13\n{row}\n", encoding="utf-8")
    materialize_corpus(root, tmp_path / "catss")
    fabric = Fabric(locations=str(tmp_path), modules=("catss",), silent="deep")
    api: Any = fabric.loadAll(silent="deep")
    assert "catss_payload" not in api.Fall()
    hits = tuple(find_sirach_witness_annotations(api, 7))
    assert len(hits) == expected
    assert all(h.payload is None and h.source_side == "mt_a" for h in hits)
    assert tuple(find_sirach_witness_annotations(api, 7, mode="lacking")) == ()
