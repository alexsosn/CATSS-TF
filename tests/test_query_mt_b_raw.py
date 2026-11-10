"""Loaded native-TF contracts for raw reconstructed MT column B query.

These synthetic forms mirror source shapes already covered by canonical writer
tests, but do not commit licensed CATSS rows.
"""

from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import pytest
from tf.fabric import Fabric  # type: ignore[import-untyped]

from catss_tf import CanonicalMtBRawHit, find_mt_b_raw_matches
from catss_tf.canonical_materializer import materialize_corpus


def _loaded(tmp_path: Path) -> Any:
    source = tmp_path / "source"
    source.mkdir()
    (source / "01.Genesis.par").write_text(
        "Gen 1:1\n"
        "=;W/KL\tKAI\\\\ PA=S\n"
        "--+ =;W/KL\tLOGOS\n"
        "^^^ ^ =W/KL\tLOGOS\n"
        "MLK\tLOGOS\n"
        "=v\tLOGOS\n"
        "Gen 1:2\n"
        "=W/KLH\tLOGOS\n",
        encoding="utf-8",
    )
    (source / "06.JoshB.par").write_text("JoshB 1:1\n=W/KL\tLOGOS\n", encoding="utf-8")
    materialize_corpus(source, tmp_path / "catss")
    return Fabric(locations=str(tmp_path), modules=("catss",), silent="deep").loadAll(silent="deep")


def _oracle(
    api: Any,
    needle: str,
    *,
    source: str | None = None,
    retro_kind: str | None = None,
) -> tuple[tuple[str, str, str, str], ...]:
    """Independent exhaustive scan of alignment slots, never a B-feature index."""
    if "catss_mt_col_b" not in set(api.Fall()):
        return ()
    result: list[tuple[str, str, str, str]] = []
    for slot in api.F.otype.s("alignment"):
        raw = api.F.catss_mt_col_b.v(slot)
        if not isinstance(raw, str) or needle not in raw:
            continue
        kind = api.F.catss_retro_kind.v(slot)
        name = api.F.catss_source.v(slot)
        if source is not None and name != source:
            continue
        if retro_kind is not None and kind != retro_kind:
            continue
        result.append((str(name), str(api.F.catss_alignment_id.v(slot)), raw, str(kind)))
    return tuple(result)


@pytest.mark.parametrize(
    ("needle", "source", "kind", "expected"),
    (
        ("W/KL", None, None, 5),
        ("W/KL", "01.Genesis.par", None, 4),
        ("W/KL", "06.JoshB.par", None, 1),
        ("W/KL", None, "context", 2),
        ("W/KL", None, "plain", 3),
        ("W/KLH", None, None, 1),
        ("w/kl", None, None, 0),
        ("MLK", None, None, 0),
        ("v", None, "vocalization", 1),
        ("W/KL", "02.Exodus.par", None, 0),
    ),
)
def test_mt_b_raw_matches_independent_loaded_tf_oracle(
    tmp_path: Path,
    needle: str,
    source: str | None,
    kind: str | None,
    expected: int,
) -> None:
    api = _loaded(tmp_path)
    hits = tuple(find_mt_b_raw_matches(api, needle, source=source, retro_kind=kind))
    assert len(hits) == expected
    assert all(isinstance(hit, CanonicalMtBRawHit) for hit in hits)
    assert tuple(
        (hit.group.source, hit.group.alignment_id, hit.mt_b_raw, hit.retro_kind) for hit in hits
    ) == _oracle(api, needle, source=source, retro_kind=kind)
    assert len({hit.group.alignment_id for hit in hits}) == len(hits)


def test_mt_b_raw_retains_marker_plus_and_original_greek_order(tmp_path: Path) -> None:
    api = _loaded(tmp_path)
    hits = tuple(find_mt_b_raw_matches(api, "W/KL", source="01.Genesis.par", retro_kind="plain"))
    assert len(hits) == 2
    assert hits[0].mt_b_raw == "W/KL"
    assert hits[0].group.mt_elements == ()
    assert hits[0].group.lxx_elements == ("LOGOS",)
    plus = tuple(find_mt_b_raw_matches(api, ";W/KL", retro_kind="context"))
    assert len(plus) == 2
    assert all(hit.group.mt_elements == () for hit in plus)
    assert plus[0].group.lxx_elements == ("KAI\\", "PA=S")
    assert plus[1].group.lxx_elements == ("LOGOS",)


def test_no_column_b_feature_returns_empty_iterator(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "01.Genesis.par").write_text("Gen 1:1\nMLK\tLOGOS\n", encoding="utf-8")
    materialize_corpus(source, tmp_path / "catss")
    api = Fabric(locations=str(tmp_path), modules=("catss",), silent="deep").loadAll(silent="deep")
    assert "catss_mt_col_b" not in set(api.Fall())
    assert tuple(find_mt_b_raw_matches(api, "MLK")) == ()


def test_invalid_search_inputs_fail_before_scanning(tmp_path: Path) -> None:
    api = _loaded(tmp_path)
    invalid: tuple[tuple[Any, dict[str, Any]], ...] = (
        ("", {}),
        ("  ", {}),
        (cast(Any, 4), {}),
        (cast(Any, b"W/KL"), {}),
        ("W/KL", {"source": ""}),
        ("W/KL", {"source": cast(Any, 3)}),
        ("W/KL", {"retro_kind": ""}),
        ("W/KL", {"retro_kind": cast(Any, 3)}),
    )
    for needle, kwargs in invalid:
        with pytest.raises(ValueError):
            tuple(find_mt_b_raw_matches(api, needle, **kwargs))


def test_wrong_parent_warp_is_rejected() -> None:
    wrong = SimpleNamespace(F=SimpleNamespace(otype=SimpleNamespace(slotType="word")))
    with pytest.raises(ValueError, match="alignment-slot"):
        tuple(find_mt_b_raw_matches(wrong, "W/KL"))
