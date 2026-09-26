"""End-to-end materializer for the CATSS enrichment module over BHSA."""

import csv
import dataclasses
import hashlib
import pathlib
import shutil
import tempfile

from catss_tf import __version__
from catss_tf.bhsa_resolver import (
    BhsaMappingReport,
    BhsaVerseProvider,
    resolve_bhsa_document,
)
from catss_tf.bhsa_schema import (
    BHSA_CHECKOUT_COMMIT,
    BHSA_CHECKOUT_TAG,
    BHSA_MAX_NODE,
    BHSA_REPOSITORY,
    BHSA_VERSION,
    BhsaParentProbe,
    BhsaSourceStatus,
    classify_catss_source,
    validate_bhsa_parent,
)
from catss_tf.parser import AlignmentRecord, ParallelDocument, VerseRecord, parse_parallel_text
from catss_tf.source import (
    ParallelSourceManifest,
    SourceFileFingerprint,
    inspect_parallel_source,
)
from catss_tf.technique import TechniqueError, derive_alignment_technique, technique_sidecar_row
from catss_tf.tf_schema import (
    SIDECAR_COLUMNS,
    TfAnchorEvent,
    TfMembership,
    TfModuleMetadata,
    compile_tf_features,
    write_tf_module,
)
from catss_tf.validation import ValidationFinding


class BhsaMaterializationError(RuntimeError):
    """Raised when a fail-closed BHSA materialization cannot be published."""


@dataclasses.dataclass(frozen=True, slots=True)
class BhsaMaterializationSummary:
    """Scalar summary of one completed catss-bhsa materialization."""

    source_files: int
    supported_documents: int
    unsupported_documents: int
    verses: int
    alignments: int
    word_mappings: int
    verse_anchors: int
    tf_features: int
    sidecar_rows: int
    ignored_validation_findings: int


@dataclasses.dataclass(frozen=True, slots=True)
class BhsaMaterializationResult:
    """Published catss-bhsa bundle and its scalar summary."""

    output_path: pathlib.Path
    summary: BhsaMaterializationSummary


@dataclasses.dataclass(frozen=True, slots=True)
class _AlignmentContext:
    source: str
    verse: VerseRecord
    alignment: AlignmentRecord


_ANNOTATION_FLAG: dict[str, str] = {
    "doublet": "catss_doublet",
    "transliteration": "catss_translit",
    "apparent_plus_minus": "catss_apparent_pm",
    "greek_agrees_ketiv": "catss_agrees_ketiv",
    "greek_agrees_qere": "catss_agrees_qere",
    "metathesis": "catss_metathesis",
    "word_separation": "catss_word_separation",
    "word_join": "catss_word_join",
    "word_division": "catss_word_division",
    "abbreviation": "catss_abbreviation",
    "greek_preverb": "catss_greek_preverb",
    "comparative_superlative": "catss_comparative",
    "asterisked_passage": "catss_asterisked",
    "doubt": "catss_doubt",
    "greek_edition_difference": "catss_greek_diff",
    "greek_correction": "catss_greek_correction",
    "preposition_added": "catss_prep_added",
    "distributive": "catss_distributive",
    "repetition": "catss_repetition",
}


def materialize_bhsa(
    source_directory: str | pathlib.Path,
    output_directory: str | pathlib.Path,
    *,
    provider: BhsaVerseProvider,
    parent_probe: BhsaParentProbe,
    allowed_validation_codes: set[str] | frozenset[str] = frozenset(),
) -> BhsaMaterializationResult:
    """Build and atomically publish a fail-closed catss-bhsa module bundle."""

    source_root = pathlib.Path(source_directory)
    destination = pathlib.Path(output_directory)
    if destination.exists():
        raise BhsaMaterializationError(f"destination already exists: {destination}")

    manifest, documents = _snapshot_parallel_source(source_root)
    parent_validation = validate_bhsa_parent(parent_probe)
    if not parent_validation.ok:
        details = ", ".join(finding.code for finding in parent_validation.findings)
        raise BhsaMaterializationError(f"BHSA parent does not satisfy v0.1 profile: {details}")

    supported: list[tuple[ParallelDocument, BhsaMappingReport]] = []
    unsupported_documents = 0
    for document in documents:
        classification = classify_catss_source(document.source_name)
        if classification.status is BhsaSourceStatus.UNKNOWN:
            raise BhsaMaterializationError(
                f"unknown CATSS source for BHSA projection: {document.source_name}"
            )
        if classification.status is BhsaSourceStatus.UNSUPPORTED:
            unsupported_documents += 1
            continue

        report = resolve_bhsa_document(
            document,
            provider,
            allowed_validation_codes=allowed_validation_codes,
        )
        if report.findings:
            codes = ", ".join(finding.code for finding in report.findings)
            raise BhsaMaterializationError(
                f"BHSA mapping failed for {document.source_name}: {codes}"
            )
        supported.append((document, report))

    try:
        (
            memberships,
            anchors,
            alignment_rows,
            technique_rows,
            annotation_rows,
            source_line_rows,
            mapping_facts,
            anchor_rows,
            diagnostic_rows,
        ) = _projection_facts(supported)
    except TechniqueError as exc:
        raise BhsaMaterializationError(f"technique derivation failed: {exc}") from exc

    features = compile_tf_features(
        projection="bhsa",
        max_node=BHSA_MAX_NODE,
        memberships=tuple(memberships),
        anchors=tuple(anchors),
    )
    mapping_rows = _mapping_rows(mapping_facts, features)
    source_rows: list[tuple[object, ...]] = [
        (source.relative_path, source.size_bytes, source.sha256) for source in manifest.files
    ]

    sidecars: dict[str, list[tuple[object, ...]]] = {
        "catss-alignments.tsv": alignment_rows,
        "catss-technique.tsv": technique_rows,
        "catss-annotations.tsv": annotation_rows,
        "catss-mappings.tsv": mapping_rows,
        "catss-anchors.tsv": anchor_rows,
        "catss-sources.tsv": source_rows,
        "catss-source-lines.tsv": source_line_rows,
        "catss-diagnostics.tsv": diagnostic_rows,
    }
    sidecar_rows = sum(len(rows) for rows in sidecars.values())

    metadata = TfModuleMetadata(
        projection="bhsa",
        parent_repo=BHSA_REPOSITORY,
        parent_version=BHSA_VERSION,
        parent_release=BHSA_CHECKOUT_TAG,
        parent_commit=BHSA_CHECKOUT_COMMIT,
        software_version=__version__,
    )

    _publish_bundle(
        destination,
        features=features,
        metadata=metadata,
        sidecars=sidecars,
    )

    ignored_validation_findings = sum(
        finding.severity == "ignored"
        for _document, report in supported
        for finding in report.validation_findings
    )
    return BhsaMaterializationResult(
        output_path=destination,
        summary=BhsaMaterializationSummary(
            source_files=len(manifest.files),
            supported_documents=len(supported),
            unsupported_documents=unsupported_documents,
            verses=sum(len(document.verses) for document, _report in supported),
            alignments=sum(
                len(verse.alignments)
                for document, _report in supported
                for verse in document.verses
            ),
            word_mappings=len(memberships),
            verse_anchors=len(anchors),
            tf_features=len(features),
            sidecar_rows=sidecar_rows,
            ignored_validation_findings=ignored_validation_findings,
        ),
    )


def _snapshot_parallel_source(
    source_root: pathlib.Path,
) -> tuple[ParallelSourceManifest, tuple[ParallelDocument, ...]]:
    """Read each selected CATSS file once; fingerprint and parse the same bytes."""

    discovered = inspect_parallel_source(source_root)
    fingerprints: list[SourceFileFingerprint] = []
    documents: list[ParallelDocument] = []

    for item in discovered.files:
        path = source_root / item.relative_path
        payload = path.read_bytes()
        fingerprint = SourceFileFingerprint(
            relative_path=item.relative_path,
            size_bytes=len(payload),
            sha256=hashlib.sha256(payload).hexdigest(),
        )
        text = payload.decode("utf-8")
        fingerprints.append(fingerprint)
        documents.append(
            parse_parallel_text(
                text,
                source_name=item.relative_path,
            )
        )

    return (
        ParallelSourceManifest(files=tuple(fingerprints)),
        tuple(documents),
    )


def _projection_facts(
    supported: list[tuple[ParallelDocument, BhsaMappingReport]],
) -> tuple[
    list[TfMembership],
    list[TfAnchorEvent],
    list[tuple[object, ...]],
    list[tuple[object, ...]],
    list[tuple[object, ...]],
    list[tuple[object, ...]],
    list[tuple[TfMembership, int, int]],
    list[tuple[object, ...]],
    list[tuple[object, ...]],
]:
    memberships: list[TfMembership] = []
    anchors: list[TfAnchorEvent] = []
    alignment_rows: list[tuple[object, ...]] = []
    technique_rows: list[tuple[object, ...]] = []
    annotation_rows: list[tuple[object, ...]] = []
    source_line_rows: list[tuple[object, ...]] = []
    mapping_facts: list[tuple[TfMembership, int, int]] = []
    anchor_rows: list[tuple[object, ...]] = []
    diagnostic_rows: list[tuple[object, ...]] = []

    for document, report in supported:
        contexts = _alignment_index(document)

        for verse in document.verses:
            for alignment in verse.alignments:
                context = contexts[alignment.alignment_id]
                alignment_rows.append(_alignment_sidecar_row(context))
                technique_rows.append(
                    technique_sidecar_row(
                        derive_alignment_technique(document.source_name, alignment)
                    )
                )
                annotation_rows.extend(
                    (
                        document.source_name,
                        alignment.alignment_id,
                        annotation.side,
                        annotation.kind,
                        annotation.raw,
                    )
                    for annotation in alignment.annotations
                )
                source_line_rows.extend(
                    (
                        document.source_name,
                        alignment.alignment_id,
                        line_no,
                        raw,
                    )
                    for line_no, raw in zip(
                        alignment.source_lines,
                        alignment.raw_lines,
                        strict=True,
                    )
                )

        for mapping in report.word_mappings:
            context = _require_context(contexts, mapping.alignment_id)
            alignment = context.alignment
            reading = alignment.mt_readings[mapping.mt_index]
            explicit_maqaf = "-" in reading.primary
            membership = TfMembership(
                node=mapping.bhsa_node,
                source=document.source_name,
                alignment_id=mapping.alignment_id,
                mapping_kind=mapping.mapping_kind,
                mt_n=alignment.mt_count,
                lxx_n=alignment.lxx_count,
                mt_i=mapping.mt_index + 1,
                mt_segment=mapping.segment_index + 1 if explicit_maqaf else None,
                lxx_i=None,
                line_first=min(alignment.source_lines),
                line_last=max(alignment.source_lines),
                line_n=len(alignment.source_lines),
                retro_kind=alignment.retroversion_kind,
                flags=_alignment_flags(alignment),
            )
            memberships.append(membership)
            mapping_facts.append((membership, mapping.mt_index, mapping.segment_index))

        for anchor in report.verse_anchors:
            context = _require_context(contexts, anchor.alignment_id)
            alignment = context.alignment
            event = TfAnchorEvent(
                node=anchor.bhsa_verse_node,
                source=document.source_name,
                alignment_id=anchor.alignment_id,
                kind="lxx_plus",
                token_n=alignment.lxx_count,
            )
            anchors.append(event)
            anchor_rows.append(
                (
                    "bhsa",
                    document.source_name,
                    anchor.alignment_id,
                    anchor.bhsa_verse_node,
                    "lxx_plus",
                    alignment.lxx_count,
                )
            )

        diagnostic_rows.extend(
            _validation_diagnostic_row(finding)
            for finding in report.validation_findings
            if finding.severity == "ignored"
        )

    alignment_rows.sort(key=lambda row: (str(row[0]), _required_int_sort(row[5]), str(row[1])))
    technique_rows.sort(key=lambda row: (str(row[0]), str(row[1])))
    annotation_rows.sort(
        key=lambda row: (
            str(row[0]),
            str(row[1]),
            str(row[2]),
            str(row[3]),
            str(row[4]),
        )
    )
    source_line_rows.sort(key=lambda row: (str(row[0]), _required_int_sort(row[2]), str(row[1])))
    anchor_rows.sort(key=lambda row: (str(row[1]), str(row[2]), _required_int_sort(row[3])))
    diagnostic_rows.sort(
        key=lambda row: (
            str(row[3]),
            _optional_int_sort(row[8]),
            str(row[2]),
            str(row[7]),
        )
    )
    memberships.sort(
        key=lambda membership: (
            membership.source,
            membership.alignment_id,
            membership.node,
            membership.mt_i or 0,
            membership.mt_segment or 0,
        )
    )
    anchors.sort(key=lambda anchor: (anchor.source, anchor.alignment_id, anchor.node))
    mapping_facts.sort(
        key=lambda fact: (
            fact[0].source,
            fact[0].alignment_id,
            fact[0].node,
            fact[1],
            fact[2],
        )
    )

    return (
        memberships,
        anchors,
        alignment_rows,
        technique_rows,
        annotation_rows,
        source_line_rows,
        mapping_facts,
        anchor_rows,
        diagnostic_rows,
    )


def _alignment_index(document: ParallelDocument) -> dict[str, _AlignmentContext]:
    contexts: dict[str, _AlignmentContext] = {}
    for verse in document.verses:
        for alignment in verse.alignments:
            if alignment.alignment_id in contexts:
                raise BhsaMaterializationError(
                    "duplicate alignment id inside "
                    f"{document.source_name}: {alignment.alignment_id}"
                )
            contexts[alignment.alignment_id] = _AlignmentContext(
                source=document.source_name,
                verse=verse,
                alignment=alignment,
            )
    return contexts


def _require_context(
    contexts: dict[str, _AlignmentContext],
    alignment_id: str,
) -> _AlignmentContext:
    context = contexts.get(alignment_id)
    if context is None:
        raise BhsaMaterializationError(f"resolver referenced unknown alignment id: {alignment_id}")
    return context


def _alignment_flags(alignment: AlignmentRecord) -> frozenset[str]:
    flags: set[str] = set()
    if alignment.is_lxx_plus:
        flags.add("catss_lxx_plus")
    if alignment.is_lxx_minus:
        flags.add("catss_lxx_minus")
    if alignment.is_ketiv:
        flags.add("catss_ketiv")
    if alignment.is_qere:
        flags.add("catss_qere")
    if alignment.is_transposition_local:
        flags.add("catss_trans_local")
    if alignment.is_transposition_remote:
        flags.add("catss_trans_remote")
    if alignment.is_transposition_stylistic:
        flags.add("catss_trans_style")
    if any(reading.doubtful for reading in alignment.mt_readings):
        flags.add("catss_doubt")

    for annotation in alignment.annotations:
        flag = _ANNOTATION_FLAG.get(annotation.kind)
        if flag is not None:
            flags.add(flag)

    return frozenset(flags)


def _alignment_sidecar_row(context: _AlignmentContext) -> tuple[object, ...]:
    alignment = context.alignment
    return (
        context.source,
        alignment.alignment_id,
        context.verse.book,
        context.verse.chapter,
        context.verse.verse,
        min(alignment.source_lines),
        max(alignment.source_lines),
        len(alignment.source_lines),
        alignment.mt_raw,
        alignment.mt_col_a,
        alignment.mt_col_b,
        alignment.retroversion_kind,
        alignment.mt_count,
        alignment.lxx_raw,
        alignment.lxx_count,
        int(alignment.is_lxx_plus),
        int(alignment.is_lxx_minus),
        int(alignment.is_ketiv),
        int(alignment.is_qere),
        int(alignment.is_transposition_local),
        int(alignment.is_transposition_remote),
        int(alignment.is_transposition_stylistic),
    )


def _mapping_rows(
    mapping_facts: list[tuple[TfMembership, int, int]],
    features: dict[str, dict[int, int | str]],
) -> list[tuple[object, ...]]:
    rows: list[tuple[object, ...]] = []
    lane_one = features.get("catss_alignment_id", {})
    lane_two = features.get("catss_alignment_id_2", {})

    for membership, mt_index, _segment_index in mapping_facts:
        if lane_one.get(membership.node) == membership.alignment_id:
            lane = 1
        elif lane_two.get(membership.node) == membership.alignment_id:
            lane = 2
        else:
            raise BhsaMaterializationError(
                "compiled TF features lost membership identity for "
                f"{membership.alignment_id} on node {membership.node}"
            )
        rows.append(
            (
                "bhsa",
                membership.source,
                membership.alignment_id,
                membership.node,
                lane,
                membership.mapping_kind,
                mt_index + 1,
                membership.mt_segment,
                None,
            )
        )

    rows.sort(
        key=lambda row: (
            str(row[1]),
            str(row[2]),
            _required_int_sort(row[3]),
            _required_int_sort(row[4]),
        )
    )
    return rows


def _validation_diagnostic_row(finding: ValidationFinding) -> tuple[object, ...]:
    return (
        "validation",
        finding.severity,
        finding.code,
        finding.source_name,
        None,
        None,
        None,
        finding.alignment_id,
        finding.line_no,
        finding.side,
        finding.raw,
        None,
        finding.message,
    )


def _publish_bundle(
    destination: pathlib.Path,
    *,
    features: dict[str, dict[int, int | str]],
    metadata: TfModuleMetadata,
    sidecars: dict[str, list[tuple[object, ...]]],
) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp_path = pathlib.Path(
        tempfile.mkdtemp(
            prefix=f".{destination.name}.tmp-",
            dir=destination.parent,
        )
    )
    try:
        write_tf_module(
            temp_path,
            features,
            metadata=metadata,
            max_node=BHSA_MAX_NODE,
        )
        for filename in sorted(SIDECAR_COLUMNS):
            _write_tsv(
                temp_path / filename,
                SIDECAR_COLUMNS[filename],
                sidecars.get(filename, []),
            )
        temp_path.replace(destination)
    except Exception:
        shutil.rmtree(temp_path, ignore_errors=True)
        raise


def _write_tsv(
    path: pathlib.Path,
    columns: tuple[str, ...],
    rows: list[tuple[object, ...]],
) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(
            handle,
            delimiter="\t",
            lineterminator="\n",
            quoting=csv.QUOTE_MINIMAL,
        )
        writer.writerow(columns)
        for row in rows:
            if len(row) != len(columns):
                raise BhsaMaterializationError(
                    f"sidecar row for {path.name} has {len(row)} fields; expected {len(columns)}"
                )
            writer.writerow("" if value is None else value for value in row)


def _required_int_sort(value: object) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise BhsaMaterializationError(f"expected integer sort cell, got {value!r}")
    return value


def _optional_int_sort(value: object) -> int:
    return value if isinstance(value, int) and not isinstance(value, bool) else -1
