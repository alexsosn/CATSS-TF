# Worked case study: co-membership is not a lexical translation edge

**Question.** Given a Hebrew MT-A spelling `MLK` and a Greek spelling
`BASILEU/S`, which *editorial CATSS alignment groups* contain both? Can a
researcher restrict the answer to one source, demand ordered multiword forms,
and avoid accidental matches across groups, reconstructed Hebrew, or distinct
books? This case study verifies the query's behavior on **synthetic** lines,
not the frequency of any phenomenon in Jewish Scripture.

## Reproduce from a clean checkout

With Python 3.11–3.13, in the repository root, run:

```sh
python -m pip install -e ".[tf]"
python examples/canonical_research_walkthrough.py
```

The script creates invented `.par` rows in a temporary directory, calls
`materialize_corpus`, reloads the **standalone** native Text-Fabric
`catss` module, runs public query APIs and prints the following JSON.
The local installation may need internet access. The script does not download
licensed corpus data.

```json
{
  "alignment_groups": 5,
  "false_cross_group_matches": 0,
  "greek_cross_group_phrase_hits": 1,
  "greek_cross_header_false_hits": 0,
  "mt_a_cross_group_phrase_hits": 1,
  "mt_a_phrase_hits": 2,
  "mt_b_as_mt_a_hits": 0,
  "mt_b_context_hits": 1,
  "mt_greek_groups": 2,
  "multi_form_groups": 1,
  "ordered_adjacent_groups": 1,
  "reference_genesis_1_1_groups": 1,
  "reference_mt_b_genesis_1_2_hits": 1,
  "reference_wrong_source_book_groups": 0,
  "reversed_greek_order_groups": 0,
  "source_documents": 2,
  "source_scoped_groups": 1
}
```

The exact result schema and values are checked by
[the clean-process regression](../tests/test_researcher_quickstart.py).
The temporary materialized module is deleted before the script exits.
The output keys are **counts** of source documents, groups or hits, not
the returned alignment records themselves.

## Examine the evidence and negative controls

The fixture contains three independent source alignments under the synthetic
`Gen 1:1` header in `01.Genesis.par`:

| MT-A | Greek | Editorial relationship |
| --- | --- | --- |
| `MLK DBR` | `BASILEU/S LOGOS` | One multi-element alignment group |
| `MLK` | `QEOS` | A different alignment group |
| `DBR` | `LOGOS` | A third alignment group |

The same source also has synthetic `Gen 1:2` containing a tentative
reconstructed column-B value `=;W/KL` and Greek `LOGOS`. The separate
`06.JoshB.par` source contains another `MLK`/`BASILEU/S` group.

First, `find_aligned_groups(api, "MLK", "BASILEU/S")` yields **2** groups
across the two source documents. Adding
`source="01.Genesis.par"` yields **1**. A correct finding should cite the
source filename, the CATSS source-header coordinates and the returned stable
`alignment_id` for each group. In the native Text-Fabric features these
come from `catss_source`, `book`/`chapter`/`verse` and
`catss_alignment_id`. Unlike numeric Text-Fabric node IDs, the source and
alignment identifiers can be used in a reproducibility note for the same
source snapshot.

Second, the following conjunction needs *all four exact spellings in one
alignment group*, not merely in one verse:

```python
from catss_tf import find_groups_with_all_forms, find_groups_with_ordered_forms

groups = tuple(
    find_groups_with_all_forms(
        api,
        mt_forms=("MLK", "DBR"),
        lxx_forms=("BASILEU/S", "LOGOS"),
        source="01.Genesis.par",
    )
)
ordered = tuple(
    find_groups_with_ordered_forms(
        api,
        mt_forms=("MLK", "DBR"),
        lxx_forms=("BASILEU/S", "LOGOS"),
        adjacent=True,
        reference=("Gen", 1, 1),
    )
)
```

Both yield **1**. The ordered query checks distinct consecutive positions
on each side of *one* group. It does not establish which specific Greek
element translates which Hebrew one. A request with Greek order reversed
(`LOGOS`, `BASILEU/S`) yields **0**.

Third, `QEOS` and `LOGOS` coexist under `Gen 1:1` but in *different*
groups, so the same-group Greek-only AND query yields **0**
(`false_cross_group_matches`). Filtering `01.Genesis.par` by
`reference=("JoshB", 1, 1)` yields **0**
(`reference_wrong_source_book_groups`), even though `JoshB` has
a matching pair. This exact `reference` tuple denotes a **CATSS source
header**, not a resolved Greek target verse or an arbitrary range.

The source-side phrase query asks a different question.
`find_source_phrase_matches` finds two MT-A occurrences of `MLK DBR` in
Genesis 1:1, one inside a group and one across groups. The Greek
`QEOS LOGOS` phrase has one cross-group occurrence, despite the same-group
conjunction above yielding zero. The adjacent `LOGOS` spellings on
opposite sides of the Genesis 1:1/1:2 header boundary yield zero phrase
hits. These four counts are produced by the same executable demo;
see [the phrase recipe](researcher-cookbook.md#10-find-a-source-side-phrase-across-consecutive-editorial-alignments)
for per-token provenance. Exact source-side adjacency does not establish
continuous manuscript attestation or a bilingual translation edge.

Finally, `find_mt_b_raw_matches(api, "W/KL", retro_kind="context")`
finds **1** raw reconstructed Hebrew context. The same `W/KL` searched as
MT-A through `find_aligned_groups(api, "W/KL", "LOGOS")` yields **0**
(`mt_b_as_mt_a_hits`). The MT-B occurrence is **not a manuscript
attestation** or a lexical `mt_element`.

## Inspect a hit's provenance yourself

The demo's `api` exists **inside** `run_demo()` in
[the executable source](../examples/canonical_research_walkthrough.py).
To see individual matches instead of the summary, insert the following
snippet immediately after the `api = Fabric(...).loadAll(...)` statement
and before `return`, then rerun the script:

```python
import sys
from catss_tf import find_aligned_groups

for group in find_aligned_groups(api, "MLK", "BASILEU/S", source="01.Genesis.par"):
    print(
        group.source,
        group.book,
        group.chapter,
        group.verse,
        group.alignment_id,
        group.mt_elements,
        group.lxx_elements,
        file=sys.stderr,
    )
```

This writes the provenance and ordered element tuples to stderr while
preserving stdout as JSON. It reads the *same loaded standalone TF warp*
used by the tested script. Do not copy numeric TF node IDs between separate
`catss`, `catss-bhsa` (BHSA) and `catss-lxx` (LXX) artifacts.

## What the result can support

For a real scholarly analysis, replace the synthetic inputs with your
authorized, authenticated **46-file** CATSS source snapshot, validate and
materialize it via the
[canonical corpus guide](canonical-corpus.md), and repeat the exact-source
spellings and queries. Record the source snapshot identity, file,
source-header coordinates and `catss_alignment_id`, and inspect raw editorial
notation using the [notation dictionary](notation-reference.md).
A matching group supports editorial **co-membership**, **not a word-to-word**
translation, full Libronix search parity, Greek-versification target mapping,
or validation of BHSA/LXX parent projections. See the
[Libronix two-product crosswalk](libronix-coverage.md),
[parent integration boundaries](integration.md) and
[researcher cookbook](researcher-cookbook.md).

This case study itself does **not** constitute a fresh-independent-agent
walkthrough or a licensed pinned-parent end-to-end run. Those gates remain
open in [#151](https://github.com/alexsosn/CATSS-TF/issues/151) and
[#126](https://github.com/alexsosn/CATSS-TF/issues/126).
