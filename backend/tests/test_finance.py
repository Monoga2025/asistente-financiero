from app.finance import compute_balance, compute_shares


def test_compute_shares_for_items_and_equal_remainders():
    shares = compute_shares(
        total_amount=163_770,
        split_type="items",
        items=[
            {"amount": 7_000, "assigned_to": "equal"},
            {"amount": 65_000, "assigned_to": "ana"},
            {"amount": 4_770, "assigned_to": "equal"},
        ],
    )

    assert shares == {"share_daniel": 49_385, "share_ana": 114_385}


def test_compute_balance_matches_current_household_debt():
    expenses = [
        {"id": 1, "title": "Paco lavanderia", "date": "2026-07-30", "total_amount": 20_000, "paid_by": "daniel", "share_ana": 10_000, "share_daniel": 10_000},
        {"id": 2, "title": "Consumidor final", "date": "2026-07-28", "total_amount": 163_770, "paid_by": "daniel", "share_ana": 114_385, "share_daniel": 49_385},
        {"id": 3, "title": "Ferrecentral", "date": "2026-07-28", "total_amount": 37_500, "paid_by": "ana", "share_ana": 18_750, "share_daniel": 18_750},
        {"id": 4, "title": "Ferrecentral", "date": "2026-07-28", "total_amount": 12_300, "paid_by": "ana", "share_ana": 6_150, "share_daniel": 6_150},
        {"id": 5, "title": "Arriendo", "date": "2026-06-30", "total_amount": 700_000, "paid_by": "daniel", "share_ana": 300_000, "share_daniel": 400_000},
    ]

    balance = compute_balance(expenses, settlements=[])

    assert balance["net"] == 399_485
    assert balance["owes"] == "ana"
    assert balance["owed"] == "daniel"
    assert balance["amount"] == 399_485
