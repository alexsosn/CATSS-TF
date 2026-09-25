import dataclasses

from catss_tf.bhsa_resolver import (
    BhsaVerse,
    BhsaWord,
    MappingFinding,
    normalize_bhsa_hebrew,
    normalize_catss_hebrew,
    resolve_bhsa_document,
)
from catss_tf.parser import parse_parallel_text


@dataclasses.dataclass
class FakeProvider:
    verses: dict[tuple[str, int, int], BhsaVerse]

    def get_verse(self, book: str, chapter: int, verse: int) -> BhsaVerse | None:
        return self.verses.get((book, chapter, verse))


def _provider(*words: BhsaWord, verse_node: int = 9001) -> FakeProvider:
    return FakeProvider(
        {
            ("Genesis", 1, 1): BhsaVerse(
                node=verse_node,
                book="Genesis",
                chapter=1,
                verse=1,
                words=words,
            )
        }
    )


def test_catss_hebrew_normalization_matches_bhsa_consonantal_form() -> None:
    assert normalize_catss_hebrew("B/R)$YT") == "בראשׁית"
    assert normalize_catss_hebrew("W/H/)RC") == "והארץ"
    assert normalize_catss_hebrew("$LWM") == "שׁלום"
    assert normalize_catss_hebrew("B/N") == "בן"


def test_bhsa_normalization_strips_pointing_but_preserves_shin_sin() -> None:
    assert normalize_bhsa_hebrew("שָׁלוֹם") == "שׁלום"
    assert normalize_bhsa_hebrew("שָׂר") == "שׂר"
    assert normalize_bhsa_hebrew("קְרֵי\n") == "קרי"


def test_catss_normalizer_rejects_unknown_lexical_characters() -> None:
    try:
        normalize_catss_hebrew("AB#CD")
    except ValueError as exc:
        assert "unsupported CATSS Hebrew character" in str(exc)
    else:
        raise AssertionError("unknown CATSS Hebrew characters must fail closed")


def test_exact_whole_verse_match_emits_word_mappings_only_after_full_equality() -> None:
    doc = parse_parallel_text(
        """Gen 1:1
B/R)$YT\tEN
BR)\tEPOI
)LHYM\tTHEOS
""",
        source_name="01.Genesis.par",
    )
    provider = _provider(
        BhsaWord(101, "בראשׁית", "בְּרֵאשִׁית", None),
        BhsaWord(102, "ברא", "בָּרָא", None),
        BhsaWord(103, "אלהים", "אֱלֹהִים", None),
    )

    report = resolve_bhsa_document(doc, provider)

    assert report.summary.resolved_verses == 1
    assert report.summary.mismatched_verses == 0
    assert [(m.alignment_id, m.mt_index, m.bhsa_node, m.mapping_kind) for m in report.word_mappings] == [
        (doc.verses[0].alignments[0].alignment_id, 0, 101, "exact"),
        (doc.verses[0].alignments[1].alignment_id, 0, 102, "exact"),
        (doc.verses[0].alignments[2].alignment_id, 0, 103, "exact"),
    ]
    assert report.findings == ()


def test_one_word_mismatch_emits_no_partial_word_mappings() -> None:
    doc = parse_parallel_text(
        """Gen 1:1
B/R)$YT\tEN
BR)\tEPOI
)LHYM\tTHEOS
""",
        source_name="01.Genesis.par",
    )
    provider = _provider(
        BhsaWord(101, "בראשׁית", None, None),
        BhsaWord(102, "ברא", None, None),
        BhsaWord(103, "אדני", None, None),
    )

    report = resolve_bhsa_document(doc, provider)

    assert report.word_mappings == ()
    assert report.summary.resolved_verses == 0
    assert report.summary.mismatched_verses == 1
    assert report.findings == (
        MappingFinding(
            code="verse_word_mismatch",
            source_name="01.Genesis.par",
            chapter=1,
            verse=1,
            position=3,
            alignment_id=doc.verses[0].alignments[2].alignment_id,
            catss_value="אלהים",
            bhsa_value="אדני",
            message="normalized CATSS MT and BHSA word differ",
        ),
    )


def test_count_mismatch_never_falls_back_to_positional_mapping() -> None:
    doc = parse_parallel_text(
        """Gen 1:1
B/R)$YT\tEN
BR)\tEPOI
""",
        source_name="01.Genesis.par",
    )
    provider = _provider(BhsaWord(101, "בראשׁית", None, None))

    report = resolve_bhsa_document(doc, provider)

    assert report.word_mappings == ()
    assert report.summary.mismatched_verses == 1
    assert report.findings[0].code == "verse_word_count_mismatch"
    assert report.findings[0].catss_value == "2"
    assert report.findings[0].bhsa_value == "1"


def test_qere_must_match_same_bhsa_word_slot() -> None:
    doc = parse_parallel_text(
        """Gen 1:1
*KTB **QRY {**}\tGR
""",
        source_name="01.Genesis.par",
    )
    provider = _provider(BhsaWord(101, "כתב", "כְּתַב", "קְרֵי"))

    report = resolve_bhsa_document(doc, provider)

    assert report.summary.qere_checks == 1
    assert report.summary.qere_mismatches == 0
    assert len(report.word_mappings) == 1
    assert report.word_mappings[0].mapping_kind == "ketiv_qere"


def test_missing_or_mismatched_qere_fails_entire_verse() -> None:
    doc = parse_parallel_text(
        """Gen 1:1
*KTB **QRY {**}\tGR
""",
        source_name="01.Genesis.par",
    )

    missing = resolve_bhsa_document(doc, _provider(BhsaWord(101, "כתב", None, None)))
    mismatch = resolve_bhsa_document(
        doc,
        _provider(BhsaWord(101, "כתב", None, "קָרָא")),
    )

    assert missing.word_mappings == ()
    assert missing.findings[0].code == "qere_missing"
    assert mismatch.word_mappings == ()
    assert mismatch.findings[0].code == "qere_mismatch"


def test_lxx_plus_gets_verse_anchor_not_neighbor_word() -> None:
    doc = parse_parallel_text(
        """Gen 1:1
B/R)$YT\tEN
--+ ''\tKAI
BR)\tEPOI
""",
        source_name="01.Genesis.par",
    )
    provider = _provider(
        BhsaWord(101, "בראשׁית", None, None),
        BhsaWord(102, "ברא", None, None),
        verse_node=9001,
    )

    report = resolve_bhsa_document(doc, provider)

    plus_id = doc.verses[0].alignments[1].alignment_id
    assert [(a.alignment_id, a.bhsa_verse_node, a.kind) for a in report.verse_anchors] == [
        (plus_id, 9001, "lxx_plus")
    ]
    assert all(mapping.alignment_id != plus_id for mapping in report.word_mappings)


def test_column_b_retroversion_never_becomes_bhsa_word() -> None:
    doc = parse_parallel_text(
        """Gen 1:1
BR) =XYZ\tEPOI
""",
        source_name="01.Genesis.par",
    )
    provider = _provider(BhsaWord(101, "ברא", None, None))

    report = resolve_bhsa_document(doc, provider)

    assert len(report.word_mappings) == 1
    assert report.word_mappings[0].bhsa_node == 101


def test_missing_bhsa_verse_is_explicit() -> None:
    doc = parse_parallel_text(
        """Gen 1:1
BR)\tEPOI
""",
        source_name="01.Genesis.par",
    )

    report = resolve_bhsa_document(doc, FakeProvider({}))

    assert report.word_mappings == ()
    assert report.summary.missing_verses == 1
    assert report.findings[0].code == "missing_bhsa_verse"


def test_declared_unsupported_source_is_not_mapping_failure() -> None:
    doc = parse_parallel_text(
        """1Esd 1:1
HB\tGR
""",
        source_name="17.1Esdras.par",
    )

    report = resolve_bhsa_document(doc, FakeProvider({}))

    assert report.summary.documents == 1
    assert report.summary.unsupported_documents == 1
    assert report.summary.unknown_documents == 0
    assert report.findings == ()


def test_unknown_source_is_explicit_finding() -> None:
    doc = parse_parallel_text(
        """Test 1:1
HB\tGR
""",
        source_name="99.Unknown.par",
    )

    report = resolve_bhsa_document(doc, FakeProvider({}))

    assert report.summary.unknown_documents == 1
    assert report.findings[0].code == "unknown_catss_source"
