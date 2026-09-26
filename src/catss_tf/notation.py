"""Closed semantic catalogue for documented CATSS notation."""

import dataclasses


@dataclasses.dataclass(frozen=True, slots=True)
class NotationSpec:
    """Stable semantic identity for one documented CATSS notation."""

    kind: str
    family: str
    contextual: bool = False


def _spec(kind: str, family: str, *, contextual: bool = False) -> NotationSpec:
    return NotationSpec(kind=kind, family=family, contextual=contextual)


_GENERAL: dict[str, NotationSpec] = {
    "+": _spec("lxx_plus", "alignment"),
    "{+}": _spec("possible_lxx_plus", "alignment"),
    "{+?}": _spec("possible_lxx_minus", "alignment"),
    "-": _spec("lxx_minus", "alignment"),
    "*": _spec("asterisked_passage", "textual"),
    "[..]": _spec("unreadable_or_greek_addition", "textual"),
    "??": _spec("possible_hebrew_variant_no_retroversion", "reconstruction"),
    "~": _spec("stylistic_or_grammatical_transposition", "transposition"),
    "abbr": _spec("possible_abbreviation", "reconstruction"),
    "act2pas": _spec("active_to_passive", "translation_technique"),
    "ad": _spec("adverb", "grammatical_label"),
    "aj": _spec("adjective", "grammatical_label"),
    "Ap+": _spec("apparent_plus", "alignment"),
    "Ap-": _spec("apparent_minus", "alignment"),
    "App": _spec("apparent_reconstructed_hebrew", "reconstruction"),
    "Aram": _spec("aramaic", "language"),
    "C": _spec("contextual_or_intuitive_reconstruction", "reconstruction", contextual=True),
    "[ce]": _spec("lxx_conjectural_emendation", "textual", contextual=True),
    "C´": _spec("reconstruction_from_other_verse", "reconstruction", contextual=True),
    "Dn": _spec("number_difference", "translation_technique"),
    "{d}": _spec("doublet", "translation_technique", contextual=True),
    "{d}tr": _spec("doublet_transposed", "transposition", contextual=True),
    "div": _spec("different_word_division", "segmentation"),
    "DR": _spec("distributive_rendering", "translation_technique", contextual=True),
    "els": _spec("parallel_elsewhere", "reference", contextual=True),
    "Ety": _spec("etymological_exegesis", "translation_technique", contextual=True),
    "EtyA": _spec("aramaic_etymological_exegesis", "translation_technique", contextual=True),
    "<fm": _spec("gender_switch", "translation_technique"),
    "g": _spec("rahlfs_goettingen_difference", "textual", contextual=True),
    "GTran": _spec("greek_transposition", "transposition", contextual=True),
    "HTran": _spec("hebrew_transposition", "transposition", contextual=True),
    "I": _spec("infinitive_absolute", "infinitive_absolute"),
    "I:+": _spec("inf_abs_without_mt_inf_abs", "infinitive_absolute"),
    "I:-": _spec("inf_abs_rendered_finite_verb", "infinitive_absolute"),
    "I:--": _spec("inf_abs_and_main_verb_omitted", "infinitive_absolute"),
    "I:ad": _spec("inf_abs_rendered_finite_verb_adverb", "infinitive_absolute"),
    "I:aj": _spec("inf_abs_rendered_finite_verb_adjective", "infinitive_absolute"),
    "I:n": _spec("inf_abs_rendered_finite_verb_noun", "infinitive_absolute"),
    "I:na": _spec("inf_abs_rendered_accusative_noun", "infinitive_absolute"),
    "I:nad": _spec("inf_abs_rendered_different_accusative_noun", "infinitive_absolute"),
    "I:nd": _spec("inf_abs_rendered_dative_noun", "infinitive_absolute"),
    "I:nd+": _spec("inf_abs_dative_without_mt_inf_abs", "infinitive_absolute"),
    "I:ndd": _spec("inf_abs_rendered_different_dative_noun", "infinitive_absolute"),
    "I:p": _spec("inf_abs_rendered_participle", "infinitive_absolute"),
    "I:p+": _spec("inf_abs_participle_without_mt_inf_abs", "infinitive_absolute"),
    "I:pc": _spec("inf_abs_rendered_participle_compositum", "infinitive_absolute"),
    "I:pd": _spec("inf_abs_rendered_different_verb_participle", "infinitive_absolute"),
    "I:v": _spec("inf_abs_rendered_verb", "infinitive_absolute"),
    "ir": _spec("incomplete_reconstruction", "reconstruction"),
    "join": _spec("mt_words_joined_in_lxx_parent", "segmentation"),
    "k-": _spec("qere_without_ketiv", "qere_ketiv"),
    "<l>": _spec("greek_lexical_problem", "textual", contextual=True),
    "lo": _spec("long_alignment_event", "alignment"),
    "LXX=K": _spec("lxx_agrees_ketiv", "qere_ketiv"),
    "LXX=Q": _spec("lxx_agrees_qere", "qere_ketiv"),
    "met": _spec("metathesis", "segmentation"),
    "n": _spec("noun", "grammatical_label"),
    "npr": _spec("reconstructed_proper_noun", "reconstruction"),
    "om": _spec("lxx_parent_omits_mt_elements", "alignment"),
    "{p}": _spec("greek_preverb", "preposition"),
    "pa": _spec("passive_to_active", "translation_technique"),
    "pass2act": _spec("passive_to_active", "translation_technique"),
    "pr": _spec("preposition_difference", "preposition", contextual=True),
    "Pr": _spec("preposition_added", "preposition", contextual=True),
    "Pr?": _spec("preposition_possibly_added", "preposition", contextual=True),
    "Pr~": _spec("preposition_added_transposed", "preposition", contextual=True),
    "prp": _spec("preposition", "grammatical_label"),
    "prp+": _spec("preposition_or_particle_added", "preposition"),
    "prp-": _spec("preposition_or_particle_not_represented", "preposition"),
    "Q": _spec("qere", "qere_ketiv", contextual=True),
    "R": _spec("element_repeated_in_lxx", "translation_technique", contextual=True),
    "q-": _spec("ketiv_without_qere", "qere_ketiv"),
    "sep": _spec("mt_word_split_in_lxx_parent", "segmentation"),
    "seq": _spec("sequence_difference", "transposition"),
    "sp": _spec("samaritan_closer_match", "textual_comparison"),
    "sp~": _spec("samaritan_partial_match", "textual_comparison"),
    "t*": _spec("job_asterisked_passage", "textual"),
    "tr": _spec("mt_reconstruction_interchange", "transposition", contextual=True),
    "Tran": _spec("hebrew_transposed_for_lxx", "transposition", contextual=True),
    "trl": _spec("transliterated_hebrew", "translation_technique"),
    "V": _spec("vocalization_difference", "translation_technique"),
    "vb": _spec("verb", "grammatical_label"),
    "v": _spec("verse_reference", "reference", contextual=True),
    "{XTM}": _spec("contextual_influence", "translation_technique", contextual=True),
    "[z]": _spec("ziegler_preferred_variant", "textual", contextual=True),
}

_SIRACH: dict[str, NotationSpec] = {
    "[]": _spec("sirach_reconstructed_letters", "sirach_manuscript"),
    "[..]": _spec("sirach_lacuna_or_illegible", "sirach_manuscript"),
    "{}": _spec("sirach_manuscript_addition", "sirach_manuscript"),
    "{{}}": _spec("sirach_manuscript_addition", "sirach_manuscript"),
    ">": _spec("sirach_reading_lacking_in_witness", "sirach_manuscript"),
    "*": _spec("sirach_uncertain_fragmentary_letter", "sirach_manuscript"),
    "1": _spec("sirach_witness_geniza_b", "sirach_witness"),
    "2": _spec("sirach_witness_geniza_b_margin", "sirach_witness"),
    "3": _spec("sirach_witness_geniza_a", "sirach_witness"),
    "4": _spec("sirach_witness_geniza_c", "sirach_witness"),
    "5": _spec("sirach_witness_geniza_d", "sirach_witness"),
    "6": _spec("sirach_witness_geniza_e", "sirach_witness"),
    "7": _spec("sirach_witness_masada", "sirach_witness"),
    "8": _spec("sirach_witness_masada_corrector", "sirach_witness"),
    "9": _spec("sirach_witness_11qpsa", "sirach_witness"),
    "10": _spec("sirach_witness_2q18", "sirach_witness"),
}


def notation_spec(raw: str, *, book: str) -> NotationSpec | None:
    """Return documented semantics for raw, with book-sensitive collisions."""

    if book == "Sir":
        sirach = _SIRACH.get(raw)
        if sirach is not None:
            return sirach
    if raw.startswith("<sp") and raw.endswith(">"):
        return _spec("samaritan_apparatus_reference", "reference", contextual=True)
    return _GENERAL.get(raw)


def documented_notation() -> frozenset[str]:
    """Return exact documented catalogue keys, excluding patterned references."""

    return frozenset(_GENERAL) | frozenset(_SIRACH)
