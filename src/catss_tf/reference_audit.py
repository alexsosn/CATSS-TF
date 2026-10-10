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
    by_source: tuple[tuple[str, int], ...]


def audit_greek_references(
    documents: typing.Iterable[ParallelDocument],
) -> GreekReferenceAudit:
    """Build an inventory without ever promoting numeric matches to TF edges."""
    raise NotImplementedError("source reference inventory not implemented (#96)")
