"""A matched Greek word is a candidate, not a verified CATSS reference target."""

import dataclasses
import tracemalloc

import pytest

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
from catss_tf.parser import parse_parallel_text
from catss_tf.reference_surface_audit import (
    _classify_joint_intervals,
    audit_lxx_reference_surface_candidates,
)


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


def _span(book: str, chapter: int, verse: int, *texts: str, subverse: str | None = None) -> LxxSpan:
    return LxxSpan(
        node=800000 + verse,
        book=book,
        chapter=chapter,
        verse=verse,
        subverse=subverse,
        words=tuple(
            LxxWord(node=1000 + i, word=word, subverse=subverse or "", orig_order=str(i))
            for i, word in enumerate(texts, start=1)
        ),
    )


class Provider:
    def __init__(self, spans: tuple[LxxSpan, ...], probe: LxxParentProbe | None = None):
        self.parent_probe = _probe() if probe is None else probe
        self.spans = {(s.book, s.chapter, s.verse, s.subverse): s for s in spans}
        self.calls: list[tuple[str, int, int, str | None]] = []

    def get_span(
        self, book: str, chapter: int, verse: int, subverse: str | None = None
    ) -> LxxSpan | None:
        key = (book, chapter, verse, subverse)
        self.calls.append(key)
        return self.spans.get(key)


def test_surface_reference_triage_never_confuses_local_candidate_with_target() -> None:
    documents = (
        parse_parallel_text(
            "Gen 1:1\nHB\tLOGOS [2] [3] [4] [5] [6]\nHB\t[7]\n",
            source_name="01.Genesis.par",
        ),
        parse_parallel_text("JoshA 1:1\nHB\tLOGOS [2]\n", source_name="07.JoshA.par"),
        parse_parallel_text("Gen 1:1\nHB\tLOGOS [2]\n", source_name="99.Unknown.par"),
    )
    provider = Provider(
        (
            _span("Gen", 1, 2, "λόγος"),
            _span("Gen", 1, 3, "λόγος", "λόγος"),
            _span("Gen", 1, 4, "ἀνήρ"),
            _span("Gen", 1, 6, "☃"),
            _span("Gen", 1, 7, "λόγος"),
        )
    )
    report = audit_lxx_reference_surface_candidates(documents, provider)
    assert report.source_files == 3
    assert report.scalar_references == 8
    assert report.exact_single == 1
    assert report.exact_multiple == 1
    assert report.no_surface_match == 1
    assert report.no_greek_tokens == 1
    assert report.catss_normalization_error == 0
    assert report.parent_normalization_error == 1
    assert report.parent_span_missing == 1
    assert report.unsupported_source == 1
    assert report.unknown_source == 1
    assert len(provider.calls) == 6
    assert ("Gen", 1, 2, None) in provider.calls


def test_parent_fingerprint_mismatch_rejected_before_looking_up_words() -> None:
    document = parse_parallel_text("Gen 1:1\nHB\tLOGOS [2]\n", source_name="01.Genesis.par")
    provider = Provider(
        (_span("Gen", 1, 2, "λόγος"),),
        dataclasses.replace(_probe(), release_commit="wrong"),
    )
    with pytest.raises(ValueError, match="parent"):
        audit_lxx_reference_surface_candidates((document,), provider)
    assert provider.calls == []


def test_forged_subverse_parent_span_cannot_be_counted_as_surface_match() -> None:
    document = parse_parallel_text("JoshB 9:2\nHB\tLOGOS [9:2a]\n", source_name="06.JoshB.par")

    class AliasProvider(Provider):
        def get_span(
            self, book: str, chapter: int, verse: int, subverse: str | None = None
        ) -> LxxSpan | None:
            self.calls.append((book, chapter, verse, subverse))
            return _span(book, chapter, verse, "λόγος")

    with pytest.raises(ValueError, match="span"):
        audit_lxx_reference_surface_candidates((document,), AliasProvider(()))


def test_unique_candidates_compete_when_distinct_alignments_claim_same_word() -> None:
    doc = parse_parallel_text(
        "Gen 1:1\nHB\tLOGOS [2]\nHB\tLOGOS [2]\n",
        source_name="01.Genesis.par",
    )
    result = audit_lxx_reference_surface_candidates(
        (doc,), Provider((_span("Gen", 1, 2, "λόγος"),))
    )
    assert result.exact_single == 2
    assert result.exact_single_with_overlap == 2
    assert result.exact_single_without_overlap == 0


def test_unique_candidate_competes_with_another_alignments_ambiguous_alternatives() -> None:
    doc = parse_parallel_text(
        "Gen 1:1\nHB\tLOGOS KAI LOGOS [2]\nHB\tLOGOS [2]\n",
        source_name="01.Genesis.par",
    )
    result = audit_lxx_reference_surface_candidates(
        (doc,), Provider((_span("Gen", 1, 2, "λόγος", "καί", "λόγος"),))
    )
    assert result.exact_single == 1
    assert result.exact_multiple == 1
    assert result.exact_single_with_overlap == 1
    assert result.exact_single_without_overlap == 0


def test_adjacent_word_intervals_do_not_count_as_competing() -> None:
    doc = parse_parallel_text(
        "Gen 1:1\nHB\tLOGOS [2]\nHB\tKAI [2]\n",
        source_name="01.Genesis.par",
    )
    result = audit_lxx_reference_surface_candidates(
        (doc,), Provider((_span("Gen", 1, 2, "λόγος", "καί"),))
    )
    assert result.exact_single == 2
    assert result.exact_single_with_overlap == 0
    assert result.exact_single_without_overlap == 2


def test_repeated_scalar_refs_in_one_alignment_do_not_compete_with_themselves() -> None:
    doc = parse_parallel_text(
        "Gen 1:1\nHB\tLOGOS [2] [2]\n",
        source_name="01.Genesis.par",
    )
    result = audit_lxx_reference_surface_candidates(
        (doc,), Provider((_span("Gen", 1, 2, "λόγος"),))
    )
    assert result.scalar_references == 2
    assert result.exact_single == 2
    assert result.exact_single_with_overlap == 0
    assert result.exact_single_without_overlap == 2


def test_distinct_catss_source_traditions_do_not_compete_even_for_same_parent_key() -> None:
    docs = (
        parse_parallel_text(
            "Ezra 1:1\nHB\tLOGOS [11:2]\n",
            source_name="18.Ezra.par",
        ),
        parse_parallel_text(
            "Neh 1:1\nHB\tLOGOS [2]\n",
            source_name="19.Neh.par",
        ),
    )
    result = audit_lxx_reference_surface_candidates(
        docs, Provider((_span("2Esdr", 11, 2, "λόγος"),))
    )
    assert result.exact_single == 2
    assert result.exact_single_with_overlap == 0
    assert result.exact_single_without_overlap == 2


def test_pairwise_overlap_is_unavoidable_when_two_unique_candidates_collide() -> None:
    document = parse_parallel_text(
        "Gen 1:1\nHB\tLOGOS [2]\nHB\tLOGOS [2]\n",
        source_name="01.Genesis.par",
    )
    report = audit_lxx_reference_surface_candidates(
        (document,), Provider((_span("Gen", 1, 2, "λόγος"),))
    )
    assert report.exact_single_with_overlap == 2
    assert report.exact_single_with_unavoidable_overlap == 2
    assert report.exact_single_with_avoidable_overlap_only == 0


def test_pairwise_overlap_can_be_avoided_by_ambiguous_competitors_alternative() -> None:
    document = parse_parallel_text(
        "Gen 1:1\nHB\tLOGOS KAI [2]\nHB\tLOGOS [2]\n",
        source_name="01.Genesis.par",
    )
    report = audit_lxx_reference_surface_candidates(
        (document,), Provider((_span("Gen", 1, 2, "λόγος", "καί", "λόγος"),))
    )
    assert report.exact_single == 1
    assert report.exact_multiple == 1
    assert report.exact_single_with_overlap == 1
    assert report.exact_single_with_unavoidable_overlap == 0
    assert report.exact_single_with_avoidable_overlap_only == 1


def test_all_ambiguous_competitor_alternatives_can_intersect_one_unique_span() -> None:
    document = parse_parallel_text(
        "Gen 1:1\nHB\tLOGOS KAI LOGOS [2]\nHB\tLOGOS [2]\n",
        source_name="01.Genesis.par",
    )
    report = audit_lxx_reference_surface_candidates(
        (document,), Provider((_span("Gen", 1, 2, "λόγος", "καί", "λόγος"),))
    )
    assert report.exact_single_with_overlap == 1
    assert report.exact_single_with_unavoidable_overlap == 1
    assert report.exact_single_with_avoidable_overlap_only == 0


def test_an_unavoidable_competitor_wins_over_other_avoidable_overlap() -> None:
    document = parse_parallel_text(
        "Gen 1:1\nHB\tLOGOS KAI [2]\nHB\tLOGOS [2]\nHB\tKAI [2]\n",
        source_name="01.Genesis.par",
    )
    report = audit_lxx_reference_surface_candidates(
        (document,), Provider((_span("Gen", 1, 2, "λόγος", "καί", "λόγος"),))
    )
    assert report.exact_single == 2
    assert report.exact_single_with_overlap == 2
    assert report.exact_single_with_unavoidable_overlap == 2
    assert report.exact_single_with_avoidable_overlap_only == 0


def test_repeated_scalar_references_are_counted_without_self_collision() -> None:
    document = parse_parallel_text(
        "Gen 1:1\nHB\tLOGOS [2] [2]\n",
        source_name="01.Genesis.par",
    )
    report = audit_lxx_reference_surface_candidates(
        (document,), Provider((_span("Gen", 1, 2, "λόγος"),))
    )
    assert report.exact_single == 2
    assert report.exact_single_with_overlap == 0
    assert report.exact_single_with_unavoidable_overlap == 0
    assert report.exact_single_with_avoidable_overlap_only == 0


def test_joint_reference_candidates_distinguish_unique_and_impossible_groups() -> None:
    unique = parse_parallel_text(
        "Gen 1:1\nHB\tLOGOS [2]\nHB\tKAI [2]\n",
        source_name="01.Genesis.par",
    )
    impossible = parse_parallel_text(
        "Gen 1:1\nHB\tLOGOS [2]\nHB\tLOGOS [2]\n",
        source_name="01.Genesis.par",
    )
    provider = Provider((_span("Gen", 1, 2, "λόγος", "καί"),))
    unique_report = audit_lxx_reference_surface_candidates((unique,), provider)
    assert unique_report.reference_groups == 1
    assert unique_report.joint_unique_groups == 1
    assert unique_report.joint_impossible_groups == 0
    impossible_report = audit_lxx_reference_surface_candidates(
        (impossible,), Provider((_span("Gen", 1, 2, "λόγος"),))
    )
    assert impossible_report.reference_groups == 1
    assert impossible_report.joint_impossible_groups == 1
    assert impossible_report.joint_unique_groups == 0


def test_joint_group_with_locally_ambiguous_word_is_not_falsely_unique() -> None:
    document = parse_parallel_text(
        "Gen 1:1\nHB\tLOGOS [2]\n",
        source_name="01.Genesis.par",
    )
    report = audit_lxx_reference_surface_candidates(
        (document,), Provider((_span("Gen", 1, 2, "λόγος", "λόγος"),))
    )
    assert report.reference_groups == 1
    assert report.joint_multiple_groups == 1
    assert report.joint_unique_groups == 0


def test_joint_group_with_missing_surface_candidate_is_incomplete_not_impossible() -> None:
    document = parse_parallel_text(
        "Gen 1:1\nHB\tLOGOS [2]\nHB\tKAI [2]\n",
        source_name="01.Genesis.par",
    )
    report = audit_lxx_reference_surface_candidates(
        (document,), Provider((_span("Gen", 1, 2, "λόγος"),))
    )
    assert report.reference_groups == 1
    assert report.joint_incomplete_groups == 1
    assert report.joint_impossible_groups == 0
    assert report.joint_unique_groups == 0


def test_joint_duplicate_scalar_reference_is_one_alignment_task() -> None:
    document = parse_parallel_text(
        "Gen 1:1\nHB\tLOGOS [2] [2]\n",
        source_name="01.Genesis.par",
    )
    report = audit_lxx_reference_surface_candidates(
        (document,), Provider((_span("Gen", 1, 2, "λόγος"),))
    )
    assert report.scalar_references == 2
    assert report.reference_groups == 1
    assert report.joint_unique_groups == 1


def test_joint_groups_isolate_distinct_catss_sources_sharing_parent_key() -> None:
    documents = (
        parse_parallel_text("Ezra 1:1\nHB\tLOGOS [11:2]\n", source_name="18.Ezra.par"),
        parse_parallel_text("Neh 1:1\nHB\tLOGOS [2]\n", source_name="19.Neh.par"),
    )
    report = audit_lxx_reference_surface_candidates(
        documents, Provider((_span("2Esdr", 11, 2, "λόγος"),))
    )
    assert report.reference_groups == 2
    assert report.joint_unique_groups == 2
    assert report.joint_impossible_groups == 0


def test_joint_solver_detects_globally_impossible_despite_all_pairwise_choices() -> None:
    # Every pair can occupy two separate words, but three distinct tasks
    # cannot all fit into two word slots.
    tasks = {
        "a": {(0, 1), (1, 2)},
        "b": {(0, 1), (1, 2)},
        "c": {(0, 1), (1, 2)},
    }
    assert _classify_joint_intervals(tasks) == "impossible"


def test_joint_search_budget_must_not_forge_unique_or_impossible() -> None:
    task = {"a": {(0, 1), (1, 2)}}
    assert _classify_joint_intervals(task, max_states=2) == "indeterminate"
    assert _classify_joint_intervals(task, max_states=3) == "multiple"
    unique = {"a": {(0, 1)}}
    assert _classify_joint_intervals(unique, max_states=1) == "indeterminate"
    assert _classify_joint_intervals(unique, max_states=2) == "unique"
    assert _classify_joint_intervals({"a": {(0, 1)}, "b": {(0, 1)}}) == "impossible"


def test_duplicate_catss_source_name_with_distinct_content_fails_closed() -> None:
    documents = (
        parse_parallel_text(
            "Gen 1:1\nHB\tLOGOS [2]\n",
            source_name="01.Genesis.par",
        ),
        parse_parallel_text(
            "Gen 1:1\nHB\tKAI [2]\n",
            source_name="01.Genesis.par",
        ),
    )
    provider = Provider((_span("Gen", 1, 2, "λόγος", "καί"),))
    with pytest.raises(ValueError, match="duplicate CATSS source name.*01.Genesis.par"):
        audit_lxx_reference_surface_candidates(documents, provider)
    # The first document is inspected, but the duplicate cannot be consumed.
    assert provider.calls == [("Gen", 1, 2, None)]


def test_duplicate_catss_source_name_in_generator_is_not_deduplicated() -> None:
    document = parse_parallel_text(
        "Gen 1:1\nHB\tLOGOS [2]\n",
        source_name="01.Genesis.par",
    )
    provider = Provider((_span("Gen", 1, 2, "λόγος"),))
    with pytest.raises(ValueError, match="duplicate CATSS source name"):
        audit_lxx_reference_surface_candidates((doc for doc in (document, document)), provider)
    assert provider.calls == [("Gen", 1, 2, None)]


def test_duplicate_empty_catss_documents_are_ambiguous_provenance() -> None:
    document = parse_parallel_text("", source_name="01.Genesis.par")
    provider = Provider(())
    with pytest.raises(ValueError, match="duplicate CATSS source name"):
        audit_lxx_reference_surface_candidates((document, document), provider)
    assert provider.calls == []


def test_joint_dfs_frontier_is_memory_bounded_before_state_cutoff() -> None:
    # The original eager pending stack allocated one selected-prefix tuple
    # for each of 80,000 siblings, despite a one-state search budget.
    task = {"one": {(i, i + 1) for i in range(80_000)}}
    tracemalloc.start()
    try:
        result = _classify_joint_intervals(task, max_states=1)
        _current, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    assert result == "indeterminate"
    assert peak < 4_000_000, f"excess DFS frontier allocation: {peak} bytes"


@pytest.mark.parametrize(
    ("tasks", "budget", "expected"),
    [
        ({"a": {(0, 1)}, "b": {(1, 2)}}, 3, "unique"),
        ({"a": {(0, 1)}, "b": {(0, 1)}}, 2, "impossible"),
        ({"a": {(0, 2)}, "b": {(1, 3), (2, 3)}}, 3, "unique"),
        ({"a": {(0, 1), (1, 2)}, "b": {(2, 3)}}, 3, "indeterminate"),
        ({"a": {(0, 1), (1, 2)}, "b": {(2, 3)}}, 4, "multiple"),
        ({"a": {(0, 1), (1, 2)}, "b": {(2, 3)}}, 5, "multiple"),
        ({"a": {(0, 1), (1, 2)}, "b": {(0, 1), (1, 2)}, "c": {(0, 1), (1, 2)}}, 100, "impossible"),
    ],
)
def test_joint_dfs_iterative_semantics_match_depth_first_oracle(
    tasks: dict[str, set[tuple[int, int]]], budget: int, expected: str
) -> None:
    assert _classify_joint_intervals(tasks, max_states=budget) == expected


def test_joint_dfs_long_chain_avoids_recursion_and_clone_of_selected_prefix() -> None:
    tasks = {f"a{i:04d}": {(2 * i, 2 * i + 1)} for i in range(1_200)}
    assert _classify_joint_intervals(tasks, max_states=1_201) == "unique"


def test_explicit_unique_group_becomes_context_impossible_when_implicit_row_collides() -> None:
    document = parse_parallel_text(
        "Gen 1:1\nHB\tLOGOS [1]\nHB\tLOGOS\n",
        source_name="01.Genesis.par",
    )
    result = audit_lxx_reference_surface_candidates(
        (document,), Provider((_span("Gen", 1, 1, "λόγος"),))
    )
    assert result.scalar_references == 1
    assert result.reference_groups == 1
    assert result.joint_unique_groups == 1
    assert result.context_groups_with_implicit == 1
    assert result.context_impossible_groups == 1
    assert result.context_unique_groups == 0


def test_implicit_disjoint_row_preserves_context_unique_group() -> None:
    document = parse_parallel_text(
        "Gen 1:1\nHB\tLOGOS [1]\nHB\tKAI\n",
        source_name="01.Genesis.par",
    )
    result = audit_lxx_reference_surface_candidates(
        (document,), Provider((_span("Gen", 1, 1, "λόγος", "καί"),))
    )
    assert result.joint_unique_groups == 1
    assert result.context_groups_with_implicit == 1
    assert result.context_unique_groups == 1
    assert result.context_impossible_groups == 0


def test_implicit_nonmatching_lexical_row_makes_context_incomplete_not_impossible() -> None:
    document = parse_parallel_text(
        "Gen 1:1\nHB\tLOGOS [1]\nHB\tANHR\n",
        source_name="01.Genesis.par",
    )
    result = audit_lxx_reference_surface_candidates(
        (document,), Provider((_span("Gen", 1, 1, "λόγος"),))
    )
    assert result.joint_unique_groups == 1
    assert result.context_groups_with_implicit == 1
    assert result.context_incomplete_groups == 1
    assert result.context_impossible_groups == 0


def test_implicit_ambiguous_row_can_create_multiple_context_placements() -> None:
    document = parse_parallel_text(
        "Gen 1:1\nHB\tLOGOS [1]\nHB\tKAI\n",
        source_name="01.Genesis.par",
    )
    result = audit_lxx_reference_surface_candidates(
        (document,), Provider((_span("Gen", 1, 1, "λόγος", "καί", "καί"),))
    )
    assert result.joint_unique_groups == 1
    assert result.context_groups_with_implicit == 1
    assert result.context_multiple_groups == 1


def test_implicit_default_rows_do_not_compete_with_explicit_override_to_other_verse() -> None:
    document = parse_parallel_text(
        "Gen 1:1\nHB\tLOGOS [2]\nHB\tLOGOS\n",
        source_name="01.Genesis.par",
    )
    result = audit_lxx_reference_surface_candidates(
        (document,), Provider((_span("Gen", 1, 2, "λόγος"),))
    )
    assert result.scalar_references == 1
    assert result.joint_unique_groups == 1
    assert result.context_groups_with_implicit == 0
    assert result.context_unique_groups == 1
    assert result.context_incomplete_groups == 0
