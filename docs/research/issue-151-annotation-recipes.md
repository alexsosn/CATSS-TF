# #151 phase 2 — real parser contracts for annotations and textual witnesses

Baseline `f1c47b2682805829a1587da693e4446c8bad05d7`, researched 2026-11-13. This extends the merged synthetic native TF researcher demo without changing the parser or schema.

## Grounding

- `tests/test_parser.py::test_parse_ketiv_and_qere_independently` proves source surface `*HBK **HBQ\tGR` yields MT lexical primary `HBK`, separate Ketiv `HBK` and Qere `HBQ`, a single MT lexical element and explicit qere/ketiv flags. `canonical_materializer._add_detail_nodes` saves these separately on `mt_element` nodes as `catss_text`, `catss_ketiv_text`, `catss_qere_text`. The same row does not imply an LXX witness or a word translation.
- `tests/test_parser.py::test_sirach_mt_manuscript_markup_is_not_silently_dropped` confirms `Sir 2:13\n[..] 3\tOU)AI\\\n[BN]* >7\tLOGOS\n` creates annotation nodes for Sirach witness 3, Sirach lacuna, fragmentary letter and a `>7` reading-lacking marker. `test_sirach_brace_manuscript_markup_keeps_raw_and_witness_payload` separately covers brace additions; do not treat the braces as direct manuscript attestation links.
- `find_sirach_witness_annotations(api, witness, mode="marked"/"lacking", side="mt_a"/"mt_b")` returns **annotation occurrences** with source, alignment ID, original source side/raw/payload and containing MT-A/Greek group. In production it explicitly rejects manuscript-word inference; source 27.Sirach.par only, no foreign parent node edges.
- `canonical_materializer` preserves the literal `catss_raw`, `catss_kind` and source on typed `annotation` nodes, and the source line on `source_line`. `catss_annotation_target` exists only for *explicitly targeted Greek lexical elements*, not for all annotations.
- The existing merged [researcher cookbook](../researcher-cookbook.md) demonstrates exact group queries and raw MT-B with a synthetic first-reader subprocess E2E; a Qere/Ketiv and Sirach witness/uncertain evidence recipe remains missing. Source-level proof is from existing parser tests, not invented manuscript data.

## Next limited deliverable

Add a **separate** `examples/annotation_evidence_walkthrough.py` and a new cookbook section. It writes only synthetic `01.Genesis.par` for `*HBK **HBQ` and `27.Sirach.par` for independently tested witness/lacuna/reading-lacking source shapes, materializes standalone TF, prints deterministic JSON counts + source-scope/bare witness negative controls. A standalone subprocess test runs it in a clean working directory and checks output and missing artifacts. The guide explains exact annotation query semantics and provenance and links #132 for uncertain reading attribution.

No need to expand the core API, release a parser or introduce new test infrastructure. The full 46-file native TF/Agora check remains a separate actual-source gate; a clean full pinned-parent BHSA/LXX E2E remains blocked for #41/#96 and must not be claimed here.
