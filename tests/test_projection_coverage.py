import importlib

import pytest


def test_source_index_coverage_counts_unique_elements_and_groups() -> None:
    audit = importlib.import_module("catss_tf.projection_coverage")
    assert audit.summarize_lexical_coverage(
        {"a": 2, "b": 2, "c": 1, "empty": 0},
        [("a", 0), ("a", 0), ("a", 1), ("b", 1)],
    ) == {
        "alignments": 4,
        "empty_side_alignments": 1,
        "lexical_alignments": 3,
        "complete_lexical_alignments": 1,
        "partial_lexical_alignments": 1,
        "unmapped_lexical_alignments": 1,
        "source_elements": 5,
        "mapped_source_elements": 3,
        "mapping_rows": 4,
    }


@pytest.mark.parametrize("mapping", [("missing", 0), ("a", -1), ("a", 1), ("empty", 0)])
def test_coverage_refuses_orphan_or_out_of_range_indices(mapping: tuple[str, int]) -> None:
    audit = importlib.import_module("catss_tf.projection_coverage")
    with pytest.raises(ValueError):
        audit.summarize_lexical_coverage({"a": 1, "empty": 0}, [mapping])
