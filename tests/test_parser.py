from pathlib import Path

from catss_tf.parser import parse_parallel_text


def test_parse_basic_alignment_ratios() -> None:
    doc = parse_parallel_text(
        """Test 1:1
HB1\tGR1
HB2\tGR2 GR3
HB3 HB4\tGR4
HB5 HB6\tGR5 GR6
""",
        source_name="99.Test.par",
    )

    rows = doc.verses[0].alignments
    assert [(row.mt_count, row.lxx_count) for row in rows] == [
        (1, 1),
        (1, 2),
        (2, 1),
        (2, 2),
    ]
    assert rows[1].mt_tokens == ("HB2",)
    assert rows[1].lxx_tokens == ("GR2", "GR3")
    assert rows[2].mt_tokens == ("HB3", "HB4")


def test_parse_plus_minus_and_column_b() -> None:
    doc = parse_parallel_text(
        """Test 1:1
--+ '' =;HBPLUS\tGRPLUS
HBMINUS\t--- ''
HBA =:ALT .dr\tGRA
""",
        source_name="99.Test.par",
    )

    plus, minus, retro = doc.verses[0].alignments

    assert plus.is_lxx_plus is True
    assert plus.mt_col_a == "--+ ''"
    assert plus.mt_col_b == ";HBPLUS"
    assert plus.mt_tokens == ()
    assert (plus.mt_count, plus.lxx_count) == (0, 1)

    assert minus.is_lxx_minus is True
    assert minus.lxx_tokens == ()
    assert (minus.mt_count, minus.lxx_count) == (1, 0)

    assert retro.mt_col_a == "HBA"
    assert retro.mt_col_b == ":ALT .dr"
    assert retro.mt_tokens == ("HBA",)
    assert retro.lxx_tokens == ("GRA",)


def test_parse_ketiv_and_qere_independently() -> None:
    doc = parse_parallel_text(
        """Test 1:1
*HBK **HBQ\tGR
""",
        source_name="99.Test.par",
    )

    row = doc.verses[0].alignments[0]
    assert row.is_ketiv is True
    assert row.is_qere is True
    assert row.mt_tokens == ("HBK",)
    assert row.mt_ketiv_tokens == ("HBK",)
    assert row.mt_qere_tokens == ("HBQ",)
    assert row.mt_count == 1


def test_parse_transposition_kinds_without_reordering() -> None:
    doc = parse_parallel_text(
        """Test 1:1
HBLOCAL ^\t^ GRLOCAL
^ HBREMOTE\t^^^
HBSTYLE\t{..^GRSTYLE}
HBPLACE\t{...GRPLACE}
""",
        source_name="99.Test.par",
    )

    local, remote, stylistic, placeholder = doc.verses[0].alignments

    assert local.is_transposition_local is True
    assert local.mt_tokens == ("HBLOCAL",)
    assert local.lxx_tokens == ("GRLOCAL",)

    assert remote.is_transposition_remote is True
    assert stylistic.is_transposition_stylistic is True
    assert stylistic.lxx_tokens == ("GRSTYLE",)
    assert placeholder.is_transposition_remote is True
    assert placeholder.lxx_tokens == ("GRPLACE",)


def test_legacy_tilde_is_preserved_as_local_transposition() -> None:
    doc = parse_parallel_text(
        """Test 1:1
HB ~\tGR
""",
        source_name="99.Test.par",
    )

    row = doc.verses[0].alignments[0]
    assert row.is_transposition_local is True
    assert row.raw_lines == ("HB ~\tGR",)


def test_discontinuous_hash_lines_form_one_logical_alignment() -> None:
    doc = parse_parallel_text(
        """Test 1:1
HBX\tGRX #
#\tGRY
HBZ #\tGRZ
HBY\t
""",
        source_name="99.Test.par",
    )

    first, second = doc.verses[0].alignments

    assert first.source_lines == (2, 3)
    assert first.raw_lines == ("HBX\tGRX #", "#\tGRY")
    assert first.mt_tokens == ("HBX",)
    assert first.lxx_tokens == ("GRX", "GRY")
    assert (first.mt_count, first.lxx_count) == (1, 2)

    assert second.source_lines == (4, 5)
    assert second.mt_tokens == ("HBZ", "HBY")
    assert second.lxx_tokens == ("GRZ",)


def test_unknown_brace_siglum_is_retained_as_annotation() -> None:
    doc = parse_parallel_text(
        """Test 1:1
HB {zzUNKNOWN}\tGR
""",
        source_name="99.Test.par",
    )

    row = doc.verses[0].alignments[0]
    unknown = [annotation for annotation in row.annotations if annotation.kind == "unknown"]
    assert [(annotation.side, annotation.raw) for annotation in unknown] == [
        ("mt_a", "{zzUNKNOWN}")
    ]
    assert row.mt_tokens == ("HB",)


def test_known_annotation_blocks_are_retained() -> None:
    doc = parse_parallel_text(
        """Test 1:1
HB {d} {t} {x} {*} {**}\tGR [2] <note>
""",
        source_name="99.Test.par",
    )

    row = doc.verses[0].alignments[0]
    kinds = {annotation.kind for annotation in row.annotations}
    assert {"doublet", "transliteration", "apparent_plus_minus"} <= kinds
    assert {"greek_agrees_ketiv", "greek_agrees_qere"} <= kinds
    assert {"verse_reference", "source_note"} <= kinds


def test_special_and_single_chapter_headers_are_parsed() -> None:
    doc = parse_parallel_text(
        """1Sam/K 2:3
HB\tGR

Obad 7
HB2\tGR2
""",
        source_name="99.Test.par",
    )

    first, second = doc.verses
    assert (first.book, first.chapter, first.verse) == ("1Sam/K", 2, 3)
    assert (second.book, second.chapter, second.verse) == ("Obad", 1, 7)


def test_blank_lines_do_not_end_current_verse() -> None:
    doc = parse_parallel_text(
        """Test 1:1
HB1\tGR1

HB2\tGR2
Test 1:2
HB3\tGR3
""",
        source_name="99.Test.par",
    )

    assert len(doc.verses) == 2
    assert len(doc.verses[0].alignments) == 2


def test_orphan_and_unsplit_lines_are_not_silently_dropped() -> None:
    doc = parse_parallel_text(
        """ORPHAN
Test 1:1
HBONLY
HB\tGR
""",
        source_name="99.Test.par",
    )

    assert [diagnostic.code for diagnostic in doc.diagnostics] == [
        "orphan_line",
        "unsplit_row",
    ]
    assert doc.diagnostics[0].raw_line == "ORPHAN"
    assert doc.verses[0].alignments[0].mt_raw == "HBONLY"
    assert doc.verses[0].alignments[0].lxx_raw == ""


def test_alignment_ids_are_deterministic_and_source_derived() -> None:
    text = """Test 1:1
HB\tGR
"""
    first = parse_parallel_text(text, source_name="/tmp/a/99.Test.par")
    second = parse_parallel_text(text, source_name="/other/path/99.Test.par")
    changed_source = parse_parallel_text(text, source_name="98.Other.par")

    first_id = first.verses[0].alignments[0].alignment_id
    second_id = second.verses[0].alignments[0].alignment_id
    changed_id = changed_source.verses[0].alignments[0].alignment_id

    assert first.source_name == "99.Test.par"
    assert first_id == second_id
    assert first_id.startswith("catss:99.Test.par:")
    assert first_id != changed_id


def test_every_nonblank_data_line_is_accounted_for_by_alignment_or_diagnostic() -> None:
    doc = parse_parallel_text(
        """JUNK
Test 1:1
HB1\tGR1
HB2\tGR2 #
#\tGR3
UNSPLIT
""",
        source_name="99.Test.par",
    )

    consumed = {
        line_no for verse in doc.verses for row in verse.alignments for line_no in row.source_lines
    }
    diagnosed = {diagnostic.line_no for diagnostic in doc.diagnostics}

    assert consumed | diagnosed == {1, 3, 4, 5, 6}


def test_mt_strategy_sigla_are_structured_not_lexical_tokens() -> None:
    doc = parse_parallel_text(
        """Test 1:1
HB .m .s .j .w .z .xx\tGR
""",
        source_name="99.Test.par",
    )

    row = doc.verses[0].alignments[0]
    assert row.mt_tokens == ("HB",)
    kinds = [annotation.kind for annotation in row.annotations if annotation.side == "mt_a"]
    assert kinds == [
        "metathesis",
        "word_separation",
        "word_join",
        "word_division",
        "abbreviation",
        "letter_interchange",
    ]


def test_annotations_distinguish_mt_a_mt_b_and_lxx() -> None:
    doc = parse_parallel_text(
        """Test 1:1
HBA .m =;ALT .s\tGR {d}
""",
        source_name="99.Test.par",
    )

    row = doc.verses[0].alignments[0]
    assert [(a.side, a.kind, a.raw) for a in row.annotations] == [
        ("mt_a", "metathesis", ".m"),
        ("mt_b", "word_separation", ".s"),
        ("lxx", "doublet", "{d}"),
    ]


def test_text_bearing_wrappers_keep_payload_and_annotation_kind() -> None:
    doc = parse_parallel_text(
        """Test 1:1
HB\t{cGRCORR} {..pGRPREP} {..dGRDIST} {..rGRREPEAT}
""",
        source_name="99.Test.par",
    )

    row = doc.verses[0].alignments[0]
    assert row.lxx_tokens == ("GRCORR", "GRPREP", "GRDIST", "GRREPEAT")
    assert [a.kind for a in row.annotations if a.side == "lxx"] == [
        "greek_correction",
        "preposition_added",
        "distributive",
        "repetition",
    ]


def test_retroversion_kind_is_structured() -> None:
    doc = parse_parallel_text(
        """Test 1:1
HB =:ALT\tGR
HB =;ALT2\tGR2
HB =%vpa\tGR3
HB =PLAIN\tGR4
""",
        source_name="99.Test.par",
    )

    rows = doc.verses[0].alignments
    assert [row.retroversion_kind for row in rows] == [
        "proper_noun",
        "context",
        "passive_to_active",
        "plain",
    ]


def test_parse_parallel_file_rejects_invalid_utf8(tmp_path: Path) -> None:
    path = tmp_path / "99.Test.par"
    path.write_bytes(b"Test 1:1\nHB\tGR\xff\n")

    try:
        from catss_tf.parser import parse_parallel_file

        parse_parallel_file(path)
    except UnicodeDecodeError:
        pass
    else:
        raise AssertionError("invalid UTF-8 must not be silently replaced")


def test_legacy_plus_minus_sigla_are_recognized_without_rewriting_raw() -> None:
    doc = parse_parallel_text(
        """Test 1:1
-+ =HBPLUS\tGRPLUS
---+ =HBPLUS2\tGRPLUS2
HBMINUS\t-- ''
""",
        source_name="99.Test.par",
    )

    plus_one, plus_two, minus = doc.verses[0].alignments
    assert plus_one.is_lxx_plus is True
    assert plus_one.mt_count == 0
    assert plus_one.raw_lines == ("-+ =HBPLUS\tGRPLUS",)

    assert plus_two.is_lxx_plus is True
    assert plus_two.mt_count == 0
    assert plus_two.raw_lines == ("---+ =HBPLUS2\tGRPLUS2",)

    assert minus.is_lxx_minus is True
    assert minus.lxx_count == 0
    assert minus.raw_lines == ("HBMINUS\t-- ''",)


def test_mt_readings_structure_inline_aramaic_and_doubt_markers() -> None:
    doc = parse_parallel_text(
        """Test 1:1
??MLK??,,a DBR,,a\tGR
""",
        source_name="99.Test.par",
    )

    first, second = doc.verses[0].alignments[0].mt_readings
    assert first.primary == "MLK"
    assert first.doubtful is True
    assert first.aramaic_section is True
    assert second.primary == "DBR"
    assert second.doubtful is False
    assert second.aramaic_section is True
    assert doc.verses[0].alignments[0].mt_tokens == ("MLK", "DBR")


def test_parser_decodes_documented_contextual_influence_annotation() -> None:
    document = parse_parallel_text(
        "Ge 1:1\nBR> {XTM}\tλογος\n",
        source_name="01.Genesis.par",
    )

    annotation = document.verses[0].alignments[0].annotations[0]
    assert annotation.kind == "contextual_influence"
    assert annotation.family == "translation_technique"
    assert annotation.contextual is True
    assert annotation.raw == "{XTM}"


def test_parser_maps_raw_catss_brace_syntax_to_documented_semantics() -> None:
    document = parse_parallel_text(
        "Ge 1:1\nBR>\tλογος {..dABC} {..pABC} {...ABC} {..rABC}\n",
        source_name="01.Genesis.par",
    )
    annotations = document.verses[0].alignments[0].annotations
    assert [(a.kind, a.family, a.contextual) for a in annotations] == [
        ("distributive", "translation_technique", True),
        ("preposition_added", "preposition", True),
        ("transposition_remote", "transposition", True),
        ("repetition", "translation_technique", True),
    ]


def test_contextual_raw_annotation_preserves_payload_text() -> None:
    document = parse_parallel_text(
        "Test 1:1\nHB\t{..dGRDIST} {..rGRREPEAT}\n",
        source_name="99.Test.par",
    )

    annotations = document.verses[0].alignments[0].annotations
    assert [(a.kind, a.raw, a.contextual) for a in annotations] == [
        ("distributive", "{..dGRDIST}", True),
        ("repetition", "{..rGRREPEAT}", True),
    ]


def test_contextual_brace_annotation_exposes_payload_separately() -> None:
    document = parse_parallel_text(
        "Test 1:1\nHB\t{..dGRDIST} {..rGRREPEAT}\n",
        source_name="99.Test.par",
    )

    annotations = document.verses[0].alignments[0].annotations
    assert [(a.kind, a.payload) for a in annotations] == [
        ("distributive", "GRDIST"),
        ("repetition", "GRREPEAT"),
    ]


def test_sirach_uncertain_transliteration_annotation_is_typed() -> None:
    document = parse_parallel_text(
        "Sir 2:13\n[..]\tOU)AI\\ {t?}\n",
        source_name="27.Sirach.par",
    )

    annotations = document.verses[0].alignments[0].annotations
    annotation = next(a for a in annotations if a.raw == "{t?}")
    assert annotation.kind == "uncertain_transliteration"
    assert annotation.family == "translation_technique"


def test_raw_mt_strategy_codes_keep_specific_semantics() -> None:
    document = parse_parallel_text(
        "Test 1:1\nHB .kb\tGR\nHB =%p-\tGR\nHB =%p+\tGR\nHB =+\tGR\nHB {!}-\tGR\n",
        source_name="99.Test.par",
    )

    alignments = document.verses[0].alignments
    assert alignments[0].annotations[0].kind == "letter_interchange"
    assert alignments[0].annotations[0].payload == "kb"
    assert alignments[1].retroversion_kind == "preposition_omission"
    assert alignments[2].retroversion_kind == "preposition_addition"
    assert alignments[3].retroversion_kind == "number_difference"
    inf_abs = next(a for a in alignments[4].annotations if a.raw == "{!}-")
    assert inf_abs.kind == "inf_abs_rendered_finite_verb"
    assert inf_abs.family == "infinitive_absolute"


def test_contextual_reference_markup_is_typed_without_false_invalid_reference() -> None:
    document = parse_parallel_text(
        "Test 1:1\nHB <sp26.35ap>\tGR [e6.16] [2.46k,10.26a] [[30:11]]\n",
        source_name="99.Test.par",
    )

    alignment = document.verses[0].alignments[0]
    by_raw = {a.raw: a for a in alignment.annotations}
    assert by_raw["<sp26.35ap>"].kind == "samaritan_apparatus_reference"
    assert by_raw["<sp26.35ap>"].family == "reference"
    assert by_raw["[e6.16]"].kind == "contextual_reference"
    assert by_raw["[e6.16]"].payload == "e6.16"
    assert by_raw["[2.46k,10.26a]"].kind == "contextual_reference"
    assert by_raw["[[30:11]]"].kind == "verse_reference"
    assert document.diagnostics == ()


def test_greek_editorial_wrappers_expose_payload() -> None:
    document = parse_parallel_text(
        "Test 1:1\nHB\tGR {c?PU/LHS} {gREADING}\n",
        source_name="99.Test.par",
    )

    annotations = document.verses[0].alignments[0].annotations
    assert [(a.kind, a.payload) for a in annotations] == [
        ("greek_correction", "?PU/LHS"),
        ("greek_edition_difference", "READING"),
    ]


def test_sirach_mt_manuscript_markup_is_not_silently_dropped() -> None:
    document = parse_parallel_text(
        "Sir 2:13\n[..] 3\tOU)AI\\\n[BN]* >7\tLOGOS\n",
        source_name="27.Sirach.par",
    )

    annotations = [
        annotation
        for alignment in document.verses[0].alignments
        for annotation in alignment.annotations
    ]
    assert sorted((a.raw, a.kind) for a in annotations) == sorted(
        [
            ("[..]", "sirach_lacuna_or_illegible"),
            ("3", "sirach_witness_geniza_a"),
            ("[BN]", "sirach_reconstructed_letters"),
            ("*", "sirach_uncertain_fragmentary_letter"),
            (">7", "sirach_reading_lacking_in_witness"),
        ]
    )


def test_sirach_brace_manuscript_markup_keeps_raw_and_witness_payload() -> None:
    document = parse_parallel_text(
        "Sir 3:1\nHB {7} {{}}\tGR\n",
        source_name="27.Sirach.par",
    )

    annotations = document.verses[0].alignments[0].annotations
    assert sorted((a.raw, a.kind, a.payload) for a in annotations) == [
        ("{7}", "sirach_lacuna_in_witness", "7"),
        ("{{}}", "sirach_manuscript_addition", None),
    ]


def test_stylistic_preposition_transposition_preserves_context_payload() -> None:
    document = parse_parallel_text(
        "Gen 1:1\nHB {..p^TARGET}\tQEOS\n",
        source_name="01.Genesis.par",
    )
    annotations = document.verses[0].alignments[0].annotations
    match = next(item for item in annotations if item.kind == "transposition_stylistic")
    assert match.payload == "TARGET"
