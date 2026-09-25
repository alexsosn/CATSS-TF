import dataclasses

from catss_tf.bhsa_schema import (
    BHSA_BOOK_BY_CATSS_STEM,
    BHSA_CHECKOUT_COMMIT,
    BHSA_CHECKOUT_TAG,
    BHSA_FEATURE_BLOB_SHAS,
    BHSA_MAX_NODE,
    BHSA_MAX_SLOT,
    BHSA_REPOSITORY,
    BHSA_REQUIRED_FEATURES,
    BHSA_SECTION_TYPES,
    BHSA_UNSUPPORTED_CATSS_STEMS,
    BHSA_VERSION,
    BhsaParentProbe,
    BhsaSourceStatus,
    classify_catss_source,
    validate_bhsa_parent,
)
from catss_tf.source import CATSS_PARALLEL_FILENAMES


def _exact_probe() -> BhsaParentProbe:
    return BhsaParentProbe(
        repository=BHSA_REPOSITORY,
        version=BHSA_VERSION,
        checkout_tag=BHSA_CHECKOUT_TAG,
        checkout_commit=BHSA_CHECKOUT_COMMIT,
        slot_type="word",
        max_slot=BHSA_MAX_SLOT,
        max_node=BHSA_MAX_NODE,
        section_types=BHSA_SECTION_TYPES,
        feature_names=BHSA_REQUIRED_FEATURES,
        feature_blob_shas=BHSA_FEATURE_BLOB_SHAS,
    )


def test_bhsa_profile_accounts_for_every_default_catss_parallel_source() -> None:
    default_stems = {name.removesuffix(".par") for name in CATSS_PARALLEL_FILENAMES}

    assert set(BHSA_BOOK_BY_CATSS_STEM) | set(BHSA_UNSUPPORTED_CATSS_STEMS) == default_stems
    assert set(BHSA_BOOK_BY_CATSS_STEM).isdisjoint(BHSA_UNSUPPORTED_CATSS_STEMS)
    assert len(BHSA_BOOK_BY_CATSS_STEM) == 42
    assert len(BHSA_UNSUPPORTED_CATSS_STEMS) == 4


def test_special_catss_editions_map_to_same_bhsa_hebrew_book() -> None:
    assert BHSA_BOOK_BY_CATSS_STEM["06.JoshB"] == "Josua"
    assert BHSA_BOOK_BY_CATSS_STEM["07.JoshA"] == "Josua"
    assert BHSA_BOOK_BY_CATSS_STEM["08.JudgesB"] == "Judices"
    assert BHSA_BOOK_BY_CATSS_STEM["09.JudgesA"] == "Judices"
    assert BHSA_BOOK_BY_CATSS_STEM["45.DanielOG"] == "Daniel"
    assert BHSA_BOOK_BY_CATSS_STEM["46.DanielTh"] == "Daniel"


def test_reigns_and_latinized_bhsa_book_names_are_explicit() -> None:
    assert BHSA_BOOK_BY_CATSS_STEM["11.1Sam"] == "Samuel_I"
    assert BHSA_BOOK_BY_CATSS_STEM["12.2Sam"] == "Samuel_II"
    assert BHSA_BOOK_BY_CATSS_STEM["13.1Kings"] == "Reges_I"
    assert BHSA_BOOK_BY_CATSS_STEM["14.2Kings"] == "Reges_II"
    assert BHSA_BOOK_BY_CATSS_STEM["20.Psalms"] == "Psalmi"
    assert BHSA_BOOK_BY_CATSS_STEM["26.Job"] == "Iob"
    assert BHSA_BOOK_BY_CATSS_STEM["40.Isaiah"] == "Jesaia"


def test_bhsa_unsupported_sources_are_declared_not_guessed() -> None:
    assert BHSA_UNSUPPORTED_CATSS_STEMS == frozenset(
        {
            "17.1Esdras",
            "22.Ps151",
            "27.Sirach",
            "42.Baruch",
        }
    )

    unsupported = classify_catss_source("17.1Esdras.par")
    assert unsupported.status is BhsaSourceStatus.UNSUPPORTED
    assert unsupported.bhsa_book is None


def test_unknown_catss_source_is_distinct_from_declared_unsupported() -> None:
    unknown = classify_catss_source("99.NotCATSS.par")

    assert unknown.status is BhsaSourceStatus.UNKNOWN
    assert unknown.bhsa_book is None


def test_supported_source_classification_uses_basename_and_stem() -> None:
    result = classify_catss_source("/tmp/catss/01.Genesis.par")

    assert result.status is BhsaSourceStatus.SUPPORTED
    assert result.source_stem == "01.Genesis"
    assert result.bhsa_book == "Genesis"


def test_exact_bhsa_2021_parent_profile_is_accepted() -> None:
    result = validate_bhsa_parent(_exact_probe(), require_blob_hashes=True)

    assert result.ok is True
    assert result.fingerprint_verified is True
    assert result.findings == ()


def test_bhsa_parent_rejects_version_and_warp_drift() -> None:
    probe = dataclasses.replace(
        _exact_probe(),
        version="2025",
        slot_type="token",
        max_slot=BHSA_MAX_SLOT + 1,
        max_node=BHSA_MAX_NODE + 1,
    )

    result = validate_bhsa_parent(probe)

    assert result.ok is False
    assert [finding.code for finding in result.findings] == [
        "version_mismatch",
        "slot_type_mismatch",
        "max_slot_mismatch",
        "max_node_mismatch",
    ]


def test_bhsa_parent_rejects_section_contract_drift() -> None:
    probe = dataclasses.replace(_exact_probe(), section_types=("book", "chapter"))

    result = validate_bhsa_parent(probe)

    assert result.ok is False
    finding = result.findings[0]
    assert finding.code == "section_types_mismatch"
    assert finding.expected == "book,chapter,verse"
    assert finding.actual == "book,chapter"


def test_bhsa_parent_rejects_missing_mapping_features() -> None:
    probe = dataclasses.replace(
        _exact_probe(),
        feature_names=frozenset(BHSA_REQUIRED_FEATURES - {"qere_utf8", "g_cons_utf8"}),
    )

    result = validate_bhsa_parent(probe)

    assert result.ok is False
    assert [(finding.code, finding.actual) for finding in result.findings] == [
        ("missing_feature", "g_cons_utf8"),
        ("missing_feature", "qere_utf8"),
    ]


def test_bhsa_parent_checks_blob_fingerprints_when_supplied() -> None:
    hashes = dict(BHSA_FEATURE_BLOB_SHAS)
    hashes["oslots"] = "deadbeef"
    probe = dataclasses.replace(_exact_probe(), feature_blob_shas=hashes)

    result = validate_bhsa_parent(probe)

    assert result.ok is False
    assert result.fingerprint_verified is False
    finding = result.findings[0]
    assert finding.code == "feature_blob_mismatch"
    assert finding.feature == "oslots"


def test_strict_parent_check_rejects_missing_blob_fingerprints() -> None:
    probe = dataclasses.replace(_exact_probe(), feature_blob_shas=None)

    result = validate_bhsa_parent(probe, require_blob_hashes=True)

    assert result.ok is False
    assert result.fingerprint_verified is False
    assert result.findings[0].code == "feature_blob_hashes_missing"


def test_non_strict_parent_check_can_use_structural_contract_without_raw_files() -> None:
    probe = dataclasses.replace(_exact_probe(), feature_blob_shas=None)

    result = validate_bhsa_parent(probe, require_blob_hashes=False)

    assert result.ok is True
    assert result.fingerprint_verified is False


def test_supported_mapping_covers_all_39_bhsa_books_exactly() -> None:
    assert set(BHSA_BOOK_BY_CATSS_STEM.values()) == {
        "Genesis",
        "Exodus",
        "Leviticus",
        "Numeri",
        "Deuteronomium",
        "Josua",
        "Judices",
        "Samuel_I",
        "Samuel_II",
        "Reges_I",
        "Reges_II",
        "Jesaia",
        "Jeremia",
        "Ezechiel",
        "Hosea",
        "Joel",
        "Amos",
        "Obadia",
        "Jona",
        "Micha",
        "Nahum",
        "Habakuk",
        "Zephania",
        "Haggai",
        "Sacharia",
        "Maleachi",
        "Psalmi",
        "Iob",
        "Proverbia",
        "Ruth",
        "Canticum",
        "Ecclesiastes",
        "Threni",
        "Esther",
        "Daniel",
        "Esra",
        "Nehemia",
        "Chronica_I",
        "Chronica_II",
    }
