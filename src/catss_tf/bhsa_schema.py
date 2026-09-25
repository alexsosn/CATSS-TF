"""Versioned parent profile for the BHSA side of CATSS-TF."""

import dataclasses
import enum
import pathlib
import typing

BHSA_REPOSITORY = "ETCBC/bhsa"
BHSA_VERSION = "2021"
BHSA_CHECKOUT_TAG = "v1.8.1"
BHSA_CHECKOUT_COMMIT = "b112c161cfd21eae403d51a2733740d8743460e7"
BHSA_SLOT_TYPE = "word"
BHSA_MAX_SLOT = 426590
BHSA_MAX_NODE = 1446831
BHSA_SECTION_TYPES = ("book", "chapter", "verse")

BHSA_REQUIRED_FEATURES = frozenset(
    {
        "otype",
        "oslots",
        "book",
        "chapter",
        "verse",
        "g_cons_utf8",
        "g_word_utf8",
        "qere_utf8",
    }
)

BHSA_FEATURE_BLOB_SHAS: dict[str, str] = {
    "otype": "ecc4d0ecd388bd673d0aebfa8ab2a81508bec23c",
    "oslots": "b389833f7624bb252dd2cf25cf798d4a6a82cc1b",
    "book": "70407385b60568eaeb44dbeb45f3a7dfafd2a6af",
    "chapter": "7834c771c0a42fe81b21a8284e95e4226a448108",
    "verse": "06046e58967de2a46b6e976584bd29c98fe2fdab",
    "g_cons_utf8": "8b1b0513cb7ae061ba180c8d6cdbfdb496aa4d44",
    "g_word_utf8": "f78cce06300190ed5c8ef9ca1fa72b16cdfca5eb",
    "qere_utf8": "c4540df6d0068776ac4bb4475a28c7a403a8904e",
}

BHSA_BOOK_BY_CATSS_STEM: dict[str, str] = {
    "01.Genesis": "Genesis",
    "02.Exodus": "Exodus",
    "03.Lev": "Leviticus",
    "04.Num": "Numeri",
    "05.Deut": "Deuteronomium",
    "06.JoshB": "Josua",
    "07.JoshA": "Josua",
    "08.JudgesB": "Judices",
    "09.JudgesA": "Judices",
    "10.Ruth": "Ruth",
    "11.1Sam": "Samuel_I",
    "12.2Sam": "Samuel_II",
    "13.1Kings": "Reges_I",
    "14.2Kings": "Reges_II",
    "15.1Chron": "Chronica_I",
    "16.2Chron": "Chronica_II",
    "18.Esther": "Esther",
    "18.Ezra": "Esra",
    "19.Neh": "Nehemia",
    "20.Psalms": "Psalmi",
    "23.Prov": "Proverbia",
    "24.Qoh": "Ecclesiastes",
    "25.Cant": "Canticum",
    "26.Job": "Iob",
    "28.Hosea": "Hosea",
    "29.Micah": "Micha",
    "30.Amos": "Amos",
    "31.Joel": "Joel",
    "32.Jonah": "Jona",
    "33.Obadiah": "Obadia",
    "34.Nahum": "Nahum",
    "35.Hab": "Habakuk",
    "36.Zeph": "Zephania",
    "37.Haggai": "Haggai",
    "38.Zech": "Sacharia",
    "39.Malachi": "Maleachi",
    "40.Isaiah": "Jesaia",
    "41.Jer": "Jeremia",
    "43.Lam": "Threni",
    "44.Ezekiel": "Ezechiel",
    "45.DanielOG": "Daniel",
    "46.DanielTh": "Daniel",
}

BHSA_UNSUPPORTED_CATSS_STEMS = frozenset(
    {
        "17.1Esdras",
        "22.Ps151",
        "27.Sirach",
        "42.Baruch",
    }
)


class BhsaSourceStatus(enum.Enum):
    """Coverage state of one CATSS parallel source for the BHSA projection."""

    SUPPORTED = "supported"
    UNSUPPORTED = "unsupported"
    UNKNOWN = "unknown"


@dataclasses.dataclass(frozen=True, slots=True)
class BhsaSourceClassification:
    """Explicit CATSS-source coverage decision for the BHSA projection."""

    source_stem: str
    status: BhsaSourceStatus
    bhsa_book: str | None


@dataclasses.dataclass(frozen=True, slots=True)
class BhsaParentProbe:
    """Observed metadata for a candidate BHSA parent dataset."""

    repository: str
    version: str
    checkout_tag: str
    checkout_commit: str
    slot_type: str
    max_slot: int
    max_node: int
    section_types: tuple[str, ...]
    feature_names: frozenset[str]
    feature_blob_shas: typing.Mapping[str, str] | None = None


@dataclasses.dataclass(frozen=True, slots=True)
class BhsaSchemaFinding:
    """One mismatch between an observed BHSA parent and the v0.1 profile."""

    code: str
    expected: str
    actual: str
    feature: str | None = None


@dataclasses.dataclass(frozen=True, slots=True)
class BhsaParentValidation:
    """Result of checking a candidate BHSA parent against the v0.1 profile."""

    findings: tuple[BhsaSchemaFinding, ...]
    fingerprint_verified: bool

    @property
    def ok(self) -> bool:
        """Whether the parent satisfies the declared BHSA contract."""

        return not self.findings


def classify_catss_source(source_name: str) -> BhsaSourceClassification:
    """Classify one CATSS parallel source for projection onto BHSA."""

    name = pathlib.Path(source_name).name
    stem = name.removesuffix(".par")
    bhsa_book = BHSA_BOOK_BY_CATSS_STEM.get(stem)
    if bhsa_book is not None:
        return BhsaSourceClassification(
            source_stem=stem,
            status=BhsaSourceStatus.SUPPORTED,
            bhsa_book=bhsa_book,
        )
    if stem in BHSA_UNSUPPORTED_CATSS_STEMS:
        return BhsaSourceClassification(
            source_stem=stem,
            status=BhsaSourceStatus.UNSUPPORTED,
            bhsa_book=None,
        )
    return BhsaSourceClassification(
        source_stem=stem,
        status=BhsaSourceStatus.UNKNOWN,
        bhsa_book=None,
    )


def validate_bhsa_parent(
    probe: BhsaParentProbe, *, require_blob_hashes: bool = False
) -> BhsaParentValidation:
    """Validate a candidate parent against the exact BHSA 2021 profile."""

    findings: list[BhsaSchemaFinding] = []

    _compare(findings, "repository_mismatch", BHSA_REPOSITORY, probe.repository)
    _compare(findings, "version_mismatch", BHSA_VERSION, probe.version)
    _compare(findings, "checkout_tag_mismatch", BHSA_CHECKOUT_TAG, probe.checkout_tag)
    _compare(
        findings,
        "checkout_commit_mismatch",
        BHSA_CHECKOUT_COMMIT,
        probe.checkout_commit,
    )
    _compare(findings, "slot_type_mismatch", BHSA_SLOT_TYPE, probe.slot_type)
    _compare(findings, "max_slot_mismatch", str(BHSA_MAX_SLOT), str(probe.max_slot))
    _compare(findings, "max_node_mismatch", str(BHSA_MAX_NODE), str(probe.max_node))

    if probe.section_types != BHSA_SECTION_TYPES:
        findings.append(
            BhsaSchemaFinding(
                code="section_types_mismatch",
                expected=",".join(BHSA_SECTION_TYPES),
                actual=",".join(probe.section_types),
            )
        )

    for feature in sorted(BHSA_REQUIRED_FEATURES - probe.feature_names):
        findings.append(
            BhsaSchemaFinding(
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
                BhsaSchemaFinding(
                    code="feature_blob_hashes_missing",
                    expected="mapping-critical BHSA 2021 Git blob hashes",
                    actual="not supplied",
                )
            )
    else:
        fingerprint_verified = True
        observed = dict(probe.feature_blob_shas)
        for feature, expected_sha in BHSA_FEATURE_BLOB_SHAS.items():
            actual_sha = observed.get(feature)
            if actual_sha is None:
                fingerprint_verified = False
                findings.append(
                    BhsaSchemaFinding(
                        code="feature_blob_missing",
                        expected=expected_sha,
                        actual="missing",
                        feature=feature,
                    )
                )
            elif actual_sha != expected_sha:
                fingerprint_verified = False
                findings.append(
                    BhsaSchemaFinding(
                        code="feature_blob_mismatch",
                        expected=expected_sha,
                        actual=actual_sha,
                        feature=feature,
                    )
                )

    return BhsaParentValidation(
        findings=tuple(findings),
        fingerprint_verified=fingerprint_verified,
    )


def _compare(
    findings: list[BhsaSchemaFinding],
    code: str,
    expected: str,
    actual: str,
) -> None:
    if expected == actual:
        return
    findings.append(
        BhsaSchemaFinding(
            code=code,
            expected=expected,
            actual=actual,
        )
    )
