"""Strict CATSS MT -> BHSA word-slot resolver."""

import dataclasses
import typing
import unicodedata

from catss_tf.bhsa_schema import BhsaSourceStatus, classify_catss_source
from catss_tf.parser import ParallelDocument

_CATSS_HEBREW = {
    ")": "א",
    "B": "ב",
    "G": "ג",
    "D": "ד",
    "H": "ה",
    "W": "ו",
    "Z": "ז",
    "X": "ח",
    "+": "ט",
    "Y": "י",
    "K": "כ",
    "L": "ל",
    "M": "מ",
    "N": "נ",
    "S": "ס",
    "(": "ע",
    "P": "פ",
    "C": "צ",
    "Q": "ק",
    "R": "ר",
    "&": "שׂ",
    "$": "שׁ",
    "T": "ת",
}
_FINAL_FORMS = {
    "כ": "ך",
    "מ": "ם",
    "נ": "ן",
    "פ": "ף",
    "צ": "ץ",
}
_SHIN_SIN_DOTS = frozenset({"ׁ", "ׂ"})


@dataclasses.dataclass(frozen=True, slots=True)
class BhsaWord:
    """Mapping-relevant view of one BHSA word slot."""

    node: int
    g_cons_utf8: str
    g_word_utf8: str | None
    qere_utf8: str | None


@dataclasses.dataclass(frozen=True, slots=True)
class BhsaVerse:
    """Mapping-relevant view of one BHSA verse node."""

    node: int
    book: str
    chapter: int
    verse: int
    words: tuple[BhsaWord, ...]


class BhsaVerseProvider(typing.Protocol):
    """Minimal parent-corpus interface required by the pure resolver."""

    def get_verse(self, book: str, chapter: int, verse: int) -> BhsaVerse | None:
        """Return exactly one BHSA verse view or None when it does not exist."""


@dataclasses.dataclass(frozen=True, slots=True)
class BhsaWordMapping:
    """A proven CATSS MT position -> BHSA word-node mapping."""

    alignment_id: str
    mt_index: int
    bhsa_node: int
    mapping_kind: typing.Literal["exact", "ketiv_qere"]


@dataclasses.dataclass(frozen=True, slots=True)
class BhsaVerseAnchor:
    """A non-word anchor for a Hebrew-empty/LXX-plus CATSS alignment."""

    alignment_id: str
    bhsa_verse_node: int
    kind: typing.Literal["lxx_plus"] = "lxx_plus"


@dataclasses.dataclass(frozen=True, slots=True)
class MappingFinding:
    """One explicit BHSA resolution failure."""

    code: str
    source_name: str
    chapter: int | None
    verse: int | None
    position: int | None
    alignment_id: str | None
    catss_value: str | None
    bhsa_value: str | None
    message: str


@dataclasses.dataclass(frozen=True, slots=True)
class BhsaMappingSummary:
    """Scalar resolver counters for automation and later materialization."""

    documents: int
    supported_documents: int
    unsupported_documents: int
    unknown_documents: int
    verses: int
    resolved_verses: int
    missing_verses: int
    mismatched_verses: int
    word_mappings: int
    verse_anchors: int
    qere_checks: int
    qere_mismatches: int
    normalization_errors: int
    finding_count: int


@dataclasses.dataclass(frozen=True, slots=True)
class BhsaMappingReport:
    """Deterministic CATSS -> BHSA mapping result."""

    summary: BhsaMappingSummary
    word_mappings: tuple[BhsaWordMapping, ...]
    verse_anchors: tuple[BhsaVerseAnchor, ...]
    findings: tuple[MappingFinding, ...]


def normalize_catss_hebrew(value: str) -> str:
    """Convert one CATSS Michigan-Claremont MT word to consonantal Unicode.

    The character mapping follows the documented CATSS transcription and the
    MIT-licensed CATSS_parsers prior art. Slash/backslash morpheme separators
    are removed. Unknown lexical characters fail closed.
    """

    output: list[str] = []
    for character in value:
        if character in {"/", "\\"}:
            continue
        mapped = _CATSS_HEBREW.get(character)
        if mapped is None:
            raise ValueError(
                f"unsupported CATSS Hebrew character {character!r} in {value!r}"
            )
        output.extend(mapped)

    if not output:
        raise ValueError("CATSS Hebrew word is empty after normalization")

    for index in range(len(output) - 1, -1, -1):
        character = output[index]
        if "א" <= character <= "ת":
            output[index] = _FINAL_FORMS.get(character, character)
            break

    return "".join(output)


def normalize_bhsa_hebrew(value: str) -> str:
    """Normalize one BHSA word-feature value to consonants + shin/sin dots."""

    output: list[str] = []
    for character in unicodedata.normalize("NFD", value):
        if character.isspace():
            continue
        if character in _SHIN_SIN_DOTS:
            output.append(character)
            continue
        if "א" <= character <= "ת":
            output.append(character)
            continue
        if unicodedata.combining(character):
            continue
        raise ValueError(f"unsupported BHSA Hebrew character {character!r} in {value!r}")

    if not output:
        raise ValueError("BHSA Hebrew value is empty after normalization")
    return "".join(output)


def resolve_bhsa_document(
    document: ParallelDocument,
    provider: BhsaVerseProvider,
) -> BhsaMappingReport:
    """Resolve one CATSS parallel document against the declared BHSA parent."""

    classification = classify_catss_source(document.source_name)
    if classification.status is BhsaSourceStatus.UNSUPPORTED:
        return _report(
            unsupported_documents=1,
            verses=len(document.verses),
        )
    if classification.status is BhsaSourceStatus.UNKNOWN:
        return _report(
            unknown_documents=1,
            verses=len(document.verses),
            findings=(
                MappingFinding(
                    code="unknown_catss_source",
                    source_name=document.source_name,
                    chapter=None,
                    verse=None,
                    position=None,
                    alignment_id=None,
                    catss_value=None,
                    bhsa_value=None,
                    message="CATSS source is not classified for the BHSA projection",
                ),
            ),
        )

    assert classification.bhsa_book is not None
    word_mappings: list[BhsaWordMapping] = []
    verse_anchors: list[BhsaVerseAnchor] = []
    findings: list[MappingFinding] = []
    resolved_verses = 0
    missing_verses = 0
    mismatched_verses = 0
    qere_checks = 0
    qere_mismatches = 0
    normalization_errors = 0

    for verse in document.verses:
        parent = provider.get_verse(
            classification.bhsa_book,
            verse.chapter,
            verse.verse,
        )
        if parent is None:
            missing_verses += 1
            findings.append(
                MappingFinding(
                    code="missing_bhsa_verse",
                    source_name=document.source_name,
                    chapter=verse.chapter,
                    verse=verse.verse,
                    position=None,
                    alignment_id=None,
                    catss_value=None,
                    bhsa_value=None,
                    message="BHSA parent has no matching book/chapter/verse",
                )
            )
            continue

        positions = [
            (alignment.alignment_id, mt_index, reading)
            for alignment in verse.alignments
            for mt_index, reading in enumerate(alignment.mt_readings)
        ]
        plus_alignments = [
            alignment for alignment in verse.alignments if alignment.is_lxx_plus
        ]

        if len(positions) != len(parent.words):
            mismatched_verses += 1
            findings.append(
                MappingFinding(
                    code="verse_word_count_mismatch",
                    source_name=document.source_name,
                    chapter=verse.chapter,
                    verse=verse.verse,
                    position=None,
                    alignment_id=None,
                    catss_value=str(len(positions)),
                    bhsa_value=str(len(parent.words)),
                    message="CATSS MT and BHSA verse have different word counts",
                )
            )
            continue

        catss_normalized: list[str] = []
        bhsa_normalized: list[str] = []
        failed = False

        for position, ((alignment_id, _mt_index, reading), word) in enumerate(
            zip(positions, parent.words, strict=True),
            start=1,
        ):
            try:
                catss_value = normalize_catss_hebrew(reading.primary)
            except ValueError as exc:
                normalization_errors += 1
                failed = True
                findings.append(
                    MappingFinding(
                        code="catss_hebrew_normalization_error",
                        source_name=document.source_name,
                        chapter=verse.chapter,
                        verse=verse.verse,
                        position=position,
                        alignment_id=alignment_id,
                        catss_value=reading.primary,
                        bhsa_value=None,
                        message=str(exc),
                    )
                )
                break
            try:
                bhsa_value = normalize_bhsa_hebrew(word.g_cons_utf8)
            except ValueError as exc:
                normalization_errors += 1
                failed = True
                findings.append(
                    MappingFinding(
                        code="bhsa_hebrew_normalization_error",
                        source_name=document.source_name,
                        chapter=verse.chapter,
                        verse=verse.verse,
                        position=position,
                        alignment_id=alignment_id,
                        catss_value=catss_value,
                        bhsa_value=word.g_cons_utf8,
                        message=str(exc),
                    )
                )
                break
            catss_normalized.append(catss_value)
            bhsa_normalized.append(bhsa_value)

        if failed:
            mismatched_verses += 1
            continue

        mismatch_index = next(
            (
                index
                for index, (catss_value, bhsa_value) in enumerate(
                    zip(catss_normalized, bhsa_normalized, strict=True)
                )
                if catss_value != bhsa_value
            ),
            None,
        )
        if mismatch_index is not None:
            mismatched_verses += 1
            alignment_id, _mt_index, _reading = positions[mismatch_index]
            findings.append(
                MappingFinding(
                    code="verse_word_mismatch",
                    source_name=document.source_name,
                    chapter=verse.chapter,
                    verse=verse.verse,
                    position=mismatch_index + 1,
                    alignment_id=alignment_id,
                    catss_value=catss_normalized[mismatch_index],
                    bhsa_value=bhsa_normalized[mismatch_index],
                    message="normalized CATSS MT and BHSA word differ",
                )
            )
            continue

        qere_failure = False
        for position, ((alignment_id, _mt_index, reading), word) in enumerate(
            zip(positions, parent.words, strict=True),
            start=1,
        ):
            if reading.qere is None:
                continue
            qere_checks += 1
            if word.qere_utf8 is None or not word.qere_utf8.strip():
                qere_mismatches += 1
                qere_failure = True
                findings.append(
                    MappingFinding(
                        code="qere_missing",
                        source_name=document.source_name,
                        chapter=verse.chapter,
                        verse=verse.verse,
                        position=position,
                        alignment_id=alignment_id,
                        catss_value=reading.qere,
                        bhsa_value=None,
                        message="CATSS Qere has no BHSA qere_utf8 value on the same word slot",
                    )
                )
                break
            try:
                catss_qere = normalize_catss_hebrew(reading.qere)
                bhsa_qere = normalize_bhsa_hebrew(word.qere_utf8)
            except ValueError as exc:
                normalization_errors += 1
                qere_mismatches += 1
                qere_failure = True
                findings.append(
                    MappingFinding(
                        code="qere_normalization_error",
                        source_name=document.source_name,
                        chapter=verse.chapter,
                        verse=verse.verse,
                        position=position,
                        alignment_id=alignment_id,
                        catss_value=reading.qere,
                        bhsa_value=word.qere_utf8,
                        message=str(exc),
                    )
                )
                break
            if catss_qere != bhsa_qere:
                qere_mismatches += 1
                qere_failure = True
                findings.append(
                    MappingFinding(
                        code="qere_mismatch",
                        source_name=document.source_name,
                        chapter=verse.chapter,
                        verse=verse.verse,
                        position=position,
                        alignment_id=alignment_id,
                        catss_value=catss_qere,
                        bhsa_value=bhsa_qere,
                        message="CATSS Qere and BHSA qere_utf8 differ on the same word slot",
                    )
                )
                break

        if qere_failure:
            mismatched_verses += 1
            continue

        resolved_verses += 1
        word_mappings.extend(
            BhsaWordMapping(
                alignment_id=alignment_id,
                mt_index=mt_index,
                bhsa_node=word.node,
                mapping_kind="ketiv_qere" if reading.qere is not None else "exact",
            )
            for (alignment_id, mt_index, reading), word in zip(
                positions, parent.words, strict=True
            )
        )
        verse_anchors.extend(
            BhsaVerseAnchor(
                alignment_id=alignment.alignment_id,
                bhsa_verse_node=parent.node,
            )
            for alignment in plus_alignments
        )

    return _report(
        supported_documents=1,
        verses=len(document.verses),
        resolved_verses=resolved_verses,
        missing_verses=missing_verses,
        mismatched_verses=mismatched_verses,
        word_mappings=tuple(word_mappings),
        verse_anchors=tuple(verse_anchors),
        qere_checks=qere_checks,
        qere_mismatches=qere_mismatches,
        normalization_errors=normalization_errors,
        findings=tuple(findings),
    )


def _report(
    *,
    supported_documents: int = 0,
    unsupported_documents: int = 0,
    unknown_documents: int = 0,
    verses: int = 0,
    resolved_verses: int = 0,
    missing_verses: int = 0,
    mismatched_verses: int = 0,
    word_mappings: tuple[BhsaWordMapping, ...] = (),
    verse_anchors: tuple[BhsaVerseAnchor, ...] = (),
    qere_checks: int = 0,
    qere_mismatches: int = 0,
    normalization_errors: int = 0,
    findings: tuple[MappingFinding, ...] = (),
) -> BhsaMappingReport:
    return BhsaMappingReport(
        summary=BhsaMappingSummary(
            documents=1,
            supported_documents=supported_documents,
            unsupported_documents=unsupported_documents,
            unknown_documents=unknown_documents,
            verses=verses,
            resolved_verses=resolved_verses,
            missing_verses=missing_verses,
            mismatched_verses=mismatched_verses,
            word_mappings=len(word_mappings),
            verse_anchors=len(verse_anchors),
            qere_checks=qere_checks,
            qere_mismatches=qere_mismatches,
            normalization_errors=normalization_errors,
            finding_count=len(findings),
        ),
        word_mappings=word_mappings,
        verse_anchors=verse_anchors,
        findings=findings,
    )


class TextFabricBhsaProvider:
    """Thin adapter over an already loaded BHSA Text-Fabric API."""

    def __init__(self, api: object) -> None:
        self._api = typing.cast(typing.Any, api)

    def get_verse(self, book: str, chapter: int, verse: int) -> BhsaVerse | None:
        """Read one BHSA verse through Text-Fabric section/locality APIs."""

        node = typing.cast(
            int | None,
            self._api.T.nodeFromSection((book, chapter, verse)),
        )
        if node is None:
            return None

        word_nodes = tuple(
            typing.cast(
                typing.Iterable[int],
                self._api.L.d(node, otype="word"),
            )
        )
        words = tuple(
            BhsaWord(
                node=word,
                g_cons_utf8=typing.cast(str, self._api.F.g_cons_utf8.v(word)),
                g_word_utf8=typing.cast(str | None, self._api.F.g_word_utf8.v(word)),
                qere_utf8=typing.cast(str | None, self._api.F.qere_utf8.v(word)),
            )
            for word in word_nodes
        )
        return BhsaVerse(
            node=node,
            book=book,
            chapter=chapter,
            verse=verse,
            words=words,
        )
