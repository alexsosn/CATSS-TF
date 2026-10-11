"""Read-only CATSS Greek reference surface-candidate diagnostics."""

import dataclasses
import typing

from catss_tf.lxx_resolver import (
    LxxSpan,
    LxxVerseProvider,
    normalize_catss_greek,
    normalize_lxx_greek,
)
from catss_tf.lxx_schema import (
    LxxSourceStatus,
    classify_catss_source,
    default_lxx_reference,
    validate_lxx_parent,
)
from catss_tf.parser import ParallelDocument

_CandidateScope: typing.TypeAlias = tuple[str, str, int, int, str | None]


@dataclasses.dataclass(frozen=True, slots=True)
class LxxReferenceSurfaceCandidates:
    """Per-scalar-reference evidence; no verified lexical or TF target mappings."""

    source_files: int
    scalar_references: int
    exact_single: int
    exact_single_with_overlap: int
    exact_single_without_overlap: int
    exact_multiple: int
    no_surface_match: int
    no_greek_tokens: int
    catss_normalization_error: int
    parent_normalization_error: int
    parent_span_missing: int
    unsupported_source: int
    unknown_source: int


def audit_lxx_reference_surface_candidates(
    documents: typing.Iterable[ParallelDocument],
    provider: LxxVerseProvider,
) -> LxxReferenceSurfaceCandidates:
    """Count textual candidates without asserting their relation is a mapping."""
    validation = validate_lxx_parent(provider.parent_probe)
    if not validation.ok:
        raise ValueError(f"invalid LXX parent fingerprint: {validation.findings}")

    counts: dict[str, int] = {
        "source_files": 0,
        "scalar_references": 0,
        "exact_single": 0,
        "exact_multiple": 0,
        "no_surface_match": 0,
        "no_greek_tokens": 0,
        "catss_normalization_error": 0,
        "parent_normalization_error": 0,
        "parent_span_missing": 0,
        "unsupported_source": 0,
        "unknown_source": 0,
    }
    span_cache: dict[tuple[str, int, int, str | None], LxxSpan | None] = {}
    token_cache: dict[tuple[str, int, int, str | None], tuple[str, ...] | None] = {}
    # Only offsets, not Greek text or parent node IDs, are retained. A candidate
    # with one local occurrence may still overlap a different alignment's
    # candidate (including ambiguous alternative occurrences).
    candidate_intervals: dict[_CandidateScope, dict[str, set[tuple[int, int]]]] = {}
    single_candidates: list[tuple[_CandidateScope, str, tuple[int, int]]] = []

    for document in documents:
        counts["source_files"] += 1
        status = classify_catss_source(document.source_name).status
        for verse in document.verses:
            for alignment in verse.alignments:
                for reference in alignment.lxx_references:
                    counts["scalar_references"] += 1
                    if status is LxxSourceStatus.UNSUPPORTED:
                        counts["unsupported_source"] += 1
                        continue
                    if status is LxxSourceStatus.UNKNOWN:
                        counts["unknown_source"] += 1
                        continue

                    default = default_lxx_reference(
                        document.source_name, verse.chapter, verse.verse
                    )
                    key = (
                        default.book,
                        default.chapter if reference.chapter is None else reference.chapter,
                        reference.verse,
                        reference.subverse,
                    )
                    if key not in span_cache:
                        span = provider.get_span(*key)
                        if span is not None:
                            if (span.book, span.chapter, span.verse, span.subverse) != key:
                                raise ValueError(f"LXX parent span identity mismatch for {key}")
                            if any(word.subverse != (key[3] or "") for word in span.words):
                                raise ValueError(f"LXX span word subverse mismatch for {key}")
                        span_cache[key] = span
                    span = span_cache[key]
                    if span is None or not span.words:
                        counts["parent_span_missing"] += 1
                        continue
                    if not alignment.lxx_tokens:
                        counts["no_greek_tokens"] += 1
                        continue

                    try:
                        needle = tuple(
                            normalize_catss_greek(token) for token in alignment.lxx_tokens
                        )
                    except ValueError:
                        counts["catss_normalization_error"] += 1
                        continue
                    if key not in token_cache:
                        try:
                            token_cache[key] = tuple(
                                normalize_lxx_greek(word.word) for word in span.words
                            )
                        except ValueError:
                            token_cache[key] = None
                    haystack = token_cache[key]
                    if haystack is None:
                        counts["parent_normalization_error"] += 1
                        continue
                    n = len(needle)
                    matches = tuple(
                        (i, i + n)
                        for i in range(len(haystack) - n + 1)
                        if haystack[i : i + n] == needle
                    )
                    if not matches:
                        counts["no_surface_match"] += 1
                        continue
                    scope = (document.source_name, *key)
                    candidate_intervals.setdefault(scope, {}).setdefault(
                        alignment.alignment_id, set()
                    ).update(matches)
                    if len(matches) == 1:
                        counts["exact_single"] += 1
                        single_candidates.append((scope, alignment.alignment_id, matches[0]))
                    else:
                        counts["exact_multiple"] += 1

    with_overlap = 0
    for scope, alignment_id, (start, stop) in single_candidates:
        competitors = candidate_intervals[scope]
        if any(
            competing_id != alignment_id and other_start < stop and start < other_stop
            for competing_id, intervals in competitors.items()
            for other_start, other_stop in intervals
        ):
            with_overlap += 1
    without_overlap = len(single_candidates) - with_overlap
    assert counts["exact_single"] == with_overlap + without_overlap

    assert counts["scalar_references"] == sum(
        value for name, value in counts.items() if name not in {"source_files", "scalar_references"}
    )
    return LxxReferenceSurfaceCandidates(
        source_files=counts["source_files"],
        scalar_references=counts["scalar_references"],
        exact_single=counts["exact_single"],
        exact_single_with_overlap=with_overlap,
        exact_single_without_overlap=without_overlap,
        exact_multiple=counts["exact_multiple"],
        no_surface_match=counts["no_surface_match"],
        no_greek_tokens=counts["no_greek_tokens"],
        catss_normalization_error=counts["catss_normalization_error"],
        parent_normalization_error=counts["parent_normalization_error"],
        parent_span_missing=counts["parent_span_missing"],
        unsupported_source=counts["unsupported_source"],
        unknown_source=counts["unknown_source"],
    )
