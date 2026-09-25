"""Versioned parent profile for the CenterBLC/LXX side of CATSS-TF."""

import dataclasses
import enum
import pathlib
import typing


LXX_REPOSITORY = "CenterBLC/LXX"
LXX_VERSION = "1935"
LXX_RELEASE_TAG = "v1.0.1"
LXX_RELEASE_COMMIT = "f32a98eddf7eb239aa73ab863d70381e416d5076"
LXX_SLOT_TYPE = "word"
LXX_MAX_SLOT = 623693
LXX_MAX_NODE = 685732
LXX_SECTION_TYPES = ("book", "chapter", "verse")

LXX_NODE_COUNTS: dict[str, int] = {
    "word": 623693,
    "subverse": 30419,
    "verse": 30371,
    "chapter": 1192,
    "book": 57,
}

LXX_REQUIRED_FEATURES = frozenset(
    {
        "otype",
        "oslots",
        "book",
        "chapter",
        "verse",
        "subverse",
        "word",
        "orig_order",
    }
)

LXX_FEATURE_BLOB_SHAS: dict[str, str] = {
    "otype": "2e6480116dfda09f20e8de7c5b9feefa76322a96",
    "oslots": "e95696a6a49f1149f8f6e850f7dfb40a26509931",
    "book": "0bfae94bb312cb7ecd33b102babb9400c554d8be",
    "chapter": "ec64b6bf72a6282e9da5064ca2e895171190208e",
    "verse": "ff8766352d7aff530c6eec4f66366adcc691740e",
    "subverse": "cecfaf2d1ddc4fd1e93958abd674a7e60e676ae5",
    "word": "f88e525991c3d09beac713a91ef8ed41e6308a03",
    "orig_order": "0d0339af8a512a0a59232fbccb309fc229da6ddd",
}

LXX_BOOK_BY_CATSS_STEM: dict[str, str] = {
    "01.Genesis": "Gen",
    "02.Exodus": "Exod",
    "03.Lev": "Lev",
    "04.Num": "Num",
    "05.Deut": "Deut",
    "06.JoshB": "Josh",
    "08.JudgesB": "Judg",
    "10.Ruth": "Ruth",
    "11.1Sam": "1Sam",
    "12.2Sam": "2Sam",
    "13.1Kings": "1Kgs",
    "14.2Kings": "2Kgs",
    "15.1Chron": "1Chr",
    "16.2Chron": "2Chr",
    "17.1Esdras": "1Esdr",
    "18.Esther": "Esth",
    "18.Ezra": "2Esdr",
    "19.Neh": "2Esdr",
    "20.Psalms": "Ps",
    "22.Ps151": "Ps",
    "23.Prov": "Prov",
    "24.Qoh": "Qoh",
    "25.Cant": "Cant",
    "26.Job": "Job",
    "27.Sirach": "Sir",
    "28.Hosea": "Hos",
    "29.Micah": "Mic",
    "30.Amos": "Amos",
    "31.Joel": "Joel",
    "32.Jonah": "Jonah",
    "33.Obadiah": "Obad",
    "34.Nahum": "Nah",
    "35.Hab": "Hab",
    "36.Zeph": "Zeph",
    "37.Haggai": "Hag",
    "38.Zech": "Zech",
    "39.Malachi": "Mal",
    "40.Isaiah": "Isa",
    "41.Jer": "Jer",
    "42.Baruch": "Bar",
    "43.Lam": "Lam",
    "44.Ezekiel": "Ezek",
    "45.DanielOG": "Dan",
    "46.DanielTh": "DanTh",
}

LXX_UNSUPPORTED_CATSS_STEMS = frozenset({"07.JoshA", "09.JudgesA"})


class LxxSourceStatus(enum.Enum):
    """Coverage state of one CATSS parallel source for the LXX projection."""

    SUPPORTED = "supported"
    UNSUPPORTED = "unsupported"
    UNKNOWN = "unknown"


class LxxReferencePolicy(enum.Enum):
    """Default CATSS-header to CenterBLC reference transform."""

    DIRECT = "direct"
    TWO_ESDR_EZRA = "two_esdr_ezra"
    TWO_ESDR_NEHEMIAH = "two_esdr_nehemiah"
    PS151 = "ps151"


@dataclasses.dataclass(frozen=True, slots=True)
class LxxSourceClassification:
    """Versioned CATSS-source coverage and default reference policy."""

    source_stem: str
    status: LxxSourceStatus
    parent_book: str | None
    reference_policy: LxxReferencePolicy | None


@dataclasses.dataclass(frozen=True, slots=True)
class LxxReference:
    """Default CenterBLC book/chapter/verse location."""

    book: str
    chapter: int
    verse: int


@dataclasses.dataclass(frozen=True, slots=True)
class LxxParentProbe:
    """Observed metadata for a candidate CenterBLC/LXX parent dataset."""

    repository: str
    version: str
    release_tag: str
    release_commit: str
    slot_type: str
    max_slot: int
    max_node: int
    section_types: tuple[str, ...]
    node_counts: typing.Mapping[str, int]
    feature_names: frozenset[str]
    feature_blob_shas: typing.Mapping[str, str] | None = None


@dataclasses.dataclass(frozen=True, slots=True)
class LxxSchemaFinding:
    """One mismatch between an observed LXX parent and the v0.1 profile."""

    code: str
    expected: str
    actual: str
    feature: str | None = None


@dataclasses.dataclass(frozen=True, slots=True)
class LxxParentValidation:
    """Result of checking a candidate parent against the exact LXX profile."""

    findings: tuple[LxxSchemaFinding, ...]
    fingerprint_verified: bool

    @property
    def ok(self) -> bool:
        """Whether the parent satisfies the declared CenterBLC/LXX contract."""

        return not self.findings


def classify_catss_source(source_name: str) -> LxxSourceClassification:
    """Classify one CATSS parallel source for projection onto CenterBLC/LXX."""

    stem = pathlib.Path(source_name).name.removesuffix(".par")
    parent_book = LXX_BOOK_BY_CATSS_STEM.get(stem)
    if parent_book is not None:
        return LxxSourceClassification(
            source_stem=stem,
            status=LxxSourceStatus.SUPPORTED,
            parent_book=parent_book,
            reference_policy=_reference_policy(stem),
        )
    if stem in LXX_UNSUPPORTED_CATSS_STEMS:
        return LxxSourceClassification(
            source_stem=stem,
            status=LxxSourceStatus.UNSUPPORTED,
            parent_book=None,
            reference_policy=None,
        )
    return LxxSourceClassification(
        source_stem=stem,
        status=LxxSourceStatus.UNKNOWN,
        parent_book=None,
        reference_policy=None,
    )


def default_lxx_reference(source_name: str, chapter: int, verse: int) -> LxxReference:
    """Translate a CATSS MT-header reference to the default CenterBLC location.

    Structured CATSS Greek-side reference evidence is applied later by the
    resolver and takes precedence over this default.
    """

    profile = classify_catss_source(source_name)
    if profile.status is not LxxSourceStatus.SUPPORTED:
        raise ValueError(
            f"CATSS source {profile.source_stem!r} has no supported LXX default reference"
        )
    assert profile.parent_book is not None
    assert profile.reference_policy is not None

    if profile.reference_policy is LxxReferencePolicy.PS151:
        return LxxReference(profile.parent_book, 151, verse)
    if profile.reference_policy is LxxReferencePolicy.TWO_ESDR_NEHEMIAH:
        return LxxReference(profile.parent_book, chapter + 10, verse)

    return LxxReference(profile.parent_book, chapter, verse)


def validate_lxx_parent(
    probe: LxxParentProbe, *, require_blob_hashes: bool = False
) -> LxxParentValidation:
    """Validate a candidate parent against CenterBLC/LXX 1935 v1.0.1."""

    findings: list[LxxSchemaFinding] = []

    _compare(findings, "repository_mismatch", LXX_REPOSITORY, probe.repository)
    _compare(findings, "version_mismatch", LXX_VERSION, probe.version)
    _compare(findings, "release_tag_mismatch", LXX_RELEASE_TAG, probe.release_tag)
    _compare(
        findings,
        "release_commit_mismatch",
        LXX_RELEASE_COMMIT,
        probe.release_commit,
    )
    _compare(findings, "slot_type_mismatch", LXX_SLOT_TYPE, probe.slot_type)
    _compare(findings, "max_slot_mismatch", str(LXX_MAX_SLOT), str(probe.max_slot))
    _compare(findings, "max_node_mismatch", str(LXX_MAX_NODE), str(probe.max_node))

    if probe.section_types != LXX_SECTION_TYPES:
        findings.append(
            LxxSchemaFinding(
                code="section_types_mismatch",
                expected=",".join(LXX_SECTION_TYPES),
                actual=",".join(probe.section_types),
            )
        )

    for node_type in sorted(LXX_NODE_COUNTS):
        expected = LXX_NODE_COUNTS[node_type]
        actual = probe.node_counts.get(node_type)
        if actual != expected:
            findings.append(
                LxxSchemaFinding(
                    code="node_count_mismatch",
                    expected=str(expected),
                    actual="missing" if actual is None else str(actual),
                    feature=node_type,
                )
            )

    for feature in sorted(LXX_REQUIRED_FEATURES - probe.feature_names):
        findings.append(
            LxxSchemaFinding(
                code="missing_feature",
                expected="present",
                actual=feature,
                feature=feature,
            )
        )

    fingerprint_verified = False
    if probe.feature_blob_shas is None:
        if require_blob_hashes:
            findings.append(
                LxxSchemaFinding(
                    code="feature_blob_hashes_missing",
                    expected="mapping-critical CenterBLC/LXX v1.0.1 Git blob hashes",
                    actual="not supplied",
                )
            )
    else:
        fingerprint_verified = True
        observed = dict(probe.feature_blob_shas)
        for feature, expected_sha in LXX_FEATURE_BLOB_SHAS.items():
            actual_sha = observed.get(feature)
            if actual_sha is None:
                fingerprint_verified = False
                findings.append(
                    LxxSchemaFinding(
                        code="feature_blob_missing",
                        expected=expected_sha,
                        actual="missing",
                        feature=feature,
                    )
                )
            elif actual_sha != expected_sha:
                fingerprint_verified = False
                findings.append(
                    LxxSchemaFinding(
                        code="feature_blob_mismatch",
                        expected=expected_sha,
                        actual=actual_sha,
                        feature=feature,
                    )
                )

    return LxxParentValidation(
        findings=tuple(findings),
        fingerprint_verified=fingerprint_verified,
    )


def _reference_policy(source_stem: str) -> LxxReferencePolicy:
    if source_stem == "18.Ezra":
        return LxxReferencePolicy.TWO_ESDR_EZRA
    if source_stem == "19.Neh":
        return LxxReferencePolicy.TWO_ESDR_NEHEMIAH
    if source_stem == "22.Ps151":
        return LxxReferencePolicy.PS151
    return LxxReferencePolicy.DIRECT


def _compare(
    findings: list[LxxSchemaFinding],
    code: str,
    expected: str,
    actual: str,
) -> None:
    if expected == actual:
        return
    findings.append(
        LxxSchemaFinding(
            code=code,
            expected=expected,
            actual=actual,
        )
    )
