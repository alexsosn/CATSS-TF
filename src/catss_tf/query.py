"""Source-exact lexical co-membership queries for standalone CATSS Text-Fabric.

Results represent complete alignment groups, not pairwise MT/Greek lexical edges.
"""

from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from typing import Any

from catss_tf.notation import notation_spec


@dataclass(frozen=True, slots=True)
class CanonicalAlignedGroup:
    """A matching source alignment with ordered lexical elements."""

    source: str
    alignment_id: str
    book: str
    chapter: int
    verse: int
    mt_elements: tuple[str, ...]
    lxx_elements: tuple[str, ...]


def _matching_slots(api: Any, mt_form: str, lxx_form: str) -> tuple[set[int], set[int]]:
    """Scan only source lexical feature entries, once for both forms.

    Text-Fabric NodeFeature.s(value) is itself a linear scan, not an index.
    A single pass over the feature data avoids repeating that scan.
    """

    mt_slots: set[int] = set()
    lxx_slots: set[int] = set()
    for node, value in api.F.catss_text.items():
        if value == mt_form and api.F.otype.v(node) == "mt_element":
            mt_slots.update(int(slot) for slot in api.L.d(node, otype="alignment"))
        elif value == lxx_form and api.F.otype.v(node) == "lxx_element":
            lxx_slots.update(int(slot) for slot in api.L.d(node, otype="alignment"))
    return mt_slots, lxx_slots


def _ordered_elements(api: Any, slot: int, element_type: str) -> tuple[str, ...]:
    nodes = api.L.u(slot, otype=element_type)
    return tuple(str(api.F.catss_text.v(n)) for n in sorted(nodes, key=api.F.catss_index.v))


def find_aligned_groups(
    api: Any,
    mt_form: str,
    lxx_form: str,
    *,
    source: str | None = None,
) -> Iterator[CanonicalAlignedGroup]:
    """Find canonical groups containing both exact source lexical forms.

    The loaded TF must use standalone alignment slots. BHSA and LXX
    projections have different node spaces and cannot use this join.
    MT search considers column A, never hypothetical column B reconstruction.
    Source filtering uses exact .par filenames; no normalization is applied.
    """

    if not mt_form or not lxx_form:
        raise ValueError("both MT and LXX search forms must be nonempty")
    if api.F.otype.slotType != "alignment":
        raise ValueError("find_aligned_groups requires the standalone CATSS alignment-slot warp")

    mt_slots, lxx_slots = _matching_slots(api, mt_form, lxx_form)
    for slot in sorted(mt_slots & lxx_slots):
        source_name = str(api.F.catss_source.v(slot))
        if source is not None and source_name != source:
            continue
        yield CanonicalAlignedGroup(
            source=source_name,
            alignment_id=str(api.F.catss_alignment_id.v(slot)),
            book=str(api.F.book.v(slot)),
            chapter=int(api.F.chapter.v(slot)),
            verse=int(api.F.verse.v(slot)),
            mt_elements=_ordered_elements(api, slot, "mt_element"),
            lxx_elements=_ordered_elements(api, slot, "lxx_element"),
        )


def find_groups_with_all_forms(
    api: Any,
    *,
    mt_forms: Sequence[str] = (),
    lxx_forms: Sequence[str] = (),
    source: str | None = None,
) -> Iterator[CanonicalAlignedGroup]:
    """Find alignment groups containing every requested exact lexical form.

    Requested forms have AND/set-membership semantics; repeated query forms
    do not require repeated tokens. MT is only column A, never speculative
    column-B reconstruction. A co-member is not a pairwise or phrase edge.
    """
    if api.F.otype.slotType != "alignment":
        raise ValueError("all-forms query requires the standalone CATSS alignment-slot warp")

    for label, forms in (("mt_forms", mt_forms), ("lxx_forms", lxx_forms)):
        if isinstance(forms, (str, bytes)) or not isinstance(forms, Sequence):
            raise ValueError(f"{label} must be a sequence of exact source forms")
        if any(not isinstance(form, str) or not form.strip() for form in forms):
            raise ValueError(f"{label} must contain only nonempty source forms")

    required = {
        *(("mt_element", form) for form in mt_forms),
        *(("lxx_element", form) for form in lxx_forms),
    }
    if not required:
        raise ValueError("at least one MT or LXX source form is required")
    if "catss_text" not in set(api.Fall()):
        return

    matching: dict[tuple[str, str], set[int]] = {key: set() for key in required}
    wanted_text = {form for _side, form in required}
    for node, value in api.F.catss_text.items():
        if value not in wanted_text:
            continue
        key = (api.F.otype.v(node), value)
        if key in matching:
            matching[key].update(int(slot) for slot in api.L.d(node, otype="alignment"))

    slots: set[int] | None = None
    for candidates in matching.values():
        slots = candidates.copy() if slots is None else slots & candidates
        if not slots:
            return
    if slots is None:
        return

    for slot in sorted(slots):
        source_name = str(api.F.catss_source.v(slot))
        if source is not None and source_name != source:
            continue
        yield CanonicalAlignedGroup(
            source=source_name,
            alignment_id=str(api.F.catss_alignment_id.v(slot)),
            book=str(api.F.book.v(slot)),
            chapter=int(api.F.chapter.v(slot)),
            verse=int(api.F.verse.v(slot)),
            mt_elements=_ordered_elements(api, slot, "mt_element"),
            lxx_elements=_ordered_elements(api, slot, "lxx_element"),
        )


@dataclass(frozen=True, slots=True)
class CanonicalMtBRawHit:
    """Raw reconstructed MT column-B evidence in one canonical alignment.

    The source B field is editorial/hypothetical notation, never an MT-A
    lexical token, normalized Hebrew lexeme, or manuscript attestation.
    """

    group: CanonicalAlignedGroup
    mt_b_raw: str
    retro_kind: str


def find_mt_b_raw_matches(
    api: Any,
    raw_substring: str,
    *,
    source: str | None = None,
    retro_kind: str | None = None,
) -> Iterator[CanonicalMtBRawHit]:
    """Find exact case-sensitive substrings in raw CATSS MT column B.

    No tokenization, normalizing, wildcard interpretation, or pairwise
    MT-to-Greek lexical correspondence is inferred. Marked source rows,
    ordinary MT-A-bearing groups and LXX-plus groups remain searchable.
    """
    if api.F.otype.slotType != "alignment":
        raise ValueError("MT-B raw query requires the standalone CATSS alignment-slot warp")
    if not isinstance(raw_substring, str) or not raw_substring.strip():
        raise ValueError("raw_substring must be a nonempty source text string")
    if source is not None and (not isinstance(source, str) or not source.strip()):
        raise ValueError("source must be a nonempty exact CATSS source filename")
    if retro_kind is not None and (
        not isinstance(retro_kind, str) or not retro_kind.strip()
    ):
        raise ValueError("retro_kind must be a nonempty exact source classification")

    available = set(api.Fall())
    if "catss_mt_col_b" not in available:
        return
    if "catss_retro_kind" not in available:
        raise ValueError("MT-B raw evidence is missing its retroversion-kind feature")

    for slot, raw in api.F.catss_mt_col_b.items():
        if not isinstance(raw, str) or raw_substring not in raw:
            continue
        if api.F.otype.v(slot) != "alignment":
            raise ValueError("MT-B raw evidence belongs to a non-alignment node")
        name = api.F.catss_source.v(slot)
        if not isinstance(name, str) or not name:
            raise ValueError("MT-B raw evidence has no canonical source identity")
        if source is not None and name != source:
            continue
        kind = api.F.catss_retro_kind.v(slot)
        if not isinstance(kind, str) or not kind:
            raise ValueError("MT-B raw evidence has no retroversion classification")
        if retro_kind is not None and kind != retro_kind:
            continue
        yield CanonicalMtBRawHit(
            group=CanonicalAlignedGroup(
                source=name,
                alignment_id=str(api.F.catss_alignment_id.v(slot)),
                book=str(api.F.book.v(slot)),
                chapter=int(api.F.chapter.v(slot)),
                verse=int(api.F.verse.v(slot)),
                mt_elements=_ordered_elements(api, int(slot), "mt_element"),
                lxx_elements=_ordered_elements(api, int(slot), "lxx_element"),
            ),
            mt_b_raw=raw,
            retro_kind=kind,
        )


@dataclass(frozen=True, slots=True)
class SirachWitnessAnnotation:
    """One raw manuscript annotation owned by a canonical alignment group.

    This record does not identify which MT lexical element a witness attests.
    Local TF node numbers are valid only within this loaded standalone warp.
    """

    source: str
    alignment_id: str
    book: str
    chapter: int
    verse: int
    alignment_slot: int
    annotation_node: int
    witness: int
    mode: str
    source_side: str
    raw: str
    payload: str | None
    mt_elements: tuple[str, ...]
    lxx_elements: tuple[str, ...]


def find_sirach_witness_annotations(
    api: Any,
    witness: int,
    *,
    mode: str = "marked",
    side: str | None = None,
) -> Iterator[SirachWitnessAnnotation]:
    """Find Sirach witness or reading-lacking markers on TF annotation nodes.

    Marked reports a manuscript number attached to an alignment group;
    lacking reports the typed >n annotation about a reading absent from
    that witness. Neither state asserts a witness-to-word attestation edge.
    Source side is the original CATSS MT-A or reconstructed MT-B column.
    """

    if type(witness) is not int or not 1 <= witness <= 10:
        raise ValueError("Sirach witness must be a number from 1 through 10")
    if mode not in {"marked", "lacking"}:
        raise ValueError("mode must be 'marked' or 'lacking'")
    if side not in {None, "mt_a", "mt_b"}:
        raise ValueError("side must be None, 'mt_a', or 'mt_b'")
    if api.F.otype.slotType != "alignment":
        raise ValueError("Sirach witness queries require a standalone alignment-slot CATSS warp")

    spec = notation_spec(str(witness), book="Sir")
    if spec is None or spec.family != "sirach_witness":
        raise ValueError("Sirach witness notation is unavailable")
    target_kind = spec.kind if mode == "marked" else "sirach_reading_lacking_in_witness"

    available = set(api.Fall())
    # Native TF omits an entire feature when no source node has a value.
    # A sparse Sirach corpus can have markers but no annotation payloads,
    # or even no annotations whatsoever; neither warrants fabricated data.
    if "catss_kind" not in available:
        return
    if mode == "lacking" and "catss_payload" not in available:
        return
    if not {"catss_side", "catss_raw"} <= available:
        raise ValueError("loaded canonical Sirach annotations require side and raw features")
    has_payload = "catss_payload" in available

    matched: list[tuple[int, int]] = []
    for node, kind in api.F.catss_kind.items():
        if kind != target_kind or api.F.otype.v(node) != "annotation":
            continue
        if mode == "lacking" and api.F.catss_payload.v(node) != str(witness):
            continue
        original_side = api.F.catss_side.v(node)
        if original_side not in {"mt_a", "mt_b"}:
            continue
        if side is not None and original_side != side:
            continue
        slots = tuple(api.L.d(node, otype="alignment"))
        if len(slots) != 1:
            raise ValueError("Sirach annotation must own exactly one canonical alignment slot")
        slot = int(slots[0])
        if api.F.catss_source.v(slot) != "27.Sirach.par":
            continue
        matched.append((slot, int(node)))

    for slot, node in sorted(matched):
        yield SirachWitnessAnnotation(
            source=str(api.F.catss_source.v(slot)),
            alignment_id=str(api.F.catss_alignment_id.v(slot)),
            book=str(api.F.book.v(slot)),
            chapter=int(api.F.chapter.v(slot)),
            verse=int(api.F.verse.v(slot)),
            alignment_slot=slot,
            annotation_node=node,
            witness=witness,
            mode=mode,
            source_side=str(api.F.catss_side.v(node)),
            raw=str(api.F.catss_raw.v(node)),
            payload=api.F.catss_payload.v(node) if has_payload else None,
            mt_elements=_ordered_elements(api, slot, "mt_element"),
            lxx_elements=_ordered_elements(api, slot, "lxx_element"),
        )


@dataclass(frozen=True, slots=True)
class AlignmentAnnotationEvidence:
    """A typed CATSS annotation co-occurring within one alignment group."""

    annotation_node: int
    kind: str
    side: str
    raw: str


@dataclass(frozen=True, slots=True)
class UnclassifiedAlignment:
    """Unresolved technique state, with verbatim source evidence and provenance."""

    alignment_slot: int
    alignment_id: str
    source: str
    book: str
    chapter: int
    verse: int
    source_line_first: int
    source_line_last: int
    reason: str
    mt_count: int
    lxx_count: int
    mt_elements: tuple[str, ...]
    lxx_elements: tuple[str, ...]
    annotations: tuple[AlignmentAnnotationEvidence, ...]


def find_unclassified_alignments(
    api: Any,
    *,
    source: str | None = None,
    reason_contains: str | None = None,
) -> Iterator[UnclassifiedAlignment]:
    """Inspect precisely unclassified native CATSS MT/LXX alignment groups.

    Reasons are returned unchanged; annotation membership says nothing about
    a manuscript's attestation of an individual lexical element. Neither
    unmarked Hebrew-empty Greek nor witness-only rows are assigned a false
    addition or omission status.
    """

    if api.F.otype.slotType != "alignment":
        raise ValueError("unclassified queries require the standalone CATSS alignment-slot warp")

    available = set(api.Fall())
    if "catss_tt_status" not in available:
        raise ValueError("canonical TF API must load catss_tt_status before querying")
    statuses = [
        int(slot)
        for slot, status in api.F.catss_tt_status.items()
        if status == "unclassified" and api.F.otype.v(slot) == "alignment"
    ]
    if not statuses:
        return
    if "catss_tt_unclassified_reason" not in available:
        raise ValueError("unclassified CATSS alignments must retain their source reason")

    for slot in sorted(statuses):
        original_source = str(api.F.catss_source.v(slot))
        if source is not None and original_source != source:
            continue
        reason = api.F.catss_tt_unclassified_reason.v(slot)
        if not reason:
            raise ValueError("unclassified CATSS alignment is missing its source reason")
        if reason_contains is not None and reason_contains not in reason:
            continue

        annotation_nodes = tuple(api.L.u(slot, otype="annotation"))
        if annotation_nodes and not {"catss_kind", "catss_side", "catss_raw"} <= available:
            raise ValueError("canonical annotation evidence is missing native TF features")
        annotations = tuple(
            AlignmentAnnotationEvidence(
                annotation_node=int(node),
                kind=str(api.F.catss_kind.v(node)),
                side=str(api.F.catss_side.v(node)),
                raw=str(api.F.catss_raw.v(node)),
            )
            for node in annotation_nodes
        )
        yield UnclassifiedAlignment(
            alignment_slot=slot,
            alignment_id=str(api.F.catss_alignment_id.v(slot)),
            source=original_source,
            book=str(api.F.book.v(slot)),
            chapter=int(api.F.chapter.v(slot)),
            verse=int(api.F.verse.v(slot)),
            source_line_first=int(api.F.catss_line_first.v(slot)),
            source_line_last=int(api.F.catss_line_last.v(slot)),
            reason=str(reason),
            mt_count=int(api.F.catss_mt_n.v(slot)),
            lxx_count=int(api.F.catss_lxx_n.v(slot)),
            mt_elements=_ordered_elements(api, slot, "mt_element"),
            lxx_elements=_ordered_elements(api, slot, "lxx_element"),
            annotations=annotations,
        )
