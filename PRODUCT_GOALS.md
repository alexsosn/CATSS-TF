# Product goals — CATSS-TF

## Users and purpose

Septuagint and Hebrew Bible textual researchers should be able to investigate the CATSS Hebrew/Aramaic–Greek alignment as a standalone TF dataset and, where attested, as native feature modules over exact BHSA and CenterBLC/LXX parent corpora.

## Representative research journeys

1. Find a Hebrew/Greek editorial alignment by book and source reference and inspect both source sides without losing their original order.
2. Query multi-token forms, plus/minus readings, transpositions and segmentation **inside the same alignment**, not through unrelated co-occurrences.
3. Distinguish physical empty alignment cells, uncertain or unclassified tokens, Qere/Ketiv and source-specific editorial notation.
4. Follow an evidenced alignment to BHSA and LXX nodes where the parent/version permits it, with explicit unresolved and unmatched cases.
5. Reproduce a textual comparison or translation-technique case study using documented TF searches and interpretable provenance.

## Minimum usable release

A researcher can install the published converter, obtain authorized CATSS source data, materialize the standalone corpus and applicable parent overlays, execute documented real-source queries and interpret the limitations. The existing 0.1.0 release is a starting point, not a claim of complete Libronix parity. A first-time-user cookbook and an honest, tested feature/siglum reference are part of usability.

## Boundaries and next focus

CATSS owns alignment identities and semantics; parent corpora retain their warp and linguistic annotations. No proprietary source redistribution or invented lexical alignments. Prioritize documented real-data researcher workflows and completion of meaningful Libronix coverage checks (issues #126/#149/#151), not new general-purpose download, certification or publication frameworks.

## Autonomous-development decision rules

- Select work by the researcher journeys above, not issue count or the ease of adding tests. Prefer finishing active PRs and releases over opening new tickets.
- Before introducing a new adapter, workflow, registry, protocol, or validation layer, demonstrate that an existing mechanism cannot meet a concrete acceptance need.
- Preserve source fidelity, access controls, security, and applicable upstream rights. Do not invent inferred text or silently weaken correctness gates.
- Batch repetitive data changes and reuse parameterized tests. Keep independent adversarial review proportional to risk, and validate the actual researcher path.
- If two successive cycles do not advance a journey or remove an observed blocker, reconsider the approach. Stop when the scoped deliverable works instead of generating optional infrastructure work.
