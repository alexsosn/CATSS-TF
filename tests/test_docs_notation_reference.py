"""Prevent drift between source CATSS sigla, canonical annotations and docs."""

from pathlib import Path

import pytest

from catss_tf import notation
from catss_tf.tf_schema import FEATURE_SPECS

PAGE = Path(__file__).resolve().parents[1] / "docs/notation-reference.md"


def _table_rows() -> list[tuple[str, ...]]:
    """Read literal Markdown table fields; no scraped or licensed CATSS data."""
    assert PAGE.is_file(), "missing the researcher notation dictionary"
    result: list[tuple[str, ...]] = []
    for line in PAGE.read_text(encoding="utf-8").splitlines():
        if not line.startswith(("| General |", "| Sirach |", "| Pattern |")):
            continue
        cells = tuple(part.strip() for part in line.strip().strip("|").split("|"))
        assert len(cells) == 7, f"expected seven table fields: {line}"
        assert cells[1].startswith("`") and cells[1].endswith("`"), line
        assert cells[5].startswith("`") and cells[5].endswith("`"), line
        assert cells[6].startswith("`") and cells[6].endswith("`"), line
        result.append(cells)
    return result


def _actual() -> dict[tuple[str, str], tuple[str, str, str, str]]:
    rows = _table_rows()
    result: dict[tuple[str, str], tuple[str, str, str, str]] = {}
    for profile, symbol, meaning, family, contextual, kind, feature in rows:
        key = (profile, symbol[1:-1])
        assert key not in result, f"duplicate catalogue entry: {key}"
        assert meaning and meaning != "TODO", key
        assert contextual in {"yes", "no"}, key
        result[key] = (family, contextual, kind[1:-1], feature[1:-1])
    return result


def test_general_and_sirach_catalogues_complete_and_typechecked() -> None:
    actual = _actual()
    expected = {
        (profile, raw): (
            spec.family,
            "yes" if spec.contextual else "no",
            spec.kind,
            notation.semantic_feature_name(spec),
        )
        for profile, entries in (
            ("General", notation._GENERAL),
            ("Sirach", notation._SIRACH),
        )
        for raw, spec in entries.items()
    }
    assert {key: actual[key] for key in actual if key[0] != "Pattern"} == expected
    assert len(expected) == 102
    assert (
        sum(1 for profile, raw in expected if profile == "General" and raw.startswith("I:"))
        == 16
    )
    for key in expected:
        assert expected[key][3] in FEATURE_SPECS, key


def test_book_sensitive_collisions_are_separate_and_not_overwritten() -> None:
    actual = _actual()
    for symbol in ("*", "[..]"):
        general = actual[("General", symbol)]
        sirach = actual[("Sirach", symbol)]
        assert general[2] != sirach[2]
        assert general[3] != sirach[3]


def test_patterned_samaritan_reference_documented() -> None:
    actual = _actual()
    key = ("Pattern", "<sp…>")
    spec = notation.notation_spec("<sp12>", book="Gen")
    assert spec is not None
    assert actual[key] == (
        spec.family,
        "yes" if spec.contextual else "no",
        spec.kind,
        notation.semantic_feature_name(spec),
    )
    assert sum(profile == "Pattern" for profile, _ in actual) == 1


@pytest.mark.parametrize(
    ("must_contain", "reason"),
    [
        ("`catss_kind`", "canonical annotation kind"),
        ("`catss_raw`", "source-facing spelling"),
        ("`catss_payload`", "contextual source note"),
        ("`catss_sem_<kind>`", "parent projection vocabulary"),
        ("`catss_sem_<kind>_2`", "second membership lane"),
        ("not a manuscript reading", "no inferred Sirach attestation"),
    ],
)
def test_dictionary_explains_scope_and_missing_semantics(
    must_contain: str, reason: str
) -> None:
    assert PAGE.is_file(), "missing the researcher notation dictionary"
    assert must_contain in PAGE.read_text(encoding="utf-8"), reason
