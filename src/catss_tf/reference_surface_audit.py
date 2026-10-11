"""Read-only CATSS Greek reference surface-candidate diagnostics."""

import dataclasses
import typing

from catss_tf.lxx_resolver import LxxVerseProvider
from catss_tf.parser import ParallelDocument


@dataclasses.dataclass(frozen=True, slots=True)
class LxxReferenceSurfaceCandidates:
    """Per-scalar-reference evidence; no verified lexical or TF target mappings."""

    source_files: int
    scalar_references: int
    exact_single: int
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
    raise NotImplementedError("R96-7 reference-surface candidates not yet implemented")
