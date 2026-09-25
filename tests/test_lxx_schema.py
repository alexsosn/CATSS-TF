import dataclasses

from catss_tf.lxx_schema import (
    LXX_BOOK_BY_CATSS_STEM,
    LXX_FEATURE_BLOB_SHAS,
    LXX_MAX_NODE,
    LXX_MAX_SLOT,
    LXX_NODE_COUNTS,
    LXX_PARENT_BOOKS,
    LXX_RELEASE_COMMIT,
    LXX_RELEASE_TAG,
    LXX_REPOSITORY,
    LXX_REQUIRED_FEATURES,
    LXX_SECTION_TYPES,
    LXX_UNSUPPORTED_CATSS_STEMS,
    LXX_VERSION,
    LxxParentProbe,
    LxxReferencePolicy,
    LxxSourceStatus,
    classify_catss_source,
    default_lxx_reference,
    validate_lxx_parent,
)
from catss_tf.source import CATSS_PARALLEL_FILENAMES


def _exact_probe() -> LxxParentProbe:
    return LxxParentProbe(
        repository=LXX_REPOSITORY,
        version=LXX_VERSION,
        release_tag=LXX_RELEASE_TAG,
        release_commit=LXX_RELEASE_COMMIT,
        slot_type="word",
        max_slot=LXX_MAX_SLOT,
        max_node=LXX_MAX_NODE,
        section_types=LXX_SECTION_TYPES,
        node_counts=LXX_NODE_COUNTS,
        feature_names=LXX_REQUIRED_FEATURES,
        feature_blob_shas=LXX_FEATURE_BLOB_SHAS,
    )


def test_lxx_profile_accounts_for_every_default_catss_parallel_source() -> None:
    default_stems = {name.removesuffix(".par") for name in CATSS_PARALLEL_FILENAMES}

    assert set(LXX_BOOK_BY_CATSS_STEM) | set(LXX_UNSUPPORTED_CATSS_STEMS) == default_stems
    assert set(LXX_BOOK_BY_CATSS_STEM).isdisjoint(LXX_UNSUPPORTED_CATSS_STEMS)
    assert len(LXX_BOOK_BY_CATSS_STEM) == 44
    assert LXX_UNSUPPORTED_CATSS_STEMS == frozenset({"07.JoshA", "09.JudgesA"})


def test_joshua_and_judges_b_are_supported_but_a_are_not_coerced() -> None:
    assert LXX_BOOK_BY_CATSS_STEM["06.JoshB"] == "Josh"
    assert LXX_BOOK_BY_CATSS_STEM["08.JudgesB"] == "Judg"

    assert classify_catss_source("07.JoshA.par").status is LxxSourceStatus.UNSUPPORTED
    assert classify_catss_source("09.JudgesA.par").status is LxxSourceStatus.UNSUPPORTED


def test_daniel_editions_remain_separate() -> None:
    old_greek = classify_catss_source("45.DanielOG.par")
    theodotion = classify_catss_source("46.DanielTh.par")

    assert old_greek.status is LxxSourceStatus.SUPPORTED
    assert old_greek.parent_book == "Dan"
    assert theodotion.status is LxxSourceStatus.SUPPORTED
    assert theodotion.parent_book == "DanTh"


def test_psalm_151_maps_inside_parent_psalms() -> None:
    profile = classify_catss_source("22.Ps151.par")

    assert profile.parent_book == "Ps"
    assert profile.reference_policy is LxxReferencePolicy.PS151

    ref = default_lxx_reference("22.Ps151.par", chapter=1, verse=4)
    assert (ref.book, ref.chapter, ref.verse) == ("Ps", 151, 4)


def test_ezra_nehemiah_map_to_parent_two_esdras() -> None:
    ezra = classify_catss_source("18.Ezra.par")
    nehemiah = classify_catss_source("19.Neh.par")

    assert ezra.parent_book == "2Esdr"
    assert ezra.reference_policy is LxxReferencePolicy.TWO_ESDR_EZRA
    assert nehemiah.parent_book == "2Esdr"
    assert nehemiah.reference_policy is LxxReferencePolicy.TWO_ESDR_NEHEMIAH

    assert default_lxx_reference("18.Ezra.par", 7, 3).chapter == 7
    assert default_lxx_reference("19.Neh.par", 1, 3).chapter == 11
    assert default_lxx_reference("19.Neh.par", 13, 31).chapter == 23


def test_ordinary_supported_source_uses_direct_reference_policy() -> None:
    profile = classify_catss_source("/tmp/catss/01.Genesis.par")
    ref = default_lxx_reference("/tmp/catss/01.Genesis.par", 23, 5)

    assert profile.status is LxxSourceStatus.SUPPORTED
    assert profile.source_stem == "01.Genesis"
    assert profile.parent_book == "Gen"
    assert profile.reference_policy is LxxReferencePolicy.DIRECT
    assert (ref.book, ref.chapter, ref.verse) == ("Gen", 23, 5)


def test_unknown_source_is_distinct_from_declared_unsupported() -> None:
    profile = classify_catss_source("99.Unknown.par")

    assert profile.status is LxxSourceStatus.UNKNOWN
    assert profile.parent_book is None
    assert profile.reference_policy is None


def test_default_reference_rejects_unsupported_and_unknown_sources() -> None:
    for name in ("07.JoshA.par", "99.Unknown.par"):
        try:
            default_lxx_reference(name, 1, 1)
        except ValueError as exc:
            assert name.removesuffix(".par") in str(exc)
        else:
            raise AssertionError(f"{name} must not receive a default LXX reference")


def test_profile_uses_surface_word_and_subverse_as_mapping_features() -> None:
    assert {"word", "subverse", "orig_order"} <= LXX_REQUIRED_FEATURES
    assert "g_cons_utf8" not in LXX_REQUIRED_FEATURES
    assert "lex_utf8" not in LXX_REQUIRED_FEATURES


def test_exact_centerblc_v101_parent_profile_is_accepted() -> None:
    result = validate_lxx_parent(_exact_probe(), require_blob_hashes=True)

    assert result.ok is True
    assert result.fingerprint_verified is True
    assert result.findings == ()


def test_lxx_parent_rejects_release_and_warp_drift() -> None:
    probe = dataclasses.replace(
        _exact_probe(),
        version="future",
        release_tag="main",
        release_commit="deadbeef",
        slot_type="token",
        max_slot=LXX_MAX_SLOT + 1,
        max_node=LXX_MAX_NODE + 1,
    )

    result = validate_lxx_parent(probe)

    assert result.ok is False
    assert [finding.code for finding in result.findings] == [
        "version_mismatch",
        "release_tag_mismatch",
        "release_commit_mismatch",
        "slot_type_mismatch",
        "max_slot_mismatch",
        "max_node_mismatch",
    ]


def test_lxx_parent_rejects_section_and_node_count_drift() -> None:
    counts = dict(LXX_NODE_COUNTS)
    counts["subverse"] += 1
    probe = dataclasses.replace(
        _exact_probe(),
        section_types=("book", "chapter"),
        node_counts=counts,
    )

    result = validate_lxx_parent(probe)

    assert result.ok is False
    assert [(finding.code, finding.feature) for finding in result.findings] == [
        ("section_types_mismatch", None),
        ("node_count_mismatch", "subverse"),
    ]


def test_lxx_parent_rejects_missing_mapping_features() -> None:
    probe = dataclasses.replace(
        _exact_probe(),
        feature_names=frozenset(LXX_REQUIRED_FEATURES - {"word", "subverse"}),
    )

    result = validate_lxx_parent(probe)

    assert [(finding.code, finding.actual) for finding in result.findings] == [
        ("missing_feature", "subverse"),
        ("missing_feature", "word"),
    ]


def test_lxx_parent_checks_exact_blob_fingerprints() -> None:
    hashes = dict(LXX_FEATURE_BLOB_SHAS)
    hashes["word"] = "deadbeef"
    probe = dataclasses.replace(_exact_probe(), feature_blob_shas=hashes)

    result = validate_lxx_parent(probe)

    assert result.ok is False
    assert result.fingerprint_verified is False
    finding = result.findings[0]
    assert finding.code == "feature_blob_mismatch"
    assert finding.feature == "word"


def test_strict_parent_check_requires_blob_fingerprints() -> None:
    probe = dataclasses.replace(_exact_probe(), feature_blob_shas=None)

    result = validate_lxx_parent(probe, require_blob_hashes=True)

    assert result.ok is False
    assert result.fingerprint_verified is False
    assert result.findings[0].code == "feature_blob_hashes_missing"


def test_structural_parent_check_can_run_without_raw_tf_files() -> None:
    probe = dataclasses.replace(_exact_probe(), feature_blob_shas=None)

    result = validate_lxx_parent(probe, require_blob_hashes=False)

    assert result.ok is True
    assert result.fingerprint_verified is False


def test_every_lxx_mapping_target_exists_in_exact_parent_book_universe() -> None:
    assert len(LXX_PARENT_BOOKS) == 57
    assert set(LXX_BOOK_BY_CATSS_STEM.values()) <= LXX_PARENT_BOOKS
    assert {"Qoh", "Cant", "Dan", "DanTh", "1Esdr", "2Esdr", "Ps"} <= LXX_PARENT_BOOKS
    assert {"JoshA", "JudgA"}.isdisjoint(LXX_PARENT_BOOKS)
