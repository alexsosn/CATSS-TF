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
    assert row.mt_tokens == ("HBK", "HBQ")


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
    assert {"verse_reference", "note"} <= kinds


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
        line_no
        for verse in doc.verses
        for row in verse.alignments
        for line_no in row.source_lines
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
        "mt_strategy_siglum",
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
