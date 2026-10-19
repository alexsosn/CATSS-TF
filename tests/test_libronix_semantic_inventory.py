"""Regression for book-sensitive Libronix notation in projection schemas.

The source spelling can have different meanings in Sirach. Enumerating by
raw glyph must not erase a general-CATSS meaning from the TF feature schema.
"""

import pytest

from catss_tf.notation import documented_notation, notation_spec
from catss_tf.tf_schema import FEATURE_SPECS


@pytest.mark.parametrize("book", ("Ge", "Sir"))
def test_every_documented_meaning_has_queryable_projection_features(book: str) -> None:
    for raw in documented_notation():
        spec = notation_spec(raw, book=book)
        if spec is None:
            continue
        base = f"catss_sem_{spec.kind}"
        for lane in ("", "_2"):
            assert f"{base}{lane}" in FEATURE_SPECS, (book, raw, spec.kind)
            assert f"{base}_payload{lane}" in FEATURE_SPECS, (book, raw, spec.kind)
            for side in ("mt_a", "mt_b", "lxx"):
                assert f"{base}_{side}{lane}" in FEATURE_SPECS, (book, raw, spec.kind)
                assert f"{base}_{side}_payload{lane}" in FEATURE_SPECS, (
                    book,
                    raw,
                    spec.kind,
                )


@pytest.mark.parametrize(
    ("raw", "general_kind", "sirach_kind"),
    (
        ("*", "asterisked_passage", "sirach_uncertain_fragmentary_letter"),
        ("[..]", "unreadable_or_greek_addition", "sirach_lacuna_or_illegible"),
    ),
)
def test_colliding_glyphs_keep_both_distinct_meanings(
    raw: str, general_kind: str, sirach_kind: str
) -> None:
    assert notation_spec(raw, book="Ge").kind == general_kind
    assert notation_spec(raw, book="Sir").kind == sirach_kind
    assert general_kind != sirach_kind
    assert f"catss_sem_{general_kind}" in FEATURE_SPECS
    assert f"catss_sem_{sirach_kind}" in FEATURE_SPECS
