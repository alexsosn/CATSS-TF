# #132 — Sirach witness attribution: preliminary code research and empirical plan

## Starting point (main 9b5a917, 2026-10-20)

The source-level parser exposes `Annotation(side, kind, raw, payload)`, and canonical TF materializes all annotations under their owner **alignment slot**. A standalone Sirach witness number (1–10) is typed `sirach_witness_*`; `>n` is `sirach_reading_lacking_in_witness` with numeric payload; manuscript additions and lacunae have independent kinds. No `target_side=mt,target_index=...` is supplied by this branch of the parser.

**Do not infer lexical reading attribution from a mere annotation being on the same alignment**, even if the group currently has one MT element. The number may refer to a whole reading, marginal intervention, a source variant or a column-level textual situation. A guessed edge would contaminate textual-critical results.

Code risk points to check against the real `27.Sirach.par`:
- standalone 1–10 markers are recognized only with whitespace boundaries;
- `>n` lacks an end-of-token boundary in the current regex, so strings such as `>12` would match a partial `>1`. Do not change this without source and notation evidence;
- `[...]`, `*`, `{{...}}`, `{n}`, `>n` and multiple witness labels can coexist;
- MT-B and Greek columns can carry independent annotations; column ambiguity matters;
- source physical continuations can span multiple lines in one logical alignment.

## Empirical research stage

Run a **read-only** audit over the already-acquired, temporary Sirach source in the existing 46-file CI job (no extra fetch, no artifacts). Emit only aggregated counts and bare identities `chapter:verse@line`, never source cells, lexical text or generated TF datasets. Record:
- total alignments, per-witness marker counts and side counts;
- `>n`, manuscript additions, reconstruction, lacuna, uncertain letters;
- multiple witness markers in a group, markers with multiple MT tokens or zero MT tokens, MT-B-bearing rows and continuations;
- overlap between witness declarations and absence/lacunae;
- limited reference samples for each shape, especially 19:14 for #60.

Synthetic unit fixtures assert the audit's counts and metadata-only outputs, without assuming any word-level edge. After the CI data are inspected, decide whether a second **behavior** ticket can safely add query-native links, or should instead expose typed *alignment-level* witnesses with explicit unresolved reading scope.

## Gates

Research + plan here → RED-first synthetic test for the bounded research audit → audit implementation → Python/ruff/mypy/release + 46-file source gate → independent skeptical final-head review. Research PR must not silently redefine any CATSS siglum or change canonical materialization.
