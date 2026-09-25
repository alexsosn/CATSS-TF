from catss_tf.parser import parse_parallel_text


def test_greek_reference_annotations_are_structured() -> None:
    doc = parse_parallel_text(
        """Gen 23:5
HB1\tMH/ [6]
HB2\tLOGOS [[23:6a]]
""",
        source_name="01.Genesis.par",
    )

    first, second = doc.verses[0].alignments
    assert [(r.chapter, r.verse, r.subverse, r.raw) for r in first.lxx_references] == [
        (None, 6, None, "[6]")
    ]
    assert [(r.chapter, r.verse, r.subverse, r.raw) for r in second.lxx_references] == [
        (23, 6, "a", "[[23:6a]]")
    ]
    assert first.lxx_tokens == ("MH/",)
    assert second.lxx_tokens == ("LOGOS",)


def test_non_numeric_square_brackets_preserve_lexical_payload() -> None:
    doc = parse_parallel_text(
        """Test 1:1
HB\t[LOGOS]
""",
        source_name="99.Test.par",
    )

    row = doc.verses[0].alignments[0]
    assert row.lxx_references == ()
    assert row.lxx_tokens == ("LOGOS",)


def test_invalid_numeric_greek_reference_is_diagnostic_not_silently_dropped() -> None:
    doc = parse_parallel_text(
        """Test 1:1
HB\tLOGOS [6x7]
""",
        source_name="99.Test.par",
    )

    assert doc.verses[0].alignments[0].lxx_tokens == ("LOGOS",)
    assert [d.code for d in doc.diagnostics] == ["invalid_lxx_reference"]
    assert doc.diagnostics[0].raw_line == "HB\tLOGOS [6x7]"


def test_greek_edition_difference_wrapper_preserves_lexical_payload() -> None:
    doc = parse_parallel_text(
        """Test 1:1
HB\t{gLOGOS}
""",
        source_name="99.Test.par",
    )

    row = doc.verses[0].alignments[0]
    assert row.lxx_tokens == ("LOGOS",)
    assert any(annotation.kind == "greek_edition_difference" for annotation in row.annotations)
