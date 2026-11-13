"""A licensed-data-free CATSS-TF research walkthrough using native Text-Fabric.

Run directly after installing catss-tf[tf]:
    python examples/canonical_research_walkthrough.py

All source and output files are synthetic and remain inside TemporaryDirectory.
"""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from tf.fabric import Fabric

from catss_tf import (
    find_aligned_groups,
    find_groups_with_all_forms,
    find_mt_b_raw_matches,
    materialize_corpus,
)


def run_demo() -> dict[str, int]:
    with TemporaryDirectory(prefix="catss-tf-research-") as work:
        root = Path(work)
        source = root / "source"
        source.mkdir()
        (source / "01.Genesis.par").write_text(
            "Gen 1:1\n"
            "MLK DBR\tBASILEU/S LOGOS\n"
            "MLK\tQEOS\n"
            "DBR\tLOGOS\n"
            "Gen 1:2\n"
            "=;W/KL\tLOGOS\n",
            encoding="utf-8",
        )
        (source / "06.JoshB.par").write_text(
            "JoshB 1:1\nMLK\tBASILEU/S\n", encoding="utf-8"
        )
        materialize_corpus(source, root / "catss")
        api = Fabric(locations=str(root), modules=("catss",), silent="deep").loadAll(
            silent="deep"
        )

        return {
            "source_documents": len(api.F.otype.s("document")),
            "alignment_groups": len(api.F.otype.s("alignment")),
            "mt_greek_groups": len(tuple(find_aligned_groups(api, "MLK", "BASILEU/S"))),
            "source_scoped_groups": len(
                tuple(
                    find_aligned_groups(
                        api, "MLK", "BASILEU/S", source="01.Genesis.par"
                    )
                )
            ),
            "multi_form_groups": len(
                tuple(
                    find_groups_with_all_forms(
                        api,
                        mt_forms=("MLK", "DBR"),
                        lxx_forms=("BASILEU/S", "LOGOS"),
                    )
                )
            ),
            # The Greek forms QEOS and LOGOS occur in the *same verse* but
            # never in a single editorial alignment group.
            "false_cross_group_matches": len(
                tuple(find_groups_with_all_forms(api, lxx_forms=("QEOS", "LOGOS")))
            ),
            "mt_b_context_hits": len(
                tuple(
                    find_mt_b_raw_matches(
                        api, "W/KL", source="01.Genesis.par", retro_kind="context"
                    )
                )
            ),
            # Reconstructed column B is never treated as lexical MT-A.
            "mt_b_as_mt_a_hits": len(tuple(find_aligned_groups(api, "W/KL", "LOGOS"))),
        }


if __name__ == "__main__":
    print(json.dumps(run_demo(), sort_keys=True))
