"""Ordered source forms must use distinct positions inside one CATSS group."""

from itertools import combinations
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import pytest
from tf.fabric import Fabric  # type: ignore[import-untyped]

import catss_tf
from catss_tf import materialize_corpus


def find_groups_with_ordered_forms(*args: Any, **kwargs: Any) -> Any:
    """Resolve the real public export at runtime, permitting mypy-clean RED."""
    return cast(Any, catss_tf).find_groups_with_ordered_forms(*args, **kwargs)


def _loaded(tmp_path: Path) -> Any:
    source = tmp_path / "source"
    source.mkdir()
    (source / "01.Genesis.par").write_text(
        """Gen 1:1
MLK DBR MLK\tBASILEU/S LOGOS BASILEU/S
MLK DBR\tLOGOS BASILEU/S
DBR MLK\tLOGOS BASILEU/S
MLK DBR\tBASILEU/S QEOS LOGOS
MLK\tPATER
Gen 1:2
MLK\tLOGOS
""",
        encoding="utf-8",
    )
    (source / "06.JoshB.par").write_text("JoshB 1:1\nMLK\tBASILEU/S\n", encoding="utf-8")
    materialize_corpus(source, tmp_path / "catss")
    return Fabric(locations=str(tmp_path), modules=("catss",), silent="deep").loadAll(silent="deep")


def _elements(api: Any, slot: int, otype: str) -> tuple[str, ...]:
    nodes = sorted(api.L.u(slot, otype=otype), key=api.F.catss_index.v)
    return tuple(str(api.F.catss_text.v(n)) for n in nodes)


def _oracle_matches(elements: tuple[str, ...], wanted: tuple[str, ...], *, adjacent: bool) -> bool:
    """Exhaustively enumerate positional combinations, not the query algorithm."""
    if not wanted:
        return True
    return any(
        tuple(elements[index] for index in indexes) == wanted
        and (not adjacent or indexes[-1] - indexes[0] + 1 == len(indexes))
        for indexes in combinations(range(len(elements)), len(wanted))
    )


def _oracle(
    api: Any,
    mt: tuple[str, ...] = (),
    lxx: tuple[str, ...] = (),
    *,
    adjacent: bool = False,
    source: str | None = None,
) -> tuple[str, ...]:
    result: list[str] = []
    for slot in api.F.otype.s("alignment"):
        if source is not None and api.F.catss_source.v(slot) != source:
            continue
        if not _oracle_matches(_elements(api, slot, "mt_element"), mt, adjacent=adjacent):
            continue
        if not _oracle_matches(_elements(api, slot, "lxx_element"), lxx, adjacent=adjacent):
            continue
        result.append(str(api.F.catss_alignment_id.v(slot)))
    return tuple(result)


@pytest.mark.parametrize(
    ("mt", "lxx", "adjacent", "expected"),
    (
        (("MLK", "DBR"), (), False, 3),
        (("DBR", "MLK"), (), False, 2),
        (("DBR", "MLK"), (), True, 2),
        (("MLK", "MLK"), (), False, 1),
        (("MLK", "MLK"), (), True, 0),
        ((), ("BASILEU/S", "LOGOS"), False, 2),
        ((), ("BASILEU/S", "LOGOS"), True, 1),
        ((), ("LOGOS", "BASILEU/S"), True, 3),
        ((), ("BASILEU/S", "BASILEU/S"), False, 1),
        ((), ("BASILEU/S", "BASILEU/S"), True, 0),
        (("MLK", "DBR"), ("BASILEU/S", "LOGOS"), False, 2),
        (("MLK", "DBR"), ("BASILEU/S", "LOGOS"), True, 1),
        ((), ("QEOS", "PATER"), False, 0),
        (("mlk",), (), False, 0),
    ),
)
def test_ordered_query_matches_exhaustive_native_tf_positional_oracle(
    tmp_path: Path,
    mt: tuple[str, ...],
    lxx: tuple[str, ...],
    adjacent: bool,
    expected: int,
) -> None:
    api = _loaded(tmp_path)
    found = tuple(
        find_groups_with_ordered_forms(api, mt_forms=mt, lxx_forms=lxx, adjacent=adjacent)
    )
    assert len(found) == expected
    assert tuple(hit.alignment_id for hit in found) == _oracle(api, mt, lxx, adjacent=adjacent)


def test_source_filter_preserves_order_and_group_identity(tmp_path: Path) -> None:
    api = _loaded(tmp_path)
    found = tuple(
        find_groups_with_ordered_forms(
            api,
            mt_forms=("MLK",),
            lxx_forms=("BASILEU/S",),
            adjacent=True,
            source="06.JoshB.par",
        )
    )
    assert len(found) == 1
    assert found[0].source == "06.JoshB.par"
    assert found[0].mt_elements == ("MLK",)
    assert found[0].lxx_elements == ("BASILEU/S",)
    assert tuple(hit.alignment_id for hit in found) == _oracle(
        api, ("MLK",), ("BASILEU/S",), adjacent=True, source="06.JoshB.par"
    )
    assert (
        tuple(find_groups_with_ordered_forms(api, mt_forms=("MLK",), source="07.JoshA.par")) == ()
    )


def test_invalid_forms_and_adjacent_are_rejected(tmp_path: Path) -> None:
    api = _loaded(tmp_path)
    with pytest.raises(ValueError, match="at least one"):
        tuple(find_groups_with_ordered_forms(api))
    for value in (1, 0, None, "yes", ()):
        with pytest.raises(ValueError, match="adjacent"):
            tuple(find_groups_with_ordered_forms(api, mt_forms=("MLK",), adjacent=cast(Any, value)))
    for values in (("",), (" ",), cast(Any, "MLK"), cast(Any, (5,))):
        with pytest.raises(ValueError):
            tuple(find_groups_with_ordered_forms(api, mt_forms=values))


def test_sparse_feature_and_noncanonical_warp_fail_closed(tmp_path: Path) -> None:
    _loaded(tmp_path)
    api = Fabric(locations=str(tmp_path), modules=("catss",), silent="deep").load(
        "catss_alignment_id", silent="deep"
    )
    assert api is not None
    assert "catss_text" not in api.Fall()
    assert tuple(find_groups_with_ordered_forms(api, mt_forms=("MLK",))) == ()
    fake = SimpleNamespace(F=SimpleNamespace(otype=SimpleNamespace(slotType="word")))
    with pytest.raises(ValueError, match="alignment-slot"):
        tuple(find_groups_with_ordered_forms(fake, mt_forms=("MLK",)))
