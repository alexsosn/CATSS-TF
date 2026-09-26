"""Cross-projection consistency checks for completed CATSS-TF bundles."""

import collections
import csv
import dataclasses
import pathlib

from catss_tf.bhsa_schema import BhsaSourceStatus
from catss_tf.bhsa_schema import classify_catss_source as classify_bhsa_source
from catss_tf.lxx_schema import LxxSourceStatus
from catss_tf.lxx_schema import classify_catss_source as classify_lxx_source
from catss_tf.tf_schema import SIDECAR_COLUMNS


_REQUIRED_SIDECARS = tuple(SIDECAR_COLUMNS)
_CANONICAL_TABLES = {
    "catss-alignments.tsv": "canonical_alignment_mismatch",
    "catss-annotations.tsv": "annotation_mismatch",
    "catss-source-lines.tsv": "source_line_mismatch",
    "catss-diagnostics.tsv": "diagnostic_mismatch",
}


@dataclasses.dataclass(frozen=True, slots=True)
class ConsistencyFinding:
    """One deterministic cross-projection inconsistency."""

    code: str
    source: str | None
    alignment_id: str | None
    table: str | None
    message: str


@dataclasses.dataclass(frozen=True, slots=True)
class ConsistencySummary:
    """Scalar cross-projection consistency counters."""

    source_files: int
    common_sources: int
    bhsa_only_sources: int
    lxx_only_sources: int
    common_alignments: int
    ordinary_shared_alignments: int
    lxx_plus_asymmetries: int
    lxx_minus_asymmetries: int
    transposition_placeholder_asymmetries: int
    transposition_carrier_asymmetries: int
    fingerprint_mismatches: int
    canonical_mismatches: int
    index_mismatches: int
    anchor_mismatches: int
    unexpected_projection_gaps: int
    finding_count: int


@dataclasses.dataclass(frozen=True, slots=True)
class ConsistencyReport:
    """Deterministic comparison of one BHSA and one LXX materialized bundle."""

    summary: ConsistencySummary
    findings: tuple[ConsistencyFinding, ...]

    @property
    def ok(self) -> bool:
        """Whether no inconsistency was found."""

        return not self.findings


@dataclasses.dataclass(frozen=True, slots=True)
class _Bundle:
    root: pathlib.Path
    tables: dict[str, tuple[dict[str, str], ...]]
    usable: frozenset[str]


def compare_projection_bundles(
    bhsa_directory: str | pathlib.Path,
    lxx_directory: str | pathlib.Path,
) -> ConsistencyReport:
    """Compare completed BHSA/LXX bundles produced from one CATSS acquisition."""

    findings: list[ConsistencyFinding] = []
    bhsa = _load_bundle(pathlib.Path(bhsa_directory), "bhsa", findings)
    lxx = _load_bundle(pathlib.Path(lxx_directory), "lxx", findings)

    bhsa_sources = _source_map(bhsa, findings)
    lxx_sources = _source_map(lxx, findings)
    all_sources = sorted(set(bhsa_sources) | set(lxx_sources))

    common_sources: set[str] = set()
    bhsa_only_sources: set[str] = set()
    lxx_only_sources: set[str] = set()
    comparable_sources: set[str] = set()

    fingerprint_mismatches = 0
    canonical_mismatches = 0
    index_mismatches = 0
    anchor_mismatches = 0
    unexpected_projection_gaps = 0

    for source in all_sources:
        bhsa_class = classify_bhsa_source(source)
        lxx_class = classify_lxx_source(source)

        if (
            bhsa_class.status is BhsaSourceStatus.SUPPORTED
            and lxx_class.status is LxxSourceStatus.SUPPORTED
        ):
            common_sources.add(source)
        elif (
            bhsa_class.status is BhsaSourceStatus.SUPPORTED
            and lxx_class.status is LxxSourceStatus.UNSUPPORTED
        ):
            bhsa_only_sources.add(source)
        elif (
            bhsa_class.status is BhsaSourceStatus.UNSUPPORTED
            and lxx_class.status is LxxSourceStatus.SUPPORTED
        ):
            lxx_only_sources.add(source)
        else:
            findings.append(
                ConsistencyFinding(
                    code="unknown_source_profile",
                    source=source,
                    alignment_id=None,
                    table="catss-sources.tsv",
                    message="source is not a declared common or projection-exclusive CATSS source",
                )
            )

        bhsa_fp = bhsa_sources.get(source)
        lxx_fp = lxx_sources.get(source)
        if bhsa_fp is None or lxx_fp is None:
            fingerprint_mismatches += 1
            findings.append(
                ConsistencyFinding(
                    code="source_set_mismatch",
                    source=source,
                    alignment_id=None,
                    table="catss-sources.tsv",
                    message=(
                        "source exists only in "
                        + ("LXX bundle" if bhsa_fp is None else "BHSA bundle")
                    ),
                )
            )
            continue
        if bhsa_fp != lxx_fp:
            fingerprint_mismatches += 1
            findings.append(
                ConsistencyFinding(
                    code="source_fingerprint_mismatch",
                    source=source,
                    alignment_id=None,
                    table="catss-sources.tsv",
                    message="source size/SHA-256 differ between projection bundles",
                )
            )
            continue
        comparable_sources.add(source)

    canonical_equal_sources = set(comparable_sources & common_sources)
    for source in sorted(canonical_equal_sources):
        source_equal = True
        for table, code in _CANONICAL_TABLES.items():
            if table not in bhsa.usable or table not in lxx.usable:
                source_equal = False
                continue
            left = _row_counter(bhsa, table, source)
            right = _row_counter(lxx, table, source)
            if left != right:
                canonical_mismatches += 1
                source_equal = False
                findings.append(
                    ConsistencyFinding(
                        code=code,
                        source=source,
                        alignment_id=None,
                        table=table,
                        message="canonical CATSS rows differ between projection bundles",
                    )
                )
        if not source_equal:
            canonical_equal_sources.discard(source)

    for source in sorted((bhsa_only_sources | lxx_only_sources) & comparable_sources):
        unsupported = lxx if source in bhsa_only_sources else bhsa
        projection_name = "LXX" if source in bhsa_only_sources else "BHSA"
        unexpected = _projection_rows_for_source(unsupported, source)
        if unexpected:
            unexpected_projection_gaps += 1
            findings.append(
                ConsistencyFinding(
                    code="unexpected_projection_gap",
                    source=source,
                    alignment_id=None,
                    table=None,
                    message=f"{projection_name}-unsupported source contains projected rows",
                )
            )

    bhsa_alignment_rows = _alignment_index(bhsa, findings)
    lxx_alignment_rows = _alignment_index(lxx, findings)
    bhsa_mappings = _rows_by_identity(bhsa, "catss-mappings.tsv", findings, "bhsa")
    lxx_mappings = _rows_by_identity(lxx, "catss-mappings.tsv", findings, "lxx")
    bhsa_anchors = _rows_by_identity(bhsa, "catss-anchors.tsv", findings, "bhsa")
    lxx_anchors = _rows_by_identity(lxx, "catss-anchors.tsv", findings, "lxx")

    common_alignments = 0
    ordinary_shared_alignments = 0
    lxx_plus_asymmetries = 0
    lxx_minus_asymmetries = 0
    transposition_placeholder_asymmetries = 0
    transposition_carrier_asymmetries = 0

    for source in sorted(canonical_equal_sources):
        identities = sorted(
            identity for identity in bhsa_alignment_rows if identity[0] == source
        )
        common_alignments += len(identities)

        for identity in identities:
            row = bhsa_alignment_rows[identity]
            if lxx_alignment_rows.get(identity) != row:
                continue

            parsed = _canonical_state(row, findings)
            if parsed is None:
                continue
            mt_n, lxx_n, lxx_plus, lxx_minus, trans_remote = parsed

            bmaps = bhsa_mappings.get(identity, ())
            lmaps = lxx_mappings.get(identity, ())
            banchors = bhsa_anchors.get(identity, ())
            lanchors = lxx_anchors.get(identity, ())

            if lxx_plus:
                lxx_plus_asymmetries += 1
                index_mismatches += _check_index_coverage(
                    identity, lmaps, "lxx_i", lxx_n, "lxx", findings
                )
                anchor_mismatches += _check_anchor(
                    identity, banchors, "lxx_plus", "bhsa", findings
                )
                anchor_mismatches += _check_no_anchor(identity, lanchors, "lxx", findings)
                unexpected_projection_gaps += _check_no_mapping(
                    identity, bmaps, "bhsa", findings
                )
                continue

            if lxx_minus:
                lxx_minus_asymmetries += 1
                index_mismatches += _check_index_coverage(
                    identity, bmaps, "mt_i", mt_n, "bhsa", findings
                )
                anchor_mismatches += _check_anchor(
                    identity, lanchors, "lxx_minus", "lxx", findings
                )
                anchor_mismatches += _check_no_anchor(identity, banchors, "bhsa", findings)
                unexpected_projection_gaps += _check_no_mapping(
                    identity, lmaps, "lxx", findings
                )
                continue

            if lxx_n == 0 and trans_remote:
                transposition_placeholder_asymmetries += 1
                if mt_n > 0:
                    index_mismatches += _check_index_coverage(
                        identity, bmaps, "mt_i", mt_n, "bhsa", findings
                    )
                else:
                    unexpected_projection_gaps += _check_no_mapping(
                        identity, bmaps, "bhsa", findings
                    )
                anchor_mismatches += _check_anchor(
                    identity,
                    lanchors,
                    "transposition_placeholder",
                    "lxx",
                    findings,
                )
                anchor_mismatches += _check_no_anchor(identity, banchors, "bhsa", findings)
                unexpected_projection_gaps += _check_no_mapping(
                    identity, lmaps, "lxx", findings
                )
                continue

            if mt_n == 0 and lxx_n > 0:
                kinds = {row.get("mapping_kind", "") for row in lmaps}
                if kinds == {"transposition_carrier"}:
                    transposition_carrier_asymmetries += 1
                    index_mismatches += _check_index_coverage(
                        identity, lmaps, "lxx_i", lxx_n, "lxx", findings
                    )
                    unexpected_projection_gaps += _check_no_mapping(
                        identity, bmaps, "bhsa", findings
                    )
                    anchor_mismatches += _check_no_anchor(
                        identity, banchors, "bhsa", findings
                    )
                    anchor_mismatches += _check_no_anchor(identity, lanchors, "lxx", findings)
                else:
                    unexpected_projection_gaps += 1
                    findings.append(
                        _finding(
                            "unexpected_projection_gap",
                            identity,
                            "catss-mappings.tsv",
                            "Hebrew-empty non-plus alignment is not a transposition carrier",
                        )
                    )
                continue

            if mt_n > 0 and lxx_n > 0:
                ordinary_shared_alignments += 1
                index_mismatches += _check_index_coverage(
                    identity, bmaps, "mt_i", mt_n, "bhsa", findings
                )
                index_mismatches += _check_index_coverage(
                    identity, lmaps, "lxx_i", lxx_n, "lxx", findings
                )
                anchor_mismatches += _check_no_anchor(identity, banchors, "bhsa", findings)
                anchor_mismatches += _check_no_anchor(identity, lanchors, "lxx", findings)
                continue

            unexpected_projection_gaps += 1
            findings.append(
                _finding(
                    "unexpected_projection_gap",
                    identity,
                    "catss-alignments.tsv",
                    "canonical alignment shape has no v0.1 projection-consistency class",
                )
            )

    _check_orphan_projection_rows(
        bhsa,
        bhsa_alignment_rows,
        "bhsa",
        findings,
    )
    _check_orphan_projection_rows(
        lxx,
        lxx_alignment_rows,
        "lxx",
        findings,
    )

    findings.sort(
        key=lambda finding: (
            finding.source or "",
            finding.alignment_id or "",
            finding.table or "",
            finding.code,
            finding.message,
        )
    )
    return ConsistencyReport(
        summary=ConsistencySummary(
            source_files=len(all_sources),
            common_sources=len(common_sources),
            bhsa_only_sources=len(bhsa_only_sources),
            lxx_only_sources=len(lxx_only_sources),
            common_alignments=common_alignments,
            ordinary_shared_alignments=ordinary_shared_alignments,
            lxx_plus_asymmetries=lxx_plus_asymmetries,
            lxx_minus_asymmetries=lxx_minus_asymmetries,
            transposition_placeholder_asymmetries=transposition_placeholder_asymmetries,
            transposition_carrier_asymmetries=transposition_carrier_asymmetries,
            fingerprint_mismatches=fingerprint_mismatches,
            canonical_mismatches=canonical_mismatches,
            index_mismatches=index_mismatches,
            anchor_mismatches=anchor_mismatches,
            unexpected_projection_gaps=unexpected_projection_gaps,
            finding_count=len(findings),
        ),
        findings=tuple(findings),
    )


def _load_bundle(
    root: pathlib.Path,
    projection: str,
    findings: list[ConsistencyFinding],
) -> _Bundle:
    tables: dict[str, tuple[dict[str, str], ...]] = {}
    usable: set[str] = set()

    for name in _REQUIRED_SIDECARS:
        path = root / name
        expected = SIDECAR_COLUMNS[name]
        if not path.is_file():
            findings.append(
                ConsistencyFinding(
                    code="missing_sidecar",
                    source=None,
                    alignment_id=None,
                    table=name,
                    message=f"{projection} bundle is missing required sidecar",
                )
            )
            tables[name] = ()
            continue

        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            actual = tuple(reader.fieldnames or ())
            if actual != expected:
                findings.append(
                    ConsistencyFinding(
                        code="sidecar_header_mismatch",
                        source=None,
                        alignment_id=None,
                        table=name,
                        message=(
                            f"{projection} header is {actual!r}; expected {expected!r}"
                        ),
                    )
                )
                tables[name] = ()
                continue
            tables[name] = tuple(dict(row) for row in reader)
            usable.add(name)

    return _Bundle(root=root, tables=tables, usable=frozenset(usable))


def _source_map(
    bundle: _Bundle,
    findings: list[ConsistencyFinding],
) -> dict[str, tuple[str, str]]:
    result: dict[str, tuple[str, str]] = {}
    for row in bundle.tables.get("catss-sources.tsv", ()):
        source = row.get("source", "")
        value = (row.get("size_bytes", ""), row.get("sha256", ""))
        if not source or source in result:
            findings.append(
                ConsistencyFinding(
                    code="source_set_mismatch",
                    source=source or None,
                    alignment_id=None,
                    table="catss-sources.tsv",
                    message="source fingerprint table contains an empty or duplicate source key",
                )
            )
            continue
        result[source] = value
    return result


def _row_counter(bundle: _Bundle, table: str, source: str) -> collections.Counter[tuple[str, ...]]:
    columns = SIDECAR_COLUMNS[table]
    return collections.Counter(
        tuple(row.get(column, "") for column in columns)
        for row in bundle.tables.get(table, ())
        if row.get("source") == source
    )


def _projection_rows_for_source(bundle: _Bundle, source: str) -> int:
    return sum(
        row.get("source") == source
        for table in (
            "catss-alignments.tsv",
            "catss-annotations.tsv",
            "catss-mappings.tsv",
            "catss-anchors.tsv",
            "catss-source-lines.tsv",
            "catss-diagnostics.tsv",
        )
        for row in bundle.tables.get(table, ())
    )


def _alignment_index(
    bundle: _Bundle,
    findings: list[ConsistencyFinding],
) -> dict[tuple[str, str], dict[str, str]]:
    result: dict[tuple[str, str], dict[str, str]] = {}
    for row in bundle.tables.get("catss-alignments.tsv", ()):
        identity = (row.get("source", ""), row.get("alignment_id", ""))
        if not all(identity) or identity in result:
            findings.append(
                _finding(
                    "canonical_alignment_mismatch",
                    identity,
                    "catss-alignments.tsv",
                    "alignment table contains empty or duplicate canonical identity",
                )
            )
            continue
        result[identity] = row
    return result


def _rows_by_identity(
    bundle: _Bundle,
    table: str,
    findings: list[ConsistencyFinding],
    projection: str,
) -> dict[tuple[str, str], tuple[dict[str, str], ...]]:
    grouped: dict[tuple[str, str], list[dict[str, str]]] = {}
    for row in bundle.tables.get(table, ()):
        identity = (row.get("source", ""), row.get("alignment_id", ""))
        if not all(identity):
            findings.append(
                _finding(
                    "orphan_projection_row",
                    identity,
                    table,
                    f"{projection} projection row has empty source/alignment identity",
                )
            )
            continue
        if row.get("projection") != projection:
            findings.append(
                _finding(
                    "orphan_projection_row",
                    identity,
                    table,
                    f"row projection {row.get('projection')!r} does not match {projection!r}",
                )
            )
        grouped.setdefault(identity, []).append(row)
    return {identity: tuple(rows) for identity, rows in grouped.items()}


def _canonical_state(
    row: dict[str, str],
    findings: list[ConsistencyFinding],
) -> tuple[int, int, bool, bool, bool] | None:
    identity = (row.get("source", ""), row.get("alignment_id", ""))
    try:
        mt_n = int(row["mt_n"])
        lxx_n = int(row["lxx_n"])
        lxx_plus = int(row["lxx_plus"]) == 1
        lxx_minus = int(row["lxx_minus"]) == 1
        trans_remote = int(row["trans_remote"]) == 1
    except (KeyError, ValueError):
        findings.append(
            _finding(
                "canonical_alignment_mismatch",
                identity,
                "catss-alignments.tsv",
                "canonical alignment contains invalid scalar state",
            )
        )
        return None
    return mt_n, lxx_n, lxx_plus, lxx_minus, trans_remote


def _check_index_coverage(
    identity: tuple[str, str],
    rows: tuple[dict[str, str], ...],
    field: str,
    count: int,
    projection: str,
    findings: list[ConsistencyFinding],
) -> int:
    expected = set(range(1, count + 1))
    actual: set[int] = set()
    invalid = False
    for row in rows:
        value = row.get(field, "")
        try:
            index = int(value)
        except ValueError:
            invalid = True
            continue
        actual.add(index)
    if invalid or actual != expected:
        findings.append(
            _finding(
                f"{field.split('_')[0]}_index_coverage_mismatch",
                identity,
                "catss-mappings.tsv",
                (
                    f"{projection} {field} coverage is {sorted(actual)!r}; "
                    f"expected {sorted(expected)!r}"
                ),
            )
        )
        return 1
    return 0


def _check_anchor(
    identity: tuple[str, str],
    rows: tuple[dict[str, str], ...],
    expected_kind: str,
    projection: str,
    findings: list[ConsistencyFinding],
) -> int:
    kinds = [row.get("anchor_kind", "") for row in rows]
    if kinds != [expected_kind]:
        findings.append(
            _finding(
                "anchor_kind_mismatch",
                identity,
                "catss-anchors.tsv",
                f"{projection} anchor kinds are {kinds!r}; expected [{expected_kind!r}]",
            )
        )
        return 1
    return 0


def _check_no_anchor(
    identity: tuple[str, str],
    rows: tuple[dict[str, str], ...],
    projection: str,
    findings: list[ConsistencyFinding],
) -> int:
    if not rows:
        return 0
    findings.append(
        _finding(
            "anchor_kind_mismatch",
            identity,
            "catss-anchors.tsv",
            f"{projection} projection has an unexpected structural anchor",
        )
    )
    return 1


def _check_no_mapping(
    identity: tuple[str, str],
    rows: tuple[dict[str, str], ...],
    projection: str,
    findings: list[ConsistencyFinding],
) -> int:
    if not rows:
        return 0
    findings.append(
        _finding(
            "unexpected_projection_gap",
            identity,
            "catss-mappings.tsv",
            f"{projection} projection has word mappings where none are expected",
        )
    )
    return 1


def _check_orphan_projection_rows(
    bundle: _Bundle,
    alignments: dict[tuple[str, str], dict[str, str]],
    projection: str,
    findings: list[ConsistencyFinding],
) -> None:
    identities = set(alignments)
    for table in ("catss-mappings.tsv", "catss-anchors.tsv"):
        for row in bundle.tables.get(table, ()):
            identity = (row.get("source", ""), row.get("alignment_id", ""))
            if all(identity) and identity not in identities:
                findings.append(
                    _finding(
                        "orphan_projection_row",
                        identity,
                        table,
                        f"{projection} projection row references no canonical alignment",
                    )
                )


def _finding(
    code: str,
    identity: tuple[str, str],
    table: str,
    message: str,
) -> ConsistencyFinding:
    source, alignment_id = identity
    return ConsistencyFinding(
        code=code,
        source=source or None,
        alignment_id=alignment_id or None,
        table=table,
        message=message,
    )
