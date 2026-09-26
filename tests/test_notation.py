from catss_tf.notation import documented_notation, notation_spec


def test_documented_general_notation_is_typed() -> None:
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


def test_context_bearing_notation_is_explicit() -> None:
    for raw in ("GTran", "HTran", "DR", "Ety", "EtyA", "Pr", "Pr?", "Pr~", "R", "[ce]"):
        spec = notation_spec(raw, book="Ge")
        assert spec is not None
        assert spec.contextual is True


def test_sirach_collision_is_book_sensitive() -> None:
    general_star = notation_spec("*", book="Ge")
    sirach_star = notation_spec("*", book="Sir")
    general_square = notation_spec("[..]", book="Ge")
    sirach_square = notation_spec("[..]", book="Sir")
    assert general_star is not None and general_star.kind == "asterisked_passage"
    assert sirach_star is not None and sirach_star.kind == "sirach_uncertain_fragmentary_letter"
    assert general_square is not None and general_square.kind == "unreadable_or_greek_addition"
    assert sirach_square is not None and sirach_square.kind == "sirach_lacuna_or_illegible"


def test_unknown_notation_has_no_fallback() -> None:
    assert notation_spec("definitely-not-catss", book="Ge") is None


def test_every_documented_notation_has_a_spec() -> None:
    for raw in documented_notation():
        book = "Sir" if raw in {"[]", "{}", "{{}}", ">", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"} else "Ge"
        assert notation_spec(raw, book=book) is not None


def test_patterned_samaritan_reference_is_typed() -> None:
    spec = notation_spec("<sp26.35ap>", book="Ge")
    assert spec is not None
    assert spec.kind == "samaritan_apparatus_reference"
    assert spec.contextual is True
