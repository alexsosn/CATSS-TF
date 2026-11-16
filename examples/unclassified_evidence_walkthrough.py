"""Explore unresolved CATSS technique evidence in standalone Text-Fabric.

Run after installing catss-tf[tf]:
    python examples/unclassified_evidence_walkthrough.py

Only synthetic sources are created in a temporary directory. Never classify
an unresolved alignment as an addition/omission without source evidence.
"""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from tf.fabric import Fabric

from catss_tf import find_unclassified_alignments, materialize_corpus


def run_demo() -> dict[str, object]:
    with TemporaryDirectory(prefix="catss-unclassified-demo-") as directory:
        root = Path(directory)
        source = root / "sources"
        source.mkdir()
        (source / "01.Genesis.par").write_text("Gen 1:1\nHB\tLOGOS\n", encoding="utf-8")
        (source / "27.Sirach.par").write_text(
            "Sir 2:13\nHB 7\tLOGOS\n3 7\tQEOS\n7\t---\n[..] 7\tLOGOS\n",
            encoding="utf-8",
        )
        materialize_corpus(source, root / "catss")
        api = Fabric(locations=str(root), modules=("catss",), silent="deep").loadAll(
            silent="deep"
        )

        hits = tuple(find_unclassified_alignments(api))
        # Independent native-TF oracle: enumerate all canonical slots rather
        # than using the query's status-feature item discovery path.
        oracle = tuple(
            (
                slot,
                str(api.F.catss_alignment_id.v(slot)),
                str(api.F.catss_tt_unclassified_reason.v(slot)),
            )
            for slot in api.F.otype.s("alignment")
            if api.F.catss_tt_status.v(slot) == "unclassified"
        )
        actual = tuple((hit.alignment_slot, hit.alignment_id, hit.reason) for hit in hits)

        sirach = tuple(find_unclassified_alignments(api, source="27.Sirach.par"))
        genesis = tuple(find_unclassified_alignments(api, source="01.Genesis.par"))
        hebrew_empty = tuple(find_unclassified_alignments(api, reason_contains="Hebrew-empty"))
        missing_mt_minus = tuple(find_unclassified_alignments(api, reason_contains="LXX-minus"))

        return {
            "alignment_groups": len(api.F.otype.s("alignment")),
            "source_documents": len(api.F.otype.s("document")),
            "unclassified_groups": len(hits),
            "unclassified_slots_direct_scan": len(oracle),
            "original_reasons_and_ids_verified": actual == oracle,
            "sirach_source_hits": len(sirach),
            "genesis_false_hits": len(genesis),
            "hebrew_empty_greek_hits": len(hebrew_empty),
            "lxx_minus_without_mt_hits": len(missing_mt_minus),
            "unclassified_mt_lexical_elements": sum(hit.mt_count for hit in hits),
            "unclassified_source_lines": [
                [hit.source_line_first, hit.source_line_last] for hit in hits
            ],
            "first_unclassified_greek_forms": list(hits[0].lxx_elements),
        }


if __name__ == "__main__":
    print(json.dumps(run_demo(), sort_keys=True))
