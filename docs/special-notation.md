# CATSS special notation: researcher guide

CATSS-TF decodes CATSS special notation into query-native Text-Fabric features while preserving the exact source notation for provenance.

## What researchers query

Every decoded semantic kind has a canonical boolean node feature named `catss_sem_<kind>`. A value of `1` means that CATSS assigns that semantic annotation to the alignment material mapped to the parent word node. Context-bearing notation additionally receives `catss_sem_<kind>_payload`.

Examples:

- `catss_sem_distributive=1` — CATSS marks distributive rendering.
- `catss_sem_distributive_payload` — the contextual payload preserved from the raw CATSS notation.
- `catss_sem_active_to_passive=1` — active/passive shift.
- `catss_sem_inf_abs_rendered_participle=1` — one documented infinitive-absolute rendering.
- `catss_sem_samaritan_partial_match=1` — partial agreement with the Samaritan Pentateuch.
- `catss_sem_lxx_conjectural_emendation=1` — LXX conjectural emendation.
- `catss_sem_sirach_uncertain_fragmentary_letter=1` — Sirach-specific meaning of `*`.

Existing convenience features such as `catss_doublet`, `catss_distributive`, and `catss_repetition` remain available where already defined. Column-B reconstruction strategy also remains available categorically as `catss_retro_kind`; non-plain raw strategies are additionally projected into the complete `catss_sem_*` interface, scoped to `_mt_b` (for example `%vap` → `catss_sem_active_to_passive_mt_b=1`). The `catss_sem_*` namespace is therefore the complete boolean semantic interface.

## Scope

The two modules never use foreign parent node IDs. Hebrew/Aramaic-side notation is projected to resolved BHSA nodes; Greek-side notation is projected to resolved LXX nodes. Corresponding material across the two independent TF node spaces is joined by the stable `catss_alignment_id`.

An annotation is not inferred from BHSA or LXX morphology. It reports CATSS's analysis. CATSS-TF preserves the distinction between source evidence and derived convenience features. On BHSA, `catss_sem_<kind>_mt_a` and `catss_sem_<kind>_mt_b` preserve whether the notation came from the MT column or reconstructed-Hebrew column; on LXX, `catss_sem_<kind>_lxx` preserves Greek-side scope. The unsuffixed `catss_sem_<kind>` remains the convenient projection-local union. Payloads likewise have scoped forms such as `catss_sem_<kind>_mt_a_payload`; the unsuffixed payload is emitted only when the payload is unambiguous across the projected source scopes.

When one parent node participates in two CATSS memberships, lane 2 uses the normal `_2` suffix, including semantic and payload features.

## Relations and alignment-level phenomena

Cross-language Hebrew↔Greek relations cannot be TF edges because BHSA and LXX are separate warps with unrelated node spaces. Query both modules by `catss_alignment_id` to join them.

Within a projection, CATSS-TF uses resolved parent nodes and the alignment membership features. A semantic annotation is attached only to the source side on which CATSS records it. Provenance sidecars retain exact one-to-many source records but are not the semantic query API.

## Contextual Greek reference ranges

CATSS occasionally uses double-bracketed Greek references rather than Greek lexical
tokens. The JoshB 9:2 structural record has MT provenance
`{...} <8.30-35>` and Greek reference range `[[9.2a-2f]]`. Its typed
`lxx_reference_ranges` record preserves the inclusive endpoints **9:2a–9:2f**,
the exact raw spelling, and the shared `catss_alignment_id`. It has no Greek
or Hebrew lexical tokens; the reference is not a translation word pair.

Where a compatible LXX parent actually provides six *distinct* and correctly
labeled subverse nodes, the optional `catss_lxx_reference_range_*` features
encode member ordinal/count, both endpoints, the CATSS alignment ID and raw range.
They are attached to existing parent nodes, without changing the TF warp.

**Current pinned-parent limitation:** CenterBLC/LXX `1935` at
`f32a98eddf7eb239aa73ab863d70381e416d5076` has only **one
unlabeled subverse node (630920)** for Josh 9:2, covering 191 words.
Consequently `a` through `f` cannot be resolved to distinct parent nodes.
The LXX resolver reports `missing_lxx_reference_range_member`; the
materializer refuses publication rather than silently dropping this evidence,
reusing one node six times or inventing parent word/subverse nodes.

The standalone canonical CATSS corpus is the proper place for a first-class
reference-range node even when the parent LXX cannot represent the targets.
Canonical integration is tracked in #40 / PR #47; the range projection
behavior is in #88 / PR #89. Do not interpret conditional range features as
currently available for this pinned Joshua passage.

## Sirach

Sirach has a book-specific notation profile. In particular `*` means an uncertain/fragmentary letter, not the general CATSS asterisked-passage meaning; `[..]` is a Sirach lacuna/illegibility marker. Witness numbers and manuscript-addition/lacuna notation are decoded separately. Researchers should therefore query the resulting semantic kind rather than interpret the raw glyph globally.

## Complete-snapshot audit\n\nRun `catss-tf validate --complete PATH` for the release gate. The command refuses a partial or extra-file snapshot before parsing, the issue-38 corpus gate requires `source_files=46`, `unaccounted_lines=0`, and `unknown_annotations=0`. General parser diagnostics (for example malformed physical continuations or legacy LXX-reference syntax) remain reported by `validate` and can still make its process exit non-zero, but they are not silently reclassified as notation. A partial directory is useful for exploration but cannot produce the project’s zero-unknown notation claim.\n\n## Empirical corpus gate

CI audits the complete configured upstream CATSS snapshot without committing or publishing the source data. The current corpus gate covers 46 files and 349,908 alignment records, requires every source data line to be accounted for, and requires `unknown_annotations=0`. Corpus-discovered forms extend the documented glossary conservatively: bracketed `c...` readings are Greek corrections; `{**?}` is possible Greek agreement with Qere; `{=number}` and dotted bracket forms such as `[v.8]` are contextual references; uppercase Beta-Code brace payloads are contextual Greek readings; and `{!}na+` is represented as `inf_abs_accusative_without_mt_inf_abs`.

The complete notation gate is intentionally narrower than the general structural validation report. The upstream files also contain legacy line-layout anomalies (for example continuation and unsplit-row diagnostics) tracked by the parser; those remain visible and fail ordinary validation unless explicitly handled, but they cannot hide or waive unknown notation in the complete-snapshot gate.

## Fail-closed behavior

Unknown notation is not mapped to `other` and is not silently discarded. Validation reports it as unresolved. A complete-snapshot audit requires all configured CATSS parallel files; a partial directory cannot establish zero unknown notation.

The raw annotation and its source line remain available in provenance TSV files for verification and round-trip inspection.

## Example

After loading a generated module with Text-Fabric, ordinary feature access works:

```python
F.catss_sem_distributive.v(node)
F.catss_sem_distributive_payload.v(node)
F.catss_alignment_id.v(node)
```

To compare the corresponding Hebrew and Greek evidence, read `catss_alignment_id` in one projection and locate the same value in the other projection. Do not compare BHSA and LXX node numbers directly.

## Semantic families

The closed catalogue covers alignment status; reconstruction; transposition; segmentation; translation technique; prepositions; Qere/Ketiv; textual criticism; Samaritan comparison; grammatical labels; infinitive-absolute renderings; contextual references; and the Sirach manuscript/witness profile.

The source-derived inventory and raw encoding notes are documented in [research-38-catss-notation.md](research-38-catss-notation.md).
