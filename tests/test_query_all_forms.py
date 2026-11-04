"""User-facing exact AND/co-membership query on loaded canonical Text-Fabric."""

from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import pytest
from tf.fabric import Fabric  # type: ignore[import-untyped]

from catss_tf import find_groups_with_all_forms
from catss_tf.canonical_materializer import materialize_corpus


def _loaded(tmp_path: Path) -> Any:
    source = tmp_path / "source"
    source.mkdir()
    (source / "01.Genesis.par").write_text(
        """Gen 1:1
MLK DBR\tBASILEU/S LOGOS
MLK\tQEOS
DBR\tLOGOS
Gen 1:2
MLK MLK\tLOGOS BASILEU/S
Gen 1:3
SAME\tOTHER
OTHER\tSAME
SAME\tSAME
""",
        encoding="utf-8",
    )
    (source / "06.JoshB.par").write_text("JoshB 1:1\nMLK\tBASILEU/S\n", encoding="utf-8")
    materialize_corpus(source, tmp_path / "catss")
    return Fabric(locations=str(tmp_path), modules=("catss",), silent="deep").loadAll(silent="deep")


def _oracle(
    api: Any,
    mt_forms: tuple[str, ...],
    lxx_forms: tuple[str, ...],
    source: str | None = None,
) -> tuple[str, ...]:
    """Independent exhaustive slot scan, never using the inverted query strategy."""
    result: list[str] = []
    for slot in api.F.otype.s("alignment"):
        if source is not None and api.F.catss_source.v(slot) != source:
            continue
        mt = {api.F.catss_text.v(n) for n in api.L.u(slot, otype="mt_element")}
        lxx = {api.F.catss_text.v(n) for n in api.L.u(slot, otype="lxx_element")}
        if set(mt_forms) <= mt and set(lxx_forms) <= lxx:
            result.append(str(api.F.catss_alignment_id.v(slot)))
    return tuple(result)


@pytest.mark.parametrize(
    ("mt_forms", "lxx_forms", "expected"),
    (
        ((), ("BASILEU/S", "LOGOS"), 2),
        (("MLK", "DBR"), (), 1),
        (("MLK", "DBR"), ("LOGOS", "BASILEU/S"), 1),
        (("DBR",), ("QEOS",), 0),
        ((), ("QEOS", "LOGOS"), 0),
        (("MLK",), ("BASILEU/S",), 3),
        (("MLK", "MLK"), (), 4),
        ((), ("logos",), 0),
    ),
)
def test_all_forms_match_independent_loaded_tf_oracle(
    tmp_path: Path,
    mt_forms: tuple[str, ...],
    lxx_forms: tuple[str, ...],
    expected: int,
) -> None:
    api = _loaded(tmp_path)
    hits = tuple(find_groups_with_all_forms(api, mt_forms=mt_forms, lxx_forms=lxx_forms))
    assert len(hits) == expected
    assert tuple(hit.alignment_id for hit in hits) == _oracle(api, mt_forms, lxx_forms)
    assert len({hit.alignment_id for hit in hits}) == len(hits)
    if hits:
        assert all(hit.alignment_id.startswith(f"catss:{hit.source}:") for hit in hits)


def test_all_forms_preserve_order_and_exact_source_scope(tmp_path: Path) -> None:
    api = _loaded(tmp_path)
    query = find_groups_with_all_forms(
        api,
        mt_forms=("MLK", "DBR"),
        lxx_forms=("BASILEU/S", "LOGOS"),
        source="01.Genesis.par",
    )
    hits = tuple(query)
    assert len(hits) == 1
    assert hits[0].mt_elements == ("MLK", "DBR")
    assert hits[0].lxx_elements == ("BASILEU/S", "LOGOS")
    assert (hits[0].book, hits[0].chapter, hits[0].verse) == ("Gen", 1, 1)
    assert tuple(hit.alignment_id for hit in hits) == _oracle(
        api, ("MLK", "DBR"), ("BASILEU/S", "LOGOS"), "01.Genesis.par"
    )
    joshb_query = find_groups_with_all_forms(
        api, mt_forms=("MLK",), lxx_forms=("BASILEU/S",), source="06.JoshB.par"
    )
    joshb = tuple(joshb_query)
    assert len(joshb) == 1
    assert joshb[0].book == "JoshB"
    absent = find_groups_with_all_forms(api, mt_forms=("MLK",), source="07.JoshA.par")
    assert tuple(absent) == ()


def test_same_spelling_on_opposite_sides_never_cross_joins(tmp_path: Path) -> None:
    api = _loaded(tmp_path)
    hits = tuple(find_groups_with_all_forms(api, mt_forms=("SAME",), lxx_forms=("SAME",)))
    assert len(hits) == 1
    assert hits[0].mt_elements == ("SAME",)
    assert hits[0].lxx_elements == ("SAME",)
    assert tuple(hit.alignment_id for hit in hits) == _oracle(api, ("SAME",), ("SAME",))
    assert tuple(find_groups_with_all_forms(
        api, mt_forms=("OTHER",), lxx_forms=("OTHER",)
    )) == ()


def test_duplicate_requested_spellings_are_membership_not_multiplicity(tmp_path: Path) -> None:
    api = _loaded(tmp_path)
    one = tuple(find_groups_with_all_forms(api, mt_forms=("MLK",)))
    repeated = tuple(find_groups_with_all_forms(api, mt_forms=("MLK", "MLK")))
    assert tuple(g.alignment_id for g in one) == tuple(g.alignment_id for g in repeated)
    assert len(one) == 4  # only one source row actually contains two MLK tokens


def test_empty_and_malformed_form_inputs_fail_explicitly(tmp_path: Path) -> None:
    api = _loaded(tmp_path)
    with pytest.raises(ValueError, match="at least one"):
        tuple(find_groups_with_all_forms(api))
    cases: tuple[dict[str, Any], ...] = (
        {"mt_forms": ("",)},
        {"lxx_forms": (" ",)},
        {"mt_forms": cast(Any, "MLK")},
        {"lxx_forms": cast(Any, b"LOGOS")},
        {"mt_forms": cast(Any, (42,))},
    )
    for kwargs in cases:
        with pytest.raises(ValueError):
            tuple(find_groups_with_all_forms(api, **kwargs))


def test_noncanonical_warp_fails_before_accessing_features() -> None:
    wrong = SimpleNamespace(F=SimpleNamespace(otype=SimpleNamespace(slotType="word")))
    with pytest.raises(ValueError, match="alignment-slot"):
        tuple(find_groups_with_all_forms(wrong, mt_forms=("MLK",)))
