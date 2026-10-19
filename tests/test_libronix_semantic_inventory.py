"""Regression for book-sensitive Libronix notation in projection schemas.

The source spelling can have different meanings in Sirach. Enumerating by
raw glyph must not erase a general-CATSS meaning from the TF feature schema.
"""

import pytest

from catss_tf.notation import documented_notation, notation_spec
from catss_tf.tf_schema import (
    FEATURE_SPECS,
    TfMembership,
    TfModuleMetadata,
    compile_tf_features,
    write_tf_module,
)


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


def test_patterned_samaritan_apparatus_semantics_are_queryable() -> None:
    spec = notation_spec("<sp26.35ap>", book="Ge")
    assert spec is not None
    assert spec.kind == "samaritan_apparatus_reference"
    assert spec.contextual
    assert f"catss_sem_{spec.kind}" in FEATURE_SPECS
    assert f"catss_sem_{spec.kind}_lxx_payload" in FEATURE_SPECS


@pytest.mark.parametrize(
    ("source", "book", "raw"),
    (
        ("01.Genesis.par", "Ge", "*"),
        ("01.Genesis.par", "Ge", "[..]"),
        ("27.Sirach.par", "Sir", "*"),
        ("27.Sirach.par", "Sir", "[..]"),
        ("01.Genesis.par", "Ge", "<sp26.35ap>"),
    ),
)
def test_documented_semantics_survive_projection_compilation_and_tf_write(
    tmp_path, source: str, book: str, raw: str
) -> None:
    spec = notation_spec(raw, book=book)
    assert spec is not None
    membership = TfMembership(
        node=1,
        source=source,
        alignment_id=f"catss:{source}:synthetic",
        mapping_kind="exact",
        mt_n=1,
        lxx_n=1,
        mt_i=None,
        mt_segment=None,
        lxx_i=1,
        line_first=1,
        line_last=1,
        line_n=1,
        retro_kind=None,
        semantic_kinds=(spec.kind,),
        semantic_scopes=((spec.kind, "lxx"),),
        semantic_scoped_payloads=((spec.kind, "lxx", raw),) if spec.contextual else (),
    )
    features = compile_tf_features(
        projection="lxx", max_node=1, memberships=(membership,), anchors=()
    )
    base = f"catss_sem_{spec.kind}"
    assert features[base] == {1: 1}
    assert features[f"{base}_lxx"] == {1: 1}
    if spec.contextual:
        assert features[f"{base}_lxx_payload"] == {1: raw}

    output = tmp_path / "module"
    write_tf_module(
        output,
        features,
        metadata=TfModuleMetadata(
            projection="lxx",
            parent_repo="synthetic/parent",
            parent_version="1",
            parent_release="v1",
            parent_commit="synthetic",
            software_version="0",
        ),
        max_node=1,
    )
    assert (output / f"{base}.tf").is_file()
    assert (output / f"{base}_lxx.tf").is_file()
