import pathlib

import pytest
from catss_tf.canonical_materializer import (
    CanonicalMaterializationError,
    materialize_corpus,
)
from tf.fabric import Fabric  # type: ignore[import-untyped]

import catss_tf
from catss_tf.parser import parse_parallel_file


def _write_source(root: pathlib.Path, name: str, text: str) -> pathlib.Path:
    root.mkdir(parents=True, exist_ok=True)
    path = root / name
    path.write_text(text, encoding="utf-8")
    return path


def _load_corpus(root: pathlib.Path, module: str = "catss"):
    fabric = Fabric(locations=str(root), modules=(module,), silent="deep")
    return fabric.loadAll(silent="deep")


def test_canonical_corpus_loads_standalone_with_alignment_slots(
    tmp_path: pathlib.Path,
) -> None:
    source = tmp_path / "source"
    source_path = _write_source(
        source,
        "01.Genesis.par",
        """Gen 1:1
)B	QEOS
--+	LOGOS
-+	AGGELOS
MLK	---
DBR	--
""",
    )
    output = tmp_path / "catss"

    result = materialize_corpus(source, output)

    assert result.output_path == output
    assert result.summary.source_files == 1
    assert result.summary.verses == 1
    assert result.summary.alignments == 5
    assert result.summary.alignment_slots == 5
    assert result.summary.audit_ok is True

    api = _load_corpus(tmp_path)
    assert tuple(api.F.otype.s("alignment")) == (1, 2, 3, 4, 5)
    assert api.F.otype.maxSlot == 5
    assert api.F.otype.slotType == "alignment"

    parsed = parse_parallel_file(source_path)
    expected_ids = tuple(
        alignment.alignment_id
        for verse in parsed.verses
        for alignment in verse.alignments
    )
    assert tuple(api.F.catss_alignment_id.v(node) for node in range(1, 6)) == expected_ids

    plus_slots = tuple(
        row[0] for row in api.S.search("alignment catss_lxx_plus=1", silent="deep")
    )
    minus_slots = tuple(
        row[0] for row in api.S.search("alignment catss_lxx_minus=1", silent="deep")
    )
    assert plus_slots == (2, 3)
    assert minus_slots == (4, 5)

    verse_node = api.F.otype.s("verse")[0]
    assert tuple(api.L.d(verse_node, otype="alignment")) == (1, 2, 3, 4, 5)


def test_lexical_nodes_preserve_elements_and_do_not_fake_empty_sides(
    tmp_path: pathlib.Path,
) -> None:
    source = tmp_path / "source"
    _write_source(
        source,
        "01.Genesis.par",
        """Gen 1:1
)B MLK	QEOS LOGOS
--+	AGGELOS
DBR	---
""",
    )
    materialize_corpus(source, tmp_path / "catss")
    api = _load_corpus(tmp_path)

    mt_nodes = tuple(api.F.otype.s("mt_element"))
    lxx_nodes = tuple(api.F.otype.s("lxx_element"))
    assert len(mt_nodes) == 3
    assert len(lxx_nodes) == 3

    plus_slot, minus_slot = 2, 3
    assert tuple(api.L.u(plus_slot, otype="mt_element")) == ()
    assert tuple(api.L.u(plus_slot, otype="lxx_element"))
    assert tuple(api.L.u(minus_slot, otype="mt_element"))
    assert tuple(api.L.u(minus_slot, otype="lxx_element")) == ()

    first_mt = api.L.u(1, otype="mt_element")[0]
    second_mt = api.L.u(1, otype="mt_element")[1]
    assert (api.F.catss_index.v(first_mt), api.F.catss_text.v(first_mt)) == (1, ")B")
    assert (api.F.catss_index.v(second_mt), api.F.catss_text.v(second_mt)) == (2, "MLK")


def test_annotations_references_and_source_lines_are_independent_nodes(
    tmp_path: pathlib.Path,
) -> None:
    source = tmp_path / "source"
    _write_source(
        source,
        "01.Genesis.par",
        """Gen 1:1
HB	MH/ [2] {d}
Gen 1:2
HB2	LOGOS
Gen 1:3
HB3	QEOS [99]
""",
    )
    materialize_corpus(source, tmp_path / "catss")
    api = _load_corpus(tmp_path)

    first_slot = 1
    annotation_nodes = tuple(api.L.u(first_slot, otype="annotation"))
    reference_nodes = tuple(api.L.u(first_slot, otype="reference"))
    source_line_nodes = tuple(api.L.u(first_slot, otype="source_line"))

    assert annotation_nodes
    assert len(reference_nodes) == 1
    assert len(source_line_nodes) == 1
    assert api.F.catss_ref_verse.v(reference_nodes[0]) == 2
    assert api.F.catss_raw.v(reference_nodes[0]) == "[2]"
    assert api.F.catss_line_no.v(source_line_nodes[0]) == 2
    assert api.F.catss_raw.v(source_line_nodes[0]) == "HB\tMH/ [2] {d}"

    target = tuple(api.E.catss_reference_target.f(reference_nodes[0]))
    assert len(target) == 1
    assert api.F.otype.v(target[0]) == "verse"
    assert api.F.verse.v(target[0]) == 2

    unresolved_ref = api.L.u(3, otype="reference")[0]
    assert tuple(api.E.catss_reference_target.f(unresolved_ref)) == ()


def test_canonical_materialization_is_byte_deterministic(tmp_path: pathlib.Path) -> None:
    source = tmp_path / "source"
    _write_source(source, "01.Genesis.par", "Gen 1:1\n)B\tQEOS\n")

    left = tmp_path / "left"
    right = tmp_path / "right"
    materialize_corpus(source, left)
    materialize_corpus(source, right)

    left_files = sorted(path.relative_to(left) for path in left.rglob("*") if path.is_file())
    right_files = sorted(path.relative_to(right) for path in right.rglob("*") if path.is_file())
    assert left_files == right_files
    for relative in left_files:
        assert (left / relative).read_bytes() == (right / relative).read_bytes()


def test_unknown_source_fails_closed_without_publishing(tmp_path: pathlib.Path) -> None:
    source = tmp_path / "source"
    _write_source(source, "99.Unknown.par", "Test 1:1\nHB\tLOGOS\n")
    output = tmp_path / "catss"

    with pytest.raises(CanonicalMaterializationError, match="unknown CATSS source"):
        materialize_corpus(source, output)

    assert not output.exists()


def test_validation_failure_is_atomic(tmp_path: pathlib.Path) -> None:
    source = tmp_path / "source"
    _write_source(
        source,
        "01.Genesis.par",
        "Gen 1:1\nHB\tLOGOS {zzUNKNOWN}\n",
    )
    output = tmp_path / "catss"

    with pytest.raises(CanonicalMaterializationError, match="validation failed"):
        materialize_corpus(source, output)

    assert not output.exists()


def test_canonical_materializer_is_public_api() -> None:
    assert catss_tf.materialize_corpus is materialize_corpus
