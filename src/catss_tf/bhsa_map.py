"""Deterministic CATSS Hebrew -> BHSA 2021 word-slot resolver."""

import dataclasses
import enum
import unicodedata
from collections.abc import Callable

from catss_tf.bhsa_schema import BhsaSourceStatus, classify_catss_source
from catss_tf.parser import AlignmentRecord, ParallelDocument, VerseRecord

_CATSS_CONSONANTS = frozenset(")BGDHWZX+YKLMNS(PCQR$&#T")
_CATSS_NONCONSONANTAL = frozenset('AFIE"OU:.,-/')
_HEBREW_TO_CATSS = {
    "א": ")",
    "ב": "B",
    "ג": "G",
    "ד": "D",
    "ה": "H",
    "ו": "W",
    "ז": "Z",
    "ח": "X",
    "ט": "+",
    "י": "Y",
    "כ": "K",
    "ך": "K",
    "ל": "L",
    "מ": "M",
    "ם": "M",
    "נ": "N",
    "ן": "N",
    "ס": "S",
    "ע": "(",
    "פ": "P",
    "ף": "P",
    "צ": "C",
    "ץ": "C",
    "ק": "Q",
    "ר": "R",
    "ש": "#",
    "ת": "T",
}


class CatssHebrewNormalizationError(ValueError):
    """Raised when source Hebrew cannot be normalized without dropping evidence."""


class BhsaMapStatus(enum.Enum):
    """Resolution state for one CATSS alignment row on the BHSA side."""

    MAPPED = "mapped"
    HEBREW_EMPTY = "hebrew_empty"
    UNSUPPORTED_SOURCE = "unsupported_source"
    VERSE_MISSING = "verse_missing"
    SEQUENCE_MISMATCH = "sequence_mismatch"
    AMBIGUOUS_SEQUENCE = "ambiguous_sequence"
    UNNORMALIZABLE = "unnormalizable"


class MappingSeverity(enum.Enum):
    """Whether a mapping finding blocks trustworthy materialization."""

    ERROR = "error"
    INFO = "info"


@dataclasses.dataclass(frozen=True, slots=True)
class BhsaWordSlot:
    """Text-bearing fields needed from one BHSA 2021 word slot."""

    node: int
    g_cons_utf8: str
    g_word_utf8: str
    qere_utf8: str | None = None


@dataclasses.dataclass(frozen=True, slots=True)
class BhsaVerse:
    """Immutable BHSA verse snapshot used by the pure resolver."""

    book: str
    chapter: int
    verse: int
    verse_node: int
    words: tuple[BhsaWordSlot, ...]


@dataclasses.dataclass(frozen=True, slots=True)
class BhsaAlignmentMapping:
    """Resolved BHSA location for one canonical CATSS alignment."""

    alignment_id: str
    status: BhsaMapStatus
    bhsa_book: str | None
    chapter: int
    verse: int
    bhsa_verse_node: int | None
    bhsa_word_nodes: tuple[int, ...]
    mapping_kind: str


@dataclasses.dataclass(frozen=True, slots=True)
class BhsaMappingFinding:
    """One typed, deterministic BHSA mapping diagnostic."""

    code: str
    severity: MappingSeverity
    source_name: str
    alignment_id: str | None
    bhsa_book: str | None
    chapter: int | None
    verse: int | None
    expected: str | None
    actual: str | None
    message: str


@dataclasses.dataclass(frozen=True, slots=True)
class BhsaMappingSummary:
    """Scalar counters for one document mapping report."""

    total_alignments: int
    mapped_alignments: int
    hebrew_empty_alignments: int
    unsupported_alignments: int
    missing_verses: int
    sequence_mismatches: int
    ambiguous_sequences: int
    qere_mismatches: int
    unnormalizable_tokens: int
    finding_count: int


@dataclasses.dataclass(frozen=True, slots=True)
class BhsaMappingReport:
    """BHSA row mappings, findings, and automation-friendly counters."""

    mappings: tuple[BhsaAlignmentMapping, ...]
    findings: tuple[BhsaMappingFinding, ...]
    summary: BhsaMappingSummary

    @property
    def ok(self) -> bool:
        """Whether no blocking mapping finding remains."""

        return not any(f.severity is MappingSeverity.ERROR for f in self.findings)


@dataclasses.dataclass(frozen=True, slots=True)
class _ParentWord:
    slot: BhsaWordSlot
    cons: str
    qere: str | None
    word_index: int


@dataclasses.dataclass(frozen=True, slots=True)
class _SourceToken:
    row_index: int
    raw: str
    mode: str


@dataclasses.dataclass(frozen=True, slots=True)
class _Realization:
    forms: tuple[str, ...]
    kind: str


@dataclasses.dataclass(frozen=True, slots=True)
class _Choice:
    source: _SourceToken
    parent_indexes: tuple[int, ...]
    kind: str
    ambiguous_shin: bool


def normalize_catss_hebrew(text: str) -> str:
    """Normalize CATSS Michigan-Claremont Hebrew to a consonantal match key.

    The return alphabet is deliberately the documented CATSS consonant alphabet.
    Morphological separators and known pointing/accent material are ignored.
    Unknown characters are rejected rather than silently discarded.
    """

    out: list[str] = []
    for char in text:
        if char in _CATSS_CONSONANTS:
            out.append(char)
            continue
        if char in _CATSS_NONCONSONANTAL or char.isspace() or char.isdigit():
            continue
        raise CatssHebrewNormalizationError(
            f"unrecognized CATSS Hebrew character {char!r} in {text!r}"
        )
    result = "".join(out)
    if not result:
        raise CatssHebrewNormalizationError(
            f"CATSS Hebrew token contains no recognizable consonants: {text!r}"
        )
    return result


def normalize_bhsa_hebrew(text: str) -> str:
    """Normalize a BHSA Hebrew feature value to the CATSS consonant alphabet."""

    out: list[str] = []
    last_shin: int | None = None
    for char in unicodedata.normalize("NFKD", text):
        mapped = _HEBREW_TO_CATSS.get(char)
        if mapped is not None:
            out.append(mapped)
            last_shin = len(out) - 1 if char == "ש" else None
            continue
        if char == "ׁ" and last_shin is not None:
            out[last_shin] = "$"
            continue
        if char == "ׂ" and last_shin is not None:
            out[last_shin] = "&"
            continue
        if unicodedata.combining(char) or char.isspace() or char == "־":
            continue
        raise CatssHebrewNormalizationError(
            f"unrecognized BHSA Hebrew character {char!r} in {text!r}"
        )
    return "".join(out)


def resolve_document_to_bhsa(
    document: ParallelDocument,
    *,
    verse_lookup: Callable[[str, int, int], BhsaVerse | None],
) -> BhsaMappingReport:
    """Resolve one canonical CATSS document against BHSA verse snapshots."""

    classification = classify_catss_source(document.source_name)
    if classification.status is not BhsaSourceStatus.SUPPORTED:
        return _unsupported_report(document, classification.status)

    assert classification.bhsa_book is not None
    mappings: list[BhsaAlignmentMapping] = []
    findings: list[BhsaMappingFinding] = []

    for verse in document.verses:
        parent = verse_lookup(classification.bhsa_book, verse.chapter, verse.verse)
        if parent is None:
            mappings.extend(
                _status_mappings(
                    verse,
                    status=BhsaMapStatus.VERSE_MISSING,
                    bhsa_book=classification.bhsa_book,
                    verse_node=None,
                    mapping_kind="none",
                )
            )
            findings.append(
                _finding(
                    code="verse_missing",
                    severity=MappingSeverity.ERROR,
                    document=document,
                    alignment_id=None,
                    bhsa_book=classification.bhsa_book,
                    chapter=verse.chapter,
                    verse=verse.verse,
                    expected=f"{classification.bhsa_book} {verse.chapter}:{verse.verse}",
                    actual=None,
                    message="BHSA parent does not contain the requested verse",
                )
            )
            continue

        if (parent.book, parent.chapter, parent.verse) != (
            classification.bhsa_book,
            verse.chapter,
            verse.verse,
        ):
            mappings.extend(
                _status_mappings(
                    verse,
                    status=BhsaMapStatus.VERSE_MISSING,
                    bhsa_book=classification.bhsa_book,
                    verse_node=None,
                    mapping_kind="none",
                )
            )
            findings.append(
                _finding(
                    code="parent_reference_mismatch",
                    severity=MappingSeverity.ERROR,
                    document=document,
                    alignment_id=None,
                    bhsa_book=classification.bhsa_book,
                    chapter=verse.chapter,
                    verse=verse.verse,
                    expected=f"{classification.bhsa_book} {verse.chapter}:{verse.verse}",
                    actual=f"{parent.book} {parent.chapter}:{parent.verse}",
                    message="BHSA verse provider returned a snapshot for another reference",
                )
            )
            continue

        verse_mappings, verse_findings = _resolve_verse(
            document=document,
            source_verse=verse,
            parent=parent,
        )
        mappings.extend(verse_mappings)
        findings.extend(verse_findings)

    return _report(tuple(mappings), tuple(findings))


def _unsupported_report(
    document: ParallelDocument, source_status: BhsaSourceStatus
) -> BhsaMappingReport:
    mappings = tuple(
        BhsaAlignmentMapping(
            alignment_id=row.alignment_id,
            status=BhsaMapStatus.UNSUPPORTED_SOURCE,
            bhsa_book=None,
            chapter=verse.chapter,
            verse=verse.verse,
            bhsa_verse_node=None,
            bhsa_word_nodes=(),
            mapping_kind="none",
        )
        for verse in document.verses
        for row in verse.alignments
    )
    declared = source_status is BhsaSourceStatus.UNSUPPORTED
    finding = BhsaMappingFinding(
        code="unsupported_source" if declared else "unknown_source",
        severity=MappingSeverity.INFO if declared else MappingSeverity.ERROR,
        source_name=document.source_name,
        alignment_id=None,
        bhsa_book=None,
        chapter=None,
        verse=None,
        expected=None,
        actual=document.source_name,
        message=(
            "CATSS source is explicitly outside BHSA projection coverage"
            if declared
            else "CATSS source is not present in the versioned BHSA source map"
        ),
    )
    return _report(mappings, (finding,))


def _resolve_verse(
    *,
    document: ParallelDocument,
    source_verse: VerseRecord,
    parent: BhsaVerse,
) -> tuple[tuple[BhsaAlignmentMapping, ...], tuple[BhsaMappingFinding, ...]]:
    findings: list[BhsaMappingFinding] = []
    parent_words: list[_ParentWord] = []

    try:
        for index, word in enumerate(parent.words):
            cons = normalize_bhsa_hebrew(word.g_cons_utf8)
            qere = normalize_bhsa_hebrew(word.qere_utf8) if word.qere_utf8 is not None else None
            parent_words.append(_ParentWord(slot=word, cons=cons, qere=qere, word_index=index))
    except CatssHebrewNormalizationError as exc:
        findings.append(
            _finding(
                code="parent_form_unnormalizable",
                severity=MappingSeverity.ERROR,
                document=document,
                alignment_id=None,
                bhsa_book=parent.book,
                chapter=parent.chapter,
                verse=parent.verse,
                expected=None,
                actual=str(exc),
                message="BHSA text feature contains an unsupported character",
            )
        )
        return (
            tuple(
                _mapping(
                    row,
                    source_verse,
                    parent,
                    status=(
                        BhsaMapStatus.HEBREW_EMPTY
                        if not row.mt_tokens
                        else BhsaMapStatus.UNNORMALIZABLE
                    ),
                    nodes=(),
                    kind="none",
                )
                for row in source_verse.alignments
            ),
            tuple(findings),
        )

    nonempty = tuple(word for word in parent_words if word.cons)
    source_tokens: list[_SourceToken] = []
    realization_by_token: list[tuple[_Realization, ...]] = []
    bad_rows: set[int] = set()

    for row_index, row in enumerate(source_verse.alignments):
        qere_only = row.is_qere and not row.is_ketiv and bool(row.mt_qere_tokens)
        mode = "qere" if qere_only else "cons"
        for raw in row.mt_tokens:
            token = _SourceToken(row_index=row_index, raw=raw, mode=mode)
            try:
                variants = _realizations(raw)
            except CatssHebrewNormalizationError as exc:
                bad_rows.add(row_index)
                findings.append(
                    _finding(
                        code="unnormalizable_token",
                        severity=MappingSeverity.ERROR,
                        document=document,
                        alignment_id=row.alignment_id,
                        bhsa_book=parent.book,
                        chapter=parent.chapter,
                        verse=parent.verse,
                        expected=raw,
                        actual=None,
                        message=str(exc),
                    )
                )
                continue
            source_tokens.append(token)
            realization_by_token.append(variants)

    if bad_rows:
        return (
            tuple(
                _mapping(
                    row,
                    source_verse,
                    parent,
                    status=(
                        BhsaMapStatus.HEBREW_EMPTY
                        if not row.mt_tokens
                        else BhsaMapStatus.UNNORMALIZABLE
                    ),
                    nodes=(),
                    kind="none",
                )
                for row in source_verse.alignments
            ),
            tuple(findings),
        )

    paths: dict[int, list[tuple[_Choice, ...]]] = {0: [()]}
    for source, variants in zip(source_tokens, realization_by_token, strict=True):
        next_paths: dict[int, list[tuple[_Choice, ...]]] = {}
        for parent_start, partials in sorted(paths.items()):
            for variant in variants:
                parent_end = parent_start + len(variant.forms)
                if parent_end > len(nonempty):
                    continue
                matched, used_ambiguous = _variant_matches(
                    source.mode,
                    variant.forms,
                    nonempty[parent_start:parent_end],
                )
                if not matched:
                    continue
                choice = _Choice(
                    source=source,
                    parent_indexes=tuple(range(parent_start, parent_end)),
                    kind=variant.kind,
                    ambiguous_shin=used_ambiguous,
                )
                bucket = next_paths.setdefault(parent_end, [])
                for partial in partials:
                    if len(bucket) >= 2:
                        break
                    bucket.append(partial + (choice,))
        paths = next_paths
        if not paths:
            break

    complete = paths.get(len(nonempty), [])
    if not complete:
        expected, actual = _first_sequence_difference(
            source_tokens,
            realization_by_token,
            nonempty,
        )
        findings.append(
            _finding(
                code="sequence_mismatch",
                severity=MappingSeverity.ERROR,
                document=document,
                alignment_id=None,
                bhsa_book=parent.book,
                chapter=parent.chapter,
                verse=parent.verse,
                expected=expected,
                actual=actual,
                message="CATSS MT sequence does not exactly cover BHSA non-empty word slots",
            )
        )
        return (
            tuple(
                _mapping(
                    row,
                    source_verse,
                    parent,
                    status=(
                        BhsaMapStatus.HEBREW_EMPTY
                        if not row.mt_tokens
                        else BhsaMapStatus.SEQUENCE_MISMATCH
                    ),
                    nodes=(),
                    kind="none",
                )
                for row in source_verse.alignments
            ),
            tuple(findings),
        )

    if len(complete) > 1:
        findings.append(
            _finding(
                code="ambiguous_sequence",
                severity=MappingSeverity.ERROR,
                document=document,
                alignment_id=None,
                bhsa_book=parent.book,
                chapter=parent.chapter,
                verse=parent.verse,
                expected=None,
                actual=None,
                message="more than one complete CATSS-to-BHSA textual mapping exists",
            )
        )
        return (
            tuple(
                _mapping(
                    row,
                    source_verse,
                    parent,
                    status=(
                        BhsaMapStatus.HEBREW_EMPTY
                        if not row.mt_tokens
                        else BhsaMapStatus.AMBIGUOUS_SEQUENCE
                    ),
                    nodes=(),
                    kind="none",
                )
                for row in source_verse.alignments
            ),
            tuple(findings),
        )

    path = complete[0]
    row_choices: dict[int, list[_Choice]] = {}
    for choice in path:
        row_choices.setdefault(choice.source.row_index, []).append(choice)

    word_by_node = {word.slot.node: word for word in parent_words}
    node_to_word_index = {word.slot.node: word.word_index for word in parent_words}
    mappings: list[BhsaAlignmentMapping] = []
    row_primary_nodes: dict[int, tuple[int, ...]] = {}

    for row_index, row in enumerate(source_verse.alignments):
        choices = row_choices.get(row_index, [])
        if not choices:
            mappings.append(
                _mapping(
                    row,
                    source_verse,
                    parent,
                    status=BhsaMapStatus.HEBREW_EMPTY,
                    nodes=(),
                    kind="none",
                )
            )
            row_primary_nodes[row_index] = ()
            continue

        primary_nodes = tuple(
            nonempty[parent_index].slot.node
            for choice in choices
            for parent_index in choice.parent_indexes
        )
        row_primary_nodes[row_index] = primary_nodes
        first_index = node_to_word_index[primary_nodes[0]]
        last_index = node_to_word_index[primary_nodes[-1]]
        span = parent_words[first_index : last_index + 1]
        primary_set = set(primary_nodes)
        unexpected = [word for word in span if word.cons and word.slot.node not in primary_set]
        if unexpected:
            findings.append(
                _finding(
                    code="noncontiguous_row_mapping",
                    severity=MappingSeverity.ERROR,
                    document=document,
                    alignment_id=row.alignment_id,
                    bhsa_book=parent.book,
                    chapter=parent.chapter,
                    verse=parent.verse,
                    expected=",".join(str(node) for node in primary_nodes),
                    actual=",".join(str(word.slot.node) for word in unexpected),
                    message="resolved row would cross a non-empty BHSA slot owned by another row",
                )
            )
            nodes = primary_nodes
        else:
            nodes = tuple(word.slot.node for word in span)

        mappings.append(
            _mapping(
                row,
                source_verse,
                parent,
                status=BhsaMapStatus.MAPPED,
                nodes=nodes,
                kind=_mapping_kind(choices),
            )
        )

    for row_index, row in enumerate(source_verse.alignments):
        if not (row.is_ketiv and row.is_qere):
            continue
        primary_nodes = row_primary_nodes.get(row_index, ())
        if len(row.mt_qere_tokens) != 1 or len(primary_nodes) != 1:
            findings.append(
                _finding(
                    code="qere_structure_ambiguous",
                    severity=MappingSeverity.ERROR,
                    document=document,
                    alignment_id=row.alignment_id,
                    bhsa_book=parent.book,
                    chapter=parent.chapter,
                    verse=parent.verse,
                    expected=" ".join(row.mt_qere_tokens),
                    actual=",".join(str(node) for node in primary_nodes),
                    message=(
                        "paired CATSS Qere cannot be associated uniquely with one BHSA word slot"
                    ),
                )
            )
            continue

        node = primary_nodes[0]
        try:
            expected_qere = normalize_catss_hebrew(row.mt_qere_tokens[0])
        except CatssHebrewNormalizationError as exc:
            findings.append(
                _finding(
                    code="unnormalizable_token",
                    severity=MappingSeverity.ERROR,
                    document=document,
                    alignment_id=row.alignment_id,
                    bhsa_book=parent.book,
                    chapter=parent.chapter,
                    verse=parent.verse,
                    expected=row.mt_qere_tokens[0],
                    actual=None,
                    message=str(exc),
                )
            )
            continue

        actual_qere = word_by_node[node].qere
        if not actual_qere:
            findings.append(
                _finding(
                    code="qere_missing_in_bhsa",
                    severity=MappingSeverity.ERROR,
                    document=document,
                    alignment_id=row.alignment_id,
                    bhsa_book=parent.book,
                    chapter=parent.chapter,
                    verse=parent.verse,
                    expected=expected_qere,
                    actual=None,
                    message="CATSS marks a Qere but BHSA qere_utf8 is empty on the resolved slot",
                )
            )
            continue

        matches, _ = _forms_match(expected_qere, actual_qere)
        if not matches:
            findings.append(
                _finding(
                    code="qere_mismatch",
                    severity=MappingSeverity.ERROR,
                    document=document,
                    alignment_id=row.alignment_id,
                    bhsa_book=parent.book,
                    chapter=parent.chapter,
                    verse=parent.verse,
                    expected=expected_qere,
                    actual=actual_qere,
                    message="CATSS Qere does not match BHSA qere_utf8 on the resolved slot",
                )
            )

    return tuple(mappings), tuple(findings)


def _realizations(raw: str) -> tuple[_Realization, ...]:
    whole = normalize_catss_hebrew(raw)
    variants = [_Realization(forms=(whole,), kind="exact")]
    if "/" not in raw:
        return tuple(variants)

    segments = raw.split("/")
    if all(segments):
        split_forms = tuple(normalize_catss_hebrew(segment) for segment in segments)
        if split_forms != (whole,):
            variants.append(_Realization(forms=split_forms, kind="slash_split"))
    return tuple(variants)


def _variant_matches(
    mode: str,
    expected: tuple[str, ...],
    parent: tuple[_ParentWord, ...],
) -> tuple[bool, bool]:
    used_ambiguous = False
    for expected_form, word in zip(expected, parent, strict=True):
        actual = word.qere if mode == "qere" else word.cons
        if not actual:
            return False, False
        matches, ambiguous = _forms_match(expected_form, actual)
        if not matches:
            return False, False
        used_ambiguous = used_ambiguous or ambiguous
    return True, used_ambiguous


def _forms_match(expected: str, actual: str) -> tuple[bool, bool]:
    if expected == actual:
        return True, False
    if len(expected) != len(actual):
        return False, False

    ambiguous = False
    for source_char, parent_char in zip(expected, actual, strict=True):
        if source_char == parent_char:
            continue
        if source_char == "#" and parent_char in {"$", "&", "#"}:
            ambiguous = True
            continue
        return False, False
    return True, ambiguous


def _first_sequence_difference(
    sources: list[_SourceToken],
    variants_by_token: list[tuple[_Realization, ...]],
    parent: tuple[_ParentWord, ...],
) -> tuple[str, str]:
    parent_index = 0
    for source, variants in zip(sources, variants_by_token, strict=True):
        matching: list[_Realization] = []
        for variant in variants:
            end = parent_index + len(variant.forms)
            if end > len(parent):
                continue
            ok, _ = _variant_matches(source.mode, variant.forms, parent[parent_index:end])
            if ok:
                matching.append(variant)
        if not matching:
            expected = variants[0].forms[0]
            if parent_index >= len(parent):
                return expected, "<end>"
            actual = (
                parent[parent_index].qere if source.mode == "qere" else parent[parent_index].cons
            )
            return expected, actual or "<missing-qere>"
        chosen = matching[0]
        parent_index += len(chosen.forms)

    if parent_index < len(parent):
        return "<end>", parent[parent_index].cons
    return "<unresolved>", "<unresolved>"


def _mapping_kind(choices: list[_Choice]) -> str:
    flags: set[str] = set()
    if any(choice.kind == "slash_split" for choice in choices):
        flags.add("slash_split")
    if any(choice.source.mode == "qere" for choice in choices):
        flags.add("qere")
    if any(choice.ambiguous_shin for choice in choices):
        flags.add("ambiguous_shin")
    if not flags:
        return "exact"
    if len(flags) == 1:
        return next(iter(flags))
    return "mixed"


def _status_mappings(
    verse: VerseRecord,
    *,
    status: BhsaMapStatus,
    bhsa_book: str | None,
    verse_node: int | None,
    mapping_kind: str,
) -> tuple[BhsaAlignmentMapping, ...]:
    return tuple(
        BhsaAlignmentMapping(
            alignment_id=row.alignment_id,
            status=status,
            bhsa_book=bhsa_book,
            chapter=verse.chapter,
            verse=verse.verse,
            bhsa_verse_node=verse_node,
            bhsa_word_nodes=(),
            mapping_kind=mapping_kind,
        )
        for row in verse.alignments
    )


def _mapping(
    row: AlignmentRecord,
    verse: VerseRecord,
    parent: BhsaVerse,
    *,
    status: BhsaMapStatus,
    nodes: tuple[int, ...],
    kind: str,
) -> BhsaAlignmentMapping:
    return BhsaAlignmentMapping(
        alignment_id=row.alignment_id,
        status=status,
        bhsa_book=parent.book,
        chapter=verse.chapter,
        verse=verse.verse,
        bhsa_verse_node=parent.verse_node,
        bhsa_word_nodes=nodes,
        mapping_kind=kind,
    )


def _finding(
    *,
    code: str,
    severity: MappingSeverity,
    document: ParallelDocument,
    alignment_id: str | None,
    bhsa_book: str | None,
    chapter: int | None,
    verse: int | None,
    expected: str | None,
    actual: str | None,
    message: str,
) -> BhsaMappingFinding:
    return BhsaMappingFinding(
        code=code,
        severity=severity,
        source_name=document.source_name,
        alignment_id=alignment_id,
        bhsa_book=bhsa_book,
        chapter=chapter,
        verse=verse,
        expected=expected,
        actual=actual,
        message=message,
    )


def _report(
    mappings: tuple[BhsaAlignmentMapping, ...],
    findings: tuple[BhsaMappingFinding, ...],
) -> BhsaMappingReport:
    return BhsaMappingReport(
        mappings=mappings,
        findings=findings,
        summary=BhsaMappingSummary(
            total_alignments=len(mappings),
            mapped_alignments=sum(m.status is BhsaMapStatus.MAPPED for m in mappings),
            hebrew_empty_alignments=sum(m.status is BhsaMapStatus.HEBREW_EMPTY for m in mappings),
            unsupported_alignments=sum(
                m.status is BhsaMapStatus.UNSUPPORTED_SOURCE for m in mappings
            ),
            missing_verses=sum(f.code == "verse_missing" for f in findings),
            sequence_mismatches=sum(f.code == "sequence_mismatch" for f in findings),
            ambiguous_sequences=sum(f.code == "ambiguous_sequence" for f in findings),
            qere_mismatches=sum(
                f.code in {"qere_mismatch", "qere_missing_in_bhsa"} for f in findings
            ),
            unnormalizable_tokens=sum(f.code == "unnormalizable_token" for f in findings),
            finding_count=len(findings),
        ),
    )
