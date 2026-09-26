"""Query-native Text-Fabric feature schema shared by CATSS projections."""

import dataclasses
import pathlib
import typing

from catss_tf.notation import documented_specs, semantic_feature_name
from catss_tf.source import CATSS_PARALLEL_FILENAMES
from catss_tf.technique import TECHNIQUE_SCHEMA_VERSION, TechniqueError, derive_technique_state

SCHEMA_VERSION = "1"
WARP_FEATURES = frozenset({"otype", "oslots", "otext"})
MAX_MEMBERSHIP_LANES = 2
Projection = typing.Literal["bhsa", "lxx"]
ValueType = typing.Literal["int", "str"]
FeatureValue = int | str


class TfSchemaError(ValueError):
    """Raised when data cannot be represented faithfully by TF schema v1."""


@dataclasses.dataclass(frozen=True, slots=True)
class TfFeatureSpec:
    """One scalar Text-Fabric node-feature contract."""

    name: str
    value_type: ValueType
    description: str


@dataclasses.dataclass(frozen=True, slots=True)
class TfMembership:
    """One CATSS alignment membership of an existing parent word node."""

    node: int
    source: str
    alignment_id: str
    mapping_kind: str
    mt_n: int
    lxx_n: int
    mt_i: int | None
    mt_segment: int | None
    lxx_i: int | None
    line_first: int
    line_last: int
    line_n: int
    retro_kind: str | None
    flags: frozenset[str] = frozenset()
    annotation_payloads: tuple[tuple[str, str], ...] = ()
    semantic_kinds: tuple[str, ...] = ()
    semantic_payloads: tuple[tuple[str, str], ...] = ()


@dataclasses.dataclass(frozen=True, slots=True)
class TfAnchorEvent:
    """One Hebrew- or Greek-empty CATSS group anchored to a parent structure node."""

    node: int
    source: str
    alignment_id: str
    kind: typing.Literal["lxx_plus", "lxx_minus", "transposition_placeholder"]
    token_n: int = 0


@dataclasses.dataclass(frozen=True, slots=True)
class TfModuleMetadata:
    """Generic metadata written to every CATSS Text-Fabric feature."""

    projection: Projection
    parent_repo: str
    parent_version: str
    parent_release: str | None
    parent_commit: str | None
    software_version: str


_LANE_CORE: dict[str, tuple[ValueType, str]] = {
    "catss_alignment_id": ("str", "stable CATSS alignment identity"),
    "catss_source": ("str", "CATSS parallel source filename"),
    "catss_mapping": ("str", "resolver mapping kind"),
    "catss_mt_n": ("int", "number of CATSS MT alignment elements"),
    "catss_lxx_n": ("int", "number of CATSS Greek lexical elements"),
    "catss_mt_i": ("int", "1-based MT alignment-element position"),
    "catss_mt_segment": ("int", "1-based segment within an explicit CATSS maqaf compound"),
    "catss_lxx_i": ("int", "1-based Greek lexical-element position"),
    "catss_line_first": ("int", "first physical CATSS source line"),
    "catss_line_last": ("int", "last physical CATSS source line"),
    "catss_line_n": ("int", "number of physical CATSS source lines"),
    "catss_retro_kind": ("str", "normalized CATSS column-B retroversion kind"),
}

_TECHNIQUE_LANE_CORE: dict[str, tuple[ValueType, str]] = {
    "catss_tt_cardinality_mt_lxx": (
        "str",
        "derived MT↔LXX token-cardinality class",
    ),
    "catss_tt_token_balance_mt_lxx": (
        "str",
        "derived MT↔LXX token-count balance; not a semantic expansion judgment",
    ),
    "catss_tt_transposition_mt_lxx": (
        "str",
        "derived CATSS transposition-evidence class for MT↔LXX",
    ),
    "catss_tt_addition_vs_mt": (
        "int",
        "derived flag: CATSS explicitly marks Greek material as LXX addition versus MT",
    ),
    "catss_tt_omission_vs_mt": (
        "int",
        "derived flag: CATSS explicitly marks MT material as omitted in LXX",
    ),
}

_MEMBERSHIP_FLAGS: dict[str, str] = {
    "catss_lxx_plus": "CATSS LXX-plus alignment",
    "catss_lxx_minus": "CATSS LXX-minus alignment",
    "catss_retro": "CATSS column-B retroversion is present",
    "catss_ketiv": "CATSS MT alignment has Ketiv evidence",
    "catss_qere": "CATSS MT alignment has Qere evidence",
    "catss_trans_local": "CATSS local transposition",
    "catss_trans_remote": "CATSS remote/reflected-elsewhere transposition",
    "catss_trans_style": "CATSS stylistic or grammatical transposition",
    "catss_doublet": "CATSS doublet annotation",
    "catss_translit": "CATSS transliteration annotation",
    "catss_apparent_pm": "CATSS apparent plus/minus annotation",
    "catss_agrees_ketiv": "Greek agrees with CATSS Ketiv",
    "catss_agrees_qere": "Greek agrees with CATSS Qere",
    "catss_metathesis": "CATSS metathesis strategy annotation",
    "catss_word_separation": "CATSS word-separation strategy annotation",
    "catss_word_join": "CATSS word-join strategy annotation",
    "catss_word_division": "CATSS word-division strategy annotation",
    "catss_abbreviation": "CATSS abbreviation strategy annotation",
    "catss_greek_preverb": "CATSS Greek-preverb strategy annotation",
    "catss_comparative": "CATSS comparative/superlative strategy annotation",
    "catss_asterisked": "CATSS asterisked-passage annotation",
    "catss_doubt": "CATSS doubt marker",
    "catss_greek_diff": "CATSS Rahlfs/Göttingen difference annotation",
    "catss_greek_correction": "CATSS Greek correction annotation",
    "catss_prep_added": "CATSS added-preposition annotation",
    "catss_distributive": "CATSS distributive-rendering annotation",
    "catss_repetition": "CATSS repetition annotation",
}

_RAW_SEMANTIC_KINDS = frozenset(
    {
        "abbreviation",
        "contextual_reference",
        "distributive",
        "doubt",
        "greek_correction",
        "greek_edition_difference",
        "letter_interchange",
        "metathesis",
        "possible_doublet",
        "preposition_added",
        "repetition",
        "sirach_lacuna_in_witness",
        "source_note",
        "transposition_remote",
        "transposition_stylistic",
        "verse_reference",
        "word_division",
        "word_join",
        "word_separation",
    }
)

_ANNOTATION_PAYLOAD_SPECS: dict[str, str] = {
    "catss_distributive_payload": "CATSS distributive-rendering contextual payload",
    "catss_prep_added_payload": "CATSS added-preposition contextual payload",
    "catss_repetition_payload": "CATSS repetition contextual payload",
    "catss_trans_remote_payload": "CATSS remote-transposition contextual payload",
    "catss_trans_style_payload": "CATSS stylistic-transposition contextual payload",
}

_AGGREGATE_BY_FLAG = {flag: f"{flag}_members" for flag in _MEMBERSHIP_FLAGS}

_ANCHOR_SPECS: dict[str, tuple[ValueType, str]] = {
    "catss_lxx_plus_n": ("int", "number of CATSS Hebrew-empty/LXX-plus groups on this verse"),
    "catss_lxx_plus_token_n": (
        "int",
        "total Greek lexical elements in CATSS LXX-plus groups on this verse",
    ),
    "catss_lxx_minus_n": ("int", "number of CATSS Greek-empty/LXX-minus groups"),
    "catss_transposition_placeholder_n": (
        "int",
        "number of CATSS Greek-empty transposition placeholder groups",
    ),
}


def lane_feature_name(base_name: str, lane: int) -> str:
    """Return the feature name for one of the two explicit membership lanes."""

    if lane not in {1, 2}:
        raise TfSchemaError(f"membership lane must be 1 or 2, got {lane}")
    if (
        base_name not in _LANE_CORE
        and base_name not in _TECHNIQUE_LANE_CORE
        and base_name not in _MEMBERSHIP_FLAGS
    ):
        raise TfSchemaError(f"unknown lane feature {base_name!r}")
    return base_name if lane == 1 else f"{base_name}_2"


def _make_feature_specs() -> dict[str, TfFeatureSpec]:
    specs: dict[str, TfFeatureSpec] = {}

    for base_name, (value_type, description) in _LANE_CORE.items():
        for lane in (1, 2):
            name = lane_feature_name(base_name, lane)
            lane_description = description if lane == 1 else f"{description} (membership lane 2)"
            specs[name] = TfFeatureSpec(name, value_type, lane_description)

    for base_name, (value_type, description) in _TECHNIQUE_LANE_CORE.items():
        for lane in (1, 2):
            name = lane_feature_name(base_name, lane)
            lane_description = description if lane == 1 else f"{description} (membership lane 2)"
            specs[name] = TfFeatureSpec(name, value_type, lane_description)

    for base_name, description in _MEMBERSHIP_FLAGS.items():
        for lane in (1, 2):
            name = lane_feature_name(base_name, lane)
            lane_description = description if lane == 1 else f"{description} (membership lane 2)"
            specs[name] = TfFeatureSpec(name, "int", lane_description)

    for name, description in _ANNOTATION_PAYLOAD_SPECS.items():
        for lane in (1, 2):
            lane_name = name if lane == 1 else f"{name}_2"
            lane_description = description if lane == 1 else f"{description} (membership lane 2)"
            specs[lane_name] = TfFeatureSpec(lane_name, "str", lane_description)

    semantic_specs = {spec.kind: spec for spec in documented_specs().values()}
    semantic_kinds = set(semantic_specs) | set(_RAW_SEMANTIC_KINDS)
    for kind in sorted(semantic_kinds):
        semantic = semantic_specs.get(kind)
        base_name = semantic_feature_name(semantic) if semantic is not None else f"catss_sem_{kind}"
        for lane in (1, 2):
            name = base_name if lane == 1 else f"{base_name}_2"
            suffix = "" if lane == 1 else " (membership lane 2)"
            specs[name] = TfFeatureSpec(
                name,
                "int",
                f"CATSS semantic annotation: {kind}{suffix}",
            )
            payload_base = f"{base_name}_payload"
            payload_name = payload_base if lane == 1 else f"{payload_base}_2"
            specs[payload_name] = TfFeatureSpec(
                payload_name,
                "str",
                f"CATSS semantic payload for {kind}{suffix}",
            )

    specs["catss_alignment_n"] = TfFeatureSpec(
        "catss_alignment_n",
        "int",
        "number of CATSS alignment memberships on this parent word node",
    )

    for flag, aggregate_name in _AGGREGATE_BY_FLAG.items():
        specs[aggregate_name] = TfFeatureSpec(
            aggregate_name,
            "int",
            f"number of CATSS memberships with {flag}",
        )

    for name, (value_type, description) in _ANCHOR_SPECS.items():
        specs[name] = TfFeatureSpec(name, value_type, description)

    return specs


FEATURE_SPECS = _make_feature_specs()
MEMBERSHIP_FLAGS = frozenset(_MEMBERSHIP_FLAGS)

SIDECAR_COLUMNS: dict[str, tuple[str, ...]] = {
    "catss-alignments.tsv": (
        "source",
        "alignment_id",
        "book",
        "chapter",
        "verse",
        "line_first",
        "line_last",
        "line_n",
        "mt_raw",
        "mt_col_a",
        "mt_col_b",
        "retro_kind",
        "mt_n",
        "lxx_raw",
        "lxx_n",
        "lxx_plus",
        "lxx_minus",
        "ketiv",
        "qere",
        "trans_local",
        "trans_remote",
        "trans_style",
    ),
    "catss-technique.tsv": (
        "source",
        "alignment_id",
        "comparison_base",
        "cardinality_mt_lxx",
        "token_balance_mt_lxx",
        "addition_vs_mt",
        "omission_vs_mt",
        "transposition_mt_lxx",
    ),
    "catss-annotations.tsv": (
        "source",
        "alignment_id",
        "side",
        "kind",
        "family",
        "contextual",
        "payload",
        "raw",
    ),
    "catss-mappings.tsv": (
        "projection",
        "source",
        "alignment_id",
        "parent_node",
        "lane",
        "mapping_kind",
        "mt_i",
        "mt_segment",
        "lxx_i",
    ),
    "catss-anchors.tsv": (
        "projection",
        "source",
        "alignment_id",
        "parent_node",
        "anchor_kind",
        "token_n",
    ),
    "catss-sources.tsv": (
        "source",
        "size_bytes",
        "sha256",
    ),
    "catss-source-lines.tsv": (
        "source",
        "alignment_id",
        "line_no",
        "raw",
    ),
    "catss-diagnostics.tsv": (
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
    ),
}

_SOURCE_RANK = {source: index for index, source in enumerate(CATSS_PARALLEL_FILENAMES)}
_ROLE_PRIORITY = {
    "exact": 0,
    "ketiv_qere": 0,
    "qere": 0,
    "transposition_alignment": 0,
    "transposition_carrier": 1,
}
_MAPPING_KINDS: dict[Projection, frozenset[str]] = {
    "bhsa": frozenset({"exact", "ketiv_qere", "qere"}),
    "lxx": frozenset({"exact", "transposition_alignment", "transposition_carrier"}),
}
_ANCHOR_KINDS: dict[Projection, frozenset[str]] = {
    "bhsa": frozenset({"lxx_plus"}),
    "lxx": frozenset({"lxx_minus", "transposition_placeholder"}),
}


def compile_tf_features(
    *,
    projection: Projection,
    max_node: int,
    memberships: tuple[TfMembership, ...],
    anchors: tuple[TfAnchorEvent, ...],
) -> dict[str, dict[int, FeatureValue]]:
    """Compile generic resolver facts into sparse query-native TF node features."""

    if projection not in _MAPPING_KINDS:
        raise TfSchemaError(f"unknown projection {projection!r}")
    if max_node < 1:
        raise TfSchemaError(f"invalid parent maxNode {max_node}")

    by_node: dict[int, list[TfMembership]] = {}
    for membership in memberships:
        _validate_membership(projection, max_node, membership)
        by_node.setdefault(membership.node, []).append(membership)

    features: dict[str, dict[int, FeatureValue]] = {}

    for node in sorted(by_node):
        node_memberships = sorted(by_node[node], key=_membership_sort_key)
        identities = [
            (
                membership.source,
                membership.alignment_id,
                membership.mapping_kind,
                membership.mt_i,
                membership.mt_segment,
                membership.lxx_i,
            )
            for membership in node_memberships
        ]
        if len(identities) != len(set(identities)):
            raise TfSchemaError(
                f"duplicate_membership: parent node {node} repeats one CATSS mapping record"
            )
        alignment_identities = [
            (membership.source, membership.alignment_id) for membership in node_memberships
        ]
        if len(alignment_identities) != len(set(alignment_identities)):
            raise TfSchemaError(
                "duplicate_alignment_membership: "
                f"parent node {node} repeats one CATSS alignment identity"
            )
        if len(node_memberships) > MAX_MEMBERSHIP_LANES:
            raise TfSchemaError(
                "membership_overflow: "
                f"parent node {node} has {len(node_memberships)} CATSS memberships; "
                f"schema v{SCHEMA_VERSION} supports {MAX_MEMBERSHIP_LANES}"
            )

        _put(features, "catss_alignment_n", node, len(node_memberships))
        aggregate_counts = {flag: 0 for flag in _MEMBERSHIP_FLAGS}

        for lane, membership in enumerate(node_memberships, start=1):
            _compile_membership(features, node, lane, membership)
            effective_flags = _effective_flags(membership)
            for flag in effective_flags:
                aggregate_counts[flag] += 1

        for flag, count in aggregate_counts.items():
            if count:
                _put(features, _AGGREGATE_BY_FLAG[flag], node, count)

    seen_anchors: set[tuple[str, str]] = set()
    for anchor in anchors:
        _validate_parent_node(max_node, anchor.node)
        if anchor.source not in _SOURCE_RANK:
            raise TfSchemaError(f"unknown CATSS source {anchor.source!r}")
        _validate_alignment_source(anchor.source, anchor.alignment_id)
        anchor_identity = (anchor.source, anchor.alignment_id)
        if anchor_identity in seen_anchors:
            raise TfSchemaError(f"duplicate_anchor: {anchor.source} {anchor.alignment_id}")
        seen_anchors.add(anchor_identity)
        if anchor.kind not in _ANCHOR_KINDS[projection]:
            raise TfSchemaError(
                f"anchor kind {anchor.kind!r} is invalid for {projection} projection"
            )
        if anchor.token_n < 0:
            raise TfSchemaError(f"anchor token_n must be non-negative, got {anchor.token_n}")
        if anchor.kind == "lxx_plus" and anchor.token_n < 1:
            raise TfSchemaError("lxx_plus anchor requires token_n >= 1")
        if anchor.kind != "lxx_plus" and anchor.token_n != 0:
            raise TfSchemaError(f"{anchor.kind} anchor requires token_n=0")

        if anchor.kind == "lxx_plus":
            _increment(features, "catss_lxx_plus_n", anchor.node, 1)
            _increment(features, "catss_lxx_plus_token_n", anchor.node, anchor.token_n)
        elif anchor.kind == "lxx_minus":
            _increment(features, "catss_lxx_minus_n", anchor.node, 1)
        else:
            _increment(features, "catss_transposition_placeholder_n", anchor.node, 1)

    return features


def _compile_membership(
    features: dict[str, dict[int, FeatureValue]],
    node: int,
    lane: int,
    membership: TfMembership,
) -> None:
    values: dict[str, FeatureValue | None] = {
        "catss_alignment_id": membership.alignment_id,
        "catss_source": membership.source,
        "catss_mapping": membership.mapping_kind,
        "catss_mt_n": membership.mt_n,
        "catss_lxx_n": membership.lxx_n,
        "catss_mt_i": membership.mt_i,
        "catss_mt_segment": membership.mt_segment,
        "catss_lxx_i": membership.lxx_i,
        "catss_line_first": membership.line_first,
        "catss_line_last": membership.line_last,
        "catss_line_n": membership.line_n,
        "catss_retro_kind": membership.retro_kind,
    }
    for kind in membership.semantic_kinds:
        feature_name = f"catss_sem_{kind}" if lane == 1 else f"catss_sem_{kind}_2"
        _put(features, feature_name, node, 1)
    for kind, payload in membership.semantic_payloads:
        base_name = f"catss_sem_{kind}_payload"
        feature_name = base_name if lane == 1 else f"{base_name}_2"
        _put(features, feature_name, node, payload)

    for payload_name, payload in membership.annotation_payloads:
        if payload_name not in _ANNOTATION_PAYLOAD_SPECS:
            raise TfSchemaError(f"unknown annotation payload feature {payload_name!r}")
        feature_name = payload_name if lane == 1 else f"{payload_name}_2"
        _put(features, feature_name, node, payload)

    for base_name, value in values.items():
        if value is not None:
            _put(features, lane_feature_name(base_name, lane), node, value)

    for flag in _effective_flags(membership):
        _put(features, lane_feature_name(flag, lane), node, 1)

    try:
        technique = derive_technique_state(
            mt_n=membership.mt_n,
            lxx_n=membership.lxx_n,
            is_lxx_plus="catss_lxx_plus" in membership.flags,
            is_lxx_minus="catss_lxx_minus" in membership.flags,
            trans_local="catss_trans_local" in membership.flags,
            trans_remote="catss_trans_remote" in membership.flags,
            trans_style="catss_trans_style" in membership.flags,
        )
    except TechniqueError as exc:
        raise TfSchemaError(f"technique derivation failed: {exc}") from exc

    technique_values: dict[str, FeatureValue] = {
        "catss_tt_cardinality_mt_lxx": technique.cardinality_mt_lxx,
        "catss_tt_token_balance_mt_lxx": technique.token_balance_mt_lxx,
        "catss_tt_transposition_mt_lxx": technique.transposition_mt_lxx,
    }
    if technique.addition_vs_mt:
        technique_values["catss_tt_addition_vs_mt"] = 1
    if technique.omission_vs_mt:
        technique_values["catss_tt_omission_vs_mt"] = 1

    for base_name, value in technique_values.items():
        _put(features, lane_feature_name(base_name, lane), node, value)


def _effective_flags(membership: TfMembership) -> frozenset[str]:
    flags = set(membership.flags)
    if membership.retro_kind is not None:
        flags.add("catss_retro")
    return frozenset(flags)


def _validate_membership(
    projection: Projection,
    max_node: int,
    membership: TfMembership,
) -> None:
    _validate_parent_node(max_node, membership.node)

    if membership.source not in _SOURCE_RANK:
        raise TfSchemaError(f"unknown CATSS source {membership.source!r}")
    if membership.mapping_kind not in _MAPPING_KINDS[projection]:
        raise TfSchemaError(
            f"mapping kind {membership.mapping_kind!r} is invalid for {projection} projection"
        )
    _validate_alignment_source(membership.source, membership.alignment_id)

    for name, value in (("mt_n", membership.mt_n), ("lxx_n", membership.lxx_n)):
        if value < 0:
            raise TfSchemaError(f"{name} must be non-negative, got {value}")

    if membership.line_first < 1 or membership.line_last < 1:
        raise TfSchemaError("CATSS source line numbers are 1-based and must be positive")
    if membership.line_n < 1:
        raise TfSchemaError("line_n must be at least 1")
    if membership.line_last < membership.line_first:
        raise TfSchemaError("line_last precedes line_first")

    for name, optional_index in (
        ("mt_i", membership.mt_i),
        ("mt_segment", membership.mt_segment),
        ("lxx_i", membership.lxx_i),
    ):
        if optional_index is not None and optional_index < 1:
            raise TfSchemaError(f"{name} is 1-based and must be positive, got {optional_index}")

    if membership.mt_i is not None and membership.mt_i > membership.mt_n:
        raise TfSchemaError(f"mt_i {membership.mt_i} exceeds CATSS mt_n {membership.mt_n}")
    if membership.lxx_i is not None and membership.lxx_i > membership.lxx_n:
        raise TfSchemaError(f"lxx_i {membership.lxx_i} exceeds CATSS lxx_n {membership.lxx_n}")

    if projection == "bhsa" and (membership.mt_n < 1 or membership.mt_i is None):
        raise TfSchemaError("BHSA membership requires a non-empty CATSS MT side and mt_i")
    if projection == "lxx" and (membership.lxx_n < 1 or membership.lxx_i is None):
        raise TfSchemaError("LXX membership requires a non-empty CATSS Greek side and lxx_i")

    unknown_flags = membership.flags - MEMBERSHIP_FLAGS
    if unknown_flags:
        raise TfSchemaError("unknown CATSS flag(s): " + ", ".join(sorted(unknown_flags)))
    if "catss_retro" in membership.flags and membership.retro_kind is None:
        raise TfSchemaError("catss_retro requires a structured retro_kind")


def _validate_alignment_source(source: str, alignment_id: str) -> None:
    expected_prefix = f"catss:{source}:"
    if not alignment_id.startswith("catss:"):
        raise TfSchemaError(f"invalid CATSS alignment id {alignment_id!r}")
    if not alignment_id.startswith(expected_prefix):
        raise TfSchemaError(
            f"alignment id source mismatch: expected prefix {expected_prefix!r}, "
            f"got {alignment_id!r}"
        )


def _validate_parent_node(max_node: int, node: int) -> None:
    if not 1 <= node <= max_node:
        raise TfSchemaError(f"parent node {node} is outside validated parent range 1..{max_node}")


def _membership_sort_key(
    membership: TfMembership,
) -> tuple[int, int, str, int, int, int]:
    return (
        _SOURCE_RANK[membership.source],
        _ROLE_PRIORITY[membership.mapping_kind],
        membership.alignment_id,
        membership.mt_i or 0,
        membership.mt_segment or 0,
        membership.lxx_i or 0,
    )


def _put(
    features: dict[str, dict[int, FeatureValue]],
    feature: str,
    node: int,
    value: FeatureValue,
) -> None:
    data = features.setdefault(feature, {})
    existing = data.get(node)
    if existing is not None and existing != value:
        raise TfSchemaError(
            f"conflicting feature value for {feature} on parent node {node}: "
            f"{existing!r} != {value!r}"
        )
    data[node] = value


def _increment(
    features: dict[str, dict[int, FeatureValue]],
    feature: str,
    node: int,
    amount: int,
) -> None:
    data = features.setdefault(feature, {})
    current = data.get(node, 0)
    if not isinstance(current, int):
        raise TfSchemaError(f"cannot increment non-integer feature {feature}")
    data[node] = current + amount


def write_tf_module(
    directory: pathlib.Path,
    node_features: dict[str, dict[int, FeatureValue]],
    *,
    metadata: TfModuleMetadata,
    max_node: int,
) -> None:
    """Write weft-only TF feature files with the frozen CATSS schema metadata."""

    if metadata.projection not in {"bhsa", "lxx"}:
        raise TfSchemaError(f"unknown projection {metadata.projection!r}")
    if WARP_FEATURES & set(node_features):
        names = ", ".join(sorted(WARP_FEATURES & set(node_features)))
        raise TfSchemaError(f"CATSS module must not contain warp feature(s): {names}")

    directory.mkdir(parents=True, exist_ok=True)
    existing_warp = tuple(name for name in WARP_FEATURES if (directory / f"{name}.tf").exists())
    if existing_warp:
        raise TfSchemaError(
            "CATSS module directory already contains warp feature(s): "
            + ", ".join(sorted(existing_warp))
        )
    existing_tf = tuple(sorted(path.name for path in directory.glob("*.tf") if path.is_file()))
    if existing_tf:
        raise TfSchemaError(
            "CATSS module directory already contains TF feature file(s): " + ", ".join(existing_tf)
        )

    for feature in sorted(node_features):
        spec = FEATURE_SPECS.get(feature)
        if spec is None:
            raise TfSchemaError(f"feature {feature!r} is not part of CATSS TF schema v1")

        data = node_features[feature]
        for node, value in data.items():
            _validate_parent_node(max_node, node)
            if spec.value_type == "int":
                if not isinstance(value, int) or isinstance(value, bool):
                    raise TfSchemaError(f"{feature} expects int values")
            elif not isinstance(value, str):
                raise TfSchemaError(f"{feature} expects str values")

        _write_feature_file(directory / f"{feature}.tf", spec, data, metadata)


def _write_feature_file(
    path: pathlib.Path,
    spec: TfFeatureSpec,
    data: dict[int, FeatureValue],
    metadata: TfModuleMetadata,
) -> None:
    headers = [
        "@node",
        f"@valueType={spec.value_type}",
        f"@description={_header_value(spec.description)}",
        f"@catssSchema={SCHEMA_VERSION}",
        f"@catssProjection={metadata.projection}",
        "@catssSourceKind=catss-parallel",
        "@writtenBy=CATSS-TF",
        f"@softwareVersion={_header_value(metadata.software_version)}",
        f"@parentRepo={_header_value(metadata.parent_repo)}",
        f"@parentVersion={_header_value(metadata.parent_version)}",
    ]
    if spec.name.startswith("catss_tt_"):
        headers.append(f"@catssTechniqueSchema={TECHNIQUE_SCHEMA_VERSION}")
    if metadata.parent_release:
        headers.append(f"@parentRelease={_header_value(metadata.parent_release)}")
    if metadata.parent_commit:
        headers.append(f"@parentCommit={_header_value(metadata.parent_commit)}")

    lines = [*headers, ""]
    for node in sorted(data):
        value = data[node]
        rendered = str(value) if isinstance(value, int) else _feature_value(value)
        lines.append(f"{node}\t{rendered}")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _header_value(value: str) -> str:
    if "\n" in value or "\r" in value:
        raise TfSchemaError("TF feature metadata values must be single-line")
    return value


def _feature_value(value: str) -> str:
    return value.replace("\\", "\\\\").replace("\t", "\\t").replace("\n", "\\n")
