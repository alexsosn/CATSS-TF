"""User-facing MT↔Greek group lookup on a *loaded* canonical Text-Fabric corpus."""

from pathlib import Path
from typing import Any

import pytest
from tf.fabric import Fabric  # type: ignore[import-untyped]

from catss_tf import find_aligned_groups
from catss_tf.canonical_materializer import materialize_corpus


def _source(root: Path, filename: str, data: str) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / filename).write_text(data, encoding="utf-8")


def _corpus(tmp_path: Path) -> Any:
    source = tmp_path / "source"
    _source(
        source,
        "01.Genesis.par",
        """Gen 1:1
MLK DBR\tBASILEU/S LOGOS
MLK\tQEOS
DBR\tBASILEU/S
--+\tBASILEU/S
Gen 1:2
MLK MLK\tLOGOS BASILEU/S
""",
    )
    _source(
        source,
        "06.JoshB.par",
        """JoshB 1:1
MLK\tBASILEU/S
""",
    )
    materialize_corpus(source, tmp_path / "catss")
    return Fabric(locations=str(tmp_path), modules=("catss",), silent="deep").loadAll(silent="deep")


def _independent_oracle(api: Any, hebrew: str, greek: str) -> tuple[str, ...]:
    """Unindexed slot scan, deliberately separate from feature-value search."""
    result: list[str] = []
    for slot in api.F.otype.s("alignment"):
        mt = {api.F.catss_text.v(node) for node in api.L.u(slot, otype="mt_element")}
        lxx = {api.F.catss_text.v(node) for node in api.L.u(slot, otype="lxx_element")}
        if hebrew in mt and greek in lxx:
            result.append(api.F.catss_alignment_id.v(slot))
    return tuple(result)


def test_group_search_matches_independent_loaded_tf_oracle(tmp_path: Path) -> None:
    api = _corpus(tmp_path)
    hits = tuple(find_aligned_groups(api, "MLK", "BASILEU/S"))

    assert len(hits) == 3
    assert tuple(hit.alignment_id for hit in hits) == _independent_oracle(api, "MLK", "BASILEU/S")
    assert hits[0].mt_elements == ("MLK", "DBR")
    assert hits[0].lxx_elements == ("BASILEU/S", "LOGOS")
    assert hits[0].source == "01.Genesis.par"
    assert (hits[0].chapter, hits[0].verse) == (1, 1)
    assert hits[1].mt_elements == ("MLK", "MLK")
    assert hits[1].lxx_elements == ("LOGOS", "BASILEU/S")
    assert hits[2].source == "06.JoshB.par"
    assert all(hit.alignment_id.startswith(f"catss:{hit.source}:") for hit in hits)


def test_lookup_does_not_join_adjacent_rows_or_invent_pairwise_edges(
    tmp_path: Path,
) -> None:
    api = _corpus(tmp_path)
    assert tuple(find_aligned_groups(api, "MLK", "LOGOS"))  # same multiword group
    assert tuple(find_aligned_groups(api, "DBR", "QEOS")) == ()  # same verse, different rows
    assert tuple(find_aligned_groups(api, "MLK", "MISSING")) == ()
    assert tuple(find_aligned_groups(api, "MISSING", "BASILEU/S")) == ()


def test_exact_source_filter_and_missing_source(tmp_path: Path) -> None:
    api = _corpus(tmp_path)
    genesis = tuple(find_aligned_groups(api, "MLK", "BASILEU/S", source="01.Genesis.par"))
    joshb = tuple(find_aligned_groups(api, "MLK", "BASILEU/S", source="06.JoshB.par"))
    assert len(genesis) == 2
    assert len(joshb) == 1
    assert all(hit.source == "01.Genesis.par" for hit in genesis)
    assert tuple(find_aligned_groups(api, "MLK", "BASILEU/S", source="07.JoshA.par")) == ()


@pytest.mark.parametrize(("hebrew", "greek"), (("", "LOGOS"), ("MLK", "")))
def test_blank_form_fails_closed(tmp_path: Path, hebrew: str, greek: str) -> None:
    api = _corpus(tmp_path)
    with pytest.raises(ValueError, match="nonempty"):
        tuple(find_aligned_groups(api, hebrew, greek))
