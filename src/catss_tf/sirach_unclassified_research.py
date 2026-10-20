"""Source-safe context research for Sirach technique judgments exposed by #134.

Legacy MT counts are replayed for research only, never for corpus construction.
Neighboring alignment membership does not establish manuscript-word scope.
"""

from collections import Counter, defaultdict
from dataclasses import dataclass, replace

from catss_tf.parser import ParallelDocument, _mt_lexical_readings
from catss_tf.technique import TechniqueError, derive_alignment_technique

SourceLocation = tuple[str, int, int, int]


@dataclass(frozen=True, slots=True)
class SirachUnclassifiedContextAudit:
    """Metadata-only transitions and context of newly unresolved Sirach rows."""

    source: str
    changed_groups: int
    newly_unclassified: int
    unexpected_transitions: int
    transition_reasons: tuple[tuple[str, int], ...]
    context_counts: tuple[tuple[str, int], ...]
    witness_kind_counts: tuple[tuple[str, int], ...]
    samples: tuple[tuple[str, tuple[SourceLocation, ...]], ...]
    new_unclassified_id_reasons: tuple[tuple[str, str], ...]


def audit_sirach_unclassified_context(
    document: ParallelDocument,
) -> SirachUnclassifiedContextAudit:
    """Compare old generic lexical counts to current source-corrected counts.

    The result contains no raw Hebrew/Greek text. Context and witness sigla
    are alignment-level evidence, never conjectural lexical attestation edges.
    """

    if document.source_name != "27.Sirach.par":
        raise ValueError("Sirach context audit requires 27.Sirach.par")

    contexts: Counter[str] = Counter()
    reasons: Counter[str] = Counter()
    kinds: Counter[str] = Counter()
    samples: dict[str, list[SourceLocation]] = defaultdict(list)
    ids: list[tuple[str, str]] = []
    changed = 0
    unexpected = 0

    for verse in document.verses:
        rows = verse.alignments
        for i, row in enumerate(rows):
            legacy_count = 0 if row.is_lxx_plus else len(_mt_lexical_readings(row.mt_col_a))
            if legacy_count == row.mt_count:
                continue
            changed += 1
            historical = replace(row, mt_count=legacy_count)

            try:
                derive_alignment_technique(document.source_name, historical)
                historical_reason = None
            except TechniqueError as error:
                historical_reason = str(error)
            try:
                derive_alignment_technique(document.source_name, row)
                current_reason = None
            except TechniqueError as error:
                current_reason = str(error)

            if historical_reason is not None or current_reason is None:
                if historical_reason != current_reason:
                    unexpected += 1
                continue

            reasons[current_reason] += 1
            ids.append((row.alignment_id, current_reason))
            position: SourceLocation = (
                verse.book,
                verse.chapter,
                verse.verse,
                min(row.source_lines),
            )
            if len(samples[current_reason]) < 3:
                samples[current_reason].append(position)

            mt_a = tuple(
                item
                for item in row.annotations
                if item.side == "mt_a" and item.kind.startswith("sirach_witness_")
            )
            mt_b = tuple(
                item
                for item in row.annotations
                if item.side == "mt_b" and item.kind.startswith("sirach_witness_")
            )
            if mt_a:
                contexts["has_mt_a_witness_marker"] += 1
            if mt_b:
                contexts["has_mt_b_witness_marker"] += 1
            if len(mt_a) > 1:
                contexts["has_multiple_mt_a_witness_markers"] += 1
            for item in (*mt_a, *mt_b):
                kinds[item.kind] += 1
            if row.mt_col_b is not None:
                contexts["has_mt_b_column"] += 1
            if row.is_lxx_minus:
                contexts["has_lxx_minus"] += 1
            if row.lxx_count:
                contexts["has_lxx_lexical"] += 1
                contexts[f"lxx_count_{row.lxx_count if row.lxx_count <= 3 else 'gt3'}"] += 1
            if any(
                item.kind == "sirach_reading_lacking_in_witness"
                for item in row.annotations
            ):
                contexts["has_absence_marker"] += 1
            if any(item.kind == "sirach_lacuna_or_illegible" for item in row.annotations):
                contexts["has_lacuna"] += 1
            if any(item.kind == "sirach_reconstructed_letters" for item in row.annotations):
                contexts["has_reconstructed_letters"] += 1
            if len(row.source_lines) > 1:
                contexts["has_continuation"] += 1

            left = i > 0 and rows[i - 1].mt_count > 0
            right = i + 1 < len(rows) and rows[i + 1].mt_count > 0
            if left:
                contexts["neighbor_left_with_mt"] += 1
            if right:
                contexts["neighbor_right_with_mt"] += 1
            if left and right:
                contexts["neighbor_both_with_mt"] += 1
            if not (left or right):
                contexts["no_immediate_mt_neighbor"] += 1

    return SirachUnclassifiedContextAudit(
        source=document.source_name,
        changed_groups=changed,
        newly_unclassified=sum(reasons.values()),
        unexpected_transitions=unexpected,
        transition_reasons=tuple(sorted(reasons.items())),
        context_counts=tuple(sorted(contexts.items())),
        witness_kind_counts=tuple(sorted(kinds.items())),
        samples=tuple(
            (reason, tuple(locations)) for reason, locations in sorted(samples.items())
        ),
        new_unclassified_id_reasons=tuple(ids),
    )
