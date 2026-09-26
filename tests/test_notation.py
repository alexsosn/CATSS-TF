from catss_tf.notation import notation_spec


def test_documented_general_notation_is_typed():
    cases = {
        "Ap+": ("apparent_plus", "alignment"),
        "GTran": ("greek_transposition", "transposition"),
        "DR": ("distributive_rendering", "translation_technique"),
        "I:nd+": ("inf_abs_dative_without_mt_inf_abs", "infinitive_absolute"),
        "Pr~": ("preposition_added_transposed", "preposition"),
        "sp~": ("samaritan_partial_match", "textual_comparison"),
        "{XTM}": ("contextual_influence", "translation_technique"),
    }
    for raw, (kind, family) in cases.items():
        spec = notation_spec(raw, book="Ge")
        assert spec is not None
        assert (spec.kind, spec.family) == (kind, family)


def test_context_bearing_notation_is_explicit():
    for raw in ("GTran", "HTran", "DR", "Ety", "EtyA", "Pr", "Pr?", "Pr~", "R", "[ce]"):
        spec = notation_spec(raw, book="Ge")
        assert spec is not None
        assert spec.contextual is True


def test_sirach_collision_is_book_sensitive():
    assert notation_spec("*", book="Ge").kind == "asterisked_passage"
    assert notation_spec("*", book="Sir").kind == "sirach_uncertain_fragmentary_letter"
    assert notation_spec("[..]", book="Ge").kind == "unreadable_or_greek_addition"
    assert notation_spec("[..]", book="Sir").kind == "sirach_lacuna_or_illegible"


def test_unknown_notation_has_no_fallback():
    assert notation_spec("definitely-not-catss", book="Ge") is None
