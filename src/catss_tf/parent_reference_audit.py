"""Fail-closed exact Greek-parent span existence diagnostics, not target mapping."""

import dataclasses
import typing

from catss_tf.lxx_resolver import LxxSpan, LxxVerseProvider
from catss_tf.lxx_schema import (
    LxxSourceStatus,
    classify_catss_source,
    default_lxx_reference,
    validate_lxx_parent,
)
from catss_tf.parser import ParallelDocument


@dataclasses.dataclass(frozen=True, slots=True)
class LxxParentSpanAvailability:
    """Counts of exact parent span existence, not CATSS↔LXX correspondences."""

    source_files: int
    scalar_references: int
    parent_span_present: int
    parent_span_missing: int
    unsupported_source: int
    unknown_source: int
    subverse_suffixes: int
    subverse_present: int
    subverse_missing: int
    subverse_unprofiled: int


def audit_lxx_parent_span_availability(
    documents: typing.Iterable[ParallelDocument],
    provider: LxxVerseProvider,
) -> LxxParentSpanAvailability:
    """Count exact pinned-parent span existence, not CATSS textual matches."""
    validation = validate_lxx_parent(provider.parent_probe)
    if not validation.ok:
        raise ValueError(f"invalid LXX parent fingerprint: {validation.findings}")

    source_files = 0
    scalar_references = 0
    present = 0
    missing = 0
    unsupported = 0
    unknown = 0
    subverse_suffixes = 0
    subverse_present = 0
    subverse_missing = 0
    subverse_unprofiled = 0
    cache: dict[tuple[str, int, int, str | None], LxxSpan | None] = {}

    for document in documents:
        source_files += 1
        profile = classify_catss_source(document.source_name)
        for verse in document.verses:
            for alignment in verse.alignments:
                for reference in alignment.lxx_references:
                    scalar_references += 1
                    lettered = reference.subverse is not None
                    if lettered:
                        subverse_suffixes += 1

                    if profile.status is LxxSourceStatus.UNSUPPORTED:
                        unsupported += 1
                        if lettered:
                            subverse_unprofiled += 1
                        continue
                    if profile.status is LxxSourceStatus.UNKNOWN:
                        unknown += 1
                        if lettered:
                            subverse_unprofiled += 1
                        continue

                    # Default parent policy is source-dependent, e.g. Neh is
                    # located in 2Esdr chapter+10. An explicitly supplied
                    # Greek reference chapter overrides the policy's chapter.
                    default = default_lxx_reference(
                        document.source_name, verse.chapter, verse.verse
                    )
                    key = (
                        default.book,
                        default.chapter if reference.chapter is None else reference.chapter,
                        reference.verse,
                        reference.subverse,
                    )
                    if key not in cache:
                        span = provider.get_span(*key)
                        if span is not None and (
                            (span.book, span.chapter, span.verse, span.subverse) != key
                        ):
                            raise ValueError(
                                f"LXX parent span identity mismatch for {key}"
                            )
                        cache[key] = span
                    span = cache[key]
                    if span is not None and span.words:
                        present += 1
                        if lettered:
                            subverse_present += 1
                    else:
                        missing += 1
                        if lettered:
                            subverse_missing += 1

    assert scalar_references == present + missing + unsupported + unknown
    assert subverse_suffixes == subverse_present + subverse_missing + subverse_unprofiled
    return LxxParentSpanAvailability(
        source_files=source_files,
        scalar_references=scalar_references,
        parent_span_present=present,
        parent_span_missing=missing,
        unsupported_source=unsupported,
        unknown_source=unknown,
        subverse_suffixes=subverse_suffixes,
        subverse_present=subverse_present,
        subverse_missing=subverse_missing,
        subverse_unprofiled=subverse_unprofiled,
    )
