import collections.abc
import csv
import pathlib

from catss_tf.bhsa_materializer import materialize_bhsa
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
from catss_tf.consistency import compare_projection_bundles
from catss_tf.lxx_materializer import materialize_lxx
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


def _bhsa_probe() -> BhsaParentProbe:
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


def _lxx_probe() -> LxxParentProbe:
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


class FakeBhsaProvider:
    def __init__(self, verses: tuple[BhsaVerse, ...]) -> None:
        self._verses = {(verse.book, verse.chapter, verse.verse): verse for verse in verses}

    def get_verse(self, book: str, chapter: int, verse: int) -> BhsaVerse | None:
        return self._verses.get((book, chapter, verse))


class FakeLxxProvider:
    def __init__(self, spans: tuple[LxxSpan, ...]) -> None:
        self.parent_probe = _lxx_probe()
        self._spans = {
            (span.book, span.chapter, span.verse, span.subverse): span for span in spans
        }

    def get_span(
        self,
        book: str,
        chapter: int,
        verse: int,
        subverse: str | None = None,
    ) -> LxxSpan | None:
        return self._spans.get((book, chapter, verse, subverse))


def _bhsa_verse(
    book: str,
    chapter: int,
    verse: int,
    node: int,
    forms: tuple[str, ...],
    start_node: int,
) -> BhsaVerse:
    return BhsaVerse(
        node=node,
        book=book,
        chapter=chapter,
        verse=verse,
        words=tuple(
            BhsaWord(
                node=start_node + index,
                g_cons_utf8=form,
                g_word_utf8=form,
                qere_utf8=None,
            )
            for index, form in enumerate(forms)
        ),
    )


def _lxx_span(
    book: str,
    chapter: int,
    verse: int,
    node: int,
    forms: tuple[str, ...],
    start_node: int,
    subverse: str | None = None,
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
                word=form,
                subverse="" if subverse is None else subverse,
                orig_order=str(start_node + index),
            )
            for index, form in enumerate(forms)
        ),
    )


def _write_source(root: pathlib.Path, name: str, text: str) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / name).write_text(text, encoding="utf-8")


def _materialize_common_bundle_pair(tmp_path: pathlib.Path) -> tuple[pathlib.Path, pathlib.Path]:
    source = tmp_path / "source"
    _write_source(
        source,
        "01.Genesis.par",
        """Gen 1:1
)B\tQEOS
GD\t--- ''
XY ^\t^^^
--+\tLOGOS
Gen 1:29
ZR(\t{..^SPORI/MOU}
ZR(\tSPE/RMATOS
{...}\tSPORI/MOU
L/KM\tU(MI=N
""",
    )

    bhsa = tmp_path / "catss-bhsa"
    lxx = tmp_path / "catss-lxx"

    materialize_bhsa(
        source,
        bhsa,
        provider=FakeBhsaProvider(
            (
                _bhsa_verse("Genesis", 1, 1, 100, ("אב", "גד", "חי"), 1),
                _bhsa_verse("Genesis", 1, 29, 101, ("זרע", "זרע", "לכם"), 10),
            )
        ),
        parent_probe=_bhsa_probe(),
    )
    materialize_lxx(
        source,
        lxx,
        provider=FakeLxxProvider(
            (
                _lxx_span("Gen", 1, 1, 200, ("θεός", "λόγος"), 1000),
                _lxx_span("Gen", 1, 29, 201, ("σπέρματος", "σπορίμου", "ὑμῖν"), 1010),
            )
        ),
    )
    return bhsa, lxx


def _rewrite_tsv(
    path: pathlib.Path,
    mutate: collections.abc.Callable[[list[dict[str, str]]], None],
) -> None:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        fieldnames = list(reader.fieldnames or ())
        rows = list(reader)
    mutate(rows)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def test_consistency_accepts_expected_projection_asymmetries(tmp_path: pathlib.Path) -> None:
    bhsa, lxx = _materialize_common_bundle_pair(tmp_path)

    report = compare_projection_bundles(bhsa, lxx)

    assert report.ok is True
    assert report.findings == ()
    assert report.summary.source_files == 1
    assert report.summary.common_sources == 1
    assert report.summary.common_alignments == 8
    assert report.summary.ordinary_shared_alignments == 4
    assert report.summary.lxx_plus_asymmetries == 1
    assert report.summary.lxx_minus_asymmetries == 1
    assert report.summary.transposition_placeholder_asymmetries == 1
    assert report.summary.transposition_carrier_asymmetries == 1
    assert report.summary.fingerprint_mismatches == 0
    assert report.summary.canonical_mismatches == 0
    assert report.summary.index_mismatches == 0
    assert report.summary.anchor_mismatches == 0
    assert report.summary.unexpected_projection_gaps == 0


def test_consistency_classifies_projection_exclusive_sources(tmp_path: pathlib.Path) -> None:
    source = tmp_path / "source"
    _write_source(source, "07.JoshA.par", "Josh 1:1\n)B\tLOGOS\n")
    _write_source(source, "22.Ps151.par", "Ps151 1\n)B\tQEOS\n")

    bhsa = tmp_path / "catss-bhsa"
    lxx = tmp_path / "catss-lxx"

    materialize_bhsa(
        source,
        bhsa,
        provider=FakeBhsaProvider(
            (_bhsa_verse("Josua", 1, 1, 300, ("אב",), 30),)
        ),
        parent_probe=_bhsa_probe(),
    )
    materialize_lxx(
        source,
        lxx,
        provider=FakeLxxProvider(
            (_lxx_span("Ps", 151, 1, 400, ("θεός",), 40),)
        ),
    )

    report = compare_projection_bundles(bhsa, lxx)

    assert report.ok is True
    assert report.summary.source_files == 2
    assert report.summary.common_sources == 0
    assert report.summary.bhsa_only_sources == 1
    assert report.summary.lxx_only_sources == 1
    assert report.summary.common_alignments == 0


def test_fingerprint_mismatch_is_hard_finding(tmp_path: pathlib.Path) -> None:
    bhsa, lxx = _materialize_common_bundle_pair(tmp_path)

    def corrupt(rows: list[dict[str, str]]) -> None:
        rows[0]["sha256"] = "0" * 64

    _rewrite_tsv(lxx / "catss-sources.tsv", corrupt)
    report = compare_projection_bundles(bhsa, lxx)

    assert report.ok is False
    assert report.summary.fingerprint_mismatches == 1
    assert report.findings[0].code == "source_fingerprint_mismatch"


def test_canonical_alignment_drift_is_detected(tmp_path: pathlib.Path) -> None:
    bhsa, lxx = _materialize_common_bundle_pair(tmp_path)

    def corrupt(rows: list[dict[str, str]]) -> None:
        rows[0]["mt_raw"] = "TAMPERED"

    _rewrite_tsv(lxx / "catss-alignments.tsv", corrupt)
    report = compare_projection_bundles(bhsa, lxx)

    assert report.ok is False
    assert report.summary.canonical_mismatches == 1
    assert any(f.code == "canonical_alignment_mismatch" for f in report.findings)


def test_annotation_and_source_line_drift_are_detected(tmp_path: pathlib.Path) -> None:
    bhsa, lxx = _materialize_common_bundle_pair(tmp_path)

    def corrupt_annotations(rows: list[dict[str, str]]) -> None:
        rows[0]["kind"] = "TAMPERED"

    def corrupt_lines(rows: list[dict[str, str]]) -> None:
        rows[0]["raw"] = "TAMPERED"

    _rewrite_tsv(lxx / "catss-annotations.tsv", corrupt_annotations)
    _rewrite_tsv(lxx / "catss-source-lines.tsv", corrupt_lines)
    report = compare_projection_bundles(bhsa, lxx)

    assert report.ok is False
    assert report.summary.canonical_mismatches == 2
    assert {f.code for f in report.findings} >= {"annotation_mismatch", "source_line_mismatch"}


def test_lxx_index_coverage_drift_is_detected(tmp_path: pathlib.Path) -> None:
    bhsa, lxx = _materialize_common_bundle_pair(tmp_path)

    def corrupt(rows: list[dict[str, str]]) -> None:
        first = next(row for row in rows if row["lxx_i"] == "1")
        first["lxx_i"] = "9"

    _rewrite_tsv(lxx / "catss-mappings.tsv", corrupt)
    report = compare_projection_bundles(bhsa, lxx)

    assert report.ok is False
    assert report.summary.index_mismatches == 1
    assert any(f.code == "lxx_index_coverage_mismatch" for f in report.findings)


def test_anchor_kind_drift_is_detected(tmp_path: pathlib.Path) -> None:
    bhsa, lxx = _materialize_common_bundle_pair(tmp_path)

    def corrupt(rows: list[dict[str, str]]) -> None:
        row = next(row for row in rows if row["anchor_kind"] == "lxx_minus")
        row["anchor_kind"] = "transposition_placeholder"

    _rewrite_tsv(lxx / "catss-anchors.tsv", corrupt)
    report = compare_projection_bundles(bhsa, lxx)

    assert report.ok is False
    assert report.summary.anchor_mismatches == 1
    assert any(f.code == "anchor_kind_mismatch" for f in report.findings)


def test_tsv_row_order_is_not_semantic(tmp_path: pathlib.Path) -> None:
    bhsa, lxx = _materialize_common_bundle_pair(tmp_path)

    for filename in ("catss-alignments.tsv", "catss-annotations.tsv", "catss-source-lines.tsv"):
        _rewrite_tsv(lxx / filename, lambda rows: rows.reverse())

    report = compare_projection_bundles(bhsa, lxx)

    assert report.ok is True


def test_missing_sidecar_and_header_mismatch_are_typed_findings(tmp_path: pathlib.Path) -> None:
    bhsa, lxx = _materialize_common_bundle_pair(tmp_path)
    (lxx / "catss-annotations.tsv").unlink()

    path = lxx / "catss-source-lines.tsv"
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace("source\talignment_id", "bad\talignment_id", 1), encoding="utf-8")

    report = compare_projection_bundles(bhsa, lxx)

    assert report.ok is False
    assert {f.code for f in report.findings} >= {
        "missing_sidecar",
        "sidecar_header_mismatch",
    }
