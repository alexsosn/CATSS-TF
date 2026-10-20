"""Metadata-only research audit for Sirach witness annotations.

This does not attribute a CATSS witness marker to individual MT lexical
elements. It records counts and source locations, never CATSS text.
"""

from collections import Counter, defaultdict
from dataclasses import dataclass

from catss_tf.notation import notation_spec
from catss_tf.parser import ParallelDocument

SourceLocation = tuple[str, int, int, int]


@dataclass(frozen=True, slots=True)
class SirachWitnessAudit:
    """Source-safe summary of the current Sirach annotation/reading shapes."""

    source: str
    alignments: int
    witness_counts: tuple[tuple[str, int], ...]
    witness_markers: int
    witness_groups: int
    multi_witness_groups: int
    witness_with_lacuna: int
    witness_groups_with_multiple_mt: int
    witness_groups_with_zero_mt: int
    witness_groups_with_column_b: int
    witness_groups_with_continuations: int
    absence_markers: int
    absence_groups: int
    annotation_counts: tuple[tuple[str, int], ...]
    witness_side_counts: tuple[tuple[str, int], ...]
    examples: tuple[tuple[str, SourceLocation], ...]


def audit_sirach_witnesses(document: ParallelDocument) -> SirachWitnessAudit:
    """Count typed Sirach annotations without inventing reading-specific links."""

    if document.source_name != "27.Sirach.par":
        raise ValueError("Sirach witness audit requires 27.Sirach.par")
    all_kinds: list[str] = []
    for n in range(1, 11):
        spec = notation_spec(str(n), book="Sir")
        if spec is None:
            raise ValueError(f"undocumented Sirach witness number: {n}")
        all_kinds.append(spec.kind)
    witness_kinds = frozenset(all_kinds)
    marker_counts: Counter[str] = Counter()
    annotation_counts: Counter[str] = Counter()
    witness_side_counts: Counter[str] = Counter()
    example_groups: dict[str, list[SourceLocation]] = defaultdict(list)
    counts: Counter[str] = Counter()

    def sample(kind: str, loc: SourceLocation) -> None:
        # Keep a bounded set of text-free source positions only.
        if len(example_groups[kind]) < 3:
            example_groups[kind].append(loc)

    for verse in document.verses:
        for row in verse.alignments:
            counts["alignments"] += 1
            location: SourceLocation = (
                verse.book,
                verse.chapter,
                verse.verse,
                min(row.source_lines),
            )
            kinds = [annotation.kind for annotation in row.annotations]
            for kind in kinds:
                if kind.startswith("sirach_"):
                    annotation_counts[kind] += 1
                    sample(kind, location)
            witness = [
                annotation
                for annotation in row.annotations
                if annotation.kind in witness_kinds
            ]
            for item in witness:
                marker_counts[item.kind] += 1
                witness_side_counts[item.side] += 1
            absent = [
                item
                for item in row.annotations
                if item.kind == "sirach_reading_lacking_in_witness"
            ]
            counts["absence_markers"] += len(absent)
            if absent:
                counts["absence_groups"] += 1
                sample("absence", location)
            if not witness:
                continue
            counts["witness_groups"] += 1
            sample("witness_group", location)
            if len(witness) > 1:
                counts["multi_witness_groups"] += 1
                sample("multi_witness", location)
            if "sirach_lacuna_or_illegible" in kinds:
                counts["witness_with_lacuna"] += 1
                sample("witness_lacuna", location)
            if row.mt_count > 1:
                counts["witness_groups_with_multiple_mt"] += 1
                sample("witness_multiple_mt", location)
            if row.mt_count == 0:
                counts["witness_groups_with_zero_mt"] += 1
                sample("witness_zero_mt", location)
            if row.mt_col_b is not None:
                counts["witness_groups_with_column_b"] += 1
                sample("witness_column_b", location)
            if len(row.source_lines) > 1:
                counts["witness_groups_with_continuations"] += 1
                sample("witness_continuation", location)

    return SirachWitnessAudit(
        source=document.source_name,
        alignments=counts["alignments"],
        witness_counts=tuple((kind, marker_counts[kind]) for kind in all_kinds),
        witness_markers=sum(marker_counts.values()),
        witness_groups=counts["witness_groups"],
        multi_witness_groups=counts["multi_witness_groups"],
        witness_with_lacuna=counts["witness_with_lacuna"],
        witness_groups_with_multiple_mt=counts["witness_groups_with_multiple_mt"],
        witness_groups_with_zero_mt=counts["witness_groups_with_zero_mt"],
        witness_groups_with_column_b=counts["witness_groups_with_column_b"],
        witness_groups_with_continuations=counts["witness_groups_with_continuations"],
        absence_markers=counts["absence_markers"],
        absence_groups=counts["absence_groups"],
        annotation_counts=tuple(sorted(annotation_counts.items())),
        witness_side_counts=tuple(sorted(witness_side_counts.items())),
        examples=tuple(
            (kind, location)
            for kind, locations in sorted(example_groups.items())
            for location in locations
        ),
    )
