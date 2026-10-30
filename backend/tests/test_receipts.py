from app.receipts import sanitize_receipt_items


def test_sanitize_receipt_items_excludes_totals_and_payment_lines():
    items = sanitize_receipt_items(
        [
            {"description": "DISPENSADOR ACEITE", "amount": "7000"},
            {"description": "TOTALES", "amount": 159000},
            {"description": "TRANSFERENCIA TARJ CREDITO", "amount": 159000},
            {"description": "SON: CIENTO CINCUENTA Y NUEVE MIL", "amount": 159000},
            {"description": "CEPILLO 6 EN 1", "amount": "65000"},
        ]
    )

    assert items == [
        {"description": "DISPENSADOR ACEITE", "amount": 7000},
        {"description": "CEPILLO 6 EN 1", "amount": 65000},
    ]
