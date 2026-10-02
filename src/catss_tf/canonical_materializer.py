"""Standalone canonical Text-Fabric materializer for CATSS alignment data."""

import csv
import dataclasses
import hashlib
import pathlib
import shutil
import tempfile
import typing

from catss_tf import __version__
from catss_tf.parser import AlignmentRecord, ParallelDocument, VerseRecord, parse_parallel_text
from catss_tf.source import (
    CATSS_PARALLEL_FILENAMES,
    ParallelSourceManifest,
    SourceFileFingerprint,
    inspect_parallel_source,
)
from catss_tf.technique import TechniqueError, derive_alignment_technique, technique_sidecar_row
from catss_tf.tf_schema import SIDECAR_COLUMNS
from catss_tf.validation import ValidationFinding, validate_documents

CANONICAL_SCHEMA_VERSION = "1"
CanonicalValue = int | str
NodeFeatures = dict[str, dict[int, CanonicalValue]]
EdgeFeatures = dict[str, dict[int, tuple[int, ...]]]

_SOURCE_RANK = {name: index for index, name in enumerate(CATSS_PARALLEL_FILENAMES)}
_CANONICAL_SIDECARS = (
    "catss-alignments.tsv",
    "catss-technique.tsv",
    "catss-annotations.tsv",
    "catss-sources.tsv",
    "catss-source-lines.tsv",
    "catss-diagnostics.tsv",
)


class CanonicalMaterializationError(RuntimeError):
    """Raised when a fail-closed standalone CATSS corpus cannot be published."""


@dataclasses.dataclass(frozen=True, slots=True)
class CanonicalMaterializationSummary:
    """Scalar summary of one completed canonical CATSS materialization."""

    source_files: int
    verses: int
    alignments: int
    alignment_slots: int
    mt_elements: int
    lxx_elements: int
    annotations: int
    references: int
    source_lines: int
    tf_features: int
    edge_features: int
    sidecar_rows: int
    ignored_validation_findings: int
    audit_ok: bool


@dataclasses.dataclass(frozen=True, slots=True)
class CanonicalMaterializationResult:
    """Published standalone CATSS corpus and its scalar summary."""

    output_path: pathlib.Path
    summary: CanonicalMaterializationSummary


@dataclasses.dataclass(frozen=True, slots=True)
class _AlignmentContext:
    source: str
    verse: VerseRecord
    alignment: AlignmentRecord
    slot: int


@dataclasses.dataclass(frozen=True, slots=True)
class _CanonicalGraph:
    node_types: dict[int, str]
    oslots: dict[int, tuple[int, ...]]
    node_features: NodeFeatures
    edge_features: EdgeFeatures
    max_slot: int
    alignment_slots: dict[str, int]


@dataclasses.dataclass(slots=True)
class _GraphBuilder:
    node_types: dict[int, str]
    oslots: dict[int, tuple[int, ...]]
    node_features: NodeFeatures
    edge_features: EdgeFeatures
    next_node: int

    def add_node(self, otype: str, slots: tuple[int, ...]) -> int:
        if not slots:
            raise CanonicalMaterializationError(
                f"canonical non-slot node {otype!r} has no alignment slot"
            )
        node = self.next_node
        self.next_node += 1
        self.node_types[node] = otype
        self.oslots[node] = slots
        return node

    def feature(self, name: str, node: int, value: CanonicalValue | None) -> None:
        if value is None:
            return
        data = self.node_features.setdefault(name, {})
        existing = data.get(node)
        if existing is not None and existing != value:
            raise CanonicalMaterializationError(
                f"conflicting canonical feature {name} on node {node}: {existing!r} != {value!r}"
            )
        data[node] = value

    def edge(self, name: str, source: int, target: int) -> None:
        data = self.edge_features.setdefault(name, {})
        current = data.get(source, ())
        if target not in current:
            data[source] = tuple(sorted((*current, target)))


def materialize_corpus(
    source_directory: str | pathlib.Path,
    output_directory: str | pathlib.Path,
    *,
    allowed_validation_codes: set[str] | frozenset[str] = frozenset(),
) -> CanonicalMaterializationResult:
    """Build and atomically publish a standalone canonical CATSS Text-Fabric corpus."""

    source_root = pathlib.Path(source_directory)
    destination = pathlib.Path(output_directory)
    if destination.exists():
        raise CanonicalMaterializationError(f"destination already exists: {destination}")

    manifest, documents = _snapshot_parallel_source(source_root)
    _validate_source_contract(manifest)
    validation = validate_documents(
        documents,
        allowed_codes=allowed_validation_codes,
    )
    if not validation.ok:
        codes = ", ".join(finding.code for finding in validation.findings)
        raise CanonicalMaterializationError(f"canonical validation failed: {codes}")

    try:
        graph, contexts = _compile_graph(documents)
        sidecars = _canonical_sidecars(manifest, contexts, validation.findings)
    except TechniqueError as exc:
        raise CanonicalMaterializationError(f"technique derivation failed: {exc}") from exc

    _audit_graph(manifest, documents, graph)

    _publish_bundle(
        destination,
        graph=graph,
        sidecars=sidecars,
    )

    node_type_counts = _node_type_counts(graph.node_types)
    sidecar_rows = sum(len(rows) for rows in sidecars.values())
    ignored = sum(finding.severity == "ignored" for finding in validation.findings)

    return CanonicalMaterializationResult(
        output_path=destination,
        summary=CanonicalMaterializationSummary(
            source_files=len(manifest.files),
            verses=sum(len(document.verses) for document in documents),
            alignments=graph.max_slot,
            alignment_slots=graph.max_slot,
            mt_elements=node_type_counts.get("mt_element", 0),
            lxx_elements=node_type_counts.get("lxx_element", 0),
            annotations=node_type_counts.get("annotation", 0),
            references=node_type_counts.get("reference", 0),
            source_lines=node_type_counts.get("source_line", 0),
            tf_features=len(graph.node_features) + 3,
            edge_features=len(graph.edge_features),
            sidecar_rows=sidecar_rows,
            ignored_validation_findings=ignored,
            audit_ok=True,
        ),
    )


def _snapshot_parallel_source(
    source_root: pathlib.Path,
) -> tuple[ParallelSourceManifest, tuple[ParallelDocument, ...]]:
    """Read each selected CATSS file once; fingerprint and parse the same bytes."""

    discovered = inspect_parallel_source(source_root)
    by_source: dict[str, tuple[SourceFileFingerprint, ParallelDocument]] = {}

    for item in discovered.files:
        path = source_root / item.relative_path
        payload = path.read_bytes()
        fingerprint = SourceFileFingerprint(
            relative_path=item.relative_path,
            size_bytes=len(payload),
            sha256=hashlib.sha256(payload).hexdigest(),
        )
        document = parse_parallel_text(
            payload.decode("utf-8"),
            source_name=item.relative_path,
        )
        by_source[item.relative_path] = (fingerprint, document)

    ordered_names = sorted(
        by_source,
        key=lambda name: (_SOURCE_RANK.get(name, len(_SOURCE_RANK)), name),
    )
    return (
        ParallelSourceManifest(files=tuple(by_source[name][0] for name in ordered_names)),
        tuple(by_source[name][1] for name in ordered_names),
    )


def _validate_source_contract(manifest: ParallelSourceManifest) -> None:
    unknown = [
        item.relative_path for item in manifest.files if item.relative_path not in _SOURCE_RANK
    ]
    if unknown:
        raise CanonicalMaterializationError(
            "unknown CATSS source(s): " + ", ".join(sorted(unknown))
        )


def _compile_graph(
    documents: tuple[ParallelDocument, ...],
) -> tuple[_CanonicalGraph, tuple[_AlignmentContext, ...]]:
    contexts: list[_AlignmentContext] = []
    alignment_slots: dict[str, int] = {}
    node_types: dict[int, str] = {}

    slot = 1
    for document in documents:
        for verse in document.verses:
            for alignment in verse.alignments:
                if alignment.alignment_id in alignment_slots:
                    raise CanonicalMaterializationError(
                        f"duplicate canonical alignment id: {alignment.alignment_id}"
                    )
                node_types[slot] = "alignment"
                alignment_slots[alignment.alignment_id] = slot
                contexts.append(
                    _AlignmentContext(
                        source=document.source_name,
                        verse=verse,
                        alignment=alignment,
                        slot=slot,
                    )
                )
                slot += 1

    max_slot = slot - 1
    if max_slot < 1:
        raise CanonicalMaterializationError("canonical CATSS corpus has no alignments")

    builder = _GraphBuilder(
        node_types=node_types,
        oslots={},
        node_features={},
        edge_features={},
        next_node=max_slot + 1,
    )

    for context in contexts:
        _alignment_features(builder, context)

    verse_nodes = _add_structural_nodes(builder, documents, contexts)
    _add_detail_nodes(builder, contexts, verse_nodes)

    return (
        _CanonicalGraph(
            node_types=builder.node_types,
            oslots=builder.oslots,
            node_features=builder.node_features,
            edge_features=builder.edge_features,
            max_slot=max_slot,
            alignment_slots=alignment_slots,
        ),
        tuple(contexts),
    )


def _alignment_features(builder: _GraphBuilder, context: _AlignmentContext) -> None:
    alignment = context.alignment
    node = context.slot
    try:
        technique = derive_alignment_technique(context.source, alignment)
    except TechniqueError as exc:
        raise CanonicalMaterializationError(
            "technique derivation failed for "
            f"{context.source}:{min(alignment.source_lines)} "
            f"{alignment.alignment_id} "
            f"mt={alignment.mt_raw!r} lxx={alignment.lxx_raw!r}: {exc}"
        ) from exc

    values: dict[str, CanonicalValue | None] = {
        "catss_alignment_id": alignment.alignment_id,
        "catss_source": context.source,
        "book": context.verse.book,
        "chapter": context.verse.chapter,
        "verse": context.verse.verse,
        "catss_line_first": min(alignment.source_lines),
        "catss_line_last": max(alignment.source_lines),
        "catss_line_n": len(alignment.source_lines),
        "catss_mt_raw": alignment.mt_raw,
        "catss_lxx_raw": alignment.lxx_raw,
        "catss_mt_col_a": alignment.mt_col_a,
        "catss_mt_col_b": alignment.mt_col_b,
        "catss_retro_kind": alignment.retroversion_kind,
        "catss_mt_n": alignment.mt_count,
        "catss_lxx_n": alignment.lxx_count,
        "catss_display": _alignment_display(alignment),
        "catss_tt_cardinality_mt_lxx": technique.cardinality_mt_lxx,
        "catss_tt_token_balance_mt_lxx": technique.token_balance_mt_lxx,
        "catss_tt_transposition_mt_lxx": technique.transposition_mt_lxx,
    }
    for name, value in values.items():
        builder.feature(name, node, value)

    flags = {
        "catss_lxx_plus": alignment.is_lxx_plus,
        "catss_lxx_minus": alignment.is_lxx_minus,
        "catss_retro": alignment.has_retroversion,
        "catss_ketiv": alignment.is_ketiv,
        "catss_qere": alignment.is_qere,
        "catss_trans_local": alignment.is_transposition_local,
        "catss_trans_remote": alignment.is_transposition_remote,
        "catss_trans_style": alignment.is_transposition_stylistic,
        "catss_column_split": alignment.column_split,
        "catss_tt_addition_vs_mt": technique.addition_vs_mt,
        "catss_tt_omission_vs_mt": technique.omission_vs_mt,
    }
    for name, value in flags.items():
        if value:
            builder.feature(name, node, 1)


def _alignment_display(alignment: AlignmentRecord) -> str:
    mt = alignment.mt_raw or "∅"
    lxx = alignment.lxx_raw or "∅"
    return f"{mt} ⇔ {lxx}"


def _add_structural_nodes(
    builder: _GraphBuilder,
    documents: tuple[ParallelDocument, ...],
    contexts: list[_AlignmentContext],
) -> dict[tuple[str, int, int], tuple[int, ...]]:
    slots_by_source: dict[str, list[int]] = {}
    slots_by_chapter: dict[tuple[str, int], list[int]] = {}
    contexts_by_verse: dict[tuple[str, int, int], list[_AlignmentContext]] = {}

    for context in contexts:
        slots_by_source.setdefault(context.source, []).append(context.slot)
        slots_by_chapter.setdefault(
            (context.source, context.verse.chapter),
            [],
        ).append(context.slot)
        contexts_by_verse.setdefault(
            (context.source, context.verse.chapter, context.verse.verse),
            [],
        ).append(context)

    for document in documents:
        document_slots = tuple(slots_by_source.get(document.source_name, ()))
        if not document_slots:
            continue
        node = builder.add_node("document", document_slots)
        builder.feature("catss_source", node, document.source_name)
        if document.verses:
            builder.feature("book", node, document.verses[0].book)

    for source, chapter in sorted(
        slots_by_chapter,
        key=lambda key: (_SOURCE_RANK[key[0]], key[1]),
    ):
        node = builder.add_node("chapter", tuple(slots_by_chapter[(source, chapter)]))
        builder.feature("catss_source", node, source)
        builder.feature("chapter", node, chapter)

    verse_nodes: dict[tuple[str, int, int], list[int]] = {}
    ordered_keys = sorted(
        contexts_by_verse,
        key=lambda key: (
            _SOURCE_RANK[key[0]],
            key[1],
            key[2],
            contexts_by_verse[key][0].verse.header_line_no,
        ),
    )
    for key in ordered_keys:
        by_record: dict[int, list[_AlignmentContext]] = {}
        for context in contexts_by_verse[key]:
            by_record.setdefault(context.verse.header_line_no, []).append(context)
        for header_line in sorted(by_record):
            verse_contexts = by_record[header_line]
            slots = tuple(context.slot for context in verse_contexts)
            node = builder.add_node("verse", slots)
            source, chapter, verse = key
            builder.feature("catss_source", node, source)
            builder.feature("book", node, verse_contexts[0].verse.book)
            builder.feature("chapter", node, chapter)
            builder.feature("verse", node, verse)
            builder.feature("catss_header_raw", node, verse_contexts[0].verse.header_raw)
            builder.feature(
                "catss_header_line_no",
                node,
                verse_contexts[0].verse.header_line_no,
            )
            verse_nodes.setdefault(key, []).append(node)

    return {key: tuple(nodes) for key, nodes in verse_nodes.items()}


def _add_detail_nodes(
    builder: _GraphBuilder,
    contexts: list[_AlignmentContext],
    verse_nodes: dict[tuple[str, int, int], tuple[int, ...]],
) -> None:
    """Allocate each Text-Fabric node type in one contiguous node-id block."""

    for context in contexts:
        alignment = context.alignment
        slot = context.slot
        for index, reading in enumerate(alignment.mt_readings, start=1):
            node = builder.add_node("mt_element", (slot,))
            builder.feature("catss_index", node, index)
            builder.feature("catss_text", node, reading.primary)
            builder.feature("catss_ketiv_text", node, reading.ketiv)
            builder.feature("catss_qere_text", node, reading.qere)
            builder.feature("catss_doubt", node, int(reading.doubtful))
            builder.feature("catss_aramaic_section", node, int(reading.aramaic_section))

    for context in contexts:
        alignment = context.alignment
        slot = context.slot
        for index, text in enumerate(alignment.lxx_tokens, start=1):
            node = builder.add_node("lxx_element", (slot,))
            builder.feature("catss_index", node, index)
            builder.feature("catss_text", node, text)

    for context in contexts:
        alignment = context.alignment
        slot = context.slot
        for annotation in alignment.annotations:
            node = builder.add_node("annotation", (slot,))
            builder.feature("catss_side", node, annotation.side)
            builder.feature("catss_kind", node, annotation.kind)
            builder.feature("catss_family", node, annotation.family)
            builder.feature("catss_contextual", node, int(annotation.contextual))
            builder.feature("catss_payload", node, annotation.payload)
            builder.feature("catss_raw", node, annotation.raw)

    for context in contexts:
        alignment = context.alignment
        slot = context.slot
        for reference in alignment.lxx_references:
            node = builder.add_node("reference", (slot,))
            builder.feature("catss_ref_chapter", node, reference.chapter)
            builder.feature("catss_ref_verse", node, reference.verse)
            builder.feature("catss_ref_subverse", node, reference.subverse)
            builder.feature("catss_raw", node, reference.raw)

            target_chapter = (
                reference.chapter if reference.chapter is not None else context.verse.chapter
            )
            targets = verse_nodes.get(
                (context.source, target_chapter, reference.verse),
                (),
            )
            if len(targets) == 1:
                builder.edge("catss_reference_target", node, targets[0])

    for context in contexts:
        alignment = context.alignment
        slot = context.slot
        for line_no, raw in zip(
            alignment.source_lines,
            alignment.raw_lines,
            strict=True,
        ):
            node = builder.add_node("source_line", (slot,))
            builder.feature("catss_line_no", node, line_no)
            builder.feature("catss_raw", node, raw)


def _canonical_sidecars(
    manifest: ParallelSourceManifest,
    contexts: tuple[_AlignmentContext, ...],
    validation_findings: tuple[ValidationFinding, ...],
) -> dict[str, list[tuple[object, ...]]]:
    alignment_rows: list[tuple[object, ...]] = []
    technique_rows: list[tuple[object, ...]] = []
    annotation_rows: list[tuple[object, ...]] = []
    source_line_rows: list[tuple[object, ...]] = []

    for context in contexts:
        alignment = context.alignment
        alignment_rows.append(_alignment_sidecar_row(context))
        technique_rows.append(
            technique_sidecar_row(derive_alignment_technique(context.source, alignment))
        )
        annotation_rows.extend(
            (
                context.source,
                alignment.alignment_id,
                annotation.side,
                annotation.kind,
                annotation.family,
                int(annotation.contextual),
                annotation.payload,
                annotation.raw,
            )
            for annotation in alignment.annotations
        )
        source_line_rows.extend(
            (
                context.source,
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

    alignment_rows.sort(
        key=lambda row: (
            _SOURCE_RANK[str(row[0])],
            _required_int(row[5]),
            str(row[1]),
        )
    )
    technique_rows.sort(key=lambda row: (_SOURCE_RANK[str(row[0])], str(row[1])))
    annotation_rows.sort(
        key=lambda row: (
            _SOURCE_RANK[str(row[0])],
            str(row[1]),
            str(row[2]),
            str(row[3]),
            str(row[4]),
        )
    )
    source_line_rows.sort(
        key=lambda row: (
            _SOURCE_RANK[str(row[0])],
            _required_int(row[2]),
            str(row[1]),
        )
    )

    source_rows: list[tuple[object, ...]] = [
        (source.relative_path, source.size_bytes, source.sha256) for source in manifest.files
    ]
    diagnostic_rows = [
        _validation_diagnostic_row(finding)
        for finding in validation_findings
        if finding.severity == "ignored"
    ]
    diagnostic_rows.sort(
        key=lambda row: (
            _SOURCE_RANK.get(str(row[3]), len(_SOURCE_RANK)),
            _optional_int(row[8]),
            str(row[2]),
            str(row[7]),
        )
    )

    return {
        "catss-alignments.tsv": alignment_rows,
        "catss-technique.tsv": technique_rows,
        "catss-annotations.tsv": annotation_rows,
        "catss-sources.tsv": source_rows,
        "catss-source-lines.tsv": source_line_rows,
        "catss-diagnostics.tsv": diagnostic_rows,
    }


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


def _audit_node_type_intervals(node_types: dict[int, str]) -> None:
    """Reject node types split across multiple Text-Fabric node-id intervals."""

    nodes_by_type: dict[str, list[int]] = {}
    for node in sorted(node_types):
        nodes_by_type.setdefault(node_types[node], []).append(node)

    for node_type, nodes in nodes_by_type.items():
        first = nodes[0]
        last = nodes[-1]
        if nodes != list(range(first, last + 1)):
            raise CanonicalMaterializationError(
                "canonical preservation audit failed: "
                f"node type {node_type!r} does not occupy one contiguous node interval"
            )


def _audit_graph(
    manifest: ParallelSourceManifest,
    documents: tuple[ParallelDocument, ...],
    graph: _CanonicalGraph,
) -> None:
    _audit_node_type_intervals(graph.node_types)

    expected_contexts = [
        (document.source_name, verse, alignment)
        for document in documents
        for verse in document.verses
        for alignment in verse.alignments
    ]
    if graph.max_slot != len(expected_contexts):
        raise CanonicalMaterializationError(
            "canonical preservation audit failed: alignment slot count mismatch"
        )

    expected_ids = [alignment.alignment_id for _source, _verse, alignment in expected_contexts]
    actual_ids = [
        typing.cast(str, graph.node_features["catss_alignment_id"][slot])
        for slot in range(1, graph.max_slot + 1)
    ]
    if actual_ids != expected_ids:
        raise CanonicalMaterializationError(
            "canonical preservation audit failed: alignment identity/order mismatch"
        )
    if len(set(actual_ids)) != len(actual_ids):
        raise CanonicalMaterializationError(
            "canonical preservation audit failed: duplicate alignment identity"
        )

    expected_by_type = {
        "mt_element": sum(
            len(alignment.mt_readings) for _source, _verse, alignment in expected_contexts
        ),
        "lxx_element": sum(
            len(alignment.lxx_tokens) for _source, _verse, alignment in expected_contexts
        ),
        "annotation": sum(
            len(alignment.annotations) for _source, _verse, alignment in expected_contexts
        ),
        "reference": sum(
            len(alignment.lxx_references) for _source, _verse, alignment in expected_contexts
        ),
        "source_line": sum(
            len(alignment.source_lines) for _source, _verse, alignment in expected_contexts
        ),
    }
    actual_by_type = _node_type_counts(graph.node_types)
    for node_type, expected in expected_by_type.items():
        if actual_by_type.get(node_type, 0) != expected:
            raise CanonicalMaterializationError(
                "canonical preservation audit failed: "
                f"{node_type} count mismatch "
                f"{actual_by_type.get(node_type, 0)} != {expected}"
            )

    for node, node_type in graph.node_types.items():
        if node <= graph.max_slot:
            if node_type != "alignment":
                raise CanonicalMaterializationError(
                    "canonical preservation audit failed: non-alignment slot"
                )
            continue
        slots = graph.oslots.get(node)
        if not slots:
            raise CanonicalMaterializationError(
                f"canonical preservation audit failed: node {node} has no oslots"
            )
        if any(slot < 1 or slot > graph.max_slot for slot in slots):
            raise CanonicalMaterializationError(
                f"canonical preservation audit failed: node {node} has invalid oslot"
            )

    child_types = {
        "mt_element",
        "lxx_element",
        "annotation",
        "reference",
        "source_line",
    }
    children_by_slot: dict[int, dict[str, int]] = {
        slot: {node_type: 0 for node_type in child_types} for slot in range(1, graph.max_slot + 1)
    }
    for node, node_type in graph.node_types.items():
        if node_type not in child_types:
            continue
        slots = graph.oslots[node]
        if len(slots) != 1:
            raise CanonicalMaterializationError(
                f"canonical preservation audit failed: {node_type} spans multiple slots"
            )
        children_by_slot[slots[0]][node_type] += 1

    for slot, (_source, _verse, alignment) in enumerate(expected_contexts, start=1):
        expected_counts = {
            "mt_element": len(alignment.mt_readings),
            "lxx_element": len(alignment.lxx_tokens),
            "annotation": len(alignment.annotations),
            "reference": len(alignment.lxx_references),
            "source_line": len(alignment.source_lines),
        }
        if children_by_slot[slot] != expected_counts:
            raise CanonicalMaterializationError(
                "canonical preservation audit failed: "
                f"alignment child mismatch for {alignment.alignment_id}"
            )

    manifest_names = tuple(item.relative_path for item in manifest.files)
    document_names = tuple(document.source_name for document in documents)
    if manifest_names != document_names:
        raise CanonicalMaterializationError(
            "canonical preservation audit failed: source manifest/document order mismatch"
        )


def _publish_bundle(
    destination: pathlib.Path,
    *,
    graph: _CanonicalGraph,
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
        _write_canonical_tf(temp_path, graph)
        for filename in _CANONICAL_SIDECARS:
            _write_tsv(
                temp_path / filename,
                SIDECAR_COLUMNS[filename],
                sidecars.get(filename, []),
            )
        temp_path.replace(destination)
    except Exception:
        shutil.rmtree(temp_path, ignore_errors=True)
        raise


def _write_canonical_tf(directory: pathlib.Path, graph: _CanonicalGraph) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    _write_otype(directory / "otype.tf", graph.node_types)
    _write_oslots(directory / "oslots.tf", graph.oslots)
    _write_otext(directory / "otext.tf")

    for name in sorted(graph.node_features):
        _write_node_feature(
            directory / f"{name}.tf",
            name,
            graph.node_features[name],
        )
    for name in sorted(graph.edge_features):
        _write_edge_feature(
            directory / f"{name}.tf",
            name,
            graph.edge_features[name],
        )


def _metadata_headers() -> list[str]:
    return [
        f"@catssCanonicalSchema={CANONICAL_SCHEMA_VERSION}",
        "@catssArtifact=catss",
        "@catssSourceKind=catss-parallel",
        "@writtenBy=CATSS-TF",
        f"@softwareVersion={_header_value(__version__)}",
    ]


def _write_otype(path: pathlib.Path, node_types: dict[int, str]) -> None:
    lines = [
        "@node",
        "@valueType=str",
        *_metadata_headers(),
        "",
    ]
    lines.extend(f"{node}\t{_feature_value(node_types[node])}" for node in sorted(node_types))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_oslots(path: pathlib.Path, oslots: dict[int, tuple[int, ...]]) -> None:
    lines = [
        "@edge",
        "@valueType=int",
        *_metadata_headers(),
        "",
    ]
    for node in sorted(oslots):
        lines.append(f"{node}\t{_node_spec(oslots[node])}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_otext(path: pathlib.Path) -> None:
    lines = [
        "@config",
        "@fmt:text-orig-full={catss_display}",
        "@fmt:text-orig-plain={catss_display}",
        "@sectionFeatures=catss_source,chapter,verse",
        "@sectionTypes=document,chapter,verse",
        *_metadata_headers(),
        "",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_node_feature(
    path: pathlib.Path,
    name: str,
    data: dict[int, CanonicalValue],
) -> None:
    value_type = _value_type(name, data)
    lines = [
        "@node",
        f"@valueType={value_type}",
        f"@description=canonical CATSS feature {_header_value(name)}",
        *_metadata_headers(),
        "",
    ]
    for node in sorted(data):
        value = data[node]
        rendered = str(value) if isinstance(value, int) else _feature_value(value)
        lines.append(f"{node}\t{rendered}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_edge_feature(
    path: pathlib.Path,
    name: str,
    data: dict[int, tuple[int, ...]],
) -> None:
    lines = [
        "@edge",
        "@valueType=int",
        f"@description=canonical CATSS edge {_header_value(name)}",
        *_metadata_headers(),
        "",
    ]
    for node in sorted(data):
        targets = data[node]
        if not targets:
            raise CanonicalMaterializationError(f"empty edge target set for {name} node {node}")
        lines.append(f"{node}\t{_node_spec(targets)}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _value_type(name: str, data: dict[int, CanonicalValue]) -> str:
    kinds = {
        "int" if isinstance(value, int) and not isinstance(value, bool) else "str"
        for value in data.values()
    }
    if not kinds:
        raise CanonicalMaterializationError(f"empty canonical node feature {name}")
    if len(kinds) != 1:
        raise CanonicalMaterializationError(f"mixed value types in canonical feature {name}")
    return next(iter(kinds))


def _node_spec(nodes: tuple[int, ...]) -> str:
    ordered = tuple(sorted(set(nodes)))
    if not ordered:
        raise CanonicalMaterializationError("cannot render empty TF node set")
    ranges: list[str] = []
    start = previous = ordered[0]
    for node in ordered[1:]:
        if node == previous + 1:
            previous = node
            continue
        ranges.append(str(start) if start == previous else f"{start}-{previous}")
        start = previous = node
    ranges.append(str(start) if start == previous else f"{start}-{previous}")
    return ",".join(ranges)


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
                raise CanonicalMaterializationError(
                    f"sidecar row for {path.name} has {len(row)} fields; expected {len(columns)}"
                )
            writer.writerow("" if value is None else value for value in row)


def _node_type_counts(node_types: dict[int, str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for node_type in node_types.values():
        counts[node_type] = counts.get(node_type, 0) + 1
    return counts


def _required_int(value: object) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise CanonicalMaterializationError(f"expected integer sort cell, got {value!r}")
    return value


def _optional_int(value: object) -> int:
    return value if isinstance(value, int) and not isinstance(value, bool) else -1


def _header_value(value: str) -> str:
    if "\n" in value or "\r" in value:
        raise CanonicalMaterializationError("TF metadata values must be single-line")
    return value


def _feature_value(value: str) -> str:
    return value.replace("\\", "\\\\").replace("\t", "\\t").replace("\n", "\\n")
