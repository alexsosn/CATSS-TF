"""Validation invariants for canonical CATSS alignment IR."""

import dataclasses
import typing

from catss_tf.parser import ParallelDocument, alignment_id_for

Severity = typing.Literal["error", "unresolved", "ignored"]


@dataclasses.dataclass(frozen=True, slots=True)
class ValidationFinding:
    """One typed validation result tied to source provenance where possible."""

    code: str
    severity: Severity
    source_name: str
    line_no: int | None
    alignment_id: str | None
    side: str | None
    raw: str | None
    message: str


@dataclasses.dataclass(frozen=True, slots=True)
class ValidationSummary:
    """Scalar corpus-level validation counters."""

    source_files: int
    verses: int
    alignments: int
    source_data_lines: int
    accounted_lines: int
    unaccounted_lines: int
    parser_diagnostics: int
    unknown_annotations: int
    invalid_alignment_ids: int
    duplicate_alignment_ids: int
    error_count: int
    unresolved_count: int
    ignored_count: int


@dataclasses.dataclass(frozen=True, slots=True)
class ValidationReport:
    """Validation findings and automation-friendly scalar summary."""

    summary: ValidationSummary
    findings: tuple[ValidationFinding, ...]

    @property
    def ok(self) -> bool:
        """Whether validation has no blocking error or unresolved finding."""

        return self.summary.error_count == 0 and self.summary.unresolved_count == 0


def validate_document(
    document: ParallelDocument, *, allowed_codes: set[str] | frozenset[str] = frozenset()
) -> ValidationReport:
    """Validate one parsed CATSS source document."""

    return validate_documents((document,), allowed_codes=allowed_codes)


def validate_documents(
    documents: tuple[ParallelDocument, ...],
    *,
    allowed_codes: set[str] | frozenset[str] = frozenset(),
) -> ValidationReport:
    """Validate a set of parsed CATSS documents as one corpus input."""

    findings: list[ValidationFinding] = []
    seen_alignment_ids: dict[str, tuple[str, int | None]] = {}

    source_files = len(documents)
    verses = 0
    alignments = 0
    source_data_lines = 0
    accounted_lines = 0
    unaccounted_lines = 0
    parser_diagnostics = 0
    unknown_annotations = 0
    invalid_alignment_ids = 0
    duplicate_alignment_ids = 0

    for document in documents:
        verses += len(document.verses)
        source_lines = set(document.data_line_numbers)
        source_data_lines += len(source_lines)
        owned_lines: dict[int, str] = {}
        accounted: set[int] = set()

        for verse in document.verses:
            alignments += len(verse.alignments)
            for alignment in verse.alignments:
                expected_id = alignment_id_for(
                    source_name=document.source_name,
                    header_raw=verse.header_raw,
                    source_lines=alignment.source_lines,
                    raw_lines=alignment.raw_lines,
                )
                if alignment.alignment_id != expected_id:
                    invalid_alignment_ids += 1
                    findings.append(
                        _finding(
                            code="alignment_id_mismatch",
                            base_severity="error",
                            allowed_codes=allowed_codes,
                            source_name=document.source_name,
                            line_no=_first_line(alignment.source_lines),
                            alignment_id=alignment.alignment_id,
                            message=f"expected deterministic alignment id {expected_id}",
                        )
                    )

                previous = seen_alignment_ids.get(alignment.alignment_id)
                if previous is not None:
                    duplicate_alignment_ids += 1
                    findings.append(
                        _finding(
                            code="duplicate_alignment_id",
                            base_severity="error",
                            allowed_codes=allowed_codes,
                            source_name=document.source_name,
                            line_no=_first_line(alignment.source_lines),
                            alignment_id=alignment.alignment_id,
                            message=(
                                "alignment id already occurred at "
                                f"{previous[0]}:{previous[1]}"
                            ),
                        )
                    )
                else:
                    seen_alignment_ids[alignment.alignment_id] = (
                        document.source_name,
                        _first_line(alignment.source_lines),
                    )

                for line_no in alignment.source_lines:
                    previous_owner = owned_lines.get(line_no)
                    if previous_owner is not None:
                        findings.append(
                            _finding(
                                code="duplicate_source_line_ownership",
                                base_severity="error",
                                allowed_codes=allowed_codes,
                                source_name=document.source_name,
                                line_no=line_no,
                                alignment_id=alignment.alignment_id,
                                message=(
                                    "physical source line is owned by more than one "
                                    f"alignment: {previous_owner}, {alignment.alignment_id}"
                                ),
                            )
                        )
                    else:
                        owned_lines[line_no] = alignment.alignment_id
                    accounted.add(line_no)

                for annotation in alignment.annotations:
                    code: str | None = None
                    if annotation.kind == "unknown":
                        code = "unknown_annotation"
                    elif annotation.kind == "mt_strategy_siglum":
                        code = "unknown_mt_strategy_siglum"
                    if code is None:
                        continue
                    unknown_annotations += 1
                    findings.append(
                        _finding(
                            code=code,
                            base_severity="unresolved",
                            allowed_codes=allowed_codes,
                            source_name=document.source_name,
                            line_no=_first_line(alignment.source_lines),
                            alignment_id=alignment.alignment_id,
                            side=annotation.side,
                            raw=annotation.raw,
                            message="CATSS source markup is preserved but not yet interpreted",
                        )
                    )

        parser_diagnostics += len(document.diagnostics)
        for diagnostic in document.diagnostics:
            accounted.add(diagnostic.line_no)
            findings.append(
                _finding(
                    code=diagnostic.code,
                    base_severity="unresolved",
                    allowed_codes=allowed_codes,
                    source_name=document.source_name,
                    line_no=diagnostic.line_no,
                    raw=diagnostic.raw_line,
                    message=diagnostic.message,
                )
            )

        for line_no in sorted(source_lines - accounted):
            unaccounted_lines += 1
            findings.append(
                _finding(
                    code="unaccounted_source_line",
                    base_severity="error",
                    allowed_codes=allowed_codes,
                    source_name=document.source_name,
                    line_no=line_no,
                    message="nonblank CATSS data line has no alignment or parser diagnostic",
                )
            )

        for line_no in sorted(accounted - source_lines):
            findings.append(
                _finding(
                    code="unexpected_source_line_reference",
                    base_severity="error",
                    allowed_codes=allowed_codes,
                    source_name=document.source_name,
                    line_no=line_no,
                    message="IR references a line not recorded in document data_line_numbers",
                )
            )

        accounted_lines += len(source_lines & accounted)

    error_count = sum(finding.severity == "error" for finding in findings)
    unresolved_count = sum(finding.severity == "unresolved" for finding in findings)
    ignored_count = sum(finding.severity == "ignored" for finding in findings)

    return ValidationReport(
        summary=ValidationSummary(
            source_files=source_files,
            verses=verses,
            alignments=alignments,
            source_data_lines=source_data_lines,
            accounted_lines=accounted_lines,
            unaccounted_lines=unaccounted_lines,
            parser_diagnostics=parser_diagnostics,
            unknown_annotations=unknown_annotations,
            invalid_alignment_ids=invalid_alignment_ids,
            duplicate_alignment_ids=duplicate_alignment_ids,
            error_count=error_count,
            unresolved_count=unresolved_count,
            ignored_count=ignored_count,
        ),
        findings=tuple(findings),
    )


def _finding(
    *,
    code: str,
    base_severity: typing.Literal["error", "unresolved"],
    allowed_codes: set[str] | frozenset[str],
    source_name: str,
    line_no: int | None,
    message: str,
    alignment_id: str | None = None,
    side: str | None = None,
    raw: str | None = None,
) -> ValidationFinding:
    severity: Severity = (
        "ignored"
        if base_severity == "unresolved" and code in allowed_codes
        else base_severity
    )
    return ValidationFinding(
        code=code,
        severity=severity,
        source_name=source_name,
        line_no=line_no,
        alignment_id=alignment_id,
        side=side,
        raw=raw,
        message=message,
    )


def _first_line(source_lines: tuple[int, ...]) -> int | None:
    return source_lines[0] if source_lines else None
