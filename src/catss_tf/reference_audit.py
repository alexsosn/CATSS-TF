"""Read-only diagnostic counts for CATSS Greek scalar-reference notation."""

import dataclasses
import typing

from catss_tf.parser import ParallelDocument


@dataclasses.dataclass(frozen=True, slots=True)
class GreekReferenceAudit:
    """Numeric MT-header candidates are never verified LXX destinations."""

    source_files: int
    scalar_references: int
    explicit_chapters: int
    subverse_suffixes: int
    numeric_candidates_zero: int
    numeric_candidates_one: int
    numeric_candidates_multiple: int
    same_header_numeric: int
    different_verse_same_chapter: int
    different_chapter: int
    by_source: tuple[tuple[str, int], ...]


def audit_greek_references(
    documents: typing.Iterable[ParallelDocument],
) -> GreekReferenceAudit:
    """Count numeric MT-header coincidences, *not* proven Greek destinations."""
    sources = 0
    scalar = 0
    explicit = 0
    suffix = 0
    zero = 0
    one = 0
    multiple = 0
    same_header_numeric = 0
    different_verse_same_chapter = 0
    different_chapter = 0
    by_source: dict[str, int] = {}

    for document in documents:
        sources += 1
        header_counts: dict[tuple[int, int], int] = {}
        for verse in document.verses:
            key = (verse.chapter, verse.verse)
            header_counts[key] = header_counts.get(key, 0) + 1

        for verse in document.verses:
            for alignment in verse.alignments:
                for reference in alignment.lxx_references:
                    scalar += 1
                    if reference.chapter is not None:
                        explicit += 1
                    if reference.subverse is not None:
                        suffix += 1
                    by_source[document.source_name] = by_source.get(document.source_name, 0) + 1
                    effective_chapter = (
                        reference.chapter if reference.chapter is not None else verse.chapter
                    )
                    if effective_chapter != verse.chapter:
                        different_chapter += 1
                    elif reference.verse != verse.verse:
                        different_verse_same_chapter += 1
                    else:
                        same_header_numeric += 1
                    key = (effective_chapter, reference.verse)
                    matching_mt_headers = header_counts.get(key, 0)
                    if matching_mt_headers == 0:
                        zero += 1
                    elif matching_mt_headers == 1:
                        one += 1
                    else:
                        multiple += 1

    assert same_header_numeric + different_verse_same_chapter + different_chapter == scalar

    return GreekReferenceAudit(
        source_files=sources,
        scalar_references=scalar,
        explicit_chapters=explicit,
        subverse_suffixes=suffix,
        numeric_candidates_zero=zero,
        numeric_candidates_one=one,
        numeric_candidates_multiple=multiple,
        same_header_numeric=same_header_numeric,
        different_verse_same_chapter=different_verse_same_chapter,
        different_chapter=different_chapter,
        by_source=tuple(sorted(by_source.items())),
    )
