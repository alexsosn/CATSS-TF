import dataclasses

from catss_tf.lxx_resolver import (
    LxxSpan,
    LxxWord,
    normalize_catss_greek,
    normalize_lxx_greek,
    resolve_lxx_document,
)
from catss_tf.lxx_schema import (
    LXX_MAX_NODE,
    LXX_MAX_SLOT,
    LXX_NODE_COUNTS,
    LXX_RELEASE_COMMIT,
    LXX_RELEASE_TAG,
    LXX_REPOSITORY,
    LXX_REQUIRED_FEATURES,
    LXX_SECTION_TYPES,
    LXX_VERSION,
    LxxParentProbe,
)
from catss_tf.parser import parse_parallel_text


@dataclasses.dataclass
class FakeProvider:
    probe: LxxParentProbe
    spans: dict[tuple[str, int, int, str], LxxSpan]

    def parent_probe(self) -> LxxParentProbe:
        return self.probe

    def get_span(self, book: str, chapter: int, verse: int, subverse: str) -> LxxSpan | None:
        return self.spans.get((book, chapter, verse, subverse))


def _exact_probe() -> LxxParentProbe:
    return LxxParentProbe(
        repository=LXX_REPOSITORY,
        version=LXX_VERSION,
        release_tag=LXX_RELEASE_TAG,
        release_commit=LXX_RELEASE_COMMIT,
        slot_type="word",
        max_slot=LXX_MAX_SLOT,
        max_node=LXX_MAX_NODE,
        section_types=LXX_SECTION_TYPES,
        node_counts=LXX_NODE_COUNTS,
        feature_names=LXX_REQUIRED_FEATURES,
        feature_blob_shas=None,
    )


def _span(
    *words: tuple[int, str],
    book: str = "Gen",
    chapter: int = 1,
    verse: int = 1,
    subverse: str = "",
    node: int = 9001,
) -> LxxSpan:
    return LxxSpan(
        node=node,
        book=book,
        chapter=chapter,
        verse=verse,
        subverse=subverse,
        words=tuple(
            LxxWord(node=word_node, word=surface, subverse=subverse, orig_order=index)
            for index, (word_node, surface) in enumerate(words, start=1)
        ),
    )


def _provider(*spans: LxxSpan, probe: LxxParentProbe | None = None) -> FakeProvider:
    return FakeProvider(
        probe=probe or _exact_probe(),
        spans={(s.book, s.chapter, s.verse, s.subverse): s for s in spans},
    )


def test_greek_normalization_preserves_surface_letters_not_lemma() -> None:
    assert normalize_catss_greek("E)POI/HSEN") == "εποιησεν"
    assert normalize_catss_greek("TO\N") == "τον"
    assert normalize_catss_greek("DI'") == "δι"
    assert normalize_catss_greek("V") == "ϝ"
    assert normalize_lxx_greek("ἐποίησεν") == "εποιησεν"
    assert normalize_lxx_greek("τὸν") == "τον"
    assert normalize_lxx_greek("λόγος·") == "λογοσ"


def test_unknown_catss_greek_character_fails_closed() -> None:
    try:
        normalize_catss_greek("LOGOS@")
    except ValueError as exc:
        assert "unsupported CATSS Greek character" in str(exc)
    else:
        raise AssertionError("unknown Greek BETA characters must not be dropped")


def test_exact_span_sequence_maps_all_words() -> None:
    doc = parse_parallel_text(
        """Gen 1:1
HB1\tE)N A)RXH=|
HB2\tE)POI/HSEN
""",
        source_name="01.Genesis.par",
    )
    provider = _provider(
        _span((101, "ἐν"), (102, "ἀρχῇ"), (103, "ἐποίησεν"))
    )

    report = resolve_lxx_document(doc, provider)

    assert report.summary.resolved_spans == 1
    assert report.summary.word_mappings == 3
    assert report.findings == ()
    assert [(m.lxx_node, m.mapping_kind) for m in report.word_mappings] == [
        (101, "exact"),
        (102, "exact"),
        (103, "exact"),
    ]


def test_reference_shift_groups_tokens_across_mt_verse_headers() -> None:
    doc = parse_parallel_text(
        """Gen 23:5
HB1\tLE/GONTES
HB2\tMH/ [6]
Gen 23:6
HB3\tA)/KOUSON
""",
        source_name="01.Genesis.par",
    )
    provider = _provider(
        _span((201, "λέγοντες"), chapter=23, verse=5, node=9105),
        _span((202, "μή"), (203, "ἄκουσον"), chapter=23, verse=6, node=9106),
    )

    report = resolve_lxx_document(doc, provider)

    assert report.summary.target_spans == 2
    assert report.summary.resolved_spans == 2
    assert [m.lxx_node for m in report.word_mappings] == [201, 202, 203]
    assert report.summary.reference_overrides == 1


def test_chapter_verse_and_subverse_reference_filters_parent_span() -> None:
    doc = parse_parallel_text(
        """Esth 1:1
HB\tLOGOS [[3:13a]]
""",
        source_name="18.Esther.par",
    )
    provider = _provider(
        _span((301, "λόγος"), book="Esth", chapter=3, verse=13, subverse="a", node=9201)
    )

    report = resolve_lxx_document(doc, provider)

    assert report.summary.resolved_spans == 1
    assert report.word_mappings[0].lxx_node == 301
    assert report.word_mappings[0].target_subverse == "a"


def test_complex_reference_is_explicit_and_emits_no_mapping_for_alignment() -> None:
    doc = parse_parallel_text(
        """1Kgs 1:1
HB\tLOGOS [2.46k,10.26a]
""",
        source_name="13.1Kings.par",
    )

    report = resolve_lxx_document(doc, _provider())

    assert report.word_mappings == ()
    assert report.summary.complex_references == 1
    assert report.findings[0].code == "complex_greek_reference"


def test_multiple_location_references_are_not_guessed() -> None:
    doc = parse_parallel_text(
        """Gen 1:1
HB\tLOGOS [2] [3]
""",
        source_name="01.Genesis.par",
    )

    report = resolve_lxx_document(doc, _provider())

    assert report.word_mappings == ()
    assert report.findings[0].code == "multiple_greek_references"


def test_unique_reordered_surfaces_can_be_placed_without_row_order_guess() -> None:
    doc = parse_parallel_text(
        """Gen 1:1
HB1\tALFA
HB2\tBHTA
HB3\tGAMMA
""",
        source_name="01.Genesis.par",
    )
    provider = _provider(
        _span((401, "βητα"), (402, "αλφα"), (403, "γαμμα"))
    )

    report = resolve_lxx_document(doc, provider)

    assert report.summary.reordered_spans == 1
    assert [(m.lxx_node, m.mapping_kind) for m in report.word_mappings] == [
        (402, "reordered"),
        (401, "reordered"),
        (403, "reordered"),
    ]


def test_repeated_surface_in_reordered_span_fails_ambiguous() -> None:
    doc = parse_parallel_text(
        """Gen 1:1
HB1\tALFA
HB2\tBHTA
HB3\tALFA
""",
        source_name="01.Genesis.par",
    )
    provider = _provider(
        _span((501, "αλφα"), (502, "αλφα"), (503, "βητα"))
    )

    report = resolve_lxx_document(doc, provider)

    assert report.word_mappings == ()
    assert report.summary.ambiguous_spans == 1
    assert report.findings[0].code == "ambiguous_reordered_surface"


def test_lxx_minus_gets_span_anchor_not_neighbor_word() -> None:
    doc = parse_parallel_text(
        """Gen 1:1
HB1\tALFA
HB2\t--- ''
""",
        source_name="01.Genesis.par",
    )
    provider = _provider(_span((601, "αλφα"), node=9601))

    report = resolve_lxx_document(doc, provider)

    minus_id = doc.verses[0].alignments[1].alignment_id
    assert [(a.alignment_id, a.parent_node, a.kind) for a in report.span_anchors] == [
        (minus_id, 9601, "lxx_minus")
    ]
    assert all(mapping.alignment_id != minus_id for mapping in report.word_mappings)


def test_greek_correction_or_edition_alternative_blocks_alignment() -> None:
    for greek in ("LOGOS {cR(HMA}", "LOGOS {gR(HMA}"):
        doc = parse_parallel_text(
            f"Gen 1:1\nHB\\t{greek}\n",
            source_name="01.Genesis.par",
        )
        report = resolve_lxx_document(doc, _provider(_span((701, "λογος"))))

        assert report.word_mappings == ()
        assert report.findings[0].code == "greek_alternative_reading_unresolved"


def test_parent_schema_mismatch_blocks_all_mapping() -> None:
    doc = parse_parallel_text(
        """Gen 1:1
HB\tLOGOS
""",
        source_name="01.Genesis.par",
    )
    bad_probe = dataclasses.replace(_exact_probe(), version="future")
    provider = _provider(_span((801, "λογος")), probe=bad_probe)

    report = resolve_lxx_document(doc, provider)

    assert report.word_mappings == ()
    assert report.summary.parent_validation_failures == 1
    assert report.findings[0].code == "lxx_parent_schema_mismatch"


def test_missing_span_and_count_mismatch_are_explicit_and_no_partial_mapping() -> None:
    missing_doc = parse_parallel_text(
        """Gen 1:1
HB\tLOGOS
""",
        source_name="01.Genesis.par",
    )
    missing = resolve_lxx_document(missing_doc, _provider())
    assert missing.findings[0].code == "missing_lxx_span"

    count_doc = parse_parallel_text(
        """Gen 1:1
HB\tLOGOS ALLOS
""",
        source_name="01.Genesis.par",
    )
    count = resolve_lxx_document(count_doc, _provider(_span((901, "λογος"))))
    assert count.word_mappings == ()
    assert count.findings[0].code == "span_word_count_mismatch"


def test_surface_mismatch_emits_no_partial_target_span_mapping() -> None:
    doc = parse_parallel_text(
        """Gen 1:1
HB1\tLOGOS
HB2\tALLOS
""",
        source_name="01.Genesis.par",
    )
    provider = _provider(_span((1001, "λογος"), (1002, "ετερος")))

    report = resolve_lxx_document(doc, provider)

    assert report.word_mappings == ()
    assert report.findings[0].code == "span_surface_mismatch"


def test_declared_unsupported_source_is_coverage_skip() -> None:
    doc = parse_parallel_text(
        """JoshA 1:1
HB\tLOGOS
""",
        source_name="07.JoshA.par",
    )

    report = resolve_lxx_document(doc, _provider())

    assert report.summary.unsupported_documents == 1
    assert report.findings == ()


def test_unknown_source_is_finding() -> None:
    doc = parse_parallel_text(
        """Test 1:1
HB\tLOGOS
""",
        source_name="99.Unknown.par",
    )

    report = resolve_lxx_document(doc, _provider())

    assert report.summary.unknown_documents == 1
    assert report.findings[0].code == "unknown_catss_source"


def test_invalid_catss_document_cannot_emit_lxx_mappings() -> None:
    doc = parse_parallel_text(
        """Gen 1:1
HB {zzUNKNOWN}\tLOGOS
""",
        source_name="01.Genesis.par",
    )
    report = resolve_lxx_document(doc, _provider(_span((1101, "λογος"))))

    assert report.word_mappings == ()
    assert report.summary.catss_validation_failures == 1
    assert report.findings[0].code == "catss_validation_unknown_annotation"


def test_ps151_and_nehemiah_default_reference_transforms_are_used() -> None:
    ps = parse_parallel_text(
        """Ps151 1:1
HB\tALFA
""",
        source_name="22.Ps151.par",
    )
    nehemiah = parse_parallel_text(
        """Neh 1:1
HB\tBHTA
""",
        source_name="19.Neh.par",
    )
    provider = _provider(
        _span((1201, "αλφα"), book="Ps", chapter=151, verse=1, node=9701),
        _span((1202, "βητα"), book="2Esdr", chapter=11, verse=1, node=9702),
    )

    ps_report = resolve_lxx_document(ps, provider)
    neh_report = resolve_lxx_document(nehemiah, provider)

    assert ps_report.word_mappings[0].lxx_node == 1201
    assert neh_report.word_mappings[0].lxx_node == 1202
