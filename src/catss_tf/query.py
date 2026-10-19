"""Source-exact lexical co-membership queries for standalone CATSS Text-Fabric.

Results represent complete alignment groups, not pairwise MT/Greek lexical edges.
"""

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class CanonicalAlignedGroup:
    """A matching source alignment with ordered lexical elements."""

    source: str
    alignment_id: str
    book: str
    chapter: int
    verse: int
    mt_elements: tuple[str, ...]
    lxx_elements: tuple[str, ...]


def _matching_slots(api: Any, mt_form: str, lxx_form: str) -> tuple[set[int], set[int]]:
    """Scan only source lexical feature entries, once for both forms.

    Text-Fabric NodeFeature.s(value) is itself a linear scan, not an index.
    A single pass over the feature data avoids repeating that scan.
    """

    mt_slots: set[int] = set()
    lxx_slots: set[int] = set()
    for node, value in api.F.catss_text.items():
        if value == mt_form and api.F.otype.v(node) == "mt_element":
            mt_slots.update(int(slot) for slot in api.L.d(node, otype="alignment"))
        elif value == lxx_form and api.F.otype.v(node) == "lxx_element":
            lxx_slots.update(int(slot) for slot in api.L.d(node, otype="alignment"))
    return mt_slots, lxx_slots


def _ordered_elements(api: Any, slot: int, element_type: str) -> tuple[str, ...]:
    nodes = api.L.u(slot, otype=element_type)
    return tuple(str(api.F.catss_text.v(n)) for n in sorted(nodes, key=api.F.catss_index.v))


def find_aligned_groups(
    api: Any,
    mt_form: str,
    lxx_form: str,
    *,
    source: str | None = None,
) -> Iterator[CanonicalAlignedGroup]:
    """Find canonical groups containing both exact source lexical forms.

    The loaded TF must use standalone alignment slots. BHSA and LXX
    projections have different node spaces and cannot use this join.
    MT search considers column A, never hypothetical column B reconstruction.
    Source filtering uses exact .par filenames; no normalization is applied.
    """

    if not mt_form or not lxx_form:
        raise ValueError("both MT and LXX search forms must be nonempty")
    if api.F.otype.slotType != "alignment":
        raise ValueError("find_aligned_groups requires the standalone CATSS alignment-slot warp")

    mt_slots, lxx_slots = _matching_slots(api, mt_form, lxx_form)
    for slot in sorted(mt_slots & lxx_slots):
        source_name = str(api.F.catss_source.v(slot))
        if source is not None and source_name != source:
            continue
        yield CanonicalAlignedGroup(
            source=source_name,
            alignment_id=str(api.F.catss_alignment_id.v(slot)),
            book=str(api.F.book.v(slot)),
            chapter=int(api.F.chapter.v(slot)),
            verse=int(api.F.verse.v(slot)),
            mt_elements=_ordered_elements(api, slot, "mt_element"),
            lxx_elements=_ordered_elements(api, slot, "lxx_element"),
        )
