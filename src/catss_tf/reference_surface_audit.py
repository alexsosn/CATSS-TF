"""Read-only CATSS Greek reference surface-candidate diagnostics."""

import dataclasses
import typing

from catss_tf.lxx_resolver import (
    LxxSpan,
    LxxVerseProvider,
    _mapping_kind,
    normalize_catss_greek,
    normalize_lxx_greek,
)
from catss_tf.lxx_schema import (
    LxxSourceStatus,
    classify_catss_source,
    default_lxx_reference,
    validate_lxx_parent,
)
from catss_tf.parser import ParallelDocument

_CandidateScope: typing.TypeAlias = tuple[str, str, int, int, str | None]


@dataclasses.dataclass(frozen=True, slots=True)
class LxxReferenceSurfaceCandidates:
    """Per-scalar-reference evidence; no verified lexical or TF target mappings."""

    source_files: int
    scalar_references: int
    exact_single: int
    exact_single_with_overlap: int
    exact_single_with_unavoidable_overlap: int
    exact_single_with_avoidable_overlap_only: int
    exact_single_without_overlap: int
    reference_groups: int
    joint_unique_groups: int
    joint_multiple_groups: int
    joint_impossible_groups: int
    joint_incomplete_groups: int
    joint_indeterminate_groups: int
    context_groups_with_implicit: int
    context_unique_groups: int
    context_multiple_groups: int
    context_impossible_groups: int
    context_incomplete_groups: int
    context_indeterminate_groups: int
    role_context_groups_with_eligible_pair: int
    role_context_changed_groups: int
    role_context_unique_groups: int
    role_context_multiple_groups: int
    role_context_impossible_groups: int
    role_context_incomplete_groups: int
    role_context_indeterminate_groups: int
    exact_multiple: int
    no_surface_match: int
    no_greek_tokens: int
    catss_normalization_error: int
    parent_normalization_error: int
    parent_span_missing: int
    unsupported_source: int
    unknown_source: int


def audit_lxx_reference_surface_candidates(
    documents: typing.Iterable[ParallelDocument],
    provider: LxxVerseProvider,
) -> LxxReferenceSurfaceCandidates:
    """Count textual candidates without asserting their relation is a mapping."""
    validation = validate_lxx_parent(provider.parent_probe)
    if not validation.ok:
        raise ValueError(f"invalid LXX parent fingerprint: {validation.findings}")

    counts: dict[str, int] = {
        "source_files": 0,
        "scalar_references": 0,
        "exact_single": 0,
        "exact_multiple": 0,
        "no_surface_match": 0,
        "no_greek_tokens": 0,
        "catss_normalization_error": 0,
        "parent_normalization_error": 0,
        "parent_span_missing": 0,
        "unsupported_source": 0,
        "unknown_source": 0,
    }
    span_cache: dict[tuple[str, int, int, str | None], LxxSpan | None] = {}
    token_cache: dict[tuple[str, int, int, str | None], tuple[str, ...] | None] = {}
    # Only offsets, not Greek text or parent node IDs, are retained. A candidate
    # with one local occurrence may still overlap a different alignment's
    # candidate (including ambiguous alternative occurrences).
    candidate_intervals: dict[_CandidateScope, dict[str, set[tuple[int, int]]]] = {}
    # Include ALL supported explicit-reference alignments before any lexical
    # validation; a missing candidate makes the whole group incomplete.
    expected_alignments: dict[_CandidateScope, set[str]] = {}
    # Implicit/default lexical rows can constrain an explicit reference group.
    # Index by source and exact unsuffixed default parent, not by MT verse alone.
    implicit_alignments: dict[_CandidateScope, dict[str, tuple[str, ...]]] = {}
    # Mirror the LXX resolver's typed annotation roles, never raw spelling.
    roles_by_scope: dict[_CandidateScope, dict[str, str]] = {}
    single_candidates: list[tuple[_CandidateScope, str, tuple[int, int]]] = []
    seen_source_names: set[str] = set()

    for document in documents:
        if document.source_name in seen_source_names:
            raise ValueError(f"duplicate CATSS source name: {document.source_name}")
        seen_source_names.add(document.source_name)
        counts["source_files"] += 1
        status = classify_catss_source(document.source_name).status
        for verse in document.verses:
            default = (
                default_lxx_reference(document.source_name, verse.chapter, verse.verse)
                if status is LxxSourceStatus.SUPPORTED
                else None
            )
            for alignment in verse.alignments:
                if (
                    default is not None
                    and alignment.lxx_tokens
                    and not alignment.lxx_references
                    and not alignment.lxx_reference_ranges
                ):
                    implicit_scope = (
                        document.source_name,
                        default.book,
                        default.chapter,
                        default.verse,
                        None,
                    )
                    implicit_alignments.setdefault(implicit_scope, {})[alignment.alignment_id] = (
                        alignment.lxx_tokens
                    )
                    roles_by_scope.setdefault(implicit_scope, {})[alignment.alignment_id] = (
                        _mapping_kind(alignment)
                    )
                for reference in alignment.lxx_references:
                    counts["scalar_references"] += 1
                    if status is LxxSourceStatus.UNSUPPORTED:
                        counts["unsupported_source"] += 1
                        continue
                    if status is LxxSourceStatus.UNKNOWN:
                        counts["unknown_source"] += 1
                        continue

                    assert default is not None
                    key = (
                        default.book,
                        default.chapter if reference.chapter is None else reference.chapter,
                        reference.verse,
                        reference.subverse,
                    )
                    scope = (document.source_name, *key)
                    expected_alignments.setdefault(scope, set()).add(alignment.alignment_id)
                    roles_by_scope.setdefault(scope, {})[alignment.alignment_id] = _mapping_kind(
                        alignment
                    )
                    if key not in span_cache:
                        span = provider.get_span(*key)
                        if span is not None:
                            if (span.book, span.chapter, span.verse, span.subverse) != key:
                                raise ValueError(f"LXX parent span identity mismatch for {key}")
                            if any(word.subverse != (key[3] or "") for word in span.words):
                                raise ValueError(f"LXX span word subverse mismatch for {key}")
                        span_cache[key] = span
                    span = span_cache[key]
                    if span is None or not span.words:
                        counts["parent_span_missing"] += 1
                        continue
                    if not alignment.lxx_tokens:
                        counts["no_greek_tokens"] += 1
                        continue

                    try:
                        needle = tuple(
                            normalize_catss_greek(token) for token in alignment.lxx_tokens
                        )
                    except ValueError:
                        counts["catss_normalization_error"] += 1
                        continue
                    if key not in token_cache:
                        try:
                            token_cache[key] = tuple(
                                normalize_lxx_greek(word.word) for word in span.words
                            )
                        except ValueError:
                            token_cache[key] = None
                    haystack = token_cache[key]
                    if haystack is None:
                        counts["parent_normalization_error"] += 1
                        continue
                    n = len(needle)
                    matches = tuple(
                        (i, i + n)
                        for i in range(len(haystack) - n + 1)
                        if haystack[i : i + n] == needle
                    )
                    if not matches:
                        counts["no_surface_match"] += 1
                        continue
                    candidate_intervals.setdefault(scope, {}).setdefault(
                        alignment.alignment_id, set()
                    ).update(matches)
                    if len(matches) == 1:
                        counts["exact_single"] += 1
                        single_candidates.append((scope, alignment.alignment_id, matches[0]))
                    else:
                        counts["exact_multiple"] += 1

    unavoidable_overlap = 0
    avoidable_overlap_only = 0
    for scope, alignment_id, (start, stop) in single_candidates:
        unavoidable = False
        possible = False
        for competing_id, intervals in candidate_intervals[scope].items():
            if competing_id == alignment_id:
                continue
            # Every competing alignment has >=1 actual candidate interval.
            # One unavoidable pairwise collision takes priority over any
            # other competitor that could choose a disjoint alternative.
            overlaps = tuple(
                other_start < stop and start < other_stop for other_start, other_stop in intervals
            )
            if all(overlaps):
                unavoidable = True
                break
            if any(overlaps):
                possible = True
        if unavoidable:
            unavoidable_overlap += 1
        elif possible:
            avoidable_overlap_only += 1
    with_overlap = unavoidable_overlap + avoidable_overlap_only
    without_overlap = len(single_candidates) - with_overlap
    assert counts["exact_single"] == with_overlap + without_overlap

    joint_counts = {
        "unique": 0,
        "multiple": 0,
        "impossible": 0,
        "incomplete": 0,
        "indeterminate": 0,
    }
    context_counts = dict.fromkeys(joint_counts, 0)
    role_context_counts = dict.fromkeys(joint_counts, 0)
    context_groups_with_implicit = 0
    role_context_groups_with_eligible_pair = 0
    role_context_changed_groups = 0
    for scope, alignment_ids in expected_alignments.items():
        candidates = candidate_intervals.get(scope, {})
        missing_explicit = any(not candidates.get(alignment_id) for alignment_id in alignment_ids)
        tasks = {
            alignment_id: candidates[alignment_id]
            for alignment_id in sorted(alignment_ids)
            if candidates.get(alignment_id)
        }
        explicit_outcome = "incomplete" if missing_explicit else _classify_joint_intervals(tasks)
        joint_counts[explicit_outcome] += 1

        context_outcome = explicit_outcome
        implicit = implicit_alignments.get(scope, {})
        if implicit:
            context_groups_with_implicit += 1
            if missing_explicit:
                context_outcome = "incomplete"
            else:
                # Explicit lexical candidates guarantee an exact-key
                # normalized Greek parent haystack already in the cache.
                haystack = token_cache.get(scope[1:])
                incomplete = haystack is None
                if haystack is not None:
                    for alignment_id, tokens in implicit.items():
                        if alignment_id in tasks:
                            raise ValueError(
                                f"duplicate alignment task in CATSS context: {alignment_id}"
                            )
                        try:
                            needle = tuple(normalize_catss_greek(token) for token in tokens)
                        except ValueError:
                            incomplete = True
                            break
                        length = len(needle)
                        implicit_matches = {
                            (i, i + length)
                            for i in range(len(haystack) - length + 1)
                            if haystack[i : i + length] == needle
                        }
                        if not implicit_matches:
                            incomplete = True
                            break
                        tasks[alignment_id] = implicit_matches
                context_outcome = "incomplete" if incomplete else _classify_joint_intervals(tasks)
        context_counts[context_outcome] += 1

        roles = roles_by_scope[scope]
        eligible_pair = (
            "transposition_alignment" in roles.values()
            and "transposition_carrier" in roles.values()
        )
        if eligible_pair:
            role_context_groups_with_eligible_pair += 1
        if context_outcome == "multiple":
            # Relaxing a conflict cannot erase two already-proven assignments.
            # Do not downgrade that proof when extra branches exhaust the budget.
            role_outcome = "multiple"
        elif eligible_pair and context_outcome != "incomplete":
            role_outcome = _classify_joint_intervals(tasks, roles=roles)
        else:
            role_outcome = context_outcome
        role_context_counts[role_outcome] += 1
        if role_outcome != context_outcome:
            role_context_changed_groups += 1

    assert sum(joint_counts.values()) == len(expected_alignments)
    assert sum(context_counts.values()) == len(expected_alignments)
    assert sum(role_context_counts.values()) == len(expected_alignments)

    assert counts["scalar_references"] == sum(
        value for name, value in counts.items() if name not in {"source_files", "scalar_references"}
    )
    return LxxReferenceSurfaceCandidates(
        source_files=counts["source_files"],
        scalar_references=counts["scalar_references"],
        exact_single=counts["exact_single"],
        exact_single_with_overlap=with_overlap,
        exact_single_with_unavoidable_overlap=unavoidable_overlap,
        exact_single_with_avoidable_overlap_only=avoidable_overlap_only,
        exact_single_without_overlap=without_overlap,
        reference_groups=len(expected_alignments),
        joint_unique_groups=joint_counts["unique"],
        joint_multiple_groups=joint_counts["multiple"],
        joint_impossible_groups=joint_counts["impossible"],
        joint_incomplete_groups=joint_counts["incomplete"],
        joint_indeterminate_groups=joint_counts["indeterminate"],
        context_groups_with_implicit=context_groups_with_implicit,
        context_unique_groups=context_counts["unique"],
        context_multiple_groups=context_counts["multiple"],
        context_impossible_groups=context_counts["impossible"],
        context_incomplete_groups=context_counts["incomplete"],
        context_indeterminate_groups=context_counts["indeterminate"],
        role_context_groups_with_eligible_pair=role_context_groups_with_eligible_pair,
        role_context_changed_groups=role_context_changed_groups,
        role_context_unique_groups=role_context_counts["unique"],
        role_context_multiple_groups=role_context_counts["multiple"],
        role_context_impossible_groups=role_context_counts["impossible"],
        role_context_incomplete_groups=role_context_counts["incomplete"],
        role_context_indeterminate_groups=role_context_counts["indeterminate"],
        exact_multiple=counts["exact_multiple"],
        no_surface_match=counts["no_surface_match"],
        no_greek_tokens=counts["no_greek_tokens"],
        catss_normalization_error=counts["catss_normalization_error"],
        parent_normalization_error=counts["parent_normalization_error"],
        parent_span_missing=counts["parent_span_missing"],
        unsupported_source=counts["unsupported_source"],
        unknown_source=counts["unknown_source"],
    )


def _classify_joint_intervals(
    tasks: dict[str, set[tuple[int, int]]],
    *,
    max_states: int = 10000,
    roles: typing.Mapping[str, str] | None = None,
) -> typing.Literal["unique", "multiple", "impossible", "indeterminate"]:
    """Count 0, 1 or 2 bounded candidate assignments, optionally role-aware."""
    if not tasks or any(not spans for spans in tasks.values()) or max_states < 1:
        raise ValueError("joint candidate tasks must be nonempty and budget positive")
    if any(start < 0 or stop <= start for spans in tasks.values() for start, stop in spans):
        raise ValueError("candidate intervals must be nonempty and nonnegative")
    if roles is not None and (
        set(roles) != set(tasks)
        or set(roles.values()) - {"exact", "transposition_alignment", "transposition_carrier"}
    ):
        raise ValueError("role-aware candidate tasks require a valid role for each alignment")

    ordered = sorted(
        ((alignment_id, tuple(sorted(spans))) for alignment_id, spans in tasks.items()),
        key=lambda item: (len(item[1]), item[0]),
    )
    # Lazy iterative DFS: one frame for each active depth rather than a
    # cloned selected-prefix tuple for every alternative candidate.
    selected: list[tuple[str, int, int]] = []
    frames: list[typing.Iterator[tuple[int, int]]] = [iter(ordered[0][1])]
    visited = 1
    solutions = 0
    while frames:
        try:
            start, stop = next(frames[-1])
        except StopIteration:
            frames.pop()
            if selected:
                selected.pop()
            continue
        alignment_id = ordered[len(frames) - 1][0]
        conflict = False
        for other_id, other_start, other_stop in selected:
            if stop <= other_start or other_stop <= start:
                continue
            if (
                roles is not None
                and start == other_start
                and stop == other_stop
                and {roles[alignment_id], roles[other_id]}
                == {"transposition_alignment", "transposition_carrier"}
            ):
                continue
            conflict = True
            break
        if conflict:
            continue
        if visited >= max_states:
            return "indeterminate"
        visited += 1
        if len(frames) == len(ordered):
            solutions += 1
            if solutions == 2:
                return "multiple"
        else:
            selected.append((alignment_id, start, stop))
            frames.append(iter(ordered[len(frames)][1]))
    return "unique" if solutions == 1 else "impossible"
