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

Existing convenience features such as `catss_doublet`, `catss_distributive`, and `catss_repetition` remain available where already defined. The `catss_sem_*` namespace is the complete semantic interface.

## Scope

The two modules never use foreign parent node IDs. Hebrew/Aramaic-side notation is projected to resolved BHSA nodes; Greek-side notation is projected to resolved LXX nodes. Corresponding material across the two independent TF node spaces is joined by the stable `catss_alignment_id`.

An annotation is not inferred from BHSA or LXX morphology. It reports CATSS's analysis. CATSS-TF preserves the distinction between source evidence and derived convenience features.

When one parent node participates in two CATSS memberships, lane 2 uses the normal `_2` suffix, including semantic and payload features.

## Relations and alignment-level phenomena

Cross-language Hebrew↔Greek relations cannot be TF edges because BHSA and LXX are separate warps with unrelated node spaces. Query both modules by `catss_alignment_id` to join them.

Within a projection, CATSS-TF uses resolved parent nodes and the alignment membership features. A semantic annotation is attached only to the source side on which CATSS records it. Provenance sidecars retain exact one-to-many source records but are not the semantic query API.

## Sirach

Sirach has a book-specific notation profile. In particular `*` means an uncertain/fragmentary letter, not the general CATSS asterisked-passage meaning; `[..]` is a Sirach lacuna/illegibility marker. Witness numbers and manuscript-addition/lacuna notation are decoded separately. Researchers should therefore query the resulting semantic kind rather than interpret the raw glyph globally.

## Complete-snapshot audit\n\nRun `catss-tf validate --complete PATH` for the release gate. The command refuses a partial or extra-file snapshot before parsing, then normal validation requires zero unresolved/unknown notation unless the researcher explicitly supplies an `--allow` code. A partial directory is therefore useful for exploration but cannot produce the project’s zero-unknown completion claim.\n\n## Fail-closed behavior

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
