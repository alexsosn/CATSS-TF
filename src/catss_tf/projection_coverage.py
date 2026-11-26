"""Read-only lexical coverage counters for the parent-projection audit."""

from collections.abc import Iterable, Mapping


def summarize_lexical_coverage(
    expected: Mapping[str, int],
    mappings: Iterable[tuple[str, int]],
) -> dict[str, int]:
    """Count unique zero-based CATSS source indices, not parent word nodes.

    A source element can expand to several BHSA word mappings (maqaf).
    Empty source sides have no lexical coverage denominator. This counts
    resolver output, not proof that the module writer can publish it.
    """
    if any(count < 0 for count in expected.values()):
        raise ValueError("negative source element count")
    observed: dict[str, set[int]] = {}
    mapping_rows = 0
    for alignment_id, index in mappings:
        if alignment_id not in expected or not 0 <= index < expected[alignment_id]:
            raise ValueError("mapping has an unknown alignment or invalid source index")
        observed.setdefault(alignment_id, set()).add(index)
        mapping_rows += 1

    empty = complete = partial = unmapped = 0
    for alignment_id, count in expected.items():
        mapped = len(observed.get(alignment_id, ()))
        if count == 0:
            empty += 1
        elif mapped == count:
            complete += 1
        elif mapped:
            partial += 1
        else:
            unmapped += 1

    return {
        "alignments": len(expected),
        "empty_side_alignments": empty,
        "lexical_alignments": complete + partial + unmapped,
        "complete_lexical_alignments": complete,
        "partial_lexical_alignments": partial,
        "unmapped_lexical_alignments": unmapped,
        "source_elements": sum(expected.values()),
        "mapped_source_elements": sum(map(len, observed.values())),
        "mapping_rows": mapping_rows,
    }
