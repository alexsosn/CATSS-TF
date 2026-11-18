"""Source-side phrase search crosses editorial rows, never source-header boundaries."""

from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import pytest
from tf.fabric import Fabric  # type: ignore[import-untyped]

import catss_tf
from catss_tf import materialize_corpus


def phrase(*args: Any, **kwargs: Any) -> Any:
    """Resolve the real exported API at runtime for a mypy-clean RED phase."""
    return cast(Any, catss_tf).find_source_phrase_matches(*args, **kwargs)


@pytest.fixture(scope="module")
def api(tmp_path_factory: pytest.TempPathFactory) -> Any:
    root = tmp_path_factory.mktemp("source-phrase")
    source = root / "source"
    source.mkdir()
    (source / "01.Genesis.par").write_text(
        "Gen 1:1\n"
        "MLK\tALFA\n"
        "DBR\tBETA\n"
        "MLK DBR\tGAMMA DELTA\n"
        "=;W/KL\tEPSILON\n"
        "MLK\tZETA\n"
        "MLK\tETA\n"
        "MLK\tTHETA\n"
        "Gen 1:2\n"
        "DBR\tIOTA\n"
        "MLK\tKAPPA\n"
        "Gen 2:1\n"
        "MLK\tLAMBDA\n",
        encoding="utf-8",
    )
    (source / "06.JoshB.par").write_text(
        "JoshB 1:1\nMLK\tALFA\nDBR\tBETA\n",
        encoding="utf-8",
    )
    materialize_corpus(source, root / "catss")
    loaded = Fabric(locations=str(root), modules=("catss",), silent="deep").loadAll(silent="deep")
    assert loaded is not None
    return loaded


def independent_oracle(
    api: Any,
    side: str,
    forms: tuple[str, ...],
    *,
    source: str | None = None,
    reference: tuple[str, int, int] | None = None,
) -> tuple[tuple[str, tuple[str, int, int], tuple[str, ...], tuple[int, ...]], ...]:
    """Exhaustively collect the corpus's per-header lexical stream, then enumerate windows.

    This oracle uses a full in-memory per-run list and direct TF nodes,
    independently of the production streaming implementation.
    """
    otype = {"mt_a": "mt_element", "lxx": "lxx_element"}[side]
    runs: list[tuple[tuple[str, str, int, int], list[tuple[str, str, int]]]] = []
    for slot in api.F.otype.s("alignment"):
        key = (
            str(api.F.catss_source.v(slot)),
            str(api.F.book.v(slot)),
            int(api.F.chapter.v(slot)),
            int(api.F.verse.v(slot)),
        )
        if not runs or runs[-1][0] != key:
            runs.append((key, []))
        lexical_nodes = sorted(api.L.u(slot, otype=otype), key=api.F.catss_index.v)
        for node in lexical_nodes:
            runs[-1][1].append(
                (
                    str(api.F.catss_text.v(node)),
                    str(api.F.catss_alignment_id.v(slot)),
                    int(api.F.catss_index.v(node)),
                )
            )

    result: list[tuple[str, tuple[str, int, int], tuple[str, ...], tuple[int, ...]]] = []
    for (name, book, chapter, verse), tokens in runs:
        if source is not None and name != source:
            continue
        if reference is not None and (book, chapter, verse) != reference:
            continue
        for offset in range(len(tokens) - len(forms) + 1):
            window = tokens[offset : offset + len(forms)]
            if tuple(item[0] for item in window) == forms:
                result.append(
                    (
                        name,
                        (book, chapter, verse),
                        tuple(item[1] for item in window),
                        tuple(item[2] for item in window),
                    )
                )
    return tuple(result)


@pytest.mark.parametrize(
    ("side", "forms", "source", "reference", "expected"),
    (
        ("mt_a", ("MLK", "DBR"), None, None, 3),
        ("mt_a", ("DBR", "MLK"), "01.Genesis.par", ("Gen", 1, 1), 2),
        ("mt_a", ("MLK", "MLK"), "01.Genesis.par", ("Gen", 1, 1), 2),
        ("mt_a", ("MLK", "MLK", "MLK"), None, None, 1),
        ("mt_a", ("MLK", "DBR", "MLK"), "01.Genesis.par", ("Gen", 1, 1), 2),
        ("lxx", ("BETA", "GAMMA"), "01.Genesis.par", ("Gen", 1, 1), 1),
        ("lxx", ("DELTA", "EPSILON"), "01.Genesis.par", ("Gen", 1, 1), 1),
        ("lxx", ("EPSILON", "ZETA", "ETA"), None, None, 1),
        ("lxx", ("BETA", "ALFA"), None, None, 0),
        ("mt_a", ("W/KL", "MLK"), None, None, 0),
        ("mt_a", ("MLK", "DBR"), "06.JoshB.par", ("JoshB", 1, 1), 1),
        ("mt_a", ("MLK", "DBR"), "01.Genesis.par", ("JoshB", 1, 1), 0),
        ("mt_a", ("MLK", "DBR"), "01.Genesis.par", ("Gen", 1, 2), 0),
    ),
)
def test_source_phrase_matches_independent_native_tf_oracle(
    api: Any,
    side: str,
    forms: tuple[str, ...],
    source: str | None,
    reference: tuple[str, int, int] | None,
    expected: int,
) -> None:
    found = tuple(phrase(api, side=side, forms=forms, source=source, reference=reference))
    oracle = independent_oracle(api, side, forms, source=source, reference=reference)
    assert len(found) == expected == len(oracle)
    assert tuple(
        (
            hit.source,
            (hit.book, hit.chapter, hit.verse),
            hit.alignment_ids,
            hit.element_indices,
        )
        for hit in found
    ) == oracle
    assert all(hit.forms == forms and hit.side == side for hit in found)


def test_phrase_crosses_alignment_but_not_source_or_verse(api: Any) -> None:
    found = tuple(
        phrase(
            api,
            side="mt_a",
            forms=("MLK", "DBR"),
            source="01.Genesis.par",
            reference=("Gen", 1, 1),
        )
    )
    assert len(found) == 2
    # One occurrence straddles rows; the other stays inside one row.
    assert found[0].alignment_ids[0] != found[0].alignment_ids[1]
    assert found[0].element_indices == (1, 1)
    assert found[1].alignment_ids[0] == found[1].alignment_ids[1]
    assert found[1].element_indices == (1, 2)

    # Greek-only zero-MT-A source row does not invent an MT token.
    gap = tuple(
        phrase(
            api,
            side="mt_a",
            forms=("DBR", "MLK"),
            source="01.Genesis.par",
            reference=("Gen", 1, 1),
        )
    )
    assert len(gap) == 2
    assert gap[1].alignment_ids[0] != gap[1].alignment_ids[1]
    assert gap[1].element_indices == (2, 1)
    assert all(not any("JoshB" in alignment_id for alignment_id in match.alignment_ids) for match in gap)


@pytest.mark.parametrize(
    ("side", "forms", "source", "reference"),
    (
        ("mt_b", ("MLK", "DBR"), None, None),
        ("word", ("MLK", "DBR"), None, None),
        ("mt_a", (), None, None),
        ("mt_a", ("MLK",), None, None),
        ("mt_a", ("MLK", ""), None, None),
        ("mt_a", ("MLK", " "), None, None),
        ("mt_a", cast(Any, "MLK DBR"), None, None),
        ("mt_a", cast(Any, ("MLK", 1)), None, None),
        ("mt_a", ("MLK", "DBR"), "", None),
        ("mt_a", ("MLK", "DBR"), None, cast(Any, ("Gen", 1, True))),
    ),
)
def test_invalid_phrase_inputs_fail_closed(
    api: Any, side: str, forms: tuple[str, ...], source: str | None, reference: Any
) -> None:
    with pytest.raises(ValueError):
        tuple(phrase(api, side=side, forms=forms, source=source, reference=reference))


def test_noncanonical_warp_and_missing_features_fail_closed(api: Any, tmp_path: Path) -> None:
    fake = SimpleNamespace(F=SimpleNamespace(otype=SimpleNamespace(slotType="word")))
    with pytest.raises(ValueError, match="alignment-slot"):
        tuple(phrase(fake, side="mt_a", forms=("MLK", "DBR")))

    # The caller must load all source-side sequence/provenance features.
    root = tmp_path / "source"
    root.mkdir()
    (root / "01.Genesis.par").write_text(
        "Gen 1:1\nMLK\tALFA\nDBR\tBETA\n", encoding="utf-8"
    )
    materialize_corpus(root, tmp_path / "catss")
    sparse = Fabric(locations=str(tmp_path), modules=("catss",), silent="deep").load(
        "catss_alignment_id", silent="deep"
    )
    assert sparse is not None
    with pytest.raises(ValueError, match="loaded"):
        tuple(phrase(sparse, side="mt_a", forms=("MLK", "DBR")))
