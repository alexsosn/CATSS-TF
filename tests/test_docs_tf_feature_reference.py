"""Keep the public TF feature/otype/API dictionary aligned with code."""

import ast
from pathlib import Path

from catss_tf import __all__ as public_symbols
from catss_tf import tf_schema
from catss_tf.notation import documented_semantic_specs

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/tf-feature-reference.md"
CANONICAL = ROOT / "src/catss_tf/canonical_materializer.py"

CATEGORIES = {
    "Lane core",
    "Technique",
    "Membership flag",
    "Payload",
    "Semantic",
    "Anchor",
    "Reference range",
    "Aggregate",
    "Canonical feature",
    "Canonical node",
    "Canonical edge",
    "Public API",
}


def _actual() -> dict[str, dict[str, str]]:
    assert DOC.is_file(), "missing complete TF feature and public API reference"
    result: dict[str, dict[str, str]] = {category: {} for category in CATEGORIES}
    for line in DOC.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| "):
            continue
        fields = [field.strip() for field in line.strip().strip("|").split("|")]
        if len(fields) != 4 or fields[0] not in CATEGORIES:
            continue
        category, identifier, value_type, meaning = fields
        assert identifier.startswith("`") and identifier.endswith("`"), line
        assert value_type in {"str", "int", "node", "edge", "Python"}, line
        assert meaning and meaning != "TODO", line
        name = identifier[1:-1]
        assert name not in result[category], (category, name)
        result[category][name] = value_type
    return result


def _canonical_source() -> tuple[set[str], set[str], set[str]]:
    tree = ast.parse(CANONICAL.read_text(encoding="utf-8"))
    otypes: set[str] = {"alignment"}
    features: set[str] = set()
    edges: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            continue
        if not isinstance(node.func.value, ast.Name) or node.func.value.id != "builder":
            continue
        if not node.args or not isinstance(node.args[0], ast.Constant):
            continue
        name = node.args[0].value
        if not isinstance(name, str):
            continue
        if node.func.attr == "add_node":
            otypes.add(name)
        elif node.func.attr == "feature":
            features.add(name)
        elif node.func.attr == "edge":
            edges.add(name)
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        if isinstance(node, ast.AnnAssign):
            names = [node.target.id] if isinstance(node.target, ast.Name) else []
        else:
            names = [target.id for target in node.targets if isinstance(target, ast.Name)]
        if not any(name in {"values", "flags"} for name in names):
            continue
        if not isinstance(node.value, ast.Dict):
            continue
        features.update(
            key.value
            for key in node.value.keys
            if isinstance(key, ast.Constant) and isinstance(key.value, str)
        )
    return otypes, features, edges


def _parent_expected() -> dict[str, dict[str, str]]:
    expected = {
        "Lane core": {key: kind for key, (kind, _) in tf_schema._LANE_CORE.items()},
        "Technique": {key: kind for key, (kind, _) in tf_schema._TECHNIQUE_LANE_CORE.items()},
        "Membership flag": {key: "int" for key in tf_schema._MEMBERSHIP_FLAGS},
        "Payload": {key: "str" for key in tf_schema._ANNOTATION_PAYLOAD_SPECS},
        "Semantic": {
            key: "int"
            for key in set(documented_semantic_specs()) | set(tf_schema._RAW_SEMANTIC_KINDS)
        },
        "Anchor": {key: kind for key, (kind, _) in tf_schema._ANCHOR_SPECS.items()},
        "Reference range": {
            key: kind for key, (kind, _) in tf_schema._REFERENCE_RANGE_SPECS.items()
        },
        "Aggregate": {
            "catss_alignment_n": "int",
            **{name: "int" for name in tf_schema._AGGREGATE_BY_FLAG.values()},
        },
    }
    return expected


def test_reference_accounts_for_parent_schema_and_public_api() -> None:
    actual = _actual()
    expected = _parent_expected()
    for category, category_items in expected.items():
        assert actual[category] == category_items, category
    assert actual["Public API"] == {key: "Python" for key in public_symbols}


def test_reference_accounts_for_canonical_nodes_edges_and_features() -> None:
    actual = _actual()
    types, features, edges = _canonical_source()
    assert actual["Canonical node"] == {name: "node" for name in types}
    assert actual["Canonical edge"] == {name: "edge" for name in edges}
    assert set(actual["Canonical feature"]) == features


def test_declared_parent_feature_expansion_is_exact() -> None:
    """The docs' small base tables describe EVERY generated feature name."""
    actual = _actual()
    expanded: set[str] = set()
    for group in ("Lane core", "Technique", "Membership flag", "Payload"):
        for base in actual[group]:
            expanded.update((base, base + "_2"))
    for kind in actual["Semantic"]:
        base = f"catss_sem_{kind}"
        for scope in ("", "_mt_a", "_mt_b", "_lxx"):
            name = base + scope
            for lane in ("", "_2"):
                expanded.add(name + lane)
                expanded.add(name + "_payload" + lane)
    for group in ("Anchor", "Reference range", "Aggregate"):
        expanded.update(actual[group])
    assert expanded == set(tf_schema.FEATURE_SPECS)
    assert all(
        actual[group][key] == tf_schema.FEATURE_SPECS[key].value_type
        for group in ("Anchor", "Reference range", "Aggregate")
        for key in actual[group]
    )


def test_reference_documents_warp_and_scope_warnings() -> None:
    text = DOC.read_text(encoding="utf-8") if DOC.is_file() else ""
    for phrase in (
        "`catss_sem_<kind>`",
        "`catss_sem_<kind>_mt_b_payload_2`",
        "`alignment`",
        "`catss_annotation_target`",
        "`otype`",
        "`oslots`",
        "`otext`",
        "not a manuscript attestation",
        "missing values",
        "different node identifiers",
    ):
        assert phrase in text
