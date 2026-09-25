import collections.abc

import pytest

from catss_tf.bhsa_map import (
    BhsaMapStatus,
    BhsaVerse,
    BhsaWordSlot,
    CatssHebrewNormalizationError,
    MappingSeverity,
    normalize_bhsa_hebrew,
    normalize_catss_hebrew,
    resolve_document_to_bhsa,
)
from catss_tf.parser import parse_parallel_text


def _provider(
    *verses: BhsaVerse,
) -> collections.abc.Callable[[str, int, int], BhsaVerse | None]:
    by_ref = {(v.book, v.chapter, v.verse): v for v in verses}

    def lookup(book: str, chapter: int, verse: int) -> BhsaVerse | None:
        return by_ref.get((book, chapter, verse))

    return lookup


def _verse(
    *forms: str,
    book: str = "Genesis",
    chapter: int = 1,
    verse: int = 1,
    verse_node: int = 1_500_000,
    start_node: int = 1,
    qeres: dict[int, str] | None = None,
) -> BhsaVerse:
    qere_by_node = qeres or {}
    return BhsaVerse(
        book=book,
        chapter=chapter,
        verse=verse,
        verse_node=verse_node,
        words=tuple(
            BhsaWordSlot(
                node=start_node + index,
                g_cons_utf8=form,
                g_word_utf8=form,
                qere_utf8=qere_by_node.get(start_node + index),
            )
            for index, form in enumerate(forms)
        ),
    )


def test_catss_normalization_uses_consonants_and_keeps_shin_sin_precision() -> None:
    assert normalize_catss_hebrew("R)$YT") == "R)$YT"
    assert normalize_catss_hebrew("$M( W/&R") == "$M(W& R".replace(" ", "")
    assert normalize_catss_hebrew("W.A73") == "W"
    assert normalize_catss_hebrew("B/)RC") == "B)RC"


def test_catss_normalization_rejects_unknown_source_symbols() -> None:
    with pytest.raises(CatssHebrewNormalizationError):
        normalize_catss_hebrew("BR@")

    with pytest.raises(CatssHebrewNormalizationError):
        normalize_catss_hebrew("123")


def test_bhsa_normalization_folds_points_and_final_forms_but_preserves_shin_sin() -> None:
    assert normalize_bhsa_hebrew("רֵאשִׁ֖ית") == "R)$YT"
    assert normalize_bhsa_hebrew("שָׂרִים") == "&RYM"
    assert normalize_bhsa_hebrew("מֶלֶךְ") == "MLK"


def test_bhsa_qere_whitespace_remains_inside_one_parent_slot() -> None:
    assert normalize_bhsa_hebrew("וַ\nיּוּשַׂ֤ם") == "WYW&M"


def test_genesis_1_1_maps_by_complete_text_not_ordinal_guessing() -> None:
    doc = parse_parallel_text(
        """Gen 1:1
B/R)$YT\tE)N A)RXH=|
BR)\tE)POI/HSEN
)LHYM\tO( QEO\\S
)T H/$MYM\tTO\\N OU)RANO\\N
W/)T H/)RC\tKAI\\ TH\\N GH=N
""",
        source_name="01.Genesis.par",
    )
    parent = _verse(
        "ב",
        "ראשׁית",
        "ברא",
        "אלהים",
        "את",
        "ה",
        "שׁמים",
        "ו",
        "את",
        "ה",
        "ארץ",
    )

    report = resolve_document_to_bhsa(doc, verse_lookup=_provider(parent))

    assert report.ok is True
    assert [mapping.status for mapping in report.mappings] == [BhsaMapStatus.MAPPED] * 5
    assert [mapping.bhsa_word_nodes for mapping in report.mappings] == [
        (1, 2),
        (3,),
        (4,),
        (5, 6, 7),
        (8, 9, 10, 11),
    ]
    assert report.summary.mapped_alignments == 5
    assert report.summary.finding_count == 0


def test_slash_suffix_can_map_as_one_bhsa_slot() -> None:
    doc = parse_parallel_text(
        """Gen 1:1
BN/YW\tGR
""",
        source_name="01.Genesis.par",
    )
    parent = _verse("בניו", start_node=3159)

    report = resolve_document_to_bhsa(doc, verse_lookup=_provider(parent))

    mapping = report.mappings[0]
    assert mapping.status is BhsaMapStatus.MAPPED
    assert mapping.bhsa_word_nodes == (3159,)
    assert mapping.mapping_kind == "exact"


def test_slash_prefix_can_expand_to_multiple_bhsa_slots() -> None:
    doc = parse_parallel_text(
        """Gen 1:1
B/)RC\tGR
""",
        source_name="01.Genesis.par",
    )
    parent = _verse("ב", "ארץ", start_node=100)

    report = resolve_document_to_bhsa(doc, verse_lookup=_provider(parent))

    mapping = report.mappings[0]
    assert mapping.bhsa_word_nodes == (100, 101)
    assert mapping.mapping_kind == "slash_split"


def test_empty_consonant_bhsa_slot_is_transparent_and_kept_inside_row_span() -> None:
    doc = parse_parallel_text(
        """Gen 1:5
L/)WR\tGR
""",
        source_name="01.Genesis.par",
    )
    parent = _verse(
        "ל",
        "",
        "אור",
        chapter=1,
        verse=5,
        start_node=61,
        verse_node=1_500_005,
    )

    report = resolve_document_to_bhsa(doc, verse_lookup=_provider(parent))

    mapping = report.mappings[0]
    assert mapping.status is BhsaMapStatus.MAPPED
    assert mapping.bhsa_word_nodes == (61, 62, 63)


def test_column_b_retroversion_is_not_used_for_bhsa_identity() -> None:
    doc = parse_parallel_text(
        """Gen 1:1
BR) =QTL\tGR
""",
        source_name="01.Genesis.par",
    )
    parent = _verse("ברא")

    report = resolve_document_to_bhsa(doc, verse_lookup=_provider(parent))

    assert report.ok is True
    assert report.mappings[0].bhsa_word_nodes == (1,)


def test_hebrew_empty_lxx_plus_gets_verse_anchor_but_no_word_anchor() -> None:
    doc = parse_parallel_text(
        """Gen 1:1
--+ '' =;PLUS\tGRPLUS
BR)\tGR
""",
        source_name="01.Genesis.par",
    )
    parent = _verse("ברא", verse_node=1_444_000)

    report = resolve_document_to_bhsa(doc, verse_lookup=_provider(parent))

    plus, regular = report.mappings
    assert plus.status is BhsaMapStatus.HEBREW_EMPTY
    assert plus.bhsa_verse_node == 1_444_000
    assert plus.bhsa_word_nodes == ()
    assert regular.bhsa_word_nodes == (1,)
    assert report.summary.hebrew_empty_alignments == 1


def test_sequence_mismatch_never_falls_back_to_same_position() -> None:
    doc = parse_parallel_text(
        """Gen 1:1
BR)\tGR
""",
        source_name="01.Genesis.par",
    )
    parent = _verse("אמר")

    report = resolve_document_to_bhsa(doc, verse_lookup=_provider(parent))

    assert report.ok is False
    assert report.mappings[0].status is BhsaMapStatus.SEQUENCE_MISMATCH
    assert report.mappings[0].bhsa_word_nodes == ()
    finding = report.findings[0]
    assert finding.code == "sequence_mismatch"
    assert finding.expected == "BR)"
    assert finding.actual == ")MR"
    assert finding.severity is MappingSeverity.ERROR


def test_extra_nonempty_bhsa_slot_causes_sequence_mismatch() -> None:
    doc = parse_parallel_text(
        """Gen 1:1
BR)\tGR
""",
        source_name="01.Genesis.par",
    )
    parent = _verse("ברא", "אלהים")

    report = resolve_document_to_bhsa(doc, verse_lookup=_provider(parent))

    assert report.ok is False
    assert report.summary.sequence_mismatches == 1


def test_paired_ketiv_qere_maps_by_ketiv_and_validates_qere_same_slot() -> None:
    doc = parse_parallel_text(
        """Gen 1:1
*KTB **QR)\tGR
""",
        source_name="01.Genesis.par",
    )
    parent = _verse("כתב", qeres={1: "קָרָא"})

    report = resolve_document_to_bhsa(doc, verse_lookup=_provider(parent))

    assert report.ok is True
    assert report.mappings[0].bhsa_word_nodes == (1,)
    assert report.summary.qere_mismatches == 0


def test_qere_mismatch_is_blocking_but_does_not_erase_primary_mapping() -> None:
    doc = parse_parallel_text(
        """Gen 1:1
*KTB **QR)\tGR
""",
        source_name="01.Genesis.par",
    )
    parent = _verse("כתב", qeres={1: "קְרִי"})

    report = resolve_document_to_bhsa(doc, verse_lookup=_provider(parent))

    assert report.ok is False
    assert report.mappings[0].bhsa_word_nodes == (1,)
    assert report.summary.qere_mismatches == 1
    assert report.findings[0].code == "qere_mismatch"


def test_qere_only_row_can_resolve_against_sparse_bhsa_qere() -> None:
    doc = parse_parallel_text(
        """Gen 1:1
**QR)\tGR
""",
        source_name="01.Genesis.par",
    )
    parent = _verse("כתב", qeres={1: "קָרָא"})

    report = resolve_document_to_bhsa(doc, verse_lookup=_provider(parent))

    assert report.ok is True
    assert report.mappings[0].bhsa_word_nodes == (1,)
    assert report.mappings[0].mapping_kind == "qere"


def test_multi_slot_paired_qere_is_explicitly_ambiguous_not_guessed() -> None:
    doc = parse_parallel_text(
        """Gen 1:1
*B/KTB **QR)\tGR
""",
        source_name="01.Genesis.par",
    )
    parent = _verse("ב", "כתב", qeres={2: "קָרָא"})

    report = resolve_document_to_bhsa(doc, verse_lookup=_provider(parent))

    assert report.ok is False
    assert report.mappings[0].bhsa_word_nodes == (1, 2)
    assert any(f.code == "qere_structure_ambiguous" for f in report.findings)


def test_ambiguous_catss_shin_can_match_bhsa_shin_or_sin_but_is_reported_in_kind() -> None:
    doc = parse_parallel_text(
        """Gen 1:1
#R\tGR
""",
        source_name="01.Genesis.par",
    )
    parent = _verse("שׂר")

    report = resolve_document_to_bhsa(doc, verse_lookup=_provider(parent))

    assert report.ok is True
    assert report.mappings[0].mapping_kind == "ambiguous_shin"


def test_unknown_catss_symbol_is_explicitly_unnormalizable() -> None:
    doc = parse_parallel_text(
        """Gen 1:1
BR@\tGR
""",
        source_name="01.Genesis.par",
    )
    parent = _verse("ברא")

    report = resolve_document_to_bhsa(doc, verse_lookup=_provider(parent))

    assert report.ok is False
    assert report.mappings[0].status is BhsaMapStatus.UNNORMALIZABLE
    assert report.summary.unnormalizable_tokens == 1
    assert report.findings[0].code == "unnormalizable_token"


def test_missing_parent_verse_is_explicit() -> None:
    doc = parse_parallel_text(
        """Gen 1:1
BR)\tGR
""",
        source_name="01.Genesis.par",
    )

    report = resolve_document_to_bhsa(doc, verse_lookup=_provider())

    assert report.ok is False
    assert report.mappings[0].status is BhsaMapStatus.VERSE_MISSING
    assert report.summary.missing_verses == 1


def test_declared_unsupported_source_is_nonblocking_and_never_looked_up() -> None:
    doc = parse_parallel_text(
        """1Esd 1:1
HB\tGR
""",
        source_name="17.1Esdras.par",
    )
    calls: list[tuple[str, int, int]] = []

    def lookup(book: str, chapter: int, verse: int) -> BhsaVerse | None:
        calls.append((book, chapter, verse))
        return None

    report = resolve_document_to_bhsa(doc, verse_lookup=lookup)

    assert report.ok is True
    assert calls == []
    assert report.mappings[0].status is BhsaMapStatus.UNSUPPORTED_SOURCE
    assert report.summary.unsupported_alignments == 1
    assert report.findings[0].severity is MappingSeverity.INFO


def test_unknown_source_is_blocking_and_distinct_from_declared_unsupported() -> None:
    doc = parse_parallel_text(
        """Test 1:1
HB\tGR
""",
        source_name="99.Test.par",
    )

    report = resolve_document_to_bhsa(doc, verse_lookup=_provider())

    assert report.ok is False
    assert report.mappings[0].status is BhsaMapStatus.UNKNOWN_SOURCE
    assert report.findings[0].code == "unknown_source"
    assert report.findings[0].severity is MappingSeverity.ERROR


def test_duplicate_parent_word_nodes_fail_closed() -> None:
    doc = parse_parallel_text(
        """Gen 1:1
B/R)$YT\tGR
""",
        source_name="01.Genesis.par",
    )
    parent = BhsaVerse(
        book="Genesis",
        chapter=1,
        verse=1,
        verse_node=1_500_000,
        words=(
            BhsaWordSlot(node=1, g_cons_utf8="ב", g_word_utf8="ב"),
            BhsaWordSlot(node=1, g_cons_utf8="ראשׁית", g_word_utf8="ראשׁית"),
        ),
    )

    report = resolve_document_to_bhsa(doc, verse_lookup=_provider(parent))

    assert report.ok is False
    assert report.mappings[0].status is BhsaMapStatus.PARENT_INVALID
    assert report.mappings[0].bhsa_word_nodes == ()
    assert report.findings[0].code == "parent_snapshot_invalid"


def test_out_of_order_parent_word_nodes_fail_closed() -> None:
    doc = parse_parallel_text(
        """Gen 1:1
B/R)$YT\tGR
""",
        source_name="01.Genesis.par",
    )
    parent = BhsaVerse(
        book="Genesis",
        chapter=1,
        verse=1,
        verse_node=1_500_000,
        words=(
            BhsaWordSlot(node=2, g_cons_utf8="ב", g_word_utf8="ב"),
            BhsaWordSlot(node=1, g_cons_utf8="ראשׁית", g_word_utf8="ראשׁית"),
        ),
    )

    report = resolve_document_to_bhsa(doc, verse_lookup=_provider(parent))

    assert report.ok is False
    assert report.mappings[0].status is BhsaMapStatus.PARENT_INVALID
    assert report.findings[0].code == "parent_snapshot_invalid"


def test_provider_reference_mismatch_has_distinct_parent_invalid_status() -> None:
    doc = parse_parallel_text(
        """Gen 1:1
BR)\tGR
""",
        source_name="01.Genesis.par",
    )
    wrong = _verse("ברא", book="Exodus")

    def lookup(_book: str, _chapter: int, _verse_no: int) -> BhsaVerse | None:
        return wrong

    report = resolve_document_to_bhsa(doc, verse_lookup=lookup)

    assert report.ok is False
    assert report.mappings[0].status is BhsaMapStatus.PARENT_INVALID
    assert report.findings[0].code == "parent_reference_mismatch"
