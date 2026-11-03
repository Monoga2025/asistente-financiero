from app.expense_text import parse_amount, parse_expenses_text, parse_voice_expense_command


def test_parse_amount_handles_colombian_formats():
    assert parse_amount("5000") == 5000
    assert parse_amount("$5.000") == 5000
    assert parse_amount("12.500") == 12500
    assert parse_amount("3 mil") == 3000
    assert parse_amount("cinco mil") == 5000
    assert parse_amount("tres mil quinientos") == 3500
    assert parse_amount("cuarenta y cinco mil") == 45000
    assert parse_amount("2k") == 2000
    assert parse_amount("1,5 millones") == 1_500_000


def test_parse_amount_rejects_non_amounts():
    assert parse_amount("pan") is None
    assert parse_amount("") is None


def test_parse_expenses_text_splits_items_with_amounts():
    items = parse_expenses_text("pan 5000, cafe 3 mil\nuber $12.500 y arriendo 700.000")

    assert items == [
        {"description": "pan", "amount": 5000},
        {"description": "cafe", "amount": 3000},
        {"description": "uber", "amount": 12500},
        {"description": "arriendo", "amount": 700000},
    ]


def test_parse_expenses_text_handles_spoken_spanish_numbers():
    items = parse_expenses_text("pan cinco mil, cafe tres mil quinientos, leche seis mil")

    assert items == [
        {"description": "pan", "amount": 5000},
        {"description": "cafe", "amount": 3500},
        {"description": "leche", "amount": 6000},
    ]


def test_parse_voice_expense_command_extracts_metadata():
    cmd = parse_voice_expense_command("Almuerzo cuarenta y cinco mil pagó Silvia con Nequi mitad y mitad")
    assert cmd["totalAmount"] == 45000
    assert cmd["paidBy"] == "silvia"
    assert cmd["bankHint"] == "nequi"
    assert cmd["splitType"] == "half"
    assert cmd["items"] == [{"description": "Almuerzo", "amount": 45000}]


def test_parse_expenses_text_drops_fragments_without_amount_or_description():
    assert parse_expenses_text("hola, 5000, mercado 20000") == [{"description": "mercado", "amount": 20000}]
    assert parse_expenses_text("   ") == []
