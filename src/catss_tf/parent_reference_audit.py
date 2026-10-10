"""Fail-closed exact Greek-parent span existence diagnostics, not target mapping."""

import dataclasses
import typing

from catss_tf.lxx_resolver import LxxVerseProvider
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
    """Do not treat a unique numeric CATSS match as a parent textual target."""
    raise NotImplementedError("R96-5 parent availability not yet implemented")
