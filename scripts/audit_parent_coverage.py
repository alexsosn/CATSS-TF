"""Measure existing resolver output against local CATSS and pinned TF parents.

This research script does not acquire data or publish any modules.
Only aggregate counts, source filenames and finding codes are printed.
"""

import argparse
import dataclasses
import json
from collections import Counter
from pathlib import Path

from tf.fabric import Fabric

from catss_tf.bhsa_resolver import TextFabricBhsaProvider, resolve_bhsa_document
from catss_tf.bhsa_schema import (
    BHSA_CHECKOUT_COMMIT,
    BHSA_CHECKOUT_TAG,
    BHSA_REPOSITORY,
    BHSA_REQUIRED_FEATURES,
    BHSA_VERSION,
    BhsaParentProbe,
    validate_bhsa_parent,
)
from catss_tf.lxx_resolver import TextFabricLxxProvider, resolve_lxx_document
from catss_tf.lxx_schema import (
    LXX_NODE_COUNTS,
    LXX_RELEASE_COMMIT,
    LXX_RELEASE_TAG,
    LXX_REPOSITORY,
    LXX_REQUIRED_FEATURES,
    LXX_VERSION,
    LxxParentProbe,
    validate_lxx_parent,
)
from catss_tf.parser import parse_parallel_file
from catss_tf.projection_coverage import summarize_lexical_coverage
from catss_tf.source import CATSS_PARALLEL_FILENAMES, inspect_parallel_source


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("bhsa", type=Path, help="Local BHSA 2021 TF directory")
    parser.add_argument("lxx", type=Path, help="Local CenterBLC/LXX 1935 TF directory")
    args = parser.parse_args()
    manifest = inspect_parallel_source(args.source)
    names = tuple(item.relative_path for item in manifest.files)
    assert set(names) == set(CATSS_PARALLEL_FILENAMES), "expected all 46 CATSS files"

    bhsa = Fabric(locations=str(args.bhsa), silent="deep").load(
        " ".join(sorted(BHSA_REQUIRED_FEATURES - {"otype", "oslots"})), silent="deep"
    )
    lxx = Fabric(locations=str(args.lxx), silent="deep").load(
        " ".join(sorted(LXX_REQUIRED_FEATURES - {"otype", "oslots"})), silent="deep"
    )
    assert bhsa is not None and lxx is not None

    # CI checks out these exact commits before calling this script.
    # The probes additionally verify the loaded mapping-relevant structure.
    bhsa_probe = BhsaParentProbe(
        repository=BHSA_REPOSITORY,
        version=BHSA_VERSION,
        checkout_tag=BHSA_CHECKOUT_TAG,
        checkout_commit=BHSA_CHECKOUT_COMMIT,
        slot_type=bhsa.F.otype.slotType,
        max_slot=bhsa.F.otype.maxSlot,
        max_node=bhsa.F.otype.maxNode,
        section_types=tuple(bhsa.T.sectionTypes),
        feature_names=frozenset((*bhsa.Fall(), *bhsa.Eall())),
    )
    lxx_probe = LxxParentProbe(
        repository=LXX_REPOSITORY,
        version=LXX_VERSION,
        release_tag=LXX_RELEASE_TAG,
        release_commit=LXX_RELEASE_COMMIT,
        slot_type=lxx.F.otype.slotType,
        max_slot=lxx.F.otype.maxSlot,
        max_node=lxx.F.otype.maxNode,
        section_types=tuple(lxx.T.sectionTypes),
        node_counts={kind: len(lxx.F.otype.s(kind)) for kind in LXX_NODE_COUNTS},
        feature_names=frozenset((*lxx.Fall(), *lxx.Eall())),
    )
    assert validate_bhsa_parent(bhsa_probe).ok, "BHSA parent profile mismatch"
    assert validate_lxx_parent(lxx_probe).ok, "LXX parent profile mismatch"
    bhsa_provider = TextFabricBhsaProvider(bhsa)
    lxx_provider = TextFabricLxxProvider(lxx, lxx_probe)

    totals = {side: Counter() for side in ("bhsa", "lxx")}
    eligible = {side: Counter() for side in ("bhsa", "lxx")}
    findings = {side: Counter() for side in ("bhsa", "lxx")}
    candidates = []
    shared_total = 0

    for name in names:
        document = parse_parallel_file(args.source / name)
        alignments = [alignment for verse in document.verses for alignment in verse.alignments]
        assert len({a.alignment_id for a in alignments}) == len(alignments)
        b_report = resolve_bhsa_document(document, bhsa_provider)
        g_report = resolve_lxx_document(document, lxx_provider)
        b_counts = summarize_lexical_coverage(
            {a.alignment_id: a.mt_count for a in alignments},
            ((m.alignment_id, m.mt_index) for m in b_report.word_mappings),
        )
        g_counts = summarize_lexical_coverage(
            {a.alignment_id: a.lxx_count for a in alignments},
            ((m.alignment_id, m.lxx_index) for m in g_report.word_mappings),
        )
        source_result = {"source": name}
        strict_candidate = True
        for side, counts, report in (
            ("bhsa", b_counts, b_report),
            ("lxx", g_counts, g_report),
        ):
            summary = report.summary
            assert summary.supported_documents + summary.unsupported_documents == 1
            codes = Counter(f.code for f in report.findings)
            assert counts["mapping_rows"] == summary.word_mappings
            totals[side].update(counts)
            findings[side].update(codes)
            if summary.supported_documents:
                eligible[side].update(counts)
            strict_candidate &= (
                summary.supported_documents == 1
                and not report.findings
                and counts["source_elements"] > 0
                and counts["mapped_source_elements"] == counts["source_elements"]
            )
            source_result[side] = {
                "lexical_coverage": counts,
                "resolver": dataclasses.asdict(summary),
                "finding_codes": dict(codes),
            }
        shared = len(
            {m.alignment_id for m in b_report.word_mappings}
            & {m.alignment_id for m in g_report.word_mappings}
        )
        shared_total += shared
        source_result["groups_with_mapping_on_both_sides"] = shared
        if strict_candidate:
            candidates.append(name)
        print("CATSS_PROJECTION_SOURCE", json.dumps(source_result, sort_keys=True), flush=True)

    print(
        "CATSS_PROJECTION_TOTAL",
        json.dumps(
            {
                "sources": len(names),
                "all_source_coverage": totals,
                "profile_eligible_coverage": eligible,
                "finding_codes": findings,
                "groups_with_mapping_on_both_sides": shared_total,
                "strict_resolver_candidates": candidates,
            },
            sort_keys=True,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
