import pytest

from catss_tf.parser import parse_parallel_text
from catss_tf.technique import (
    TechniqueError,
    derive_alignment_technique,
    derive_technique_state,
)


def test_one_to_one_alignment_derives_conservative_mt_lxx_state() -> None:
    doc = parse_parallel_text(
        """Gen 1:1
HB\tLOGOS
""",
        source_name="01.Genesis.par",
    )
    alignment = doc.verses[0].alignments[0]

    technique = derive_alignment_technique("01.Genesis.par", alignment)

    assert technique.comparison_base == "mt_lxx"
    assert technique.cardinality_mt_lxx == "one_one"
    assert technique.token_balance_mt_lxx == "equal"
    assert technique.addition_vs_mt is False
    assert technique.omission_vs_mt is False
    assert technique.transposition_mt_lxx == "none_marked"


@pytest.mark.parametrize(
    ("mt_n", "lxx_n", "expected"),
    (
        (0, 0, "zero_zero"),
        (0, 1, "zero_one"),
        (0, 3, "zero_many"),
        (1, 0, "one_zero"),
        (3, 0, "many_zero"),
        (1, 1, "one_one"),
        (1, 2, "one_many"),
        (2, 1, "many_one"),
        (2, 3, "many_many"),
    ),
)
def test_cardinality_classes_are_closed_and_deterministic(
    mt_n: int, lxx_n: int, expected: str
) -> None:
    state = derive_technique_state(
        mt_n=mt_n,
        lxx_n=lxx_n,
        is_lxx_plus=mt_n == 0 and lxx_n > 0,
        is_lxx_minus=mt_n > 0 and lxx_n == 0,
        trans_local=False,
        trans_remote=False,
        trans_style=False,
    )

    assert state.cardinality_mt_lxx == expected


@pytest.mark.parametrize(
    ("mt_n", "lxx_n", "expected"),
    (
        (1, 1, "equal"),
        (2, 2, "equal"),
        (1, 2, "lxx_more"),
        (3, 2, "lxx_fewer"),
        (0, 2, "not_applicable"),
        (2, 0, "not_applicable"),
        (0, 0, "not_applicable"),
    ),
)
def test_token_balance_is_descriptive_not_semantic_expansion(
    mt_n: int, lxx_n: int, expected: str
) -> None:
    state = derive_technique_state(
        mt_n=mt_n,
        lxx_n=lxx_n,
        is_lxx_plus=mt_n == 0 and lxx_n > 0,
        is_lxx_minus=mt_n > 0 and lxx_n == 0,
        trans_local=False,
        trans_remote=False,
        trans_style=False,
    )

    assert state.token_balance_mt_lxx == expected


def test_addition_and_omission_require_explicit_catss_source_evidence() -> None:
    plus = derive_technique_state(
        mt_n=0,
        lxx_n=2,
        is_lxx_plus=True,
        is_lxx_minus=False,
        trans_local=False,
        trans_remote=False,
        trans_style=False,
    )
    minus = derive_technique_state(
        mt_n=2,
        lxx_n=0,
        is_lxx_plus=False,
        is_lxx_minus=True,
        trans_local=False,
        trans_remote=False,
        trans_style=False,
    )

    assert plus.addition_vs_mt is True
    assert plus.omission_vs_mt is False
    assert minus.addition_vs_mt is False
    assert minus.omission_vs_mt is True

    with pytest.raises(TechniqueError, match="LXX-plus"):
        derive_technique_state(
            mt_n=0,
            lxx_n=2,
            is_lxx_plus=False,
            is_lxx_minus=False,
            trans_local=False,
            trans_remote=False,
            trans_style=False,
        )

    with pytest.raises(TechniqueError, match="LXX-minus"):
        derive_technique_state(
            mt_n=2,
            lxx_n=0,
            is_lxx_plus=False,
            is_lxx_minus=False,
            trans_local=False,
            trans_remote=False,
            trans_style=False,
        )


def test_source_flags_cannot_contradict_nonempty_sides() -> None:
    with pytest.raises(TechniqueError, match="non-empty MT"):
        derive_technique_state(
            mt_n=1,
            lxx_n=1,
            is_lxx_plus=True,
            is_lxx_minus=False,
            trans_local=False,
            trans_remote=False,
            trans_style=False,
        )

    with pytest.raises(TechniqueError, match="non-empty Greek"):
        derive_technique_state(
            mt_n=1,
            lxx_n=1,
            is_lxx_plus=False,
            is_lxx_minus=True,
            trans_local=False,
            trans_remote=False,
            trans_style=False,
        )


@pytest.mark.parametrize(
    ("flags", "expected"),
    (
        ((False, False, False), "none_marked"),
        ((True, False, False), "local"),
        ((False, True, False), "remote"),
        ((False, False, True), "stylistic"),
        ((True, True, False), "multiple"),
        ((True, False, True), "multiple"),
    ),
)
def test_transposition_feature_reports_evidence_not_same_order(
    flags: tuple[bool, bool, bool], expected: str
) -> None:
    state = derive_technique_state(
        mt_n=1,
        lxx_n=1,
        is_lxx_plus=False,
        is_lxx_minus=False,
        trans_local=flags[0],
        trans_remote=flags[1],
        trans_style=flags[2],
    )

    assert state.transposition_mt_lxx == expected


def test_transposition_is_not_applicable_when_one_side_is_empty() -> None:
    state = derive_technique_state(
        mt_n=0,
        lxx_n=1,
        is_lxx_plus=True,
        is_lxx_minus=False,
        trans_local=True,
        trans_remote=False,
        trans_style=False,
    )

    assert state.transposition_mt_lxx == "not_applicable"


def test_negative_counts_fail_closed() -> None:
    with pytest.raises(TechniqueError, match="non-negative"):
        derive_technique_state(
            mt_n=-1,
            lxx_n=1,
            is_lxx_plus=False,
            is_lxx_minus=False,
            trans_local=False,
            trans_remote=False,
            trans_style=False,
        )


def test_alignment_derivation_preserves_canonical_identity() -> None:
    doc = parse_parallel_text(
        """Gen 1:1
--+\tLOGOS
""",
        source_name="01.Genesis.par",
    )
    alignment = doc.verses[0].alignments[0]

    technique = derive_alignment_technique(doc.source_name, alignment)

    assert technique.source == "01.Genesis.par"
    assert technique.alignment_id == alignment.alignment_id
    assert technique.cardinality_mt_lxx == "zero_one"
    assert technique.addition_vs_mt is True


def test_alignment_source_must_match_alignment_id() -> None:
    doc = parse_parallel_text(
        """Gen 1:1
HB\tLOGOS
""",
        source_name="01.Genesis.par",
    )

    with pytest.raises(TechniqueError, match="source mismatch"):
        derive_alignment_technique("02.Exodus.par", doc.verses[0].alignments[0])


def test_zero_side_transposition_carrier_is_not_misclassified_as_addition() -> None:
    state = derive_technique_state(
        mt_n=0,
        lxx_n=1,
        is_lxx_plus=False,
        is_lxx_minus=False,
        trans_local=False,
        trans_remote=True,
        trans_style=False,
    )

    assert state.cardinality_mt_lxx == "zero_one"
    assert state.addition_vs_mt is False
    assert state.omission_vs_mt is False
    assert state.token_balance_mt_lxx == "not_applicable"
    assert state.transposition_mt_lxx == "not_applicable"


def test_zero_side_transposition_placeholder_is_not_misclassified_as_omission() -> None:
    state = derive_technique_state(
        mt_n=1,
        lxx_n=0,
        is_lxx_plus=False,
        is_lxx_minus=False,
        trans_local=False,
        trans_remote=True,
        trans_style=False,
    )

    assert state.cardinality_mt_lxx == "one_zero"
    assert state.addition_vs_mt is False
    assert state.omission_vs_mt is False
