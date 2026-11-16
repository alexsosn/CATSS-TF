"""Exact native source-header reference filtering, independent of Greek targets."""

from pathlib import Path
from typing import Any, cast

import pytest
from tf.fabric import Fabric  # type: ignore[import-untyped]

from catss_tf import (
    find_aligned_groups,
    find_groups_with_all_forms,
    find_groups_with_ordered_forms,
    find_mt_b_raw_matches,
    materialize_corpus,
)

GEN_1_1 = ("Gen", 1, 1)
GEN_1_2 = ("Gen", 1, 2)
GEN_2_1 = ("Gen", 2, 1)
JOSHB_1_1 = ("JoshB", 1, 1)


def _loaded(tmp_path: Path) -> Any:
    source = tmp_path / "source"
    source.mkdir()
    (source / "01.Genesis.par").write_text(
        "Gen 1:1\nMLK DBR\tBASILEU/S LOGOS\n"
        "Gen 1:2\nMLK\tBASILEU/S\n=;W/KL\tLOGOS\n"
        "Gen 2:1\nMLK DBR\tBASILEU/S LOGOS\n=;W/KL\tLOGOS\n",
        encoding="utf-8",
    )
    (source / "06.JoshB.par").write_text("JoshB 1:1\nMLK\tBASILEU/S\n", encoding="utf-8")
    materialize_corpus(source, tmp_path / "catss")
    return Fabric(locations=str(tmp_path), modules=("catss",), silent="deep").loadAll(silent="deep")


def _native_ids(
    api: Any,
    reference: tuple[str, int, int],
    *,
    source: str | None = None,
    mt: tuple[str, ...] = (),
    lxx: tuple[str, ...] = (),
    raw_b: str | None = None,
) -> tuple[str, ...]:
    """Exhaustive slot/feature oracle; no production search helpers used."""
    matches: list[str] = []
    for slot in api.F.otype.s("alignment"):
        if (api.F.book.v(slot), api.F.chapter.v(slot), api.F.verse.v(slot)) != reference:
            continue
        if source is not None and api.F.catss_source.v(slot) != source:
            continue
        if raw_b is not None and raw_b not in (api.F.catss_mt_col_b.v(slot) or ""):
            continue
        mt_values = {api.F.catss_text.v(n) for n in api.L.u(slot, otype="mt_element")}
        lxx_values = {api.F.catss_text.v(n) for n in api.L.u(slot, otype="lxx_element")}
        if set(mt) <= mt_values and set(lxx) <= lxx_values:
            matches.append(str(api.F.catss_alignment_id.v(slot)))
    return tuple(matches)


@pytest.mark.parametrize("reference", (GEN_1_1, GEN_1_2, GEN_2_1, JOSHB_1_1))
def test_exact_reference_mt_greek_and_source_are_conjunctive(
    tmp_path: Path, reference: tuple[str, int, int]
) -> None:
    api = _loaded(tmp_path)
    hits = tuple(find_aligned_groups(api, "MLK", "BASILEU/S", reference=reference))
    assert tuple(hit.alignment_id for hit in hits) == _native_ids(
        api, reference, mt=("MLK",), lxx=("BASILEU/S",)
    )
    assert len(hits) == 1
    wrong = "06.JoshB.par" if reference[0] == "Gen" else "01.Genesis.par"
    assert (
        tuple(
            find_aligned_groups(
                api, "MLK", "BASILEU/S", reference=reference, source=wrong
            )
        )
        == ()
    )
    assert len(tuple(find_aligned_groups(api, "MLK", "BASILEU/S"))) == 4


@pytest.mark.parametrize("reference", (GEN_1_1, GEN_1_2, GEN_2_1, JOSHB_1_1))
def test_all_forms_exact_reference_matches_independent_native_tf(
    tmp_path: Path, reference: tuple[str, int, int]
) -> None:
    api = _loaded(tmp_path)
    hits = tuple(
        find_groups_with_all_forms(
            api, mt_forms=("MLK", "DBR"), lxx_forms=("BASILEU/S", "LOGOS"),
            reference=reference,
        )
    )
    assert tuple(hit.alignment_id for hit in hits) == _native_ids(
        api, reference, mt=("MLK", "DBR"), lxx=("BASILEU/S", "LOGOS")
    )
    assert len(hits) == (1 if reference in (GEN_1_1, GEN_2_1) else 0)


@pytest.mark.parametrize("reference", (GEN_1_1, GEN_1_2, GEN_2_1, JOSHB_1_1))
def test_ordered_source_positions_keep_exact_reference(
    tmp_path: Path, reference: tuple[str, int, int]
) -> None:
    api = _loaded(tmp_path)
    hits = tuple(
        find_groups_with_ordered_forms(
            api, mt_forms=("MLK", "DBR"), lxx_forms=("BASILEU/S", "LOGOS"),
            adjacent=True, reference=reference,
        )
    )
    expected = _native_ids(
        api, reference, mt=("MLK", "DBR"), lxx=("BASILEU/S", "LOGOS")
    )
    assert tuple(hit.alignment_id for hit in hits) == expected
    assert len(hits) == (1 if reference in (GEN_1_1, GEN_2_1) else 0)


@pytest.mark.parametrize("reference", (GEN_1_1, GEN_1_2, GEN_2_1, JOSHB_1_1))
def test_reconstructed_column_b_scope_never_becomes_mt_a(
    tmp_path: Path, reference: tuple[str, int, int]
) -> None:
    api = _loaded(tmp_path)
    hits = tuple(find_mt_b_raw_matches(api, "W/KL", reference=reference))
    assert tuple(hit.group.alignment_id for hit in hits) == _native_ids(
        api, reference, raw_b="W/KL"
    )
    assert len(hits) == (1 if reference in (GEN_1_2, GEN_2_1) else 0)
    assert tuple(find_aligned_groups(api, "W/KL", "LOGOS", reference=reference)) == ()


@pytest.mark.parametrize(
    "invalid",
    (
        "Gen 1:1",
        ("Gen", 1),
        ("Gen", 1, 1, 1),
        ("", 1, 1),
        (" ", 1, 1),
        (123, 1, 1),
        ("Gen", -1, 1),
        ("Gen", 1, -1),
        ("Gen", True, 1),
        ("Gen", 1, False),
        ("Gen", 1.0, 1),
    ),
)
def test_invalid_reference_rejected_consistently(
    tmp_path: Path, invalid: Any
) -> None:
    api = _loaded(tmp_path)
    # Cast preserves a RED test run with the old public type signature.
    for fn, args, kwargs in (
        (find_aligned_groups, ("MLK", "BASILEU/S"), {}),
        (find_groups_with_all_forms, (), {"mt_forms": ("MLK",)}),
        (find_groups_with_ordered_forms, (), {"mt_forms": ("MLK",)}),
        (find_mt_b_raw_matches, ("W/KL",), {}),
    ):
        with pytest.raises(ValueError, match="reference"):
            tuple(cast(Any, fn)(api, *args, reference=invalid, **kwargs))


def test_unmatched_source_reference_does_not_guess_versification(tmp_path: Path) -> None:
    api = _loaded(tmp_path)
    assert tuple(find_aligned_groups(api, "MLK", "BASILEU/S", reference=("JoshA", 1, 1))) == ()
    assert tuple(find_mt_b_raw_matches(api, "W/KL", reference=("JoshB", 2, 1))) == ()
