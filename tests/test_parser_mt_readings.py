from catss_tf.parser import parse_parallel_text


def test_mt_readings_preserve_ketiv_qere_pairing_per_position() -> None:
    doc = parse_parallel_text(
        """Gen 1:1
*W/HBW)TY/M **W/HBY)WTY/M {**}\tGR
""",
        source_name="01.Genesis.par",
    )

    row = doc.verses[0].alignments[0]
    assert len(row.mt_readings) == 1
    reading = row.mt_readings[0]
    assert reading.primary == "W/HBW)TY/M"
    assert reading.ketiv == "W/HBW)TY/M"
    assert reading.qere == "W/HBY)WTY/M"
    assert reading.doubtful is False
    assert reading.aramaic_section is False
    assert row.mt_tokens == ("W/HBW)TY/M",)
    assert row.mt_ketiv_tokens == ("W/HBW)TY/M",)
    assert row.mt_qere_tokens == ("W/HBY)WTY/M",)
    assert row.mt_count == 1


def test_mt_readings_pair_multiple_ketiv_qere_positions() -> None:
    doc = parse_parallel_text(
        """Gen 1:1
*KTYB **QRY *KTYB2 **QRY2\tGR
""",
        source_name="01.Genesis.par",
    )

    readings = doc.verses[0].alignments[0].mt_readings
    assert [(r.primary, r.ketiv, r.qere) for r in readings] == [
        ("KTYB", "KTYB", "QRY"),
        ("KTYB2", "KTYB2", "QRY2"),
    ]


def test_aramaic_and_doubt_markers_are_structured_not_lexical() -> None:
    doc = parse_parallel_text(
        """Gen 1:1
,,a ?)LHYM?\tGR
""",
        source_name="01.Genesis.par",
    )

    row = doc.verses[0].alignments[0]
    assert row.mt_tokens == (")LHYM",)
    assert row.mt_count == 1
    assert row.mt_readings[0].aramaic_section is True
    assert row.mt_readings[0].doubtful is True


def test_postfix_aramaic_marker_applies_to_preceding_reading() -> None:
    doc = parse_parallel_text(
        """Gen 1:1
(L M$KB/Y ,,a\tGR
""",
        source_name="01.Genesis.par",
    )

    readings = doc.verses[0].alignments[0].mt_readings
    assert len(readings) == 2
    assert readings[0].primary == "(L"
    assert readings[0].aramaic_section is False
    assert readings[1].primary == "M$KB/Y"
    assert readings[1].aramaic_section is True
