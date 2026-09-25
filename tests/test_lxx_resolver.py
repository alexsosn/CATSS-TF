import dataclasses
import types

from catss_tf.lxx_resolver import (
    LxxSpan,
    LxxWord,
    TextFabricLxxProvider,
    normalize_catss_greek,
    normalize_lxx_greek,
    resolve_lxx_document,
    resolve_lxx_documents,
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
    LXX_SLOT_TYPE,
    LXX_VERSION,
    LxxParentProbe,
)
from catss_tf.parser import parse_parallel_text


def _probe() -> LxxParentProbe:
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


class FakeProvider:
    def __init__(
        self,
        spans: tuple[LxxSpan, ...],
        *,
        probe: LxxParentProbe | None = None,
    ) -> None:
        self.parent_probe = _probe() if probe is None else probe
        self._spans = {(span.book, span.chapter, span.verse, span.subverse): span for span in spans}

    def get_span(
        self,
        book: str,
        chapter: int,
        verse: int,
        subverse: str | None = None,
    ) -> LxxSpan | None:
        return self._spans.get((book, chapter, verse, subverse))


def _span(
    *words: str,
    book: str = "Gen",
    chapter: int = 1,
    verse: int = 1,
    subverse: str | None = None,
    node: int = 900001,
    start_node: int = 1,
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
                word=word,
                subverse="" if subverse is None else subverse,
                orig_order=str(start_node + index),
            )
            for index, word in enumerate(words)
        ),
    )


def test_greek_normalization_matches_catss_beta_to_parent_surface() -> None:
    assert normalize_catss_greek("E)N") == normalize_lxx_greek("ἐν")
    assert normalize_catss_greek("A)RXH=|") == normalize_lxx_greek("ἀρχῇ")
    assert normalize_catss_greek("E)POI/HSEN") == normalize_lxx_greek("ἐποίησεν")
    assert normalize_catss_greek("QEO\\S") == normalize_lxx_greek("θεὸς")
    assert normalize_catss_greek("KAI\\") == normalize_lxx_greek("καὶ")


def test_simple_alignment_rows_map_to_exact_parent_words() -> None:
    doc = parse_parallel_text(
        """Gen 1:1
HB1\tE)N A)RXH=|
HB2\tE)POI/HSEN
""",
        source_name="01.Genesis.par",
    )
    provider = FakeProvider((_span("ἐν", "ἀρχῇ", "ἐποίησεν"),))

    report = resolve_lxx_document(doc, provider)

    assert report.ok is True
    assert report.summary.resolved_reference_groups == 1
    assert report.summary.word_mappings == 3
    assert [(m.lxx_index, m.lxx_node) for m in report.word_mappings] == [
        (0, 1),
        (1, 2),
        (0, 3),
    ]


def test_joint_assignment_disambiguates_repeated_surface_by_non_overlap() -> None:
    doc = parse_parallel_text(
        """Gen 1:1
HB1\tKAI\\ LOGOS
HB2\tKAI\\
""",
        source_name="01.Genesis.par",
    )
    provider = FakeProvider((_span("καὶ", "λόγος", "καὶ"),))

    report = resolve_lxx_document(doc, provider)

    assert report.ok is True
    assert [(m.alignment_id, m.lxx_node) for m in report.word_mappings] == [
        (doc.verses[0].alignments[0].alignment_id, 1),
        (doc.verses[0].alignments[0].alignment_id, 2),
        (doc.verses[0].alignments[1].alignment_id, 3),
    ]


def test_repeated_surface_without_unique_joint_assignment_fails_closed() -> None:
    doc = parse_parallel_text(
        """Gen 1:1
HB1\tKAI\\
""",
        source_name="01.Genesis.par",
    )
    provider = FakeProvider((_span("καὶ", "λόγος", "καὶ"),))

    report = resolve_lxx_document(doc, provider)

    assert report.ok is False
    assert report.summary.ambiguous_reference_groups == 1
    assert report.word_mappings == ()
    assert report.findings[0].code == "surface_placement_ambiguous"


def test_explicit_greek_reference_overrides_mt_header_verse() -> None:
    doc = parse_parallel_text(
        """Gen 23:5
HB\tMH/ [6]
""",
        source_name="01.Genesis.par",
    )
    provider = FakeProvider(
        (
            _span("λέγοντες", book="Gen", chapter=23, verse=5, node=900005, start_node=50),
            _span("μή", book="Gen", chapter=23, verse=6, node=900006, start_node=60),
        )
    )

    report = resolve_lxx_document(doc, provider)

    assert report.ok is True
    assert report.summary.reference_overrides == 1
    assert report.word_mappings[0].lxx_node == 60
    assert report.word_mappings[0].reference_verse == 6


def test_explicit_chapter_verse_subverse_filters_esther_parent_span() -> None:
    doc = parse_parallel_text(
        """Esth 1:1
HB\tLOGOS [1:1a]
""",
        source_name="18.Esther.par",
    )
    provider = FakeProvider(
        (
            _span(
                "λόγος",
                book="Esth",
                chapter=1,
                verse=1,
                subverse="a",
                node=910001,
                start_node=100,
            ),
        )
    )

    report = resolve_lxx_document(doc, provider)

    assert report.ok is True
    mapping = report.word_mappings[0]
    assert mapping.reference_subverse == "a"
    assert mapping.lxx_node == 100


def test_psalm_151_default_reference_transform_is_applied() -> None:
    doc = parse_parallel_text(
        """Ps151 1
HB\tLOGOS
""",
        source_name="22.Ps151.par",
    )
    provider = FakeProvider(
        (_span("λόγος", book="Ps", chapter=151, verse=1, node=920001, start_node=200),)
    )

    report = resolve_lxx_document(doc, provider)

    assert report.ok is True
    assert report.word_mappings[0].reference_chapter == 151


def test_lxx_minus_gets_reference_anchor_not_neighbor_word() -> None:
    doc = parse_parallel_text(
        """Gen 1:1
HB\t--- ''
""",
        source_name="01.Genesis.par",
    )
    provider = FakeProvider((_span("λόγος", node=930001),))

    report = resolve_lxx_document(doc, provider)

    assert report.ok is True
    assert report.word_mappings == ()
    assert len(report.reference_anchors) == 1
    assert report.reference_anchors[0].kind == "lxx_minus"
    assert report.reference_anchors[0].lxx_reference_node == 930001


def test_empty_remote_transposition_placeholder_gets_anchor() -> None:
    doc = parse_parallel_text(
        """Gen 1:1
HB ^\t^^^
""",
        source_name="01.Genesis.par",
    )
    provider = FakeProvider((_span("λόγος", node=930002),))

    report = resolve_lxx_document(doc, provider)

    assert report.ok is True
    assert report.reference_anchors[0].kind == "transposition_placeholder"


def test_unexplained_empty_greek_row_is_finding() -> None:
    doc = parse_parallel_text(
        """Gen 1:1
HB\t
""",
        source_name="01.Genesis.par",
    )
    provider = FakeProvider((_span("λόγος"),))

    report = resolve_lxx_document(doc, provider)

    assert report.ok is False
    assert report.findings[0].code == "empty_lxx_alignment"


def test_missing_parent_reference_is_explicit() -> None:
    doc = parse_parallel_text(
        """Gen 1:1
HB\tLOGOS
""",
        source_name="01.Genesis.par",
    )
    provider = FakeProvider(())

    report = resolve_lxx_document(doc, provider)

    assert report.ok is False
    assert report.summary.missing_reference_groups == 1
    assert report.findings[0].code == "missing_lxx_reference"


def test_surface_sequence_not_found_is_explicit() -> None:
    doc = parse_parallel_text(
        """Gen 1:1
HB\tLOGOS
""",
        source_name="01.Genesis.par",
    )
    provider = FakeProvider((_span("θεός"),))

    report = resolve_lxx_document(doc, provider)

    assert report.ok is False
    assert report.summary.mismatched_reference_groups == 1
    assert report.findings[0].code == "surface_placement_missing"


def test_multiple_distinct_greek_references_on_one_alignment_fail() -> None:
    doc = parse_parallel_text(
        """Gen 1:1
HB\tLOGOS [2] [3]
""",
        source_name="01.Genesis.par",
    )
    provider = FakeProvider((_span("λόγος"),))

    report = resolve_lxx_document(doc, provider)

    assert report.ok is False
    assert report.findings[0].code == "multiple_lxx_references"


def test_unsupported_a_tradition_is_declared_without_mapping() -> None:
    doc = parse_parallel_text(
        """Josh 1:1
HB\tLOGOS
""",
        source_name="07.JoshA.par",
    )
    provider = FakeProvider(())

    report = resolve_lxx_document(doc, provider)

    assert report.ok is True
    assert report.summary.unsupported_documents == 1
    assert report.word_mappings == ()


def test_parent_version_mismatch_suppresses_all_mapping() -> None:
    doc = parse_parallel_text(
        """Gen 1:1
HB\tLOGOS
""",
        source_name="01.Genesis.par",
    )
    bad_probe = dataclasses.replace(_probe(), version="future")
    provider = FakeProvider((_span("λόγος"),), probe=bad_probe)

    report = resolve_lxx_document(doc, provider)

    assert report.ok is False
    assert report.summary.parent_failures == 1
    assert report.word_mappings == ()
    assert report.findings[0].code == "parent_version_mismatch"


def test_catss_validation_gate_suppresses_mapping() -> None:
    doc = parse_parallel_text(
        """Gen 1:1
HB {zzUNKNOWN}\tLOGOS
""",
        source_name="01.Genesis.par",
    )
    provider = FakeProvider((_span("λόγος"),))

    report = resolve_lxx_document(doc, provider)

    assert report.ok is False
    assert report.summary.validation_failures == 1
    assert report.word_mappings == ()
    assert report.findings[0].code == "catss_validation_unknown_annotation"


def test_unknown_greek_character_fails_closed() -> None:
    doc = parse_parallel_text(
        """Gen 1:1
HB\tLOGOS%
""",
        source_name="01.Genesis.par",
    )
    provider = FakeProvider((_span("λόγος"),))

    report = resolve_lxx_document(doc, provider)

    assert report.ok is False
    assert report.summary.normalization_errors == 1
    assert report.findings[0].code == "catss_greek_normalization_error"


def test_multi_document_audit_aggregates_same_resolver() -> None:
    first = parse_parallel_text(
        """Gen 1:1
HB\tLOGOS
""",
        source_name="01.Genesis.par",
    )
    second = parse_parallel_text(
        """Exod 1:1
HB\tQEOS
""",
        source_name="02.Exodus.par",
    )
    provider = FakeProvider(
        (
            _span("λόγος", book="Gen", chapter=1, verse=1, node=940001, start_node=300),
            _span("θεός", book="Exod", chapter=1, verse=1, node=940002, start_node=400),
        )
    )

    report = resolve_lxx_documents((first, second), provider)

    assert report.ok is True
    assert report.summary.documents == 2
    assert report.summary.supported_documents == 2
    assert report.summary.resolved_reference_groups == 2
    assert report.summary.word_mappings == 2


def test_canonical_and_lettered_subverse_groups_coexist_deterministically() -> None:
    doc = parse_parallel_text(
        """Esth 1:1
HB1\tLOGOS
HB2\tQEOS [1:1a]
""",
        source_name="18.Esther.par",
    )
    provider = FakeProvider(
        (
            _span(
                "λόγος",
                book="Esth",
                chapter=1,
                verse=1,
                subverse=None,
                node=950001,
                start_node=500,
            ),
            _span(
                "θεός",
                book="Esth",
                chapter=1,
                verse=1,
                subverse="a",
                node=950002,
                start_node=600,
            ),
        )
    )

    report = resolve_lxx_document(doc, provider)

    assert report.ok is True
    assert report.summary.resolved_reference_groups == 2
    assert [mapping.lxx_node for mapping in report.word_mappings] == [500, 600]


def test_text_fabric_provider_excludes_lettered_subverses_from_canonical_span() -> None:
    class Feature:
        def __init__(self, values: dict[int, object]) -> None:
            self.values = values

        def v(self, node: int) -> object:
            return self.values[node]

    api = types.SimpleNamespace(
        T=types.SimpleNamespace(nodeFromSection=lambda section: 900001),
        L=types.SimpleNamespace(
            d=lambda node, otype: (1, 2, 3),
            u=lambda node, otype: (910001,) if node == 2 else (910002,),
        ),
        F=types.SimpleNamespace(
            word=Feature({1: "λόγος", 2: "θεός", 3: "καί"}),
            subverse=Feature({1: "", 2: "a", 3: ""}),
            orig_order=Feature({1: "1", 2: "2", 3: "3"}),
        ),
    )
    provider = TextFabricLxxProvider(api, _probe())

    canonical = provider.get_span("Esth", 1, 1)
    addition = provider.get_span("Esth", 1, 1, "a")

    assert canonical is not None
    assert [word.node for word in canonical.words] == [1, 3]
    assert canonical.node == 900001
    assert addition is not None
    assert [word.node for word in addition.words] == [2]
    assert addition.node == 910001


def test_stylistic_transposition_proxy_and_carrier_may_share_parent_words() -> None:
    doc = parse_parallel_text(
        """Gen 1:29
ZR(\t{..^SPORI/MOU}
ZR(\tSPE/RMATOS
{...}\tSPORI/MOU
L/KM\tU(MI=N
""",
        source_name="01.Genesis.par",
    )
    provider = FakeProvider((_span("σπέρματος", "σπορίμου", "ὑμῖν", chapter=1, verse=29),))

    report = resolve_lxx_document(doc, provider)

    assert report.ok is True
    assert [(mapping.lxx_node, mapping.mapping_kind) for mapping in report.word_mappings] == [
        (2, "transposition_alignment"),
        (1, "exact"),
        (2, "transposition_carrier"),
        (3, "exact"),
    ]


def test_unmarked_duplicate_rows_cannot_share_one_parent_word() -> None:
    doc = parse_parallel_text(
        """Gen 1:1
HB1\tLOGOS
HB2\tLOGOS
""",
        source_name="01.Genesis.par",
    )
    provider = FakeProvider((_span("λόγος"),))

    report = resolve_lxx_document(doc, provider)

    assert report.ok is False
    assert report.word_mappings == ()
    assert report.findings[0].code == "surface_placement_conflict"


def test_equivalent_relative_and_explicit_greek_references_are_deduplicated() -> None:
    doc = parse_parallel_text(
        """Gen 23:5
HB\tMH/ [6] [[23:6]]
""",
        source_name="01.Genesis.par",
    )
    provider = FakeProvider(
        (_span("μή", book="Gen", chapter=23, verse=6, node=960006, start_node=700),)
    )

    report = resolve_lxx_document(doc, provider)

    assert report.ok is True
    assert report.summary.reference_overrides == 1
    assert report.word_mappings[0].lxx_node == 700
