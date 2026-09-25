"""Strict CATSS Greek -> CenterBLC/LXX word-slot resolver."""

import dataclasses
import typing
import unicodedata

from catss_tf.lxx_schema import (
    LxxParentProbe,
    LxxSourceStatus,
    classify_catss_source,
    default_lxx_reference,
    validate_lxx_parent,
)
from catss_tf.parser import AlignmentRecord, GreekReference, ParallelDocument
from catss_tf.validation import ValidationFinding, validate_document

_CATSS_GREEK = {
    "A": "α",
    "B": "β",
    "G": "γ",
    "D": "δ",
    "E": "ε",
    "V": "ϝ",
    "Z": "ζ",
    "H": "η",
    "Q": "θ",
    "I": "ι",
    "K": "κ",
    "L": "λ",
    "M": "μ",
    "N": "ν",
    "C": "ξ",
    "O": "ο",
    "P": "π",
    "R": "ρ",
    "S": "σ",
    "J": "σ",
    "T": "τ",
    "U": "υ",
    "F": "φ",
    "X": "χ",
    "Y": "ψ",
    "W": "ω",
}
_CATSS_DIACRITICS = frozenset({"(", ")", "/", "\\", "=", "+", "|", "*"})
_APOSTROPHES = frozenset({"'", "ʼ", "’", "᾽"})
_EMPTY_ALIGNMENT_MESSAGE = "Greek-empty alignment has no recognized empty-row semantics"


@dataclasses.dataclass(frozen=True, slots=True)
class LxxWord:
    """Mapping-relevant view of one CenterBLC word slot."""

    node: int
    word: str
    subverse: str
    orig_order: str


@dataclasses.dataclass(frozen=True, slots=True)
class LxxSpan:
    """One exact parent reference span used for placement."""

    node: int
    book: str
    chapter: int
    verse: int
    subverse: str | None
    words: tuple[LxxWord, ...]


class LxxVerseProvider(typing.Protocol):
    """Minimal parent-corpus interface required by the pure resolver."""

    parent_probe: LxxParentProbe

    def get_span(
        self,
        book: str,
        chapter: int,
        verse: int,
        subverse: str | None = None,
    ) -> LxxSpan | None:
        """Return one exact CenterBLC verse/subverse span or None."""


@dataclasses.dataclass(frozen=True, slots=True)
class LxxWordMapping:
    """A proven CATSS Greek token -> CenterBLC word-node mapping."""

    alignment_id: str
    lxx_index: int
    lxx_node: int
    reference_book: str
    reference_chapter: int
    reference_verse: int
    reference_subverse: str | None
    mapping_kind: typing.Literal[
        "exact", "transposition_alignment", "transposition_carrier"
    ] = "exact"


@dataclasses.dataclass(frozen=True, slots=True)
class LxxReferenceAnchor:
    """A non-word anchor for a Greek-empty CATSS alignment."""

    alignment_id: str
    lxx_reference_node: int
    reference_book: str
    reference_chapter: int
    reference_verse: int
    reference_subverse: str | None
    kind: typing.Literal["lxx_minus", "transposition_placeholder"]


@dataclasses.dataclass(frozen=True, slots=True)
class LxxMappingFinding:
    """One explicit LXX resolution failure."""

    code: str
    source_name: str
    chapter: int | None
    verse: int | None
    alignment_id: str | None
    catss_value: str | None
    parent_value: str | None
    message: str


@dataclasses.dataclass(frozen=True, slots=True)
class LxxMappingSummary:
    """Scalar resolver counters for automation and corpus audits."""

    documents: int
    supported_documents: int
    unsupported_documents: int
    unknown_documents: int
    verses: int
    reference_groups: int
    resolved_reference_groups: int
    missing_reference_groups: int
    mismatched_reference_groups: int
    ambiguous_reference_groups: int
    word_mappings: int
    reference_anchors: int
    reference_overrides: int
    normalization_errors: int
    parent_failures: int
    validation_failures: int
    validation_ignored: int
    finding_count: int


@dataclasses.dataclass(frozen=True, slots=True)
class LxxMappingReport:
    """Deterministic CATSS -> CenterBLC mapping/audit result."""

    summary: LxxMappingSummary
    word_mappings: tuple[LxxWordMapping, ...]
    reference_anchors: tuple[LxxReferenceAnchor, ...]
    findings: tuple[LxxMappingFinding, ...]
    validation_findings: tuple[ValidationFinding, ...]

    @property
    def ok(self) -> bool:
        """Whether the report contains no blocking mapping finding."""

        return not self.findings


@dataclasses.dataclass(frozen=True, slots=True)
class _ReferenceKey:
    book: str
    chapter: int
    verse: int
    subverse: str | None


@dataclasses.dataclass(frozen=True, slots=True)
class _PlacementTask:
    order: int
    alignment: AlignmentRecord
    reference: _ReferenceKey
    normalized_tokens: tuple[str, ...]


@dataclasses.dataclass(frozen=True, slots=True)
class _Candidate:
    start: int
    stop: int


def normalize_catss_greek(value: str) -> str:
    """Normalize one CATSS BETA-coded Greek surface token for identity."""

    output: list[str] = []
    for character in value:
        mapped = _CATSS_GREEK.get(character)
        if mapped is not None:
            output.append(mapped)
            continue
        if character in _CATSS_DIACRITICS:
            continue
        if character in _APOSTROPHES:
            output.append("ʼ")
            continue
        if character == "-":
            output.append(character)
            continue
        raise ValueError(f"unsupported CATSS Greek character {character!r} in {value!r}")

    if not output:
        raise ValueError("CATSS Greek token is empty after normalization")
    return "".join(output)


def normalize_lxx_greek(value: str) -> str:
    """Normalize one CenterBLC realized Greek word without lemmatizing it."""

    output: list[str] = []
    for character in unicodedata.normalize("NFD", value):
        if unicodedata.combining(character):
            continue
        if character.isspace():
            continue
        if character in _APOSTROPHES:
            output.append("ʼ")
            continue
        if character == "-":
            output.append(character)
            continue
        lowered = character.lower()
        if lowered == "ς":
            lowered = "σ"
        if ("α" <= lowered <= "ω") or lowered == "ϝ":
            output.append(lowered)
            continue
        raise ValueError(f"unsupported CenterBLC Greek character {character!r} in {value!r}")

    if not output:
        raise ValueError("CenterBLC Greek word is empty after normalization")
    return "".join(output)


def resolve_lxx_document(
    document: ParallelDocument,
    provider: LxxVerseProvider,
    *,
    allowed_validation_codes: set[str] | frozenset[str] = frozenset(),
) -> LxxMappingReport:
    """Resolve one CATSS parallel document against CenterBLC/LXX."""

    return resolve_lxx_documents(
        (document,),
        provider,
        allowed_validation_codes=allowed_validation_codes,
    )


def resolve_lxx_documents(
    documents: tuple[ParallelDocument, ...],
    provider: LxxVerseProvider,
    *,
    allowed_validation_codes: set[str] | frozenset[str] = frozenset(),
) -> LxxMappingReport:
    """Resolve/audit multiple CATSS documents through one strict mapping path."""

    parent_validation = validate_lxx_parent(provider.parent_probe)
    if not parent_validation.ok:
        findings = tuple(
            LxxMappingFinding(
                code=f"parent_{finding.code}",
                source_name="<parent>",
                chapter=None,
                verse=None,
                alignment_id=None,
                catss_value=finding.expected,
                parent_value=finding.actual,
                message="CenterBLC parent does not satisfy the v0.1 LXX profile",
            )
            for finding in parent_validation.findings
        )
        return _report(
            documents=len(documents),
            parent_failures=len(parent_validation.findings),
            findings=findings,
        )

    word_mappings: list[LxxWordMapping] = []
    anchors: list[LxxReferenceAnchor] = []
    findings: list[LxxMappingFinding] = []
    validation_findings: list[ValidationFinding] = []

    supported_documents = 0
    unsupported_documents = 0
    unknown_documents = 0
    verses = 0
    reference_groups = 0
    resolved_reference_groups = 0
    missing_reference_groups = 0
    mismatched_reference_groups = 0
    ambiguous_reference_groups = 0
    reference_overrides = 0
    normalization_errors = 0
    validation_failures = 0
    validation_ignored = 0

    for document in documents:
        verses += len(document.verses)
        classification = classify_catss_source(document.source_name)
        if classification.status is LxxSourceStatus.UNSUPPORTED:
            unsupported_documents += 1
            continue
        if classification.status is LxxSourceStatus.UNKNOWN:
            unknown_documents += 1
            findings.append(
                LxxMappingFinding(
                    code="unknown_catss_source",
                    source_name=document.source_name,
                    chapter=None,
                    verse=None,
                    alignment_id=None,
                    catss_value=None,
                    parent_value=None,
                    message="CATSS source is not classified for the LXX projection",
                )
            )
            continue

        supported_documents += 1
        validation = validate_document(document, allowed_codes=allowed_validation_codes)
        validation_findings.extend(validation.findings)
        validation_ignored += validation.summary.ignored_count
        if not validation.ok:
            failures = validation.summary.error_count + validation.summary.unresolved_count
            validation_failures += failures
            findings.extend(
                LxxMappingFinding(
                    code=f"catss_validation_{finding.code}",
                    source_name=finding.source_name,
                    chapter=None,
                    verse=None,
                    alignment_id=finding.alignment_id,
                    catss_value=finding.raw,
                    parent_value=None,
                    message=f"CATSS validation {finding.severity}: {finding.message}",
                )
                for finding in validation.findings
                if finding.severity != "ignored"
            )
            continue

        tasks_by_reference: dict[_ReferenceKey, list[_PlacementTask]] = {}
        empty_by_reference: dict[_ReferenceKey, list[AlignmentRecord]] = {}
        broken_references: set[_ReferenceKey] = set()
        task_order = 0

        for verse in document.verses:
            default = default_lxx_reference(document.source_name, verse.chapter, verse.verse)
            for alignment in verse.alignments:
                reference, override, reference_finding = _alignment_reference(
                    document.source_name,
                    verse.chapter,
                    verse.verse,
                    alignment,
                    default.book,
                    default.chapter,
                    default.verse,
                )
                if reference_finding is not None:
                    findings.append(reference_finding)
                    continue
                assert reference is not None
                if override:
                    reference_overrides += 1

                if not alignment.lxx_tokens:
                    if alignment.is_lxx_minus or alignment.is_transposition_remote:
                        empty_by_reference.setdefault(reference, []).append(alignment)
                    else:
                        findings.append(
                            LxxMappingFinding(
                                code="empty_lxx_alignment",
                                source_name=document.source_name,
                                chapter=verse.chapter,
                                verse=verse.verse,
                                alignment_id=alignment.alignment_id,
                                catss_value=alignment.lxx_raw,
                                parent_value=None,
                                message=_EMPTY_ALIGNMENT_MESSAGE,
                            )
                        )
                        broken_references.add(reference)
                    continue

                normalized: list[str] = []
                failed = False
                for token in alignment.lxx_tokens:
                    try:
                        normalized.append(normalize_catss_greek(token))
                    except ValueError as exc:
                        normalization_errors += 1
                        findings.append(
                            LxxMappingFinding(
                                code="catss_greek_normalization_error",
                                source_name=document.source_name,
                                chapter=verse.chapter,
                                verse=verse.verse,
                                alignment_id=alignment.alignment_id,
                                catss_value=token,
                                parent_value=None,
                                message=str(exc),
                            )
                        )
                        broken_references.add(reference)
                        failed = True
                        break
                if failed:
                    continue

                tasks_by_reference.setdefault(reference, []).append(
                    _PlacementTask(
                        order=task_order,
                        alignment=alignment,
                        reference=reference,
                        normalized_tokens=tuple(normalized),
                    )
                )
                task_order += 1

        all_references = set(tasks_by_reference) | set(empty_by_reference) | broken_references
        reference_groups += len(all_references)

        for reference in sorted(all_references, key=_reference_sort_key):
            span = provider.get_span(
                reference.book,
                reference.chapter,
                reference.verse,
                reference.subverse,
            )
            if span is None:
                missing_reference_groups += 1
                findings.append(
                    LxxMappingFinding(
                        code="missing_lxx_reference",
                        source_name=document.source_name,
                        chapter=reference.chapter,
                        verse=reference.verse,
                        alignment_id=None,
                        catss_value=_reference_text(reference),
                        parent_value=None,
                        message="CenterBLC parent has no matching reference span",
                    )
                )
                continue

            for alignment in empty_by_reference.get(reference, ()):
                anchors.append(
                    LxxReferenceAnchor(
                        alignment_id=alignment.alignment_id,
                        lxx_reference_node=span.node,
                        reference_book=reference.book,
                        reference_chapter=reference.chapter,
                        reference_verse=reference.verse,
                        reference_subverse=reference.subverse,
                        kind="lxx_minus" if alignment.is_lxx_minus else "transposition_placeholder",
                    )
                )

            if reference in broken_references:
                mismatched_reference_groups += 1
                continue

            tasks = tasks_by_reference.get(reference, [])
            if not tasks:
                resolved_reference_groups += 1
                continue

            try:
                parent_tokens = tuple(normalize_lxx_greek(word.word) for word in span.words)
            except ValueError as exc:
                normalization_errors += 1
                mismatched_reference_groups += 1
                findings.append(
                    LxxMappingFinding(
                        code="parent_greek_normalization_error",
                        source_name=document.source_name,
                        chapter=reference.chapter,
                        verse=reference.verse,
                        alignment_id=None,
                        catss_value=None,
                        parent_value=None,
                        message=str(exc),
                    )
                )
                continue

            candidates: dict[int, tuple[_Candidate, ...]] = {}
            missing_task: _PlacementTask | None = None
            for task in tasks:
                task_candidates = _find_candidates(task.normalized_tokens, parent_tokens)
                candidates[task.order] = task_candidates
                if not task_candidates and missing_task is None:
                    missing_task = task

            if missing_task is not None:
                mismatched_reference_groups += 1
                findings.append(
                    LxxMappingFinding(
                        code="surface_placement_missing",
                        source_name=document.source_name,
                        chapter=reference.chapter,
                        verse=reference.verse,
                        alignment_id=missing_task.alignment.alignment_id,
                        catss_value=" ".join(missing_task.normalized_tokens),
                        parent_value=" ".join(parent_tokens),
                        message="no exact CenterBLC surface span matches this CATSS Greek row",
                    )
                )
                continue

            solutions = _solve_unique_assignment(tasks, candidates)
            if len(solutions) != 1:
                if not solutions:
                    mismatched_reference_groups += 1
                    code = "surface_placement_conflict"
                else:
                    ambiguous_reference_groups += 1
                    code = "surface_placement_ambiguous"
                findings.append(
                    LxxMappingFinding(
                        code=code,
                        source_name=document.source_name,
                        chapter=reference.chapter,
                        verse=reference.verse,
                        alignment_id=None,
                        catss_value=None,
                        parent_value=None,
                        message=(
                            "exact CATSS Greek rows have no non-overlapping joint placement"
                            if not solutions
                            else "more than one exact non-overlapping joint placement exists"
                        ),
                    )
                )
                continue

            assignment = solutions[0]
            for task in sorted(tasks, key=lambda item: item.order):
                candidate = assignment[task.order]
                word_indexes = range(candidate.start, candidate.stop)
                for lxx_index, word_index in enumerate(word_indexes):
                    word = span.words[word_index]
                    word_mappings.append(
                        LxxWordMapping(
                            alignment_id=task.alignment.alignment_id,
                            lxx_index=lxx_index,
                            lxx_node=word.node,
                            reference_book=reference.book,
                            reference_chapter=reference.chapter,
                            reference_verse=reference.verse,
                            reference_subverse=reference.subverse,
                            mapping_kind=_mapping_kind(task.alignment),
                        )
                    )
            resolved_reference_groups += 1

    return _report(
        documents=len(documents),
        supported_documents=supported_documents,
        unsupported_documents=unsupported_documents,
        unknown_documents=unknown_documents,
        verses=verses,
        reference_groups=reference_groups,
        resolved_reference_groups=resolved_reference_groups,
        missing_reference_groups=missing_reference_groups,
        mismatched_reference_groups=mismatched_reference_groups,
        ambiguous_reference_groups=ambiguous_reference_groups,
        word_mappings=tuple(word_mappings),
        reference_anchors=tuple(anchors),
        reference_overrides=reference_overrides,
        normalization_errors=normalization_errors,
        parent_failures=0,
        validation_failures=validation_failures,
        validation_ignored=validation_ignored,
        findings=tuple(findings),
        validation_findings=tuple(validation_findings),
    )


def _alignment_reference(
    source_name: str,
    source_chapter: int,
    source_verse: int,
    alignment: AlignmentRecord,
    default_book: str,
    default_chapter: int,
    default_verse: int,
) -> tuple[_ReferenceKey | None, bool, LxxMappingFinding | None]:
    distinct = tuple(dict.fromkeys(alignment.lxx_references))
    if len(distinct) > 1:
        return (
            None,
            False,
            LxxMappingFinding(
                code="multiple_lxx_references",
                source_name=source_name,
                chapter=source_chapter,
                verse=source_verse,
                alignment_id=alignment.alignment_id,
                catss_value=" ".join(reference.raw for reference in distinct),
                parent_value=None,
                message="one CATSS alignment carries multiple distinct Greek references",
            ),
        )

    if not distinct:
        return (
            _ReferenceKey(default_book, default_chapter, default_verse, None),
            False,
            None,
        )

    override: GreekReference = distinct[0]
    return (
        _ReferenceKey(
            default_book,
            default_chapter if override.chapter is None else override.chapter,
            override.verse,
            override.subverse,
        ),
        True,
        None,
    )


def _find_candidates(
    needle: tuple[str, ...],
    haystack: tuple[str, ...],
) -> tuple[_Candidate, ...]:
    width = len(needle)
    if width == 0 or width > len(haystack):
        return ()
    return tuple(
        _Candidate(start=index, stop=index + width)
        for index in range(len(haystack) - width + 1)
        if haystack[index : index + width] == needle
    )


def _solve_unique_assignment(
    tasks: list[_PlacementTask],
    candidates: dict[int, tuple[_Candidate, ...]],
) -> list[dict[int, _Candidate]]:
    ordered = sorted(tasks, key=lambda task: (len(candidates[task.order]), task.order))
    task_by_order = {task.order: task for task in tasks}
    solutions: list[dict[int, _Candidate]] = []

    def visit(
        index: int,
        assignment: dict[int, _Candidate],
    ) -> None:
        if len(solutions) >= 2:
            return
        if index == len(ordered):
            solutions.append(dict(assignment))
            return

        task = ordered[index]
        for candidate in candidates[task.order]:
            if any(
                _placements_conflict(
                    task,
                    candidate,
                    task_by_order[existing_order],
                    existing_candidate,
                )
                for existing_order, existing_candidate in assignment.items()
            ):
                continue
            assignment[task.order] = candidate
            visit(index + 1, assignment)
            assignment.pop(task.order, None)

    visit(0, {})
    return solutions


def _placements_conflict(
    left_task: _PlacementTask,
    left: _Candidate,
    right_task: _PlacementTask,
    right: _Candidate,
) -> bool:
    overlap = max(left.start, right.start) < min(left.stop, right.stop)
    if not overlap:
        return False
    if left != right:
        return True

    roles = {_mapping_kind(left_task.alignment), _mapping_kind(right_task.alignment)}
    return roles != {"transposition_alignment", "transposition_carrier"}


def _mapping_kind(
    alignment: AlignmentRecord,
) -> typing.Literal["exact", "transposition_alignment", "transposition_carrier"]:
    if any(
        annotation.side == "lxx"
        and annotation.kind in {"transposition_stylistic", "transposition_remote"}
        for annotation in alignment.annotations
    ):
        return "transposition_alignment"
    if any(
        annotation.side == "mt_a"
        and annotation.kind == "transposition_remote"
        and annotation.raw == "{...}"
        for annotation in alignment.annotations
    ):
        return "transposition_carrier"
    return "exact"


def _reference_sort_key(reference: _ReferenceKey) -> tuple[str, int, int, str]:
    return (
        reference.book,
        reference.chapter,
        reference.verse,
        "" if reference.subverse is None else reference.subverse,
    )


def _reference_text(reference: _ReferenceKey) -> str:
    suffix = "" if reference.subverse is None else reference.subverse
    return f"{reference.book} {reference.chapter}:{reference.verse}{suffix}"


def _report(
    *,
    documents: int,
    supported_documents: int = 0,
    unsupported_documents: int = 0,
    unknown_documents: int = 0,
    verses: int = 0,
    reference_groups: int = 0,
    resolved_reference_groups: int = 0,
    missing_reference_groups: int = 0,
    mismatched_reference_groups: int = 0,
    ambiguous_reference_groups: int = 0,
    word_mappings: tuple[LxxWordMapping, ...] = (),
    reference_anchors: tuple[LxxReferenceAnchor, ...] = (),
    reference_overrides: int = 0,
    normalization_errors: int = 0,
    parent_failures: int = 0,
    validation_failures: int = 0,
    validation_ignored: int = 0,
    findings: tuple[LxxMappingFinding, ...] = (),
    validation_findings: tuple[ValidationFinding, ...] = (),
) -> LxxMappingReport:
    return LxxMappingReport(
        summary=LxxMappingSummary(
            documents=documents,
            supported_documents=supported_documents,
            unsupported_documents=unsupported_documents,
            unknown_documents=unknown_documents,
            verses=verses,
            reference_groups=reference_groups,
            resolved_reference_groups=resolved_reference_groups,
            missing_reference_groups=missing_reference_groups,
            mismatched_reference_groups=mismatched_reference_groups,
            ambiguous_reference_groups=ambiguous_reference_groups,
            word_mappings=len(word_mappings),
            reference_anchors=len(reference_anchors),
            reference_overrides=reference_overrides,
            normalization_errors=normalization_errors,
            parent_failures=parent_failures,
            validation_failures=validation_failures,
            validation_ignored=validation_ignored,
            finding_count=len(findings),
        ),
        word_mappings=word_mappings,
        reference_anchors=reference_anchors,
        findings=findings,
        validation_findings=validation_findings,
    )


class TextFabricLxxProvider:
    """Thin adapter over an already-loaded CenterBLC Text-Fabric API."""

    def __init__(self, api: object, parent_probe: LxxParentProbe) -> None:
        self._api = typing.cast(typing.Any, api)
        self.parent_probe = parent_probe

    def get_span(
        self,
        book: str,
        chapter: int,
        verse: int,
        subverse: str | None = None,
    ) -> LxxSpan | None:
        """Read one verse/subverse span through Text-Fabric APIs."""

        verse_node = typing.cast(
            int | None,
            self._api.T.nodeFromSection((book, chapter, verse)),
        )
        if verse_node is None:
            return None

        word_nodes = tuple(
            typing.cast(typing.Iterable[int], self._api.L.d(verse_node, otype="word"))
        )
        if subverse is None:
            word_nodes = tuple(
                word
                for word in word_nodes
                if not (typing.cast(str | None, self._api.F.subverse.v(word)) or "")
            )
        else:
            word_nodes = tuple(
                word
                for word in word_nodes
                if typing.cast(str | None, self._api.F.subverse.v(word)) == subverse
            )
        if not word_nodes:
            return None

        span_node = verse_node
        if subverse is not None:
            parent_nodes = tuple(
                typing.cast(
                    typing.Iterable[int],
                    self._api.L.u(word_nodes[0], otype="subverse"),
                )
            )
            if len(parent_nodes) != 1:
                return None
            span_node = parent_nodes[0]

        words = tuple(
            LxxWord(
                node=word,
                word=typing.cast(str, self._api.F.word.v(word)),
                subverse=typing.cast(str | None, self._api.F.subverse.v(word)) or "",
                orig_order=str(self._api.F.orig_order.v(word)),
            )
            for word in word_nodes
        )
        return LxxSpan(
            node=span_node,
            book=book,
            chapter=chapter,
            verse=verse,
            subverse=subverse,
            words=words,
        )
