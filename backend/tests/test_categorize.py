from app.categorize import CATEGORIES, categorize_by_rules, normalize_category


def test_rules_map_known_keywords_to_categories():
    assert categorize_by_rules("Almuerzo en restaurante") == "Alimentacion"
    assert categorize_by_rules("Uber al aeropuerto") == "Transporte"
    assert categorize_by_rules("Pago arriendo") == "Vivienda"
    assert categorize_by_rules("Netflix") == "Ocio"


def test_rules_are_accent_and_case_insensitive():
    assert categorize_by_rules("CAFÉ con pan") == "Alimentacion"


def test_unknown_description_falls_back_to_otros():
    assert categorize_by_rules("zzz qqq") == "Otros"
    assert categorize_by_rules("") == "Otros"


def test_normalize_category_only_accepts_fixed_list():
    assert normalize_category("transporte") == "Transporte"
    assert normalize_category("Respuesta: Salud.") == "Salud"
    assert normalize_category("categoria inventada") == "Otros"
    assert "Otros" in CATEGORIES
