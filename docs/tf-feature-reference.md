# Text-Fabric features, node types and CATSS-TF Python API

This is the **code-audited public schema dictionary** for the standalone
`catss` Text-Fabric corpus and the `catss-bhsa` / `catss-lxx`
**parent projection modules**. Every parent feature family, declared
semantic kind, canonical scalar feature, node and edge type and package
export is represented in the tables below. The tests
(`tests/test_docs_tf_feature_reference.py`) compare all identifiers to
the implementation and expand every declared parent feature name from
the documented rules.

For source symbols rather than feature names, start with the
[CATSS notation dictionary](notation-reference.md); for actual workflows
use the [canonical corpus guide](canonical-corpus.md),
[notation guide](special-notation.md) and
[Libronix crosswalk](libronix-coverage.md). A feature's presence in the
schema is **not** proof that its value was emitted or that a philological
relationship exists in a particular verse.

## Choose the right TF warp

| Artifact | Slots | Node space and intended query |
| --- | --- | --- |
| `catss` | `alignment` | Canonical editorial alignment groups, lexical MT-A and Greek elements, source lines, annotation and reference nodes |
| `catss-bhsa` | BHSA parent `word` | Scalar overlay features on existing BHSA nodes; the parent must match the pinned version |
| `catss-lxx` | LXX parent `word` | Scalar overlay features on existing Greek parent nodes; some range/anchor values attach to structural nodes |

They have **different node identifiers**. Join separate result sets by
the exact `catss_source` and `catss_alignment_id`, subject to each
projection's mapping evidence. Never pass a canonical alignment node number
into a BHSA/LXX API. Word-level semantic attribution must be independently
supported by source scope, and a Sirach witness flag is **not a manuscript attestation**
for a particular word.

Text-Fabric's structural warp features `otype`, `oslots`, and
`otext` are written separately from the CATSS scalar features below.
Canonical slots are ordered alignment groups, **not individual words**.

## Parent-module feature naming (lossless expansion)

The parent feature tables below contain the **base names** and their
scalar value types. For **Lane core**, **Technique**, **Membership flag**
and **Payload**, both a first-lane feature `base` and a second-lane
feature `base_2` are declared. The two lanes represent *distinct*
memberships when needed, not sequential text tokens or duplicate evidence.

For each **Semantic** row with semantic identity `<kind>`,
`FEATURE_SPECS` declares **16 names**, from all combinations of:

- Four scopes: unscoped, `_mt_a`, `_mt_b`, `_lxx`.
- Two values per scope: `catss_sem_<kind>` (integer flag) and
  `catss_sem_<kind>_payload` (string, optional original contextual note).
- Two membership lanes: unsuffixed and `_2`, appended **after** the
  scope and/or `_payload`.

For example, `catss_sem_<kind>_mt_b_payload_2` represents the second
membership's contextual MT-column-B payload of that semantic kind. This
is a *schema template*: on a real node the corresponding feature may
not have been materialized at all. In the tables below, **Semantic**
rows name the `<kind>` substituted into the template, while every other
row names the exact base or nonlane feature.

**Anchor**, **Reference range** and **Aggregate** rows have their exact
names, without automatic `_2`. There are **134**
semantic kinds: source-glossary kinds and additional raw parser semantic
types. These are not all literal sigla in the source text.

The current schema expands to **2286** declared parent feature names. This count
is checked against the actual `tf_schema.FEATURE_SPECS` set; it is
**not** a count of observed populated features or reconstructed lexemes.

## Canonical features and meaning

The standalone warp has **11** node types. The **Canonical node**
rows identify the node roles, **Canonical feature** rows identify the
stored scalar fields and types, and the single **Canonical edge** row
identifies an explicitly justified source-scoped connection. A feature
can exist only on particular node types, have **missing values**, or be
absent entirely in a partial corpus. `catss_mt_col_b` on an alignment
preserves parsed editorial reconstruction; `mt_b_carrier` denotes a
restricted A-empty exception and cannot be used as a complete MT-B index.
The raw physical source lives on `source_line` nodes in `catss_raw`.

An `annotation` uses `catss_kind`, `catss_family`,
`catss_side`, `catss_raw`, optional `catss_payload`,
and optional explicit `catss_annotation_target` edge. The parent
`catss_sem_*` features are **not** canonical alignment features.
Greek reference nodes may contain unresolved or textually ambiguous
targets; `catss_reference_target` evidence is not a licensed shortcut
to a coincidentally numbered Hebrew verse.

## Complete inventory

Every row names an exact identifier, except **Semantic** rows, which
name a kind used by the 16-name expansion above.

| Category | Name or semantic kind | Value type | Meaning |
| --- | --- | --- | --- |
| Lane core | `catss_alignment_id` | str | stable CATSS alignment identity |
| Lane core | `catss_source` | str | CATSS parallel source filename |
| Lane core | `catss_mapping` | str | resolver mapping kind |
| Lane core | `catss_mt_n` | int | number of CATSS MT alignment elements |
| Lane core | `catss_lxx_n` | int | number of CATSS Greek lexical elements |
| Lane core | `catss_mt_i` | int | 1-based MT alignment-element position |
| Lane core | `catss_mt_segment` | int | 1-based segment within an explicit CATSS maqaf compound |
| Lane core | `catss_lxx_i` | int | 1-based Greek lexical-element position |
| Lane core | `catss_line_first` | int | first physical CATSS source line |
| Lane core | `catss_line_last` | int | last physical CATSS source line |
| Lane core | `catss_line_n` | int | number of physical CATSS source lines |
| Lane core | `catss_retro_kind` | str | normalized CATSS column-B retroversion kind |
| Technique | `catss_tt_cardinality_mt_lxx` | str | derived MT↔LXX token-cardinality class |
| Technique | `catss_tt_token_balance_mt_lxx` | str | derived MT↔LXX token-count balance; not a semantic expansion judgment |
| Technique | `catss_tt_transposition_mt_lxx` | str | derived CATSS transposition-evidence class for MT↔LXX |
| Technique | `catss_tt_addition_vs_mt` | int | derived flag: CATSS explicitly marks Greek material as LXX addition versus MT |
| Technique | `catss_tt_omission_vs_mt` | int | derived flag: CATSS explicitly marks MT material as omitted in LXX |
| Membership flag | `catss_lxx_plus` | int | CATSS LXX-plus alignment |
| Membership flag | `catss_lxx_minus` | int | CATSS LXX-minus alignment |
| Membership flag | `catss_retro` | int | CATSS column-B retroversion is present |
| Membership flag | `catss_ketiv` | int | CATSS MT alignment has Ketiv evidence |
| Membership flag | `catss_qere` | int | CATSS MT alignment has Qere evidence |
| Membership flag | `catss_trans_local` | int | CATSS local transposition |
| Membership flag | `catss_trans_remote` | int | CATSS remote/reflected-elsewhere transposition |
| Membership flag | `catss_trans_style` | int | CATSS stylistic or grammatical transposition |
| Membership flag | `catss_doublet` | int | CATSS doublet annotation |
| Membership flag | `catss_translit` | int | CATSS transliteration annotation |
| Membership flag | `catss_apparent_pm` | int | CATSS apparent plus/minus annotation |
| Membership flag | `catss_agrees_ketiv` | int | Greek agrees with CATSS Ketiv |
| Membership flag | `catss_agrees_qere` | int | Greek agrees with CATSS Qere |
| Membership flag | `catss_metathesis` | int | CATSS metathesis strategy annotation |
| Membership flag | `catss_word_separation` | int | CATSS word-separation strategy annotation |
| Membership flag | `catss_word_join` | int | CATSS word-join strategy annotation |
| Membership flag | `catss_word_division` | int | CATSS word-division strategy annotation |
| Membership flag | `catss_abbreviation` | int | CATSS abbreviation strategy annotation |
| Membership flag | `catss_greek_preverb` | int | CATSS Greek-preverb strategy annotation |
| Membership flag | `catss_comparative` | int | CATSS comparative/superlative strategy annotation |
| Membership flag | `catss_asterisked` | int | CATSS asterisked-passage annotation |
| Membership flag | `catss_doubt` | int | CATSS doubt marker |
| Membership flag | `catss_greek_diff` | int | CATSS Rahlfs/Göttingen difference annotation |
| Membership flag | `catss_greek_correction` | int | CATSS Greek correction annotation |
| Membership flag | `catss_prep_added` | int | CATSS added-preposition annotation |
| Membership flag | `catss_distributive` | int | CATSS distributive-rendering annotation |
| Membership flag | `catss_repetition` | int | CATSS repetition annotation |
| Payload | `catss_distributive_payload` | str | CATSS distributive-rendering contextual payload |
| Payload | `catss_prep_added_payload` | str | CATSS added-preposition contextual payload |
| Payload | `catss_repetition_payload` | str | CATSS repetition contextual payload |
| Payload | `catss_trans_remote_payload` | str | CATSS remote-transposition contextual payload |
| Payload | `catss_trans_style_payload` | str | CATSS stylistic-transposition contextual payload |
| Anchor | `catss_lxx_plus_n` | int | number of CATSS Hebrew-empty/LXX-plus groups on this verse |
| Anchor | `catss_lxx_plus_token_n` | int | total Greek lexical elements in CATSS LXX-plus groups on this verse |
| Anchor | `catss_lxx_minus_n` | int | number of CATSS Greek-empty/LXX-minus groups |
| Anchor | `catss_apparent_mt_minus_n` | int | number of CATSS Hebrew-empty apparent-MT-minus groups on this verse |
| Anchor | `catss_transposition_placeholder_n` | int | number of CATSS Greek-empty transposition placeholder groups |
| Reference range | `catss_lxx_reference_range_id` | str | stable CATSS alignment identity for this range |
| Reference range | `catss_lxx_reference_range_source` | str | CATSS source filename for this range |
| Reference range | `catss_lxx_reference_range_raw` | str | raw CATSS contextual-reference range spelling |
| Reference range | `catss_lxx_reference_range_member_i` | int | 1-based member ordinal within the range |
| Reference range | `catss_lxx_reference_range_member_n` | int | number of parent subverse members in range |
| Reference range | `catss_lxx_reference_range_start_chapter` | int | range start chapter |
| Reference range | `catss_lxx_reference_range_start_verse` | int | range start verse |
| Reference range | `catss_lxx_reference_range_start_subverse` | str | range start subverse |
| Reference range | `catss_lxx_reference_range_end_chapter` | int | range end chapter |
| Reference range | `catss_lxx_reference_range_end_verse` | int | range end verse |
| Reference range | `catss_lxx_reference_range_end_subverse` | str | range end subverse |
| Aggregate | `catss_alignment_n` | int | Number of CATSS alignment memberships on the parent word |
| Aggregate | `catss_lxx_plus_members` | int | Count of CATSS memberships carrying catss_lxx_plus |
| Aggregate | `catss_lxx_minus_members` | int | Count of CATSS memberships carrying catss_lxx_minus |
| Aggregate | `catss_retro_members` | int | Count of CATSS memberships carrying catss_retro |
| Aggregate | `catss_ketiv_members` | int | Count of CATSS memberships carrying catss_ketiv |
| Aggregate | `catss_qere_members` | int | Count of CATSS memberships carrying catss_qere |
| Aggregate | `catss_trans_local_members` | int | Count of CATSS memberships carrying catss_trans_local |
| Aggregate | `catss_trans_remote_members` | int | Count of CATSS memberships carrying catss_trans_remote |
| Aggregate | `catss_trans_style_members` | int | Count of CATSS memberships carrying catss_trans_style |
| Aggregate | `catss_doublet_members` | int | Count of CATSS memberships carrying catss_doublet |
| Aggregate | `catss_translit_members` | int | Count of CATSS memberships carrying catss_translit |
| Aggregate | `catss_apparent_pm_members` | int | Count of CATSS memberships carrying catss_apparent_pm |
| Aggregate | `catss_agrees_ketiv_members` | int | Count of CATSS memberships carrying catss_agrees_ketiv |
| Aggregate | `catss_agrees_qere_members` | int | Count of CATSS memberships carrying catss_agrees_qere |
| Aggregate | `catss_metathesis_members` | int | Count of CATSS memberships carrying catss_metathesis |
| Aggregate | `catss_word_separation_members` | int | Count of CATSS memberships carrying catss_word_separation |
| Aggregate | `catss_word_join_members` | int | Count of CATSS memberships carrying catss_word_join |
| Aggregate | `catss_word_division_members` | int | Count of CATSS memberships carrying catss_word_division |
| Aggregate | `catss_abbreviation_members` | int | Count of CATSS memberships carrying catss_abbreviation |
| Aggregate | `catss_greek_preverb_members` | int | Count of CATSS memberships carrying catss_greek_preverb |
| Aggregate | `catss_comparative_members` | int | Count of CATSS memberships carrying catss_comparative |
| Aggregate | `catss_asterisked_members` | int | Count of CATSS memberships carrying catss_asterisked |
| Aggregate | `catss_doubt_members` | int | Count of CATSS memberships carrying catss_doubt |
| Aggregate | `catss_greek_diff_members` | int | Count of CATSS memberships carrying catss_greek_diff |
| Aggregate | `catss_greek_correction_members` | int | Count of CATSS memberships carrying catss_greek_correction |
| Aggregate | `catss_prep_added_members` | int | Count of CATSS memberships carrying catss_prep_added |
| Aggregate | `catss_distributive_members` | int | Count of CATSS memberships carrying catss_distributive |
| Aggregate | `catss_repetition_members` | int | Count of CATSS memberships carrying catss_repetition |
| Semantic | `abbreviation` | int | Raw parser-derived or source notation semantic kind: abbreviation |
| Semantic | `active_to_passive` | int | Raw parser-derived or source notation semantic kind: active to passive |
| Semantic | `adjective` | int | Source glossary semantic kind: adjective |
| Semantic | `adverb` | int | Source glossary semantic kind: adverb |
| Semantic | `apparent_minus` | int | Source glossary semantic kind: apparent minus |
| Semantic | `apparent_plus` | int | Source glossary semantic kind: apparent plus |
| Semantic | `apparent_reconstructed_hebrew` | int | Source glossary semantic kind: apparent reconstructed hebrew |
| Semantic | `aramaic` | int | Source glossary semantic kind: aramaic |
| Semantic | `aramaic_etymological_exegesis` | int | Source glossary semantic kind: aramaic etymological exegesis |
| Semantic | `asterisked_passage` | int | Source glossary semantic kind: asterisked passage |
| Semantic | `context` | int | Raw parser-derived or source notation semantic kind: context |
| Semantic | `contextual_greek_reading` | int | Raw parser-derived or source notation semantic kind: contextual greek reading |
| Semantic | `contextual_influence` | int | Source glossary semantic kind: contextual influence |
| Semantic | `contextual_or_intuitive_reconstruction` | int | Source glossary semantic kind: contextual or intuitive reconstruction |
| Semantic | `contextual_reference` | int | Raw parser-derived or source notation semantic kind: contextual reference |
| Semantic | `continuation_marker` | int | Raw parser-derived or source notation semantic kind: continuation marker |
| Semantic | `different_word_division` | int | Source glossary semantic kind: different word division |
| Semantic | `distributive` | int | Raw parser-derived or source notation semantic kind: distributive |
| Semantic | `distributive_rendering` | int | Source glossary semantic kind: distributive rendering |
| Semantic | `doublet` | int | Source glossary semantic kind: doublet |
| Semantic | `doublet_transposed` | int | Raw parser-derived or source notation semantic kind: doublet transposed |
| Semantic | `doubt` | int | Raw parser-derived or source notation semantic kind: doubt |
| Semantic | `element_repeated_in_lxx` | int | Source glossary semantic kind: element repeated in LXX |
| Semantic | `etymological` | int | Raw parser-derived or source notation semantic kind: etymological |
| Semantic | `etymological_exegesis` | int | Source glossary semantic kind: etymological exegesis |
| Semantic | `gender_switch` | int | Source glossary semantic kind: gender switch |
| Semantic | `greek_correction` | int | Raw parser-derived or source notation semantic kind: greek correction |
| Semantic | `greek_edition_difference` | int | Raw parser-derived or source notation semantic kind: greek edition difference |
| Semantic | `greek_lexical_problem` | int | Source glossary semantic kind: greek lexical problem |
| Semantic | `greek_preverb` | int | Source glossary semantic kind: greek preverb |
| Semantic | `greek_transposition` | int | Source glossary semantic kind: greek transposition |
| Semantic | `hebrew_transposed_for_lxx` | int | Source glossary semantic kind: hebrew transposed for LXX |
| Semantic | `hebrew_transposition` | int | Source glossary semantic kind: hebrew transposition |
| Semantic | `incomplete` | int | Raw parser-derived or source notation semantic kind: incomplete |
| Semantic | `incomplete_reconstruction` | int | Source glossary semantic kind: incomplete reconstruction |
| Semantic | `inf_abs_accusative_without_mt_inf_abs` | int | Raw parser-derived or source notation semantic kind: inf abs accusative without MT inf abs |
| Semantic | `inf_abs_and_main_verb_omitted` | int | Source glossary semantic kind: inf abs and main verb omitted |
| Semantic | `inf_abs_dative_without_mt_inf_abs` | int | Source glossary semantic kind: inf abs dative without MT inf abs |
| Semantic | `inf_abs_participle_without_mt_inf_abs` | int | Source glossary semantic kind: inf abs participle without MT inf abs |
| Semantic | `inf_abs_rendered_accusative_noun` | int | Source glossary semantic kind: inf abs rendered accusative noun |
| Semantic | `inf_abs_rendered_dative_noun` | int | Source glossary semantic kind: inf abs rendered dative noun |
| Semantic | `inf_abs_rendered_different_accusative_noun` | int | Source glossary semantic kind: inf abs rendered different accusative noun |
| Semantic | `inf_abs_rendered_different_dative_noun` | int | Source glossary semantic kind: inf abs rendered different dative noun |
| Semantic | `inf_abs_rendered_different_verb_participle` | int | Source glossary semantic kind: inf abs rendered different verb participle |
| Semantic | `inf_abs_rendered_finite_verb` | int | Source glossary semantic kind: inf abs rendered finite verb |
| Semantic | `inf_abs_rendered_finite_verb_adjective` | int | Source glossary semantic kind: inf abs rendered finite verb adjective |
| Semantic | `inf_abs_rendered_finite_verb_adverb` | int | Source glossary semantic kind: inf abs rendered finite verb adverb |
| Semantic | `inf_abs_rendered_finite_verb_noun` | int | Source glossary semantic kind: inf abs rendered finite verb noun |
| Semantic | `inf_abs_rendered_participle` | int | Source glossary semantic kind: inf abs rendered participle |
| Semantic | `inf_abs_rendered_participle_compositum` | int | Source glossary semantic kind: inf abs rendered participle compositum |
| Semantic | `inf_abs_rendered_verb` | int | Source glossary semantic kind: inf abs rendered verb |
| Semantic | `inf_abs_without_mt_inf_abs` | int | Source glossary semantic kind: inf abs without MT inf abs |
| Semantic | `infinitive_absolute` | int | Source glossary semantic kind: infinitive absolute |
| Semantic | `job_asterisked_passage` | int | Source glossary semantic kind: job asterisked passage |
| Semantic | `ketiv_without_qere` | int | Source glossary semantic kind: KETIV without QERE |
| Semantic | `letter_interchange` | int | Raw parser-derived or source notation semantic kind: letter interchange |
| Semantic | `long_alignment_event` | int | Source glossary semantic kind: long alignment event |
| Semantic | `lxx_agrees_ketiv` | int | Source glossary semantic kind: LXX agrees KETIV |
| Semantic | `lxx_agrees_qere` | int | Source glossary semantic kind: LXX agrees QERE |
| Semantic | `lxx_conjectural_emendation` | int | Source glossary semantic kind: LXX conjectural emendation |
| Semantic | `lxx_minus` | int | Source glossary semantic kind: LXX minus |
| Semantic | `lxx_parent_omits_mt_elements` | int | Source glossary semantic kind: LXX parent omits MT elements |
| Semantic | `lxx_plus` | int | Source glossary semantic kind: LXX plus |
| Semantic | `metathesis` | int | Raw parser-derived or source notation semantic kind: metathesis |
| Semantic | `mt_reconstruction_interchange` | int | Source glossary semantic kind: MT reconstruction interchange |
| Semantic | `mt_word_split_in_lxx_parent` | int | Source glossary semantic kind: MT word split in LXX parent |
| Semantic | `mt_words_joined_in_lxx_parent` | int | Source glossary semantic kind: MT words joined in LXX parent |
| Semantic | `noun` | int | Source glossary semantic kind: noun |
| Semantic | `number_difference` | int | Raw parser-derived or source notation semantic kind: number difference |
| Semantic | `parallel_elsewhere` | int | Source glossary semantic kind: parallel elsewhere |
| Semantic | `passive_to_active` | int | Raw parser-derived or source notation semantic kind: passive to active |
| Semantic | `possible_abbreviation` | int | Source glossary semantic kind: possible abbreviation |
| Semantic | `possible_doublet` | int | Raw parser-derived or source notation semantic kind: possible doublet |
| Semantic | `possible_greek_agrees_qere` | int | Raw parser-derived or source notation semantic kind: possible greek agrees QERE |
| Semantic | `possible_hebrew_variant_no_retroversion` | int | Source glossary semantic kind: possible hebrew variant no retroversion |
| Semantic | `possible_lxx_minus` | int | Source glossary semantic kind: possible LXX minus |
| Semantic | `possible_lxx_plus` | int | Source glossary semantic kind: possible LXX plus |
| Semantic | `preposition` | int | Source glossary semantic kind: preposition |
| Semantic | `preposition_added` | int | Raw parser-derived or source notation semantic kind: preposition added |
| Semantic | `preposition_added_transposed` | int | Source glossary semantic kind: preposition added transposed |
| Semantic | `preposition_addition` | int | Raw parser-derived or source notation semantic kind: preposition addition |
| Semantic | `preposition_difference` | int | Raw parser-derived or source notation semantic kind: preposition difference |
| Semantic | `preposition_marker` | int | Raw parser-derived or source notation semantic kind: preposition marker |
| Semantic | `preposition_omission` | int | Raw parser-derived or source notation semantic kind: preposition omission |
| Semantic | `preposition_or_particle_added` | int | Source glossary semantic kind: preposition or particle added |
| Semantic | `preposition_or_particle_not_represented` | int | Source glossary semantic kind: preposition or particle not represented |
| Semantic | `preposition_possibly_added` | int | Source glossary semantic kind: preposition possibly added |
| Semantic | `proper_noun` | int | Raw parser-derived or source notation semantic kind: proper noun |
| Semantic | `qere` | int | Source glossary semantic kind: QERE |
| Semantic | `qere_without_ketiv` | int | Source glossary semantic kind: QERE without KETIV |
| Semantic | `rahlfs_goettingen_difference` | int | Source glossary semantic kind: rahlfs goettingen difference |
| Semantic | `reconstructed_proper_noun` | int | Source glossary semantic kind: reconstructed proper noun |
| Semantic | `reconstruction_from_other_verse` | int | Source glossary semantic kind: reconstruction from other verse |
| Semantic | `repetition` | int | Raw parser-derived or source notation semantic kind: repetition |
| Semantic | `samaritan_apparatus_reference` | int | Source glossary semantic kind: samaritan apparatus reference |
| Semantic | `samaritan_closer_match` | int | Source glossary semantic kind: samaritan closer match |
| Semantic | `samaritan_partial_match` | int | Source glossary semantic kind: samaritan partial match |
| Semantic | `sequence_difference` | int | Source glossary semantic kind: sequence difference |
| Semantic | `sirach_lacuna_in_witness` | int | Raw parser-derived or source notation semantic kind: SIRACH lacuna in witness |
| Semantic | `sirach_lacuna_or_illegible` | int | Source glossary semantic kind: SIRACH lacuna or illegible |
| Semantic | `sirach_manuscript_addition` | int | Source glossary semantic kind: SIRACH manuscript addition |
| Semantic | `sirach_reading_lacking_in_witness` | int | Source glossary semantic kind: SIRACH reading lacking in witness |
| Semantic | `sirach_reconstructed_letters` | int | Source glossary semantic kind: SIRACH reconstructed letters |
| Semantic | `sirach_uncertain_fragmentary_letter` | int | Source glossary semantic kind: SIRACH uncertain fragmentary letter |
| Semantic | `sirach_witness_11qpsa` | int | Source glossary semantic kind: SIRACH witness 11qpsa |
| Semantic | `sirach_witness_2q18` | int | Source glossary semantic kind: SIRACH witness 2q18 |
| Semantic | `sirach_witness_geniza_a` | int | Source glossary semantic kind: SIRACH witness geniza a |
| Semantic | `sirach_witness_geniza_b` | int | Source glossary semantic kind: SIRACH witness geniza b |
| Semantic | `sirach_witness_geniza_b_margin` | int | Source glossary semantic kind: SIRACH witness geniza b margin |
| Semantic | `sirach_witness_geniza_c` | int | Source glossary semantic kind: SIRACH witness geniza c |
| Semantic | `sirach_witness_geniza_d` | int | Source glossary semantic kind: SIRACH witness geniza d |
| Semantic | `sirach_witness_geniza_e` | int | Source glossary semantic kind: SIRACH witness geniza e |
| Semantic | `sirach_witness_masada` | int | Source glossary semantic kind: SIRACH witness masada |
| Semantic | `sirach_witness_masada_corrector` | int | Source glossary semantic kind: SIRACH witness masada corrector |
| Semantic | `source_corruption_note` | int | Raw parser-derived or source notation semantic kind: source corruption note |
| Semantic | `source_format_note` | int | Raw parser-derived or source notation semantic kind: source format note |
| Semantic | `source_note` | int | Raw parser-derived or source notation semantic kind: source note |
| Semantic | `source_repair` | int | Raw parser-derived or source notation semantic kind: source repair |
| Semantic | `stylistic_or_grammatical_transposition` | int | Source glossary semantic kind: stylistic or grammatical transposition |
| Semantic | `transliterated_hebrew` | int | Source glossary semantic kind: transliterated hebrew |
| Semantic | `transposition_remote` | int | Raw parser-derived or source notation semantic kind: transposition remote |
| Semantic | `transposition_stylistic` | int | Raw parser-derived or source notation semantic kind: transposition stylistic |
| Semantic | `uncertain_transliteration` | int | Source glossary semantic kind: uncertain transliteration |
| Semantic | `unreadable_or_greek_addition` | int | Source glossary semantic kind: unreadable or greek addition |
| Semantic | `verb` | int | Source glossary semantic kind: verb |
| Semantic | `verse_reference` | int | Raw parser-derived or source notation semantic kind: verse reference |
| Semantic | `vocalization` | int | Raw parser-derived or source notation semantic kind: vocalization |
| Semantic | `vocalization_difference` | int | Source glossary semantic kind: vocalization difference |
| Semantic | `vocalization_shin_sin` | int | Raw parser-derived or source notation semantic kind: vocalization shin sin |
| Semantic | `word_division` | int | Raw parser-derived or source notation semantic kind: word division |
| Semantic | `word_join` | int | Raw parser-derived or source notation semantic kind: word join |
| Semantic | `word_separation` | int | Raw parser-derived or source notation semantic kind: word separation |
| Semantic | `ziegler_preferred_variant` | int | Source glossary semantic kind: ziegler preferred variant |
| Semantic | `ziegler_variant` | int | Raw parser-derived or source notation semantic kind: ziegler variant |
| Canonical node | `alignment` | node | One ordered CATSS editorial MT–Greek group; it is the canonical TF slot |
| Canonical node | `annotation` | node | Typed source-side editorial symbol with raw spelling and optional context |
| Canonical node | `chapter` | node | A source-scoped chapter covering alignment slots |
| Canonical node | `document` | node | One CATSS source file with its contained alignment slots |
| Canonical node | `lxx_element` | node | One Greek lexical element in an alignment |
| Canonical node | `mt_b_carrier` | node | Special physically MT-A-empty reconstruction carrier; not every MT-B row |
| Canonical node | `mt_element` | node | One lexical MT-A element, not a reconstructed MT-B token |
| Canonical node | `reference` | node | Scalar Greek contextual reference with chapter/verse/subverse |
| Canonical node | `reference_range` | node | Greek contextual range endpoints; target may remain unresolved |
| Canonical node | `source_line` | node | Physical CATSS source line, preserving raw text and line number |
| Canonical node | `verse` | node | A source-scoped verse/header record covering alignment slots |
| Canonical feature | `book` | str | Source book identifier; edition/source identity is preserved separately |
| Canonical feature | `catss_alignment_id` | str | Stable editorial CATSS alignment identity; join key, not a parent node number |
| Canonical feature | `catss_aramaic_section` | int | Canonical source feature: catss aramaic section |
| Canonical feature | `catss_column_split` | int | Canonical source feature: catss column split |
| Canonical feature | `catss_contextual` | int | Whether the source annotation is context-bearing |
| Canonical feature | `catss_display` | str | Convenience display string joining raw MT and LXX evidence |
| Canonical feature | `catss_doubt` | int | Canonical source feature: catss doubt |
| Canonical feature | `catss_family` | str | Editorial classification family, on annotation nodes |
| Canonical feature | `catss_header_line_no` | int | Canonical source feature: catss header line no |
| Canonical feature | `catss_header_raw` | str | Canonical source feature: catss header raw |
| Canonical feature | `catss_index` | int | Canonical source feature: catss index |
| Canonical feature | `catss_ketiv` | int | Canonical source feature: catss KETIV |
| Canonical feature | `catss_ketiv_text` | str | Canonical source feature: catss KETIV text |
| Canonical feature | `catss_kind` | str | Canonical parser annotation kind, on annotation nodes |
| Canonical feature | `catss_line_first` | int | Canonical source feature: catss line first |
| Canonical feature | `catss_line_last` | int | Canonical source feature: catss line last |
| Canonical feature | `catss_line_n` | int | Canonical source feature: catss line n |
| Canonical feature | `catss_line_no` | int | Canonical source feature: catss line no |
| Canonical feature | `catss_lxx_minus` | int | Canonical source feature: catss LXX minus |
| Canonical feature | `catss_lxx_n` | int | Canonical source feature: catss LXX n |
| Canonical feature | `catss_lxx_plus` | int | Canonical source feature: catss LXX plus |
| Canonical feature | `catss_lxx_raw` | str | Parsed Greek cell including source notation |
| Canonical feature | `catss_mt_b_raw` | str | Raw reconstructed column B text on special mt_b_carrier nodes |
| Canonical feature | `catss_mt_col_a` | str | MT-A source text; lexical readings come from mt_element nodes |
| Canonical feature | `catss_mt_col_b` | str | Parsed reconstructed Hebrew B column (after first = and trimming) |
| Canonical feature | `catss_mt_n` | int | Canonical source feature: catss MT n |
| Canonical feature | `catss_mt_raw` | str | Parsed complete MT cell including source notation |
| Canonical feature | `catss_payload` | str | Contextual note payload when actually supplied |
| Canonical feature | `catss_qere` | int | Canonical source feature: catss QERE |
| Canonical feature | `catss_qere_text` | str | Canonical source feature: catss QERE text |
| Canonical feature | `catss_range_end_chapter` | int | Canonical source feature: catss range end chapter |
| Canonical feature | `catss_range_end_subverse` | str | Canonical source feature: catss range end subverse |
| Canonical feature | `catss_range_end_verse` | int | Canonical source feature: catss range end verse |
| Canonical feature | `catss_range_start_chapter` | int | Canonical source feature: catss range start chapter |
| Canonical feature | `catss_range_start_subverse` | str | Canonical source feature: catss range start subverse |
| Canonical feature | `catss_range_start_verse` | int | Canonical source feature: catss range start verse |
| Canonical feature | `catss_raw` | str | Original annotation/reference/physical-line surface spelling |
| Canonical feature | `catss_ref_chapter` | int | Canonical source feature: catss ref chapter |
| Canonical feature | `catss_ref_subverse` | str | Canonical source feature: catss ref subverse |
| Canonical feature | `catss_ref_verse` | int | Canonical source feature: catss ref verse |
| Canonical feature | `catss_retro` | int | Canonical source feature: catss retro |
| Canonical feature | `catss_retro_kind` | str | Editorial classification of reconstructed MT-B evidence |
| Canonical feature | `catss_side` | str | Source side of an annotation |
| Canonical feature | `catss_source` | str | Exact CATSS parallel-source filename |
| Canonical feature | `catss_target_index` | int | Explicit 1-based destination element position |
| Canonical feature | `catss_target_side` | str | Explicit scoped annotation destination side |
| Canonical feature | `catss_text` | str | Lexical MT-A or Greek source spelling on an element node |
| Canonical feature | `catss_trans_local` | int | Canonical source feature: catss trans local |
| Canonical feature | `catss_trans_remote` | int | Canonical source feature: catss trans remote |
| Canonical feature | `catss_trans_style` | int | Canonical source feature: catss trans style |
| Canonical feature | `catss_tt_addition_vs_mt` | int | Canonical source feature: catss tt addition vs MT |
| Canonical feature | `catss_tt_cardinality_mt_lxx` | str | Canonical source feature: catss tt cardinality MT LXX |
| Canonical feature | `catss_tt_omission_vs_mt` | int | Canonical source feature: catss tt omission vs MT |
| Canonical feature | `catss_tt_status` | str | Translation-technique derivation state, including unclassified |
| Canonical feature | `catss_tt_token_balance_mt_lxx` | str | Canonical source feature: catss tt token balance MT LXX |
| Canonical feature | `catss_tt_transposition_mt_lxx` | str | Canonical source feature: catss tt transposition MT LXX |
| Canonical feature | `catss_tt_unclassified_reason` | str | Reason technical technique derivation could not be justified |
| Canonical feature | `chapter` | int | Chapter number in source structure |
| Canonical feature | `verse` | int | Verse number in source structure |
| Canonical edge | `catss_annotation_target` | edge | Explicit source-side annotation target in the same canonical alignment |
| Public API | `__version__` | Python | Installed package version string |
| Public API | `compare_canonical_projection_bundle` | Python | Compare canonical corpus evidence against a projection bundle |
| Public API | `compare_projection_bundles` | Python | Validate source fingerprints and shared alignment evidence of two projections |
| Public API | `AlignmentAnnotationEvidence` | Python | Typed canonical source annotation evidence |
| Public API | `CanonicalAlignedGroup` | Python | Typed canonical editorial alignment result |
| Public API | `CanonicalMtBRawHit` | Python | Typed raw reconstruction evidence result |
| Public API | `SirachWitnessAnnotation` | Python | Typed Sirach manuscript annotation evidence |
| Public API | `UnclassifiedAlignment` | Python | Typed translation-technique unclassified result |
| Public API | `find_aligned_groups` | Python | Find one MT-A form and one Greek form in the same alignment |
| Public API | `find_groups_with_all_forms` | Python | Find conjunction of exact MT-A and LXX forms within one editorial group |
| Public API | `find_mt_b_raw_matches` | Python | Search exact case-sensitive substring of parsed reconstructed MT-B |
| Public API | `find_sirach_witness_annotations` | Python | Return source-provenanced Sirach witness indicators |
| Public API | `find_unclassified_alignments` | Python | Inspect unresolved translation-technique groups without guessing |
| Public API | `materialize_bhsa` | Python | Project alignment evidence onto a pinned ETCBC/BHSA parent |
| Public API | `materialize_corpus` | Python | Create standalone native Text-Fabric corpus from authorized CATSS sources |
| Public API | `materialize_lxx` | Python | Project alignment evidence onto pinned CenterBLC/LXX parent |
| Public API | `TextFabricBhsaProvider` | Python | Read-only BHSA parent access adapter |
| Public API | `TextFabricLxxProvider` | Python | Read-only LXX parent access adapter |

## Query examples and interpretation

Inspect the *declared* parent feature contract without assuming that a
particular module contains all those values:

```python
from catss_tf.tf_schema import FEATURE_SPECS

spec = FEATURE_SPECS["catss_sem_qere_mt_a_payload_2"]
print(spec.value_type, spec.description)
# str — second membership lane, MT-A contextual note (if supplied)
```

On a **loaded canonical `catss`** API, inspect actual editorial evidence
without guessing that a source note belongs to one lexical word:

```python
for alignment in api.F.otype.s("alignment"):
    annotations = api.L.d(alignment, otype="annotation")
    for node in annotations:
        print(
            api.F.catss_alignment_id.v(alignment),
            api.F.catss_kind.v(node),
            api.F.catss_side.v(node),
            api.F.catss_raw.v(node),
        )
```

A source annotation need not have a resolved parent-word mapping. The
global `catss_alignment_n` and `catss_*_members` counters count
memberships, **not** distinct manuscript attestations. An absent
`catss_sem_*` value does not imply a negative textual judgment;
`0` is not invented where no source evidence or mapping exists.
The Greek and Hebrew parent projection modules can have different
coverage for the same stable CATSS alignment ID.

## Public API and remaining parity work

**Public API** rows enumerate `catss_tf.__all__`. These are importable
symbols, not assertions that source data for every manuscript/word mapping
or a Libronix-equivalent UI are provided. There is a difference between
`find_groups_with_all_forms` (co-membership in **one** editorial group)
and pairwise lexical translation, and between
`find_mt_b_raw_matches` (raw parsed B substring) and a reconstructed
Hebrew lemma search.

Install and source access requirements are in [integration.md](integration.md).
Use authorized CATSS data, authenticated HTTPS and pinned parent releases.
The full 46-file **standalone** canonical smoke does not prove that strict
`catss-bhsa` / `catss-lxx` parent projections are complete
(JoshB lettered-subverse availability remains a known blocker).
Research issues [#96](https://github.com/alexsosn/CATSS-TF/issues/96)
and [#132](https://github.com/alexsosn/CATSS-TF/issues/132) track
uncertain reference and Sirach witness-to-reading relationships.
A tested researcher cookbook and independent new-user walkthrough
remain tracked in [#151](https://github.com/alexsosn/CATSS-TF/issues/151);
Libronix feature parity in [#126](https://github.com/alexsosn/CATSS-TF/issues/126).
