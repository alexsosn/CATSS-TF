"""Query-native Text-Fabric feature schema shared by CATSS projections."""

import dataclasses
import pathlib
import typing

from catss_tf.source import CATSS_PARALLEL_FILENAMES


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


@dataclasses.dataclass(frozen=True, slots=True)
class TfAnchorEvent:
    """One Hebrew- or Greek-empty CATSS group anchored to a parent structure node."""

    node: int
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

_AGGREGATE_BY_FLAG = {
    flag: f"{flag}_members"
    for flag in _MEMBERSHIP_FLAGS
}

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
    if base_name not in _LANE_CORE and base_name not in _MEMBERSHIP_FLAGS:
        raise TfSchemaError(f"unknown lane feature {base_name!r}")
    return base_name if lane == 1 else f"{base_name}_2"


def _make_feature_specs() -> dict[str, TfFeatureSpec]:
    specs: dict[str, TfFeatureSpec] = {}

    for base_name, (value_type, description) in _LANE_CORE.items():
        for lane in (1, 2):
            name = lane_feature_name(base_name, lane)
            lane_description = description if lane == 1 else f"{description} (membership lane 2)"
            specs[name] = TfFeatureSpec(name, value_type, lane_description)

    for base_name, description in _MEMBERSHIP_FLAGS.items():
        for lane in (1, 2):
            name = lane_feature_name(base_name, lane)
            lane_description = description if lane == 1 else f"{description} (membership lane 2)"
            specs[name] = TfFeatureSpec(name, "int", lane_description)

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
    "catss-annotations.tsv": (
        "source",
        "alignment_id",
        "side",
        "kind",
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
    "catss-diagnostics.tsv": (
        "stage",
        "severity",
        "code",
        "source",
        "alignment_id",
        "line_no",
        "message",
    ),
}

_SOURCE_RANK = {
    source: index
    for index, source in enumerate(CATSS_PARALLEL_FILENAMES)
}
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

    for anchor in anchors:
        _validate_parent_node(max_node, anchor.node)
        if anchor.kind not in _ANCHOR_KINDS[projection]:
            raise TfSchemaError(
                f"anchor kind {anchor.kind!r} is invalid for {projection} projection"
            )
        if anchor.token_n < 0:
            raise TfSchemaError(f"anchor token_n must be non-negative, got {anchor.token_n}")

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
    for base_name, value in values.items():
        if value is not None:
            _put(features, lane_feature_name(base_name, lane), node, value)

    for flag in _effective_flags(membership):
        _put(features, lane_feature_name(flag, lane), node, 1)


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
    if not membership.alignment_id.startswith("catss:"):
        raise TfSchemaError(f"invalid CATSS alignment id {membership.alignment_id!r}")

    for name, value in (
        ("mt_n", membership.mt_n),
        ("lxx_n", membership.lxx_n),
        ("line_first", membership.line_first),
        ("line_last", membership.line_last),
        ("line_n", membership.line_n),
    ):
        if value < 0:
            raise TfSchemaError(f"{name} must be non-negative, got {value}")

    if membership.line_n < 1:
        raise TfSchemaError("line_n must be at least 1")
    if membership.line_last < membership.line_first:
        raise TfSchemaError("line_last precedes line_first")

    for name, value in (
        ("mt_i", membership.mt_i),
        ("mt_segment", membership.mt_segment),
        ("lxx_i", membership.lxx_i),
    ):
        if value is not None and value < 1:
            raise TfSchemaError(f"{name} is 1-based and must be positive, got {value}")

    unknown_flags = membership.flags - MEMBERSHIP_FLAGS
    if unknown_flags:
        raise TfSchemaError(
            "unknown CATSS flag(s): " + ", ".join(sorted(unknown_flags))
        )
    if "catss_retro" in membership.flags and membership.retro_kind is None:
        raise TfSchemaError("catss_retro requires a structured retro_kind")


def _validate_parent_node(max_node: int, node: int) -> None:
    if not 1 <= node <= max_node:
        raise TfSchemaError(
            f"parent node {node} is outside validated parent range 1..{max_node}"
        )


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
    features.setdefault(feature, {})[node] = value


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
