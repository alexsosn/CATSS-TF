# #137 — Query Sirach witness annotations from native Text-Fabric

## Research
The canonical compiler (src/catss_tf/canonical_materializer.py) writes one native TF **annotation** node per parsed CATSS annotation, with features catss_kind, catss_side, catss_raw, catss_payload. Each annotation owns its source **alignment slot** in oslots. The alignment slot owns catss_source, catss_alignment_id, book/chapter/verse. MT-A and LXX lexical element nodes have catss_text/catss_index and the same slot. Reuse that warp: never introduce new node types or reverse foreign corpus node IDs.

notation.py provides book-sensitive witness numbers 1..10 as sirach_witness_* kinds, and >n is a separate kind sirach_reading_lacking_in_witness with payload n. A label in an alignment does **not** identify which MT word or reconstructed reading it modifies. Keep marker vs lacking and mt_a vs mt_b distinct in the result. Do not infer witness attestation of any individual text element.

Empirical basis (full 46-file audit from #133/#135): 8,119 typed Sirach witness markers, 254 Masada (7) markers, 92 total lacking-in-witness (>n) markers. These are counts of annotation occurrences, not verses or unique manuscript readings. MT-A numeric witness pseudo-words were fixed in #135; query only the typed annotations.

## Plan
1. RED-first user materialization+TF reload fixtures; public function imported but not implemented. Check specific witness/mode/side, MT-B marker without false MT-A, multiple markers per group, unchanged raw payload and full ordered group membership, negative sources and wrong warp.
2. GREEN minimal helper in src/catss_tf/query.py, export public API from __init__.py, no deps or extra index. Scan native catss_kind feature entries (linear; no false indexing claim), match annotation node type, kind/payload, exact 27.Sirach.par and source column, follow L.d(annotation, otype='alignment'); yield per annotation occurrence. Make ordering deterministic by source slot+annotation node.
3. Document a short researcher example and its non-pairwise, non-reading-specific boundaries.
4. Run Python 3.11-3.13, Context-Fabric, release, 46-file canonical+Agora acceptance. Add full-data query smoke checking 254 witness 7 occurrences on the loaded canonical module against independent source audit count.
5. Separate final-head skeptical review: validate no invented witness-to-word association, leakage across MT-B/MT-A or documents, truth of negative markers and licensed data boundary. No merge before green.

#132 stays open for source-grounded manuscript-to-specific-reading relations; #137 does not assert them.
