"""Executable source-honest Qere/Ketiv and Sirach annotation smoke.

Run after installing catss-tf[tf]:
    python examples/annotation_evidence_walkthrough.py

Only synthetic sources are used; temporary TF data are deleted on exit.
"""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from tf.fabric import Fabric

from catss_tf import find_sirach_witness_annotations, materialize_corpus


def run_demo() -> dict[str, int]:
    with TemporaryDirectory(prefix="catss-tf-annotation-demo-") as directory:
        root = Path(directory)
        sources = root / "sources"
        sources.mkdir()
        (sources / "01.Genesis.par").write_text(
            "Gen 1:1\n*HBK **HBQ\tGR\n", encoding="utf-8"
        )
        (sources / "27.Sirach.par").write_text(
            "Sir 2:13\n[..] 3\tOU)AI\\\n[BN]* >7\tLOGOS\n",
            encoding="utf-8",
        )
        materialize_corpus(sources, root / "catss")
        api = Fabric(locations=str(root), modules=("catss",), silent="deep").loadAll(
            silent="deep"
        )

        mt_nodes = tuple(api.F.otype.s("mt_element"))
        primary = {node for node in mt_nodes if api.F.catss_text.v(node) == "HBK"}
        ketiv = {node for node in mt_nodes if api.F.catss_ketiv_text.v(node) == "HBK"}
        qere = {node for node in mt_nodes if api.F.catss_qere_text.v(node) == "HBQ"}

        annotations = tuple(api.F.otype.s("annotation"))

        def has_sirach_source(node: int) -> bool:
            alignment_slots = tuple(api.L.d(node, otype="alignment"))
            return len(alignment_slots) == 1 and (
                api.F.catss_source.v(alignment_slots[0]) == "27.Sirach.par"
            )

        def direct_count(kind: str, raw: str, payload: str | None = None) -> int:
            return sum(
                1
                for node in annotations
                if has_sirach_source(node)
                and api.F.catss_kind.v(node) == kind
                and api.F.catss_raw.v(node) == raw
                and api.F.catss_side.v(node) == "mt_a"
                and (payload is None or api.F.catss_payload.v(node) == payload)
            )

        target_edges = (
            sum(len(api.E.catss_annotation_target.f(node)) for node in annotations)
            if "catss_annotation_target" in api.Eall()
            else 0
        )
        return {
            "alignment_groups": len(api.F.otype.s("alignment")),
            "source_documents": len(api.F.otype.s("document")),
            "mt_ketiv_nodes": len(ketiv),
            "mt_qere_nodes": len(qere),
            "mt_primary_hbk_nodes": len(primary),
            "same_mt_word_for_ketiv_qere": len(primary & ketiv & qere),
            "sirach_3_marked": len(
                tuple(find_sirach_witness_annotations(api, 3, mode="marked", side="mt_a"))
            ),
            "sirach_3_independent_oracle": direct_count("sirach_witness_geniza_a", "3"),
            "sirach_7_lacking_mt_a": len(
                tuple(find_sirach_witness_annotations(api, 7, mode="lacking", side="mt_a"))
            ),
            "sirach_7_lacking_independent_oracle": direct_count(
                "sirach_reading_lacking_in_witness", ">7", payload="7"
            ),
            "sirach_7_lacking_mt_b": len(
                tuple(find_sirach_witness_annotations(api, 7, mode="lacking", side="mt_b"))
            ),
            "sirach_8_marked": len(tuple(find_sirach_witness_annotations(api, 8))),
            "sirach_lacuna_annotations": direct_count("sirach_lacuna_or_illegible", "[..]"),
            "sirach_fragmentary_letters": direct_count(
                "sirach_uncertain_fragmentary_letter", "*"
            ),
            "invented_annotation_targets": target_edges,
        }


if __name__ == "__main__":
    print(json.dumps(run_demo(), sort_keys=True))
