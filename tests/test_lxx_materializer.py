import csv
import dataclasses
import hashlib
import pathlib

import pytest
from tf.fabric import Fabric  # type: ignore[import-untyped]

import catss_tf.lxx_materializer as lxx_materializer
from catss_tf.lxx_materializer import (
    LxxMaterializationError,
    materialize_lxx,
)
from catss_tf.lxx_resolver import LxxSpan, LxxWord
from catss_tf.lxx_schema import (
    LXX_MAX_NODE,
    LXX_MAX_SLOT,
    LXX_NODE_COUNTS,
    LXX_RELEASE_COMMIT,
    LXX_RELEASE_TAG,
    LXX_REPOSITORY,
    LXX_REQUIRED_FEATURES,
    LXX_SECTION_TYPES,
    LXX_SLOT_TYPE,
    LXX_VERSION,
    LxxParentProbe,
)
from catss_tf.tf_schema import SIDECAR_COLUMNS


def _probe() -> LxxParentProbe:
    return LxxParentProbe(
        repository=LXX_REPOSITORY,
        version=LXX_VERSION,
        release_tag=LXX_RELEASE_TAG,
        release_commit=LXX_RELEASE_COMMIT,
        slot_type=LXX_SLOT_TYPE,
        max_slot=LXX_MAX_SLOT,
        max_node=LXX_MAX_NODE,
        section_types=LXX_SECTION_TYPES,
        node_counts=LXX_NODE_COUNTS,
        feature_names=LXX_REQUIRED_FEATURES,
    )


class FakeLxxProvider:
    def __init__(
        self,
        spans: tuple[LxxSpan, ...],
        *,
        probe: LxxParentProbe | None = None,
    ) -> None:
        self.parent_probe = _probe() if probe is None else probe
        self._spans = {(span.book, span.chapter, span.verse, span.subverse): span for span in spans}

    def get_span(
        self,
        book: str,
        chapter: int,
        verse: int,
        subverse: str | None = None,
    ) -> LxxSpan | None:
        return self._spans.get((book, chapter, verse, subverse))


def _span(
    *words: str,
    book: str = "Gen",
    chapter: int = 1,
    verse: int = 1,
    subverse: str | None = None,
    node: int = 2,
    start_node: int = 1,
) -> LxxSpan:
    return LxxSpan(
        node=node,
        book=book,
        chapter=chapter,
        verse=verse,
        subverse=subverse,
        words=tuple(
            LxxWord(
                node=start_node + index,
                word=word,
                subverse="" if subverse is None else subverse,
                orig_order=str(start_node + index),
            )
            for index, word in enumerate(words)
        ),
    )


def _write_source(root: pathlib.Path, name: str, text: str) -> pathlib.Path:
    root.mkdir(parents=True, exist_ok=True)
    path = root / name
    path.write_text(text, encoding="utf-8")
    return path


def _read_tsv(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def _write_synthetic_parent(root: pathlib.Path) -> None:
    parent = root / "parent"
    parent.mkdir()
    (parent / "otype.tf").write_text(
        """@node
@valueType=str

1\tword
2\tverse
""",
        encoding="utf-8",
    )
    (parent / "oslots.tf").write_text(
        """@edge
@valueType=str

2\t1
""",
        encoding="utf-8",
    )
    (parent / "word.tf").write_text(
        """@node
@valueType=str

1\tθεός
""",
        encoding="utf-8",
    )
    (parent / "otext.tf").write_text(
        """@config
@fmt:text-orig-full={word} 
@writtenBy=CATSS-TF-test

""",
        encoding="utf-8",
    )


def test_simple_lxx_materialization_writes_query_native_module_and_sidecars(
    tmp_path: pathlib.Path,
) -> None:
    source = tmp_path / "source"
    _write_source(
        source,
        "01.Genesis.par",
        """Gen 1:1
HB1\tQEOS
HB2\t--- ''
""",
    )
    output = tmp_path / "catss-lxx"
    provider = FakeLxxProvider((_span("θεός"),))

    result = materialize_lxx(source, output, provider=provider)

    assert result.output_path == output
    assert result.summary.source_files == 1
    assert result.summary.supported_documents == 1
    assert result.summary.unsupported_documents == 0
    assert result.summary.word_mappings == 1
    assert result.summary.reference_anchors == 1
    assert result.summary.tf_features > 0

    assert not (output / "otype.tf").exists()
    assert not (output / "oslots.tf").exists()
    assert not (output / "otext.tf").exists()

    mappings = _read_tsv(output / "catss-mappings.tsv")
    assert mappings == [
        {
            "projection": "lxx",
            "source": "01.Genesis.par",
            "alignment_id": mappings[0]["alignment_id"],
            "parent_node": "1",
            "lane": "1",
            "mapping_kind": "exact",
            "mt_i": "",
            "mt_segment": "",
            "lxx_i": "1",
        }
    ]

    anchors = _read_tsv(output / "catss-anchors.tsv")
    assert anchors[0]["projection"] == "lxx"
    assert anchors[0]["parent_node"] == "2"
    assert anchors[0]["anchor_kind"] == "lxx_minus"
    assert anchors[0]["token_n"] == "0"

    alignments = _read_tsv(output / "catss-alignments.tsv")
    assert len(alignments) == 2
    source_lines = _read_tsv(output / "catss-source-lines.tsv")
    assert [row["line_no"] for row in source_lines] == ["2", "3"]

    sources = _read_tsv(output / "catss-sources.tsv")
    payload = (source / "01.Genesis.par").read_bytes()
    assert sources == [
        {
            "source": "01.Genesis.par",
            "size_bytes": str(len(payload)),
            "sha256": hashlib.sha256(payload).hexdigest(),
        }
    ]

    assert tuple(_read_tsv(output / "catss-diagnostics.tsv")) == ()


def test_generated_lxx_module_loads_over_parent_warp_and_is_searchable(
    tmp_path: pathlib.Path,
) -> None:
    source = tmp_path / "source"
    _write_source(source, "01.Genesis.par", "Gen 1:1\nHB\tQEOS\n")
    output = tmp_path / "catss-lxx"
    provider = FakeLxxProvider((_span("θεός"),))

    materialize_lxx(source, output, provider=provider)
    _write_synthetic_parent(tmp_path)

    fabric = Fabric(
        locations=str(tmp_path),
        modules=("parent", "catss-lxx"),
        silent="deep",
    )
    api = fabric.loadAll(silent="deep")

    assert api.F.otype.v(1) == "word"
    assert api.F.catss_alignment_n.v(1) == 1
    assert api.F.catss_source.v(1) == "01.Genesis.par"
    assert api.F.catss_lxx_i.v(1) == 1
    assert (1,) in api.S.search("word catss_lxx_n=1", silent="deep")


def test_transposition_alignment_and_carrier_use_two_scalar_lanes(
    tmp_path: pathlib.Path,
) -> None:
    source = tmp_path / "source"
    _write_source(
        source,
        "01.Genesis.par",
        """Gen 1:29
ZR(\t{..^SPORI/MOU}
ZR(\tSPE/RMATOS
{...}\tSPORI/MOU
L/KM\tU(MI=N
""",
    )
    output = tmp_path / "catss-lxx"
    provider = FakeLxxProvider(
        (_span("σπέρματος", "σπορίμου", "ὑμῖν", chapter=1, verse=29, node=20),)
    )

    materialize_lxx(source, output, provider=provider)

    alignment_n = (output / "catss_alignment_n.tf").read_text(encoding="utf-8")
    mapping_one = (output / "catss_mapping.tf").read_text(encoding="utf-8")
    mapping_two = (output / "catss_mapping_2.tf").read_text(encoding="utf-8")

    assert "2\t2" in alignment_n
    assert "2\ttransposition_alignment" in mapping_one
    assert "2\ttransposition_carrier" in mapping_two

    rows = [row for row in _read_tsv(output / "catss-mappings.tsv") if row["parent_node"] == "2"]
    assert [(row["lane"], row["mapping_kind"], row["lxx_i"]) for row in rows] == [
        ("1", "transposition_alignment", "1"),
        ("2", "transposition_carrier", "1"),
    ]


def test_lxx_minus_and_transposition_placeholder_aggregate_on_reference_node(
    tmp_path: pathlib.Path,
) -> None:
    source = tmp_path / "source"
    _write_source(
        source,
        "01.Genesis.par",
        """Gen 1:1
HB1\t--- ''
HB2 ^\t^^^
""",
    )
    output = tmp_path / "catss-lxx"
    provider = FakeLxxProvider((_span("λόγος", node=2),))

    materialize_lxx(source, output, provider=provider)

    assert "2\t1" in (output / "catss_lxx_minus_n.tf").read_text(encoding="utf-8")
    assert "2\t1" in (output / "catss_transposition_placeholder_n.tf").read_text(encoding="utf-8")

    anchors = _read_tsv(output / "catss-anchors.tsv")
    assert [(row["anchor_kind"], row["token_n"]) for row in anchors] == [
        ("lxx_minus", "0"),
        ("transposition_placeholder", "0"),
    ]


def test_declared_unsupported_a_source_is_fingerprinted_but_not_projected(
    tmp_path: pathlib.Path,
) -> None:
    source = tmp_path / "source"
    _write_source(source, "07.JoshA.par", "Josh 1:1\nHB\tLOGOS\n")
    output = tmp_path / "catss-lxx"

    result = materialize_lxx(source, output, provider=FakeLxxProvider(()))

    assert result.summary.unsupported_documents == 1
    assert _read_tsv(output / "catss-sources.tsv")[0]["source"] == "07.JoshA.par"
    assert _read_tsv(output / "catss-alignments.tsv") == []
    assert _read_tsv(output / "catss-mappings.tsv") == []
    assert _read_tsv(output / "catss-anchors.tsv") == []


def test_parent_mismatch_fails_before_output_publication(tmp_path: pathlib.Path) -> None:
    source = tmp_path / "source"
    _write_source(source, "01.Genesis.par", "Gen 1:1\nHB\tQEOS\n")
    output = tmp_path / "catss-lxx"
    bad_probe = dataclasses.replace(_probe(), version="future")
    provider = FakeLxxProvider((_span("θεός"),), probe=bad_probe)

    with pytest.raises(LxxMaterializationError, match="CenterBLC parent"):
        materialize_lxx(source, output, provider=provider)

    assert not output.exists()


def test_mapping_failure_is_fail_closed_and_leaves_no_output(tmp_path: pathlib.Path) -> None:
    source = tmp_path / "source"
    _write_source(source, "01.Genesis.par", "Gen 1:1\nHB\tQEOS\n")
    output = tmp_path / "catss-lxx"
    provider = FakeLxxProvider((_span("λόγος"),))

    with pytest.raises(LxxMaterializationError, match="mapping failed"):
        materialize_lxx(source, output, provider=provider)

    assert not output.exists()


def test_unknown_catss_source_is_fail_closed(tmp_path: pathlib.Path) -> None:
    source = tmp_path / "source"
    _write_source(source, "99.Unknown.par", "Test 1:1\nHB\tQEOS\n")
    output = tmp_path / "catss-lxx"

    with pytest.raises(LxxMaterializationError, match="unknown CATSS source"):
        materialize_lxx(source, output, provider=FakeLxxProvider(()))

    assert not output.exists()


def test_existing_destination_is_not_overwritten(tmp_path: pathlib.Path) -> None:
    source = tmp_path / "source"
    _write_source(source, "01.Genesis.par", "Gen 1:1\nHB\tQEOS\n")
    output = tmp_path / "catss-lxx"
    output.mkdir()
    marker = output / "keep.txt"
    marker.write_text("keep", encoding="utf-8")

    with pytest.raises(LxxMaterializationError, match="destination already exists"):
        materialize_lxx(source, output, provider=FakeLxxProvider((_span("θεός"),)))

    assert marker.read_text(encoding="utf-8") == "keep"


def test_allowed_validation_finding_is_retained_in_diagnostics_sidecar(
    tmp_path: pathlib.Path,
) -> None:
    source = tmp_path / "source"
    _write_source(
        source,
        "01.Genesis.par",
        "Gen 1:1\nHB {zzUNKNOWN}\tQEOS\n",
    )
    output = tmp_path / "catss-lxx"

    result = materialize_lxx(
        source,
        output,
        provider=FakeLxxProvider((_span("θεός"),)),
        allowed_validation_codes={"unknown_annotation"},
    )

    assert result.summary.ignored_validation_findings == 1
    diagnostics = _read_tsv(output / "catss-diagnostics.tsv")
    assert diagnostics[0]["stage"] == "validation"
    assert diagnostics[0]["severity"] == "ignored"
    assert diagnostics[0]["code"] == "unknown_annotation"


def test_mid_write_failure_removes_temporary_bundle(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "source"
    _write_source(source, "01.Genesis.par", "Gen 1:1\nHB\tQEOS\n")
    output = tmp_path / "catss-lxx"

    def fail_tsv(
        path: pathlib.Path,
        columns: tuple[str, ...],
        rows: list[tuple[object, ...]],
    ) -> None:
        del path, columns, rows
        raise OSError("synthetic sidecar write failure")

    monkeypatch.setattr(lxx_materializer, "_write_tsv", fail_tsv)

    with pytest.raises(OSError, match="synthetic sidecar write failure"):
        materialize_lxx(source, output, provider=FakeLxxProvider((_span("θεός"),)))

    assert not output.exists()
    assert list(tmp_path.glob(".catss-lxx.tmp-*")) == []


def test_sidecar_writer_quotes_raw_tab_provenance(
    tmp_path: pathlib.Path,
) -> None:
    source = tmp_path / "source"
    _write_source(source, "01.Genesis.par", "Gen 1:1\nHB\tQEOS\n")
    output = tmp_path / "catss-lxx"

    materialize_lxx(source, output, provider=FakeLxxProvider((_span("θεός"),)))

    rows = _read_tsv(output / "catss-source-lines.tsv")
    assert rows[0]["raw"] == "HB\tQEOS"
    assert len(rows[0]) == len(SIDECAR_COLUMNS["catss-source-lines.tsv"])


def test_lettered_subverse_minus_anchor_stays_on_subverse_node(
    tmp_path: pathlib.Path,
) -> None:
    source = tmp_path / "source"
    _write_source(
        source,
        "18.Esther.par",
        "Esth 1:1\nHB\t--- '' [1:1a]\n",
    )
    output = tmp_path / "catss-lxx"
    provider = FakeLxxProvider(
        (
            _span(
                "θεός",
                book="Esth",
                chapter=1,
                verse=1,
                subverse="a",
                node=3,
                start_node=10,
            ),
        )
    )

    materialize_lxx(source, output, provider=provider)

    anchors = _read_tsv(output / "catss-anchors.tsv")
    assert anchors[0]["parent_node"] == "3"
    assert anchors[0]["anchor_kind"] == "lxx_minus"
    assert "3\t1" in (output / "catss_lxx_minus_n.tf").read_text(encoding="utf-8")


def test_lxx_plus_materializer_emits_explicit_addition_vs_mt_feature(
    tmp_path: pathlib.Path,
) -> None:
    source = tmp_path / "source"
    _write_source(source, "01.Genesis.par", "Gen 1:1\n--+\tLOGOS\n")
    output = tmp_path / "catss-lxx"

    materialize_lxx(source, output, provider=FakeLxxProvider((_span("λόγος"),)))

    assert "1\t1" in (output / "catss_tt_addition_vs_mt.tf").read_text(encoding="utf-8")
    assert "1\tzero_one" in (output / "catss_tt_cardinality_mt_lxx.tf").read_text(encoding="utf-8")

    rows = _read_tsv(output / "catss-technique.tsv")
    assert rows[0]["comparison_base"] == "mt_lxx"
    assert rows[0]["addition_vs_mt"] == "1"
    assert rows[0]["omission_vs_mt"] == "0"
    assert rows[0]["token_balance_mt_lxx"] == "not_applicable"


def test_lxx_does_not_project_mt_scoped_annotation_onto_greek_word(
    tmp_path: pathlib.Path,
) -> None:
    source = tmp_path / "source"
    _write_source(source, "01.Genesis.par", "Gen 1:1\nHB {..dGRDIST}\tQEOS\n")
    output = tmp_path / "catss-lxx"

    materialize_lxx(source, output, provider=FakeLxxProvider((_span("θεός"),)))

    assert not (output / "catss_distributive.tf").exists()
    legacy_payload = (output / "catss_distributive_payload.tf").read_text(encoding="utf-8")
    assert not any(line.startswith("1") for line in legacy_payload.splitlines())


def test_lxx_exposes_lxx_scoped_canonical_semantic_feature(
    tmp_path: pathlib.Path,
) -> None:
    source = tmp_path / "source"
    _write_source(source, "01.Genesis.par", "Gen 1:1\nHB\tQEOS {..rQEOS}\n")
    output = tmp_path / "catss-lxx"
    materialize_lxx(source, output, provider=FakeLxxProvider((_span("θεός", "θεός"),)))
    assert "1\t1" in (output / "catss_sem_repetition.tf").read_text(encoding="utf-8")
    payload_text = (output / "catss_sem_repetition_payload.tf").read_text(encoding="utf-8")
    assert "1\tQEOS" in payload_text
