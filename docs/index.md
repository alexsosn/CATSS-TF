# CATSS-TF: researcher's starting point

CATSS-TF lets you inspect **editorial Hebrew/Aramaic–Greek alignment groups** from a user-authorized CATSS/CCAT parallel source snapshot. Start with the **synthetic, corpus-download-free** walkthrough below before attempting licensed data or parent projections. CATSS alignment co-membership is not a word-to-word translation link.

## Choose the artifact before querying

| Research question | Artifact | First step |
| --- | --- | --- |
| Which exact MT-A and Greek spellings occur in the same CATSS editorial alignment? | Standalone `catss`, with **alignment slots** | [Runnable canonical walkthrough](../examples/canonical_research_walkthrough.py) and [cookbook](researcher-cookbook.md) |
| What does a Qere/Ketiv or Sirach witness marker actually annotate? | Standalone `catss` annotation and lexical nodes | [Runnable annotation walkthrough](../examples/annotation_evidence_walkthrough.py) and [notation dictionary](notation-reference.md) |
| Which source alignments remain unclassified, and why? | Standalone `catss` technique status and source provenance | [Runnable unresolved-evidence walkthrough](../examples/unclassified_evidence_walkthrough.py) |
| How do CATSS alignments relate to BHSA Hebrew nodes? | `catss-bhsa` **features on BHSA parent nodes** | [Integration and parent requirements](integration.md) |
| How do CATSS alignments relate to LXX Greek nodes? | `catss-lxx` **features on LXX parent nodes** | [Integration and known JoshB limit](integration.md) |
| What can I reproduce from the two Libronix CATSS products? | Source-backed queries, **not** Libronix UI | [Libronix coverage crosswalk](libronix-coverage.md) |

The three artifacts do not share numeric node IDs. The canonical `catss` warp has `alignment` slots, while `catss-bhsa` and `catss-lxx` add features to independently pinned parent warps. Never pass a parent TF API to a canonical alignment-slot query.

## First session: no licensed corpus required

Use a clean Python 3.11–3.13 checkout. The `[tf]` extra enables native Text-Fabric loading. Installing dependencies may require network access, but the scripts do not fetch licensed corpora:

```sh
python -m pip install -e ".[tf]"
python examples/canonical_research_walkthrough.py
python examples/annotation_evidence_walkthrough.py
python examples/unclassified_evidence_walkthrough.py
```

Each script creates invented source lines, materializes native `catss`, reloads the resulting Text-Fabric corpus and prints a JSON summary. The source and output are temporary. Counts are **synthetic smoke expectations**, not historical corpus frequencies. Run these commands from the repository checkout. For a detailed explanation of each query and its false-positive boundaries, follow the [step-by-step researcher cookbook](researcher-cookbook.md).

In native Text-Fabric, a **slot** is the atomic unit of the corpus warp, a **node** is a typed entity such as `mt_element` or `annotation`, and a **feature** stores a value or relationship. In canonical CATSS, an `alignment` slot records editorial grouping, not a lexical equivalence. `catss_mt_col_b` is tentative reconstructed Hebrew context, not an attested MT-A word. Preserve `catss_source`, source line numbers and `catss_alignment_id` when reporting evidence.

## From synthetic example to authorized source research

1. Acquire the licensed `46-file` CCAT `.par` source snapshot yourself. Use only independently authenticated HTTPS/CA or user-authorized local files. Follow [source acquisition and validation](integration.md). Do not commit source rows or generated corpora.
2. Build and reload standalone `catss` using the commands in [canonical corpus materialization](canonical-corpus.md). Inspect the exact `catss_text` spelling in your own data before substituting query forms. The examples do not normalize Greek/Hebrew spelling.
3. Run source-scoped, source-header-reference-scoped and same-group searches from the [cookbook](researcher-cookbook.md). Verify the `catss_source` and `catss_alignment_id` provenance. Do not infer an individual Greek-to-Hebrew word link from co-membership.
4. Decode editorial signs using the [notation dictionary](notation-reference.md), then inspect the [TF feature and API dictionary](tf-feature-reference.md). The same raw sign may mean different things in general CATSS and Sirach.
5. For interactive exploration, use the [standard Text-Fabric browser](browser.md). For an external host, the [Agora materializer](../agora.materializer.json) currently advertises standalone `catss` only. An executable manifest is **not** proof of installation in Agora.
6. Only if you have the separately pinned BHSA 2021 and CenterBLC/LXX 1935 parents, follow [parent projection setup](integration.md). The strict LXX projection is constrained by the JoshB lettered-subverse mismatch. A successful standalone build does not establish parent E2E compatibility.

## Troubleshooting and interpretation

| Symptom | Check |
| --- | --- |
| A query returns no hits | Confirm the native `alignment`-slot warp, loaded features, exact case-sensitive `catss_text` spelling, source filename and native CATSS header reference. A Greek reference annotation is not a source header. |
| A marker or optional feature is absent | Sparse TF features may be omitted when no node supplies a value. Consult [feature semantics and nulls](tf-feature-reference.md). Do not interpret a missing feature as negative manuscript evidence. |
| CCAT fetch fails TLS verification | Supply an independently authenticated CA or local authorized snapshot. Never disable TLS verification. See [integration](integration.md). |
| Parent projection cannot map a Greek subverse | Check the exact LXX parent version and [JoshB issue #96](https://github.com/alexsosn/CATSS-TF/issues/96). Do not invent target nodes. |
| Libronix phrase search, pop-up or witness-to-word link has no matching query | See the [two-resource coverage matrix](libronix-coverage.md). The missing semantic capabilities are tracked in [#126](https://github.com/alexsosn/CATSS-TF/issues/126) and [#132](https://github.com/alexsosn/CATSS-TF/issues/132). |

## Verification and release boundary

The CI checks the complete canonical 46-file source-to-native-TF readback and the standalone Agora adapter. Synthetic examples test public query behavior without redistributing licensed text. A **fresh-reader complete workflow** and authorized **pinned-parent BHSA/LXX end-to-end smoke** are **not yet verified**. The current published `v0.1.0` wheel predates unreleased source changes. Do not infer feature parity or new release availability from passing standalone tests.

For outstanding acceptance criteria, see [researcher onboarding #151](https://github.com/alexsosn/CATSS-TF/issues/151), [full documentation #149](https://github.com/alexsosn/CATSS-TF/issues/149), and [Libronix parity #126](https://github.com/alexsosn/CATSS-TF/issues/126).
