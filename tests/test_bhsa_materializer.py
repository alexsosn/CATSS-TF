import csv
import dataclasses
import hashlib
import pathlib

import pytest
from tf.fabric import Fabric  # type: ignore[import-untyped]

import catss_tf.bhsa_materializer as bhsa_materializer
from catss_tf.bhsa_materializer import (
    BhsaMaterializationError,
    materialize_bhsa,
)
from catss_tf.bhsa_resolver import BhsaVerse, BhsaWord
from catss_tf.bhsa_schema import (
    BHSA_CHECKOUT_COMMIT,
    BHSA_CHECKOUT_TAG,
    BHSA_MAX_NODE,
    BHSA_MAX_SLOT,
    BHSA_REPOSITORY,
    BHSA_REQUIRED_FEATURES,
    BHSA_SECTION_TYPES,
    BHSA_VERSION,
    BhsaParentProbe,
)
from catss_tf.tf_schema import SIDECAR_COLUMNS


def _probe() -> BhsaParentProbe:
    return BhsaParentProbe(
        repository=BHSA_REPOSITORY,
        version=BHSA_VERSION,
        checkout_tag=BHSA_CHECKOUT_TAG,
        checkout_commit=BHSA_CHECKOUT_COMMIT,
        slot_type="word",
        max_slot=BHSA_MAX_SLOT,
        max_node=BHSA_MAX_NODE,
        section_types=BHSA_SECTION_TYPES,
        feature_names=BHSA_REQUIRED_FEATURES,
    )


class FakeBhsaProvider:
    def __init__(self, verses: tuple[BhsaVerse, ...]) -> None:
        self._verses = {(verse.book, verse.chapter, verse.verse): verse for verse in verses}

    def get_verse(self, book: str, chapter: int, verse: int) -> BhsaVerse | None:
        return self._verses.get((book, chapter, verse))


def _verse(
    *,
    node: int = 2,
    word_node: int = 1,
    book: str = "Genesis",
    chapter: int = 1,
    verse: int = 1,
    g_cons: str = "אב",
) -> BhsaVerse:
    return BhsaVerse(
        node=node,
        book=book,
        chapter=chapter,
        verse=verse,
        words=(
            BhsaWord(
                node=word_node,
                g_cons_utf8=g_cons,
                g_word_utf8=g_cons,
                qere_utf8=None,
            ),
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
    (parent / "g_cons_utf8.tf").write_text(
        """@node
@valueType=str

1\tאב
""",
        encoding="utf-8",
    )
    (parent / "otext.tf").write_text(
        """@config
@fmt:text-orig-full={g_cons_utf8} 
@writtenBy=CATSS-TF-test

""",
        encoding="utf-8",
    )


def test_simple_bhsa_materialization_writes_query_native_module_and_sidecars(
    tmp_path: pathlib.Path,
) -> None:
    source = tmp_path / "source"
    _write_source(
        source,
        "01.Genesis.par",
        """Gen 1:1
)B\tQEOS
--+\tLOGOS
""",
    )
    output = tmp_path / "catss-bhsa"
    provider = FakeBhsaProvider((_verse(),))

    result = materialize_bhsa(
        source,
        output,
        provider=provider,
        parent_probe=_probe(),
    )

    assert result.output_path == output
    assert result.summary.source_files == 1
    assert result.summary.supported_documents == 1
    assert result.summary.unsupported_documents == 0
    assert result.summary.word_mappings == 1
    assert result.summary.verse_anchors == 1
    assert result.summary.tf_features > 0
    assert not (output / "otype.tf").exists()
    assert not (output / "oslots.tf").exists()
    assert not (output / "otext.tf").exists()

    mappings = _read_tsv(output / "catss-mappings.tsv")
    assert mappings == [
        {
            "projection": "bhsa",
            "source": "01.Genesis.par",
            "alignment_id": mappings[0]["alignment_id"],
            "parent_node": "1",
            "lane": "1",
            "mapping_kind": "exact",
            "mt_i": "1",
            "mt_segment": "",
            "lxx_i": "",
        }
    ]

    anchors = _read_tsv(output / "catss-anchors.tsv")
    assert anchors[0]["projection"] == "bhsa"
    assert anchors[0]["parent_node"] == "2"
    assert anchors[0]["anchor_kind"] == "lxx_plus"
    assert anchors[0]["token_n"] == "1"

    alignments = _read_tsv(output / "catss-alignments.tsv")
    assert len(alignments) == 2
    source_lines = _read_tsv(output / "catss-source-lines.tsv")
    assert [row["line_no"] for row in source_lines] == ["2", "3"]

    sources = _read_tsv(output / "catss-sources.tsv")
    assert sources[0]["source"] == "01.Genesis.par"
    payload = (source / "01.Genesis.par").read_bytes()
    assert sources[0]["size_bytes"] == str(len(payload))
    assert sources[0]["sha256"] == hashlib.sha256(payload).hexdigest()

    assert tuple(_read_tsv(output / "catss-diagnostics.tsv")) == ()


def test_generated_bhsa_module_loads_over_parent_warp_and_is_searchable(
    tmp_path: pathlib.Path,
) -> None:
    source = tmp_path / "source"
    _write_source(source, "01.Genesis.par", "Gen 1:1\n)B\tQEOS\n")
    output = tmp_path / "catss-bhsa"
    provider = FakeBhsaProvider((_verse(),))

    materialize_bhsa(source, output, provider=provider, parent_probe=_probe())
    _write_synthetic_parent(tmp_path)

    fabric = Fabric(
        locations=str(tmp_path),
        modules=("parent", "catss-bhsa"),
        silent="deep",
    )
    api = fabric.loadAll(silent="deep")

    assert api.F.otype.v(1) == "word"
    assert api.F.catss_alignment_n.v(1) == 1
    assert api.F.catss_source.v(1) == "01.Genesis.par"
    assert (1,) in api.S.search("word catss_mt_n=1", silent="deep")


def test_two_bhsa_sources_on_same_parent_word_use_deterministic_lanes(
    tmp_path: pathlib.Path,
) -> None:
    source = tmp_path / "source"
    _write_source(source, "45.DanielOG.par", "Dan 1:1\n)B\tLOGOS\n")
    _write_source(source, "46.DanielTh.par", "Dan 1:1\n)B\tQEOS\n")
    output = tmp_path / "catss-bhsa"
    provider = FakeBhsaProvider((_verse(book="Daniel", node=20, word_node=10),))

    materialize_bhsa(source, output, provider=provider, parent_probe=_probe())

    assert "45.DanielOG.par" in (output / "catss_source.tf").read_text(encoding="utf-8")
    assert "46.DanielTh.par" in (output / "catss_source_2.tf").read_text(encoding="utf-8")
    mappings = _read_tsv(output / "catss-mappings.tsv")
    assert [(row["source"], row["lane"]) for row in mappings] == [
        ("45.DanielOG.par", "1"),
        ("46.DanielTh.par", "2"),
    ]


def test_declared_unsupported_source_is_fingerprinted_but_not_projected(
    tmp_path: pathlib.Path,
) -> None:
    source = tmp_path / "source"
    _write_source(source, "22.Ps151.par", "Ps151 1\n--+\tLOGOS\n")
    output = tmp_path / "catss-bhsa"

    result = materialize_bhsa(
        source,
        output,
        provider=FakeBhsaProvider(()),
        parent_probe=_probe(),
    )

    assert result.summary.unsupported_documents == 1
    assert _read_tsv(output / "catss-sources.tsv")[0]["source"] == "22.Ps151.par"
    assert _read_tsv(output / "catss-alignments.tsv") == []
    assert _read_tsv(output / "catss-mappings.tsv") == []
    assert _read_tsv(output / "catss-anchors.tsv") == []


def test_parent_mismatch_fails_before_output_publication(tmp_path: pathlib.Path) -> None:
    source = tmp_path / "source"
    _write_source(source, "01.Genesis.par", "Gen 1:1\n)B\tQEOS\n")
    output = tmp_path / "catss-bhsa"
    bad_probe = dataclasses.replace(_probe(), version="future")

    with pytest.raises(BhsaMaterializationError, match="BHSA parent"):
        materialize_bhsa(
            source,
            output,
            provider=FakeBhsaProvider((_verse(),)),
            parent_probe=bad_probe,
        )

    assert not output.exists()


def test_mapping_failure_is_fail_closed_and_leaves_no_output(tmp_path: pathlib.Path) -> None:
    source = tmp_path / "source"
    _write_source(source, "01.Genesis.par", "Gen 1:1\n)B\tQEOS\n")
    output = tmp_path / "catss-bhsa"
    provider = FakeBhsaProvider((_verse(g_cons="גד"),))

    with pytest.raises(BhsaMaterializationError, match="mapping failed"):
        materialize_bhsa(source, output, provider=provider, parent_probe=_probe())

    assert not output.exists()


def test_unknown_catss_source_is_fail_closed(tmp_path: pathlib.Path) -> None:
    source = tmp_path / "source"
    _write_source(source, "99.Unknown.par", "Test 1:1\n)B\tQEOS\n")
    output = tmp_path / "catss-bhsa"

    with pytest.raises(BhsaMaterializationError, match="unknown CATSS source"):
        materialize_bhsa(
            source,
            output,
            provider=FakeBhsaProvider(()),
            parent_probe=_probe(),
        )

    assert not output.exists()


def test_existing_destination_is_not_overwritten(tmp_path: pathlib.Path) -> None:
    source = tmp_path / "source"
    _write_source(source, "01.Genesis.par", "Gen 1:1\n)B\tQEOS\n")
    output = tmp_path / "catss-bhsa"
    output.mkdir()
    marker = output / "keep.txt"
    marker.write_text("keep", encoding="utf-8")

    with pytest.raises(BhsaMaterializationError, match="destination already exists"):
        materialize_bhsa(
            source,
            output,
            provider=FakeBhsaProvider((_verse(),)),
            parent_probe=_probe(),
        )

    assert marker.read_text(encoding="utf-8") == "keep"


def test_sidecar_writer_quotes_raw_tab_provenance_without_packed_blob(
    tmp_path: pathlib.Path,
) -> None:
    source = tmp_path / "source"
    _write_source(source, "01.Genesis.par", "Gen 1:1\n)B\tQEOS\n")
    output = tmp_path / "catss-bhsa"

    materialize_bhsa(
        source,
        output,
        provider=FakeBhsaProvider((_verse(),)),
        parent_probe=_probe(),
    )

    rows = _read_tsv(output / "catss-source-lines.tsv")
    assert rows[0]["raw"] == ")B\tQEOS"
    assert len(rows[0]) == len(SIDECAR_COLUMNS["catss-source-lines.tsv"])


def test_allowed_validation_finding_is_retained_in_diagnostics_sidecar(
    tmp_path: pathlib.Path,
) -> None:
    source = tmp_path / "source"
    _write_source(
        source,
        "01.Genesis.par",
        "Gen 1:1\n)B {zzUNKNOWN}\tQEOS\n",
    )
    output = tmp_path / "catss-bhsa"

    result = materialize_bhsa(
        source,
        output,
        provider=FakeBhsaProvider((_verse(),)),
        parent_probe=_probe(),
        allowed_validation_codes={"unknown_annotation"},
    )

    assert result.summary.ignored_validation_findings == 1
    diagnostics = _read_tsv(output / "catss-diagnostics.tsv")
    assert diagnostics[0]["stage"] == "validation"
    assert diagnostics[0]["severity"] == "ignored"
    assert diagnostics[0]["code"] == "unknown_annotation"
    assert diagnostics[0]["side"] == "mt_a"


def test_mid_write_failure_removes_temporary_bundle(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "source"
    _write_source(source, "01.Genesis.par", "Gen 1:1\n)B\tQEOS\n")
    output = tmp_path / "catss-bhsa"

    def fail_tsv(
        path: pathlib.Path,
        columns: tuple[str, ...],
        rows: list[tuple[object, ...]],
    ) -> None:
        del path, columns, rows
        raise OSError("synthetic sidecar write failure")

    monkeypatch.setattr(bhsa_materializer, "_write_tsv", fail_tsv)

    with pytest.raises(OSError, match="synthetic sidecar write failure"):
        materialize_bhsa(
            source,
            output,
            provider=FakeBhsaProvider((_verse(),)),
            parent_probe=_probe(),
        )

    assert not output.exists()
    assert list(tmp_path.glob(".catss-bhsa.tmp-*")) == []


def test_maqaf_expansion_emits_segment_only_when_explicit(
    tmp_path: pathlib.Path,
) -> None:
    source = tmp_path / "source"
    _write_source(source, "01.Genesis.par", "Gen 1:1\n)B-GD\tQEOS\n")
    output = tmp_path / "catss-bhsa"
    provider = FakeBhsaProvider(
        (
            BhsaVerse(
                node=3,
                book="Genesis",
                chapter=1,
                verse=1,
                words=(
                    BhsaWord(node=1, g_cons_utf8="אב", g_word_utf8="אב", qere_utf8=None),
                    BhsaWord(node=2, g_cons_utf8="גד", g_word_utf8="גד", qere_utf8=None),
                ),
            ),
        )
    )

    materialize_bhsa(source, output, provider=provider, parent_probe=_probe())

    mappings = _read_tsv(output / "catss-mappings.tsv")
    assert [(row["parent_node"], row["mt_i"], row["mt_segment"]) for row in mappings] == [
        ("1", "1", "1"),
        ("2", "1", "2"),
    ]


def test_bhsa_materializer_emits_queryable_technique_features_and_sidecar(
    tmp_path: pathlib.Path,
) -> None:
    source = tmp_path / "source"
    _write_source(source, "01.Genesis.par", "Gen 1:1\n)B\tQEOS LOGOS\n")
    output = tmp_path / "catss-bhsa"

    materialize_bhsa(
        source,
        output,
        provider=FakeBhsaProvider((_verse(g_cons="אב"),)),
        parent_probe=_probe(),
    )

    assert "1\tone_many" in (output / "catss_tt_cardinality_mt_lxx.tf").read_text(encoding="utf-8")
    assert "1\tlxx_more" in (output / "catss_tt_token_balance_mt_lxx.tf").read_text(
        encoding="utf-8"
    )
    assert "@catssTechniqueSchema=1" in (output / "catss_tt_cardinality_mt_lxx.tf").read_text(
        encoding="utf-8"
    )

    rows = _read_tsv(output / "catss-technique.tsv")
    assert rows == [
        {
            "source": "01.Genesis.par",
            "alignment_id": rows[0]["alignment_id"],
            "comparison_base": "mt_lxx",
            "cardinality_mt_lxx": "one_many",
            "token_balance_mt_lxx": "lxx_more",
            "addition_vs_mt": "0",
            "omission_vs_mt": "0",
            "transposition_mt_lxx": "none_marked",
        }
    ]


def test_bhsa_materializes_mt_scoped_annotation_semantics_as_node_features(
    tmp_path: pathlib.Path,
) -> None:
    source = tmp_path / "source"
    _write_source(source, "01.Genesis.par", "Gen 1:1\n)B {..dGRDIST}\tQEOS\n")
    output = tmp_path / "catss-bhsa"

    materialize_bhsa(
        source,
        output,
        provider=FakeBhsaProvider((_verse(),)),
        parent_probe=_probe(),
    )

    assert "1\t1" in (output / "catss_distributive.tf").read_text(encoding="utf-8")
    assert "1\\tGRDIST" in (output / "catss_distributive_payload.tf").read_text(encoding="utf-8")


def test_bhsa_exposes_canonical_semantic_feature_for_documented_notation(
    tmp_path: pathlib.Path,
) -> None:
    source = tmp_path / "source"
    _write_source(source, "01.Genesis.par", "Gen 1:1\n)B {..dGRDIST}\tQEOS\n")
    output = tmp_path / "catss-bhsa"
    materialize_bhsa(source, output, provider=FakeBhsaProvider((_verse(),)), parent_probe=_probe())
    assert "1\t1" in (output / "catss_sem_distributive.tf").read_text(encoding="utf-8")
    assert "1\\tGRDIST" in (output / "catss_sem_distributive_payload.tf").read_text(encoding="utf-8")
