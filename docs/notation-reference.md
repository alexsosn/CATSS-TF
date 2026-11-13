# CATSS notation dictionary: source symbols and Text-Fabric meanings

This is the **complete declared, book-aware exact-symbol catalogue** implemented
by [`catss_tf.notation`](../src/catss_tf/notation.py), not an assertion that every
symbol occurs in every source, that every editorial inference is correct, or
that Libronix's UI or full-text indexes have been reproduced. The table is
checked against the source catalogue by `tests/test_docs_notation_reference.py`.
It covers **86 general entries**, **16 Sirach-specific entries**, and one
patterned Samaritan-apparatus reference. Two source spellings have different
meanings depending on the text (`*`, `[..]`).

Start with the [researcher guide](special-notation.md) for annotation scope
and [canonical corpus guide](canonical-corpus.md) for TF node types; consult
[Libronix coverage](libronix-coverage.md) for product-level limitations.

## Reading the table

- **Source notation** is the documented symbol or marker. It is not a
  Unicode-normalized lemma and may be parsed with surrounding context; a
  documented glyph is not a promise of a one-to-one raw string occurrence.
- **Plain meaning** is a short explanation of the declared catalogue kind,
  not a philological judgment about an individual verse.
- **Family** groups related editorial operations; **Context payload = yes**
  means the catalogue allows a contextual explanation or source reference,
  *not* that a payload is present for every occurrence.
- **Canonical annotation kind** is the string stored on a standalone
  `annotation` node in `catss_kind` when the parser recognizes that
  annotation. Its original token is in `catss_raw`, its side in
  `catss_side` and contextual source note, where supplied, in
  `catss_payload`; absent values must not be fabricated.
- **Parent semantic feature** is a declared *projection* feature in
  `catss-bhsa` or `catss-lxx`: `catss_sem_<kind>` on matched parent
  word nodes, with optional scoped `_mt_a` / `_mt_b` / `_lxx` and
  `_payload` variants. A second membership lane uses
  `catss_sem_<kind>_2` (and the corresponding scoped/payload suffixes).
  A feature can be declared but **absent** from a particular materialized
  module or have no value for an individual node.
- The standalone `catss` corpus stores annotation nodes and source
  provenance. It **does not have** the parent-word
  `catss_sem_<kind>` feature vocabulary on its alignment slots.
  Parent BHSA/LXX node identifiers cannot be substituted for canonical
  alignment node identifiers.

## Declared symbols, by profile

The **General** profile applies unless a book-specific override exists.
The **Sirach** profile applies when `book="Sir"`. This is a reference
catalogue of supported *glossary kinds*, not a corpus-frequency report.

| Profile | Source notation | Plain meaning | Family | Context payload | Canonical annotation kind | Parent semantic feature |
| --- | --- | --- | --- | --- | --- | --- |
| General | `-` | Greek material marked as absent relative to MT | `alignment` | no | `lxx_minus` | `catss_sem_lxx_minus` |
| General | `??` | Possible Hebrew variant no retroversion | `reconstruction` | no | `possible_hebrew_variant_no_retroversion` | `catss_sem_possible_hebrew_variant_no_retroversion` |
| General | `[..]` | Unreadable passage or Greek addition in the general apparatus | `textual` | no | `unreadable_or_greek_addition` | `catss_sem_unreadable_or_greek_addition` |
| General | `[ce]` | Conjectural emendation of the Greek reading | `textual` | yes | `lxx_conjectural_emendation` | `catss_sem_lxx_conjectural_emendation` |
| General | `[z]` | Ziegler preferred variant | `textual` | yes | `ziegler_preferred_variant` | `catss_sem_ziegler_preferred_variant` |
| General | `{+?}` | Possible Greek omission | `alignment` | no | `possible_lxx_minus` | `catss_sem_possible_lxx_minus` |
| General | `{+}` | Possible Greek addition | `alignment` | no | `possible_lxx_plus` | `catss_sem_possible_lxx_plus` |
| General | `{d}` | Doublet | `translation_technique` | yes | `doublet` | `catss_sem_doublet` |
| General | `{d}tr` | Doublet transposed | `transposition` | yes | `doublet_transposed` | `catss_sem_doublet_transposed` |
| General | `{p}` | Greek preverb | `preposition` | no | `greek_preverb` | `catss_sem_greek_preverb` |
| General | `{t?}` | Uncertain transliteration | `translation_technique` | no | `uncertain_transliteration` | `catss_sem_uncertain_transliteration` |
| General | `{XTM}` | Contextual influence on the Greek translation | `translation_technique` | yes | `contextual_influence` | `catss_sem_contextual_influence` |
| General | `*` | Asterisk marking in general textual apparatus | `textual` | no | `asterisked_passage` | `catss_sem_asterisked_passage` |
| General | `+` | Greek material marked as an addition relative to MT | `alignment` | no | `lxx_plus` | `catss_sem_lxx_plus` |
| General | `<fm` | Gender switch | `translation_technique` | no | `gender_switch` | `catss_sem_gender_switch` |
| General | `<l>` | Greek lexical problem | `textual` | yes | `greek_lexical_problem` | `catss_sem_greek_lexical_problem` |
| General | `~` | Stylistic or grammatical transposition | `transposition` | no | `stylistic_or_grammatical_transposition` | `catss_sem_stylistic_or_grammatical_transposition` |
| General | `abbr` | Possible abbreviation | `reconstruction` | no | `possible_abbreviation` | `catss_sem_possible_abbreviation` |
| General | `act2pas` | Active to passive | `translation_technique` | no | `active_to_passive` | `catss_sem_active_to_passive` |
| General | `ad` | Adverb | `grammatical_label` | no | `adverb` | `catss_sem_adverb` |
| General | `aj` | Adjective | `grammatical_label` | no | `adjective` | `catss_sem_adjective` |
| General | `Ap-` | Apparent minus | `alignment` | no | `apparent_minus` | `catss_sem_apparent_minus` |
| General | `Ap+` | Apparent plus | `alignment` | no | `apparent_plus` | `catss_sem_apparent_plus` |
| General | `App` | Apparent reconstructed Hebrew | `reconstruction` | no | `apparent_reconstructed_hebrew` | `catss_sem_apparent_reconstructed_hebrew` |
| General | `Aram` | Aramaic | `language` | no | `aramaic` | `catss_sem_aramaic` |
| General | `C` | Reconstruction based on context or editorial intuition | `reconstruction` | yes | `contextual_or_intuitive_reconstruction` | `catss_sem_contextual_or_intuitive_reconstruction` |
| General | `C´` | Reconstruction informed by another verse | `reconstruction` | yes | `reconstruction_from_other_verse` | `catss_sem_reconstruction_from_other_verse` |
| General | `div` | Different word division | `segmentation` | no | `different_word_division` | `catss_sem_different_word_division` |
| General | `Dn` | Number difference | `translation_technique` | no | `number_difference` | `catss_sem_number_difference` |
| General | `DR` | Distributive rendering | `translation_technique` | yes | `distributive_rendering` | `catss_sem_distributive_rendering` |
| General | `els` | Parallel elsewhere | `reference` | yes | `parallel_elsewhere` | `catss_sem_parallel_elsewhere` |
| General | `Ety` | Etymological exegesis | `translation_technique` | yes | `etymological_exegesis` | `catss_sem_etymological_exegesis` |
| General | `EtyA` | Aramaic etymological exegesis | `translation_technique` | yes | `aramaic_etymological_exegesis` | `catss_sem_aramaic_etymological_exegesis` |
| General | `g` | Rahlfs Göttingen difference | `textual` | yes | `rahlfs_goettingen_difference` | `catss_sem_rahlfs_goettingen_difference` |
| General | `GTran` | Greek-side transposition, possibly with contextual note | `transposition` | yes | `greek_transposition` | `catss_sem_greek_transposition` |
| General | `HTran` | Hebrew-side transposition, possibly with contextual note | `transposition` | yes | `hebrew_transposition` | `catss_sem_hebrew_transposition` |
| General | `I` | Infinitive absolute | `infinitive_absolute` | no | `infinitive_absolute` | `catss_sem_infinitive_absolute` |
| General | `I:-` | Infinitive absolute: rendered finite verb | `infinitive_absolute` | no | `inf_abs_rendered_finite_verb` | `catss_sem_inf_abs_rendered_finite_verb` |
| General | `I:--` | Infinitive absolute: and main verb omitted | `infinitive_absolute` | no | `inf_abs_and_main_verb_omitted` | `catss_sem_inf_abs_and_main_verb_omitted` |
| General | `I:+` | Infinitive-absolute pattern without MT infinitive absolute | `infinitive_absolute` | no | `inf_abs_without_mt_inf_abs` | `catss_sem_inf_abs_without_mt_inf_abs` |
| General | `I:ad` | Infinitive absolute: rendered finite verb adverb | `infinitive_absolute` | no | `inf_abs_rendered_finite_verb_adverb` | `catss_sem_inf_abs_rendered_finite_verb_adverb` |
| General | `I:aj` | Infinitive absolute: rendered finite verb adjective | `infinitive_absolute` | no | `inf_abs_rendered_finite_verb_adjective` | `catss_sem_inf_abs_rendered_finite_verb_adjective` |
| General | `I:n` | Infinitive absolute: rendered finite verb noun | `infinitive_absolute` | no | `inf_abs_rendered_finite_verb_noun` | `catss_sem_inf_abs_rendered_finite_verb_noun` |
| General | `I:na` | Infinitive absolute: rendered accusative noun | `infinitive_absolute` | no | `inf_abs_rendered_accusative_noun` | `catss_sem_inf_abs_rendered_accusative_noun` |
| General | `I:nad` | Infinitive absolute: rendered different accusative noun | `infinitive_absolute` | no | `inf_abs_rendered_different_accusative_noun` | `catss_sem_inf_abs_rendered_different_accusative_noun` |
| General | `I:nd` | Infinitive absolute: rendered dative noun | `infinitive_absolute` | no | `inf_abs_rendered_dative_noun` | `catss_sem_inf_abs_rendered_dative_noun` |
| General | `I:nd+` | Infinitive absolute: dative without MT inf abs | `infinitive_absolute` | no | `inf_abs_dative_without_mt_inf_abs` | `catss_sem_inf_abs_dative_without_mt_inf_abs` |
| General | `I:ndd` | Infinitive absolute: rendered different dative noun | `infinitive_absolute` | no | `inf_abs_rendered_different_dative_noun` | `catss_sem_inf_abs_rendered_different_dative_noun` |
| General | `I:p` | Infinitive absolute: rendered participle | `infinitive_absolute` | no | `inf_abs_rendered_participle` | `catss_sem_inf_abs_rendered_participle` |
| General | `I:p+` | Infinitive absolute: participle without MT inf abs | `infinitive_absolute` | no | `inf_abs_participle_without_mt_inf_abs` | `catss_sem_inf_abs_participle_without_mt_inf_abs` |
| General | `I:pc` | Infinitive absolute: rendered participle compositum | `infinitive_absolute` | no | `inf_abs_rendered_participle_compositum` | `catss_sem_inf_abs_rendered_participle_compositum` |
| General | `I:pd` | Infinitive absolute: rendered different verb participle | `infinitive_absolute` | no | `inf_abs_rendered_different_verb_participle` | `catss_sem_inf_abs_rendered_different_verb_participle` |
| General | `I:v` | Infinitive absolute: rendered verb | `infinitive_absolute` | no | `inf_abs_rendered_verb` | `catss_sem_inf_abs_rendered_verb` |
| General | `ir` | Incomplete reconstruction | `reconstruction` | no | `incomplete_reconstruction` | `catss_sem_incomplete_reconstruction` |
| General | `join` | MT words joined in LXX parent | `segmentation` | no | `mt_words_joined_in_lxx_parent` | `catss_sem_mt_words_joined_in_lxx_parent` |
| General | `k-` | Qere reading lacking a Ketiv counterpart | `qere_ketiv` | no | `qere_without_ketiv` | `catss_sem_qere_without_ketiv` |
| General | `lo` | Long alignment event | `alignment` | no | `long_alignment_event` | `catss_sem_long_alignment_event` |
| General | `LXX=K` | Greek reading agrees with Ketiv | `qere_ketiv` | no | `lxx_agrees_ketiv` | `catss_sem_lxx_agrees_ketiv` |
| General | `LXX=Q` | Greek reading agrees with Qere | `qere_ketiv` | no | `lxx_agrees_qere` | `catss_sem_lxx_agrees_qere` |
| General | `met` | Metathesis | `segmentation` | no | `metathesis` | `catss_sem_metathesis` |
| General | `n` | Noun | `grammatical_label` | no | `noun` | `catss_sem_noun` |
| General | `npr` | Reconstructed proper noun | `reconstruction` | no | `reconstructed_proper_noun` | `catss_sem_reconstructed_proper_noun` |
| General | `om` | LXX parent omits MT elements | `alignment` | no | `lxx_parent_omits_mt_elements` | `catss_sem_lxx_parent_omits_mt_elements` |
| General | `pa` | Passive to active | `translation_technique` | no | `passive_to_active` | `catss_sem_passive_to_active` |
| General | `pass2act` | Passive to active | `translation_technique` | no | `passive_to_active` | `catss_sem_passive_to_active` |
| General | `pr` | Preposition difference, with possible contextual explanation | `preposition` | yes | `preposition_difference` | `catss_sem_preposition_difference` |
| General | `Pr` | Preposition added | `preposition` | yes | `preposition_added` | `catss_sem_preposition_added` |
| General | `Pr?` | Preposition possibly added | `preposition` | yes | `preposition_possibly_added` | `catss_sem_preposition_possibly_added` |
| General | `Pr~` | Preposition added transposed | `preposition` | yes | `preposition_added_transposed` | `catss_sem_preposition_added_transposed` |
| General | `prp` | Preposition | `grammatical_label` | no | `preposition` | `catss_sem_preposition` |
| General | `prp-` | Preposition or particle not represented | `preposition` | no | `preposition_or_particle_not_represented` | `catss_sem_preposition_or_particle_not_represented` |
| General | `prp+` | Preposition or particle added | `preposition` | no | `preposition_or_particle_added` | `catss_sem_preposition_or_particle_added` |
| General | `Q` | Qere reading note, potentially with context | `qere_ketiv` | yes | `qere` | `catss_sem_qere` |
| General | `q-` | Ketiv reading lacking a Qere counterpart | `qere_ketiv` | no | `ketiv_without_qere` | `catss_sem_ketiv_without_qere` |
| General | `R` | Element repeated in LXX | `translation_technique` | yes | `element_repeated_in_lxx` | `catss_sem_element_repeated_in_lxx` |
| General | `sep` | MT word split in LXX parent | `segmentation` | no | `mt_word_split_in_lxx_parent` | `catss_sem_mt_word_split_in_lxx_parent` |
| General | `seq` | Sequence difference | `transposition` | no | `sequence_difference` | `catss_sem_sequence_difference` |
| General | `sp` | Samaritan closer match | `textual_comparison` | no | `samaritan_closer_match` | `catss_sem_samaritan_closer_match` |
| General | `sp~` | Samaritan partial match | `textual_comparison` | no | `samaritan_partial_match` | `catss_sem_samaritan_partial_match` |
| General | `t*` | Job asterisked passage | `textual` | no | `job_asterisked_passage` | `catss_sem_job_asterisked_passage` |
| General | `tr` | MT reconstruction interchange | `transposition` | yes | `mt_reconstruction_interchange` | `catss_sem_mt_reconstruction_interchange` |
| General | `Tran` | Hebrew sequence transposed to align with Greek | `transposition` | yes | `hebrew_transposed_for_lxx` | `catss_sem_hebrew_transposed_for_lxx` |
| General | `trl` | Transliterated Hebrew | `translation_technique` | no | `transliterated_hebrew` | `catss_sem_transliterated_hebrew` |
| General | `v` | Verse reference | `reference` | yes | `verse_reference` | `catss_sem_verse_reference` |
| General | `V` | Vocalization difference | `translation_technique` | no | `vocalization_difference` | `catss_sem_vocalization_difference` |
| General | `vb` | Verb | `grammatical_label` | no | `verb` | `catss_sem_verb` |
| Sirach | `[..]` | Sirach lacuna or illegible material | `sirach_manuscript` | no | `sirach_lacuna_or_illegible` | `catss_sem_sirach_lacuna_or_illegible` |
| Sirach | `[]` | Editorially reconstructed Sirach letters | `sirach_manuscript` | no | `sirach_reconstructed_letters` | `catss_sem_sirach_reconstructed_letters` |
| Sirach | `{{}}` | Addition sign in a Sirach manuscript | `sirach_manuscript` | no | `sirach_manuscript_addition` | `catss_sem_sirach_manuscript_addition` |
| Sirach | `{}` | Addition sign in a Sirach manuscript | `sirach_manuscript` | no | `sirach_manuscript_addition` | `catss_sem_sirach_manuscript_addition` |
| Sirach | `*` | Uncertain or fragmentary Sirach letter | `sirach_manuscript` | no | `sirach_uncertain_fragmentary_letter` | `catss_sem_sirach_uncertain_fragmentary_letter` |
| Sirach | `>` | Reading lacking in a specified Sirach witness | `sirach_manuscript` | no | `sirach_reading_lacking_in_witness` | `catss_sem_sirach_reading_lacking_in_witness` |
| Sirach | `1` | Sirach Geniza manuscript B | `sirach_witness` | no | `sirach_witness_geniza_b` | `catss_sem_sirach_witness_geniza_b` |
| Sirach | `10` | Sirach 2Q18 witness label | `sirach_witness` | no | `sirach_witness_2q18` | `catss_sem_sirach_witness_2q18` |
| Sirach | `2` | Marginal hand or note of Sirach manuscript B | `sirach_witness` | no | `sirach_witness_geniza_b_margin` | `catss_sem_sirach_witness_geniza_b_margin` |
| Sirach | `3` | Sirach Geniza manuscript A | `sirach_witness` | no | `sirach_witness_geniza_a` | `catss_sem_sirach_witness_geniza_a` |
| Sirach | `4` | Sirach Geniza manuscript C | `sirach_witness` | no | `sirach_witness_geniza_c` | `catss_sem_sirach_witness_geniza_c` |
| Sirach | `5` | Sirach Geniza manuscript D | `sirach_witness` | no | `sirach_witness_geniza_d` | `catss_sem_sirach_witness_geniza_d` |
| Sirach | `6` | Sirach Geniza manuscript E | `sirach_witness` | no | `sirach_witness_geniza_e` | `catss_sem_sirach_witness_geniza_e` |
| Sirach | `7` | Sirach Masada manuscript | `sirach_witness` | no | `sirach_witness_masada` | `catss_sem_sirach_witness_masada` |
| Sirach | `8` | Correcting hand associated with the Masada manuscript | `sirach_witness` | no | `sirach_witness_masada_corrector` | `catss_sem_sirach_witness_masada_corrector` |
| Sirach | `9` | Sirach 11QPs(a) witness label | `sirach_witness` | no | `sirach_witness_11qpsa` | `catss_sem_sirach_witness_11qpsa` |
| Pattern | `<sp…>` | Contextual reference to the Samaritan textual apparatus | `reference` | yes | `samaritan_apparatus_reference` | `catss_sem_samaritan_apparatus_reference` |

## Contextual examples and limits

- **General `*`** denotes an asterisked textual passage; **Sirach
  `*`** denotes an uncertain or fragmentary letter. The same literal
  symbol cannot be assigned one universal semantic identity.
- **General `[..]`** denotes unreadable text or a Greek addition;
  **Sirach `[..]`** denotes a lacuna or illegibility in a Hebrew witness.
- **Sixteen `I:...` entries** (starting `I:+`, `I:-` and ending
  `I:v`) express different renderings or absences of the Hebrew
  infinitive absolute. These are *translation/editorial annotations*, not
  an independent morphological tagger.
- **Sirach numerals `1`–`10`** label witnesses or hands, including
  Masada and its corrector separately; `>` indicates missing reading
  evidence relative to a witness. The symbol alone is **not a manuscript reading**
  attached to a particular word. A word-level association requires
  independently evidenced source scope; see [issue #132](https://github.com/alexsosn/CATSS-TF/issues/132).
- **`<sp…>`** is a patterned Samaritan apparatus-reference marker,
  matched by the catalogue only when a spelling starts with `<sp` and
  ends with `>`. Its exact payload comes from source context. This is
  distinct from the exact `sp` and `sp~` comparison codes.
- The editorial reconstructed Hebrew in MT **column B** is separate
  from the MT-A lexical sequence. `catss_mt_col_b` is the parsed source
  value, not a manuscript attestation or a normalized Hebrew lemma.
- A Greek-side `reference` or `reference_range` node can preserve
  the textual reference without proving that its target is the
  identically numbered Hebrew verse; see [issue #96](https://github.com/alexsosn/CATSS-TF/issues/96).

## Inspecting the documented meaning

```python
from catss_tf.notation import notation_spec

assert notation_spec("*", book="Gen").kind == "asterisked_passage"
assert notation_spec("*", book="Sir").kind == "sirach_uncertain_fragmentary_letter"
assert notation_spec("[..]", book="Sir").kind == "sirach_lacuna_or_illegible"
assert notation_spec("<sp12>", book="Gen").kind == "samaritan_apparatus_reference"
```

With a **loaded standalone** `catss` Text-Fabric API (`api`, from
`Fabric(...).loadAll()`), inspect *actual source-grounded annotations*
without assuming parent-word mapping:

```python
for annotation in api.F.otype.s("annotation"):
    if api.F.catss_kind.v(annotation) != "sirach_witness_masada":
        continue
    for alignment in api.L.u(annotation, otype="alignment"):
        print(
            api.F.catss_alignment_id.v(alignment),
            api.F.catss_source.v(alignment),
            api.F.catss_raw.v(annotation),
            api.F.catss_payload.v(annotation),
        )
```

Absence of any output means that the **loaded corpus** has no such
annotation to report; it is not evidence that a historical witness
lacks a reading. See [the canonical query examples](canonical-corpus.md)
and [the researcher cookbook task](https://github.com/alexsosn/CATSS-TF/issues/151)
for a fuller range of user workflows.

## Coverage and remaining work

This page enumerates the **declared exact notation catalogue** and the
Samaritan pattern. The parser also derives additional raw semantic kinds
from physical source formats and notes that are **not** entries in the
general/Sirach glossary (for example source repairs and continuation
markers). The parent projection feature schema
(`catss_tf.tf_schema.FEATURE_SPECS`) includes these raw kinds,
aggregate counters, membership lanes, reference-range values, and
non-semantic fields. A complete **feature/otype dictionary** is tracked
in [#150](https://github.com/alexsosn/CATSS-TF/issues/150);
a tested beginner-to-expert workflow guide in
[#151](https://github.com/alexsosn/CATSS-TF/issues/151).
The broader Libronix functional parity gate remains
[#126](https://github.com/alexsosn/CATSS-TF/issues/126).
