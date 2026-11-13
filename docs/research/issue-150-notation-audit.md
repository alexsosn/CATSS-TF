# #150 — source audit of the researcher notation dictionary

Snapshot: main `973a9026b840bf6663379814caf6153e4d163203` (2026-11-13). Documentation child of #149, semantics user-workflow parent #126.

## Verified model evidence

- `src/catss_tf/notation.py` defines **86 general catalogue rows** and **16 Sirach-specific rows**, hence **102 profile-specific glyph entries** (100 distinct spellings) plus the patterned Samaritan `<sp…>` reference. The same `*` and `[..]` have *different* general and Sirach meanings; conflating rows by literal spelling loses two semantic kinds. The general inventory includes **16** exact `I:...` patterns.
- `documented_specs()` merges `_GENERAL` / `_SIRACH` by raw glyph and loses the two general collision meanings. Use `documented_semantic_specs()` (kind-keyed) or a separate **profile+raw** catalogue for a complete dictionary. Do not derive the glossary from a raw-key-only dictionary.
- `src/catss_tf/tf_schema.py` `FEATURE_SPECS` declares parent-projection semantic flags `catss_sem_<kind>`, plus optional `_payload`, scoped `_mt_a`/`_mt_b`/`_lxx` variants and membership `_2` lanes. The exact semantic kind inventory is broader than the source glossary (raw parser-generated kinds); the docs must not claim that a source notation catalogue alone exhausts overlay TF features.
- The canonical standalone writer `src/catss_tf/canonical_materializer.py` creates `annotation` nodes with `catss_kind`, `catss_family`, `catss_raw`, `catss_payload`, `catss_side` and `catss_contextual`. It **does not emit** parent-projection `catss_sem_*` features onto canonical nodes. A parent semantic flag is not a word-specific manuscript attestation; a source-positioned annotation can remain unscoped.
- `docs/special-notation.md` explains semantic families and null/limit cases, but does not list every general/Sirach glyph with exact kind, family, payload indicator and available TF location. The full 46-file audit with zero unknown annotations is an empirical parser finding, not proof of Libronix equivalent UI/semantics.

## Narrow first PR scope

Write an accessible *complete catalogue* of all **102** profile+glyph entries and the dynamic Samaritan `<sp…>` pattern, with distinct general-vs-Sirach meanings, family, contextuality, the exact annotation-node kind and corresponding declared parent projection semantic feature. Keep the table static/legible, machine-check it against source code to prevent drift. Include reproducible Python recipes for looking up a glyph and inspecting canonical annotation nodes; distinguish raw source notes, parent projection flags, missing scopes and manuscript evidence.

The **separate full canonical/overlay feature dictionary** remains a follow-up in #150; `docs/canonical-corpus.md` and `docs/special-notation.md` already offer the deeper feature model and will be linked explicitly. Do not call this scoped slice completion of #150.

TDD gates: source-code-driven test added before the page exists, observe missing-page RED in CI, author page/links, run exact-head Python+release+Context-Fabric+46-file corpus/Agora, independently adversarial review final diff before merging. No corpus text in git.
