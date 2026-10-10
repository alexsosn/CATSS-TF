from catss_tf.parser import alignment_id_for, parse_parallel_text


def test_joshb_contextual_reference_range_is_structured_without_lexical_fabrication() -> None:
    raw = "{...} <8.30-35>\t[[9.2a-2f]]"
    document = parse_parallel_text(
        f"JoshB 9:2\n{raw}\n",
        source_name="06.JoshB.par",
    )

    alignment = document.verses[0].alignments[0]

    assert alignment.raw_lines == (raw,)
    assert alignment.mt_raw == "{...} <8.30-35>"
    assert alignment.lxx_raw == "[[9.2a-2f]]"
    assert alignment.mt_tokens == ()
    assert alignment.lxx_tokens == ()
    assert alignment.lxx_references == ()
    assert len(alignment.lxx_reference_ranges) == 1

    range_ref = alignment.lxx_reference_ranges[0]
    assert (
        range_ref.start_chapter,
        range_ref.start_verse,
        range_ref.start_subverse,
        range_ref.end_chapter,
        range_ref.end_verse,
        range_ref.end_subverse,
        range_ref.raw,
    ) == (9, 2, "a", 9, 2, "f", "[[9.2a-2f]]")

    assert any(
        annotation.side == "mt_a"
        and annotation.kind == "transposition_remote"
        and annotation.raw == "{...}"
        for annotation in alignment.annotations
    )
    assert any(
        annotation.side == "mt_a"
        and annotation.raw == "<8.30-35>"
        and annotation.payload == "8.30-35"
        for annotation in alignment.annotations
    )
    assert any(
        annotation.side == "lxx"
        and annotation.kind == "contextual_reference"
        and annotation.raw == "[[9.2a-2f]]"
        and annotation.payload == "9.2a-2f"
        for annotation in alignment.annotations
    )
    assert not any(
        diagnostic.code == "invalid_lxx_reference" for diagnostic in document.diagnostics
    )

    assert alignment.alignment_id == alignment_id_for(
        source_name="06.JoshB.par",
        header_raw="JoshB 9:2",
        source_lines=(2,),
        raw_lines=(raw,),
    )


def test_reversed_contextual_reference_range_remains_fail_closed() -> None:
    document = parse_parallel_text(
        "JoshB 9:2\n{...} <8.30-35>\t[[9.2f-2a]]\n",
        source_name="06.JoshB.par",
    )

    alignment = document.verses[0].alignments[0]

    assert alignment.lxx_reference_ranges == ()
    assert any(
        diagnostic.code in {"invalid_lxx_reference", "invalid_lxx_reference_range"}
        for diagnostic in document.diagnostics
    )
