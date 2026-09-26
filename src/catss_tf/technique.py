"""Deterministic translation-technique derivation from canonical CATSS alignment facts."""

import dataclasses
import typing

from catss_tf.parser import AlignmentRecord

TECHNIQUE_SCHEMA_VERSION = "1"

Cardinality = typing.Literal[
    "zero_zero",
    "zero_many",
    "many_zero",
    "one_one",
    "one_many",
    "many_one",
    "many_many",
]
TokenBalance = typing.Literal["equal", "lxx_more", "lxx_fewer", "not_applicable"]
TranspositionEvidence = typing.Literal[
    "none_marked",
    "local",
    "remote",
    "stylistic",
    "multiple",
    "not_applicable",
]


class TechniqueError(ValueError):
    """Raised when canonical CATSS state is contradictory for technique derivation."""


@dataclasses.dataclass(frozen=True, slots=True)
class TechniqueState:
    """Derived MT↔LXX technique facts independent of projection/node identity."""

    cardinality_mt_lxx: Cardinality
    token_balance_mt_lxx: TokenBalance
    addition_vs_mt: bool
    omission_vs_mt: bool
    transposition_mt_lxx: TranspositionEvidence


@dataclasses.dataclass(frozen=True, slots=True)
class TechniqueRecord:
    """Canonical derived record for one CATSS alignment identity."""

    source: str
    alignment_id: str
    comparison_base: typing.Literal["mt_lxx"]
    cardinality_mt_lxx: Cardinality
    token_balance_mt_lxx: TokenBalance
    addition_vs_mt: bool
    omission_vs_mt: bool
    transposition_mt_lxx: TranspositionEvidence


def derive_technique_state(
    *,
    mt_n: int,
    lxx_n: int,
    is_lxx_plus: bool,
    is_lxx_minus: bool,
    trans_local: bool,
    trans_remote: bool,
    trans_style: bool,
) -> TechniqueState:
    """Derive conservative MT↔LXX technique facts from canonical scalar state."""

    if mt_n < 0 or lxx_n < 0:
        raise TechniqueError("MT/LXX counts must be non-negative")

    if is_lxx_plus and mt_n != 0:
        raise TechniqueError("CATSS LXX-plus contradicts a non-empty MT side")
    if is_lxx_minus and lxx_n != 0:
        raise TechniqueError("CATSS LXX-minus contradicts a non-empty Greek side")
    transposition_marked = trans_local or trans_remote or trans_style
    if mt_n == 0 and lxx_n > 0 and not is_lxx_plus and not transposition_marked:
        raise TechniqueError(
            "Hebrew-empty Greek alignment requires CATSS LXX-plus or transposition evidence"
        )
    if mt_n > 0 and lxx_n == 0 and not is_lxx_minus and not transposition_marked:
        raise TechniqueError(
            "Greek-empty MT alignment requires CATSS LXX-minus or transposition evidence"
        )
    if is_lxx_plus and is_lxx_minus:
        raise TechniqueError("CATSS alignment cannot be both LXX-plus and LXX-minus")

    cardinality = _cardinality(mt_n, lxx_n)

    if mt_n == 0 or lxx_n == 0:
        token_balance: TokenBalance = "not_applicable"
        transposition: TranspositionEvidence = "not_applicable"
    else:
        if mt_n == lxx_n:
            token_balance = "equal"
        elif lxx_n > mt_n:
            token_balance = "lxx_more"
        else:
            token_balance = "lxx_fewer"

        marked = [
            name
            for name, value in (
                ("local", trans_local),
                ("remote", trans_remote),
                ("stylistic", trans_style),
            )
            if value
        ]
        if not marked:
            transposition = "none_marked"
        elif len(marked) == 1:
            transposition = typing.cast(TranspositionEvidence, marked[0])
        else:
            transposition = "multiple"

    return TechniqueState(
        cardinality_mt_lxx=cardinality,
        token_balance_mt_lxx=token_balance,
        addition_vs_mt=is_lxx_plus and mt_n == 0 and lxx_n > 0,
        omission_vs_mt=is_lxx_minus and mt_n > 0 and lxx_n == 0,
        transposition_mt_lxx=transposition,
    )


def derive_alignment_technique(source: str, alignment: AlignmentRecord) -> TechniqueRecord:
    """Derive one canonical technique-v1 row from a parsed CATSS alignment."""

    expected_prefix = f"catss:{source}:"
    if not alignment.alignment_id.startswith(expected_prefix):
        raise TechniqueError(
            f"alignment/source mismatch: expected alignment id prefix {expected_prefix!r}"
        )

    state = derive_technique_state(
        mt_n=alignment.mt_count,
        lxx_n=alignment.lxx_count,
        is_lxx_plus=alignment.is_lxx_plus,
        is_lxx_minus=alignment.is_lxx_minus,
        trans_local=alignment.is_transposition_local,
        trans_remote=alignment.is_transposition_remote,
        trans_style=alignment.is_transposition_stylistic,
    )
    return TechniqueRecord(
        source=source,
        alignment_id=alignment.alignment_id,
        comparison_base="mt_lxx",
        cardinality_mt_lxx=state.cardinality_mt_lxx,
        token_balance_mt_lxx=state.token_balance_mt_lxx,
        addition_vs_mt=state.addition_vs_mt,
        omission_vs_mt=state.omission_vs_mt,
        transposition_mt_lxx=state.transposition_mt_lxx,
    )


def _cardinality(mt_n: int, lxx_n: int) -> Cardinality:
    if mt_n == 0 and lxx_n == 0:
        return "zero_zero"
    if mt_n == 0:
        return "zero_many"
    if lxx_n == 0:
        return "many_zero"
    if mt_n == 1 and lxx_n == 1:
        return "one_one"
    if mt_n == 1:
        return "one_many"
    if lxx_n == 1:
        return "many_one"
    return "many_many"
