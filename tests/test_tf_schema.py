import dataclasses
import pathlib

import pytest
from tf.fabric import Fabric  # type: ignore[import-untyped]

from catss_tf.tf_schema import (
    FEATURE_SPECS,
    SIDECAR_COLUMNS,
    Projection,
    TfAnchorEvent,
    TfMembership,
    TfModuleMetadata,
    TfSchemaError,
    compile_tf_features,
    lane_feature_name,
    write_tf_module,
)


def _membership(
    *,
    node: int = 1,
    source: str = "01.Genesis.par",
    alignment_id: str = "catss:01.Genesis.par:aaa",
    mapping_kind: str = "exact",
    mt_n: int = 1,
    lxx_n: int = 2,
    mt_i: int | None = 1,
    mt_segment: int | None = 1,
    lxx_i: int | None = None,
    retro_kind: str | None = None,
    flags: frozenset[str] = frozenset(),
) -> TfMembership:
    return TfMembership(
        node=node,
        source=source,
        alignment_id=alignment_id,
        mapping_kind=mapping_kind,
        mt_n=mt_n,
        lxx_n=lxx_n,
        mt_i=mt_i,
        mt_segment=mt_segment,
        lxx_i=lxx_i,
        line_first=10,
        line_last=11,
        line_n=2,
        retro_kind=retro_kind,
        flags=flags,
    )


def _metadata(projection: Projection = "bhsa") -> TfModuleMetadata:
    return TfModuleMetadata(
        projection=projection,
        parent_repo="synthetic/parent",
        parent_version="1",
        parent_release="v1",
        parent_commit="deadbeef",
        software_version="0.0.0",
    )


def _anchor(
    *,
    node: int = 9,
    source: str = "01.Genesis.par",
    alignment_id: str = "catss:01.Genesis.par:anchor",
    kind: str = "lxx_plus",
    token_n: int = 0,
) -> TfAnchorEvent:
    return TfAnchorEvent(
        node=node,
        source=source,
        alignment_id=alignment_id,
        kind=kind,  # type: ignore[arg-type]
        token_n=token_n,
    )


def test_feature_contract_uses_only_scalar_int_and_str_values() -> None:
    assert FEATURE_SPECS
    assert {spec.value_type for spec in FEATURE_SPECS.values()} <= {"int", "str"}
    assert not {"otype", "oslots", "otext"} & set(FEATURE_SPECS)
    assert all("json" not in name for name in FEATURE_SPECS)
    assert all(not name.endswith(("_list", "_lists")) for name in FEATURE_SPECS)


def test_lane_two_feature_names_are_explicit_scalars() -> None:
    assert lane_feature_name("catss_alignment_id", 1) == "catss_alignment_id"
    assert lane_feature_name("catss_alignment_id", 2) == "catss_alignment_id_2"

    with pytest.raises(TfSchemaError, match="lane"):
        lane_feature_name("catss_alignment_id", 3)


def test_single_membership_compiles_query_native_features() -> None:
    compiled = compile_tf_features(
        projection="bhsa",
        max_node=10,
        memberships=(
            _membership(
                retro_kind="plain",
                flags=frozenset(
                    {
                        "catss_retro",
                        "catss_trans_style",
                        "catss_doubt",
                    }
                ),
            ),
        ),
        anchors=(),
    )

    assert compiled["catss_alignment_n"] == {1: 1}
    assert compiled["catss_alignment_id"] == {1: "catss:01.Genesis.par:aaa"}
    assert compiled["catss_source"] == {1: "01.Genesis.par"}
    assert compiled["catss_mapping"] == {1: "exact"}
    assert compiled["catss_mt_n"] == {1: 1}
    assert compiled["catss_lxx_n"] == {1: 2}
    assert compiled["catss_mt_i"] == {1: 1}
    assert compiled["catss_mt_segment"] == {1: 1}
    assert compiled["catss_line_first"] == {1: 10}
    assert compiled["catss_line_last"] == {1: 11}
    assert compiled["catss_line_n"] == {1: 2}
    assert compiled["catss_retro"] == {1: 1}
    assert compiled["catss_trans_style"] == {1: 1}
    assert compiled["catss_doubt"] == {1: 1}
    assert compiled["catss_retro_members"] == {1: 1}
    assert compiled["catss_trans_style_members"] == {1: 1}
    assert compiled["catss_doubt_members"] == {1: 1}


def test_two_memberships_use_deterministic_source_ranked_lanes() -> None:
    compiled = compile_tf_features(
        projection="bhsa",
        max_node=10,
        memberships=(
            _membership(
                source="07.JoshA.par",
                alignment_id="catss:07.JoshA.par:zzz",
                lxx_n=3,
            ),
            _membership(
                source="06.JoshB.par",
                alignment_id="catss:06.JoshB.par:aaa",
                lxx_n=1,
            ),
        ),
        anchors=(),
    )

    assert compiled["catss_alignment_n"] == {1: 2}
    assert compiled["catss_source"] == {1: "06.JoshB.par"}
    assert compiled["catss_lxx_n"] == {1: 1}
    assert compiled["catss_source_2"] == {1: "07.JoshA.par"}
    assert compiled["catss_lxx_n_2"] == {1: 3}


def test_lxx_transposition_alignment_precedes_carrier_in_two_lanes() -> None:
    compiled = compile_tf_features(
        projection="lxx",
        max_node=10,
        memberships=(
            _membership(
                source="01.Genesis.par",
                alignment_id="catss:01.Genesis.par:carrier",
                mapping_kind="transposition_carrier",
                mt_i=None,
                mt_segment=None,
                lxx_i=1,
            ),
            _membership(
                source="01.Genesis.par",
                alignment_id="catss:01.Genesis.par:semantic",
                mapping_kind="transposition_alignment",
                mt_i=None,
                mt_segment=None,
                lxx_i=1,
            ),
        ),
        anchors=(),
    )

    assert compiled["catss_mapping"] == {1: "transposition_alignment"}
    assert compiled["catss_mapping_2"] == {1: "transposition_carrier"}


def test_third_membership_is_hard_schema_error() -> None:
    memberships = tuple(
        _membership(
            source=source,
            alignment_id=f"catss:{source}:{index}",
        )
        for index, source in enumerate(
            ("06.JoshB.par", "07.JoshA.par", "01.Genesis.par"),
            start=1,
        )
    )

    with pytest.raises(TfSchemaError, match="membership_overflow"):
        compile_tf_features(
            projection="bhsa",
            max_node=10,
            memberships=memberships,
            anchors=(),
        )


def test_membership_nodes_must_belong_to_parent_warp() -> None:
    with pytest.raises(TfSchemaError, match="parent node"):
        compile_tf_features(
            projection="bhsa",
            max_node=3,
            memberships=(_membership(node=4),),
            anchors=(),
        )


def test_unknown_membership_flag_is_rejected_not_serialized() -> None:
    with pytest.raises(TfSchemaError, match="unknown CATSS flag"):
        compile_tf_features(
            projection="bhsa",
            max_node=10,
            memberships=(_membership(flags=frozenset({"catss_magic"})),),
            anchors=(),
        )


def test_bhsa_plus_anchors_aggregate_on_structural_node() -> None:
    compiled = compile_tf_features(
        projection="bhsa",
        max_node=10,
        memberships=(),
        anchors=(
            _anchor(alignment_id="catss:01.Genesis.par:plus-a", token_n=2),
            _anchor(alignment_id="catss:01.Genesis.par:plus-b", token_n=3),
        ),
    )

    assert compiled["catss_lxx_plus_n"] == {9: 2}
    assert compiled["catss_lxx_plus_token_n"] == {9: 5}


def test_lxx_empty_anchors_aggregate_without_alignment_id_blob() -> None:
    compiled = compile_tf_features(
        projection="lxx",
        max_node=10,
        memberships=(),
        anchors=(
            _anchor(alignment_id="catss:01.Genesis.par:minus-a", kind="lxx_minus"),
            _anchor(alignment_id="catss:01.Genesis.par:minus-b", kind="lxx_minus"),
            _anchor(
                alignment_id="catss:01.Genesis.par:placeholder",
                kind="transposition_placeholder",
            ),
        ),
    )

    assert compiled["catss_lxx_minus_n"] == {9: 2}
    assert compiled["catss_transposition_placeholder_n"] == {9: 1}
    assert "catss_alignment_id" not in compiled


def test_sidecar_contracts_are_normalized_repeated_row_tables() -> None:
    assert SIDECAR_COLUMNS["catss-annotations.tsv"] == (
        "source",
        "alignment_id",
        "side",
        "kind",
        "family",
        "contextual",
        "payload",
        "raw",
    )
    assert "alignment_id" in SIDECAR_COLUMNS["catss-mappings.tsv"]
    assert "parent_node" in SIDECAR_COLUMNS["catss-mappings.tsv"]
    assert "sha256" in SIDECAR_COLUMNS["catss-sources.tsv"]
    assert SIDECAR_COLUMNS["catss-diagnostics.tsv"] == (
        "stage",
        "severity",
        "code",
        "source",
        "chapter",
        "verse",
        "position",
        "alignment_id",
        "line_no",
        "side",
        "catss_value",
        "parent_value",
        "message",
    )
    assert SIDECAR_COLUMNS["catss-source-lines.tsv"] == (
        "source",
        "alignment_id",
        "line_no",
        "raw",
    )


def _write_synthetic_parent(root: pathlib.Path) -> None:
    parent = root / "parent"
    parent.mkdir()
    (parent / "otype.tf").write_text(
        """@node
@valueType=str

1-3\tword
4\tverse
""",
        encoding="utf-8",
    )
    (parent / "oslots.tf").write_text(
        """@edge
@valueType=str

4\t1-3
""",
        encoding="utf-8",
    )
    (parent / "word.tf").write_text(
        """@node
@valueType=str

1\tone
2\ttwo
3\tthree
""",
        encoding="utf-8",
    )
    (parent / "otext.tf").write_text(
        """@config
@fmt:text-orig-full={word} 
@writtenBy=CATSS-TF-test

""",
        encoding="utf-8",
    )


def test_written_module_loads_over_synthetic_parent_warp(tmp_path: pathlib.Path) -> None:
    _write_synthetic_parent(tmp_path)
    module = tmp_path / "module"

    compiled = compile_tf_features(
        projection="bhsa",
        max_node=4,
        memberships=(
            _membership(node=1),
            _membership(
                node=1,
                source="02.Exodus.par",
                alignment_id="catss:02.Exodus.par:bbb",
                lxx_n=1,
            ),
        ),
        anchors=(
            _anchor(
                node=4,
                alignment_id="catss:01.Genesis.par:load-plus",
                token_n=2,
            ),
        ),
    )
    write_tf_module(
        module,
        compiled,
        metadata=_metadata(),
        max_node=4,
    )

    assert not (module / "otype.tf").exists()
    assert not (module / "oslots.tf").exists()
    assert not (module / "otext.tf").exists()

    fabric = Fabric(
        locations=str(tmp_path),
        modules=("parent", "module"),
        silent="deep",
    )
    api = fabric.loadAll(silent="deep")

    assert api.F.otype.v(1) == "word"
    assert api.F.otype.v(4) == "verse"
    assert api.F.catss_alignment_n.v(1) == 2
    assert api.F.catss_alignment_id.v(1) == "catss:01.Genesis.par:aaa"
    assert api.F.catss_alignment_id_2.v(1) == "catss:02.Exodus.par:bbb"
    assert api.F.catss_mt_n.v(1) == 1
    assert api.F.catss_lxx_plus_n.v(4) == 1
    assert api.F.catss_lxx_plus_token_n.v(4) == 2

    results = api.S.search("word catss_mt_n=1", silent="deep")
    assert (1,) in results
    lane_two_results = api.S.search("word catss_lxx_n_2=1", silent="deep")
    assert (1,) in lane_two_results


def test_module_writer_rejects_warp_features(tmp_path: pathlib.Path) -> None:
    with pytest.raises(TfSchemaError, match="warp"):
        write_tf_module(
            tmp_path,
            {"otype": {1: "word"}},
            metadata=_metadata(),
            max_node=1,
        )


def test_duplicate_membership_record_is_rejected_not_given_two_lanes() -> None:
    duplicate = _membership()

    with pytest.raises(TfSchemaError, match="duplicate_membership"):
        compile_tf_features(
            projection="bhsa",
            max_node=10,
            memberships=(duplicate, duplicate),
            anchors=(),
        )


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("line_first", 0),
        ("line_last", 0),
    ),
)
def test_source_line_numbers_are_one_based(field: str, value: int) -> None:
    membership = (
        dataclasses.replace(_membership(), line_first=value)
        if field == "line_first"
        else dataclasses.replace(_membership(), line_last=value)
    )

    with pytest.raises(TfSchemaError, match="source line"):
        compile_tf_features(
            projection="bhsa",
            max_node=10,
            memberships=(membership,),
            anchors=(),
        )


def test_source_side_indices_cannot_exceed_alignment_cardinality() -> None:
    bad_mt = dataclasses.replace(_membership(mt_n=1, mt_i=2), mt_i=2)
    bad_lxx = _membership(
        mt_i=None,
        mt_segment=None,
        lxx_n=1,
        lxx_i=2,
        mapping_kind="exact",
    )

    with pytest.raises(TfSchemaError, match="mt_i"):
        compile_tf_features(
            projection="bhsa",
            max_node=10,
            memberships=(bad_mt,),
            anchors=(),
        )

    with pytest.raises(TfSchemaError, match="lxx_i"):
        compile_tf_features(
            projection="lxx",
            max_node=10,
            memberships=(bad_lxx,),
            anchors=(),
        )


def test_projection_requires_its_mapped_side_index_and_nonempty_cardinality() -> None:
    with pytest.raises(TfSchemaError, match="BHSA membership"):
        compile_tf_features(
            projection="bhsa",
            max_node=10,
            memberships=(_membership(mt_n=0, mt_i=None, mt_segment=None),),
            anchors=(),
        )

    with pytest.raises(TfSchemaError, match="LXX membership"):
        compile_tf_features(
            projection="lxx",
            max_node=10,
            memberships=(
                _membership(
                    mt_i=None,
                    mt_segment=None,
                    lxx_n=0,
                    lxx_i=None,
                ),
            ),
            anchors=(),
        )


def test_anchor_token_counts_follow_empty_side_semantics() -> None:
    with pytest.raises(TfSchemaError, match="lxx_plus"):
        compile_tf_features(
            projection="bhsa",
            max_node=10,
            memberships=(),
            anchors=(
                _anchor(
                    alignment_id="catss:01.Genesis.par:bad-plus",
                    token_n=0,
                ),
            ),
        )

    with pytest.raises(TfSchemaError, match="lxx_minus"):
        compile_tf_features(
            projection="lxx",
            max_node=10,
            memberships=(),
            anchors=(
                _anchor(
                    alignment_id="catss:01.Genesis.par:bad-minus",
                    kind="lxx_minus",
                    token_n=1,
                ),
            ),
        )


def test_duplicate_anchor_event_is_rejected_not_double_counted() -> None:
    duplicate = _anchor(
        alignment_id="catss:01.Genesis.par:duplicate-anchor",
        token_n=2,
    )

    with pytest.raises(TfSchemaError, match="duplicate_anchor"):
        compile_tf_features(
            projection="bhsa",
            max_node=10,
            memberships=(),
            anchors=(duplicate, duplicate),
        )


def test_anchor_requires_canonical_source_and_alignment_identity() -> None:
    with pytest.raises(TfSchemaError, match="unknown CATSS source"):
        compile_tf_features(
            projection="bhsa",
            max_node=10,
            memberships=(),
            anchors=(
                _anchor(
                    source="99.NotCATSS.par",
                    alignment_id="catss:99.NotCATSS.par:anchor",
                    token_n=1,
                ),
            ),
        )

    with pytest.raises(TfSchemaError, match="alignment id"):
        compile_tf_features(
            projection="bhsa",
            max_node=10,
            memberships=(),
            anchors=(
                _anchor(
                    alignment_id="not-catss",
                    token_n=1,
                ),
            ),
        )


def test_membership_source_must_match_alignment_identity() -> None:
    mismatched = _membership(
        source="02.Exodus.par",
        alignment_id="catss:01.Genesis.par:wrong-source",
    )

    with pytest.raises(TfSchemaError, match="alignment id source"):
        compile_tf_features(
            projection="bhsa",
            max_node=10,
            memberships=(mismatched,),
            anchors=(),
        )


def test_anchor_source_must_match_alignment_identity() -> None:
    with pytest.raises(TfSchemaError, match="alignment id source"):
        compile_tf_features(
            projection="bhsa",
            max_node=10,
            memberships=(),
            anchors=(
                _anchor(
                    source="02.Exodus.par",
                    alignment_id="catss:01.Genesis.par:wrong-source",
                    token_n=1,
                ),
            ),
        )


def test_same_alignment_cannot_consume_two_lanes_on_one_parent_node() -> None:
    first = _membership(
        mt_i=None,
        mt_segment=None,
        lxx_n=2,
        lxx_i=1,
        mapping_kind="exact",
    )
    second = dataclasses.replace(first, lxx_i=2)

    with pytest.raises(TfSchemaError, match="duplicate_alignment_membership"):
        compile_tf_features(
            projection="lxx",
            max_node=10,
            memberships=(first, second),
            anchors=(),
        )


def test_module_writer_rejects_stale_existing_tf_features(tmp_path: pathlib.Path) -> None:
    module = tmp_path / "module"
    module.mkdir()
    (module / "catss_alignment_id.tf").write_text(
        "@node\n@valueType=str\n\n1\tstale\n",
        encoding="utf-8",
    )

    with pytest.raises(TfSchemaError, match="already contains TF feature"):
        write_tf_module(
            module,
            {"catss_alignment_n": {1: 1}},
            metadata=_metadata(),
            max_node=1,
        )


def test_technique_features_compile_in_same_membership_lane() -> None:
    compiled = compile_tf_features(
        projection="bhsa",
        max_node=10,
        memberships=(_membership(mt_n=1, lxx_n=2),),
        anchors=(),
    )

    assert compiled["catss_tt_cardinality_mt_lxx"] == {1: "one_many"}
    assert compiled["catss_tt_token_balance_mt_lxx"] == {1: "lxx_more"}
    assert compiled["catss_tt_transposition_mt_lxx"] == {1: "none_marked"}
    assert "catss_tt_addition_vs_mt" not in compiled
    assert "catss_tt_omission_vs_mt" not in compiled


def test_technique_lane_two_tracks_source_lane_two() -> None:
    compiled = compile_tf_features(
        projection="bhsa",
        max_node=10,
        memberships=(
            _membership(
                source="06.JoshB.par",
                alignment_id="catss:06.JoshB.par:a",
                mt_n=1,
                lxx_n=1,
            ),
            _membership(
                source="07.JoshA.par",
                alignment_id="catss:07.JoshA.par:b",
                mt_n=2,
                lxx_n=1,
            ),
        ),
        anchors=(),
    )

    assert compiled["catss_source"] == {1: "06.JoshB.par"}
    assert compiled["catss_tt_cardinality_mt_lxx"] == {1: "one_one"}
    assert compiled["catss_source_2"] == {1: "07.JoshA.par"}
    assert compiled["catss_tt_cardinality_mt_lxx_2"] == {1: "many_one"}
    assert compiled["catss_tt_token_balance_mt_lxx_2"] == {1: "lxx_fewer"}


def test_lxx_plus_word_membership_gets_explicit_derived_addition_flag() -> None:
    compiled = compile_tf_features(
        projection="lxx",
        max_node=10,
        memberships=(
            _membership(
                mt_n=0,
                lxx_n=1,
                mt_i=None,
                mt_segment=None,
                lxx_i=1,
                flags=frozenset({"catss_lxx_plus"}),
            ),
        ),
        anchors=(),
    )

    assert compiled["catss_tt_cardinality_mt_lxx"] == {1: "zero_one"}
    assert compiled["catss_tt_token_balance_mt_lxx"] == {1: "not_applicable"}
    assert compiled["catss_tt_transposition_mt_lxx"] == {1: "not_applicable"}
    assert compiled["catss_tt_addition_vs_mt"] == {1: 1}
    assert "catss_tt_omission_vs_mt" not in compiled


def test_lxx_minus_bhsa_membership_gets_explicit_derived_omission_flag() -> None:
    compiled = compile_tf_features(
        projection="bhsa",
        max_node=10,
        memberships=(
            _membership(
                mt_n=1,
                lxx_n=0,
                flags=frozenset({"catss_lxx_minus"}),
            ),
        ),
        anchors=(),
    )

    assert compiled["catss_tt_cardinality_mt_lxx"] == {1: "one_zero"}
    assert compiled["catss_tt_omission_vs_mt"] == {1: 1}
    assert "catss_tt_addition_vs_mt" not in compiled


def test_transposition_carrier_is_not_derived_as_addition() -> None:
    compiled = compile_tf_features(
        projection="lxx",
        max_node=10,
        memberships=(
            _membership(
                mt_n=0,
                lxx_n=1,
                mt_i=None,
                mt_segment=None,
                lxx_i=1,
                mapping_kind="transposition_carrier",
                flags=frozenset({"catss_trans_remote"}),
            ),
        ),
        anchors=(),
    )

    assert compiled["catss_tt_cardinality_mt_lxx"] == {1: "zero_one"}
    assert "catss_tt_addition_vs_mt" not in compiled


def test_technique_sidecar_contract_is_scalar_and_explicitly_based() -> None:
    assert SIDECAR_COLUMNS["catss-technique.tsv"] == (
        "source",
        "alignment_id",
        "comparison_base",
        "cardinality_mt_lxx",
        "token_balance_mt_lxx",
        "addition_vs_mt",
        "omission_vs_mt",
        "transposition_mt_lxx",
    )


def test_annotation_sidecar_contract_exposes_typed_semantics_and_payload() -> None:
    assert SIDECAR_COLUMNS["catss-annotations.tsv"] == (
        "source",
        "alignment_id",
        "side",
        "kind",
        "family",
        "contextual",
        "payload",
        "raw",
    )


def test_typed_annotation_payloads_compile_as_distinct_query_native_features() -> None:
    membership = dataclasses.replace(
        _membership(flags=frozenset({"catss_distributive", "catss_repetition"})),
        annotation_payloads=(
            ("catss_distributive_payload", "GRDIST"),
            ("catss_repetition_payload", "GRREPEAT"),
        ),
    )

    compiled = compile_tf_features(
        projection="bhsa",
        max_node=10,
        memberships=(membership,),
        anchors=(),
    )

    assert compiled["catss_distributive"] == {1: 1}
    assert compiled["catss_repetition"] == {1: 1}
    assert compiled["catss_distributive_payload"] == {1: "GRDIST"}
    assert compiled["catss_repetition_payload"] == {1: "GRREPEAT"}


def test_semantic_features_are_dynamic_scalar_tf_features_without_packing() -> None:
    membership = dataclasses.replace(
        _membership(),
        semantic_kinds=("distributive_rendering", "gender_switch"),
        semantic_payloads=(("distributive_rendering", "Gen 1:2"),),
    )
    compiled = compile_tf_features(
        projection="bhsa", max_node=10, memberships=(membership,), anchors=()
    )
    assert compiled["catss_sem_distributive_rendering"] == {1: 1}
    assert compiled["catss_sem_gender_switch"] == {1: 1}
    assert compiled["catss_sem_distributive_rendering_payload"] == {1: "Gen 1:2"}


def test_writer_accepts_registered_complete_semantic_features(tmp_path: pathlib.Path) -> None:
    write_tf_module(
        tmp_path / "module",
        {
            "catss_sem_distributive_rendering": {1: 1},
            "catss_sem_distributive_rendering_payload": {1: "Gen 1:2"},
        },
        metadata=_metadata(),
        max_node=10,
    )
    assert (tmp_path / "module" / "catss_sem_distributive_rendering.tf").exists()
    assert (tmp_path / "module" / "catss_sem_distributive_rendering_payload.tf").exists()


def test_conflicting_semantic_payloads_fail_closed_instead_of_overwriting() -> None:
    membership = dataclasses.replace(
        _membership(),
        semantic_kinds=("repetition",),
        semantic_payloads=(("repetition", "A"), ("repetition", "B")),
    )
    with pytest.raises(TfSchemaError, match="conflicting feature value"):
        compile_tf_features(projection="bhsa", max_node=10, memberships=(membership,), anchors=())


def test_researcher_can_load_and_query_semantic_features_with_text_fabric(
    tmp_path: pathlib.Path,
) -> None:
    module = tmp_path / "module"
    write_tf_module(
        module,
        {
            "catss_sem_distributive_rendering": {1: 1},
            "catss_sem_distributive_rendering_payload": {1: "Gen 1:2"},
        },
        metadata=_metadata(),
        max_node=10,
    )

    api = Fabric(locations=str(module), silent="deep").load(
        "catss_sem_distributive_rendering catss_sem_distributive_rendering_payload"
    )
    assert api.F.catss_sem_distributive_rendering.v(1) == 1
    assert api.F.catss_sem_distributive_rendering_payload.v(1) == "Gen 1:2"