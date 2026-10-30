from __future__ import annotations

from typing import Any


ANA = "ana"
DANIEL = "daniel"


def split_equal(amount: int) -> dict[str, int]:
    ana = amount // 2
    return {"share_ana": ana, "share_daniel": amount - ana}


def compute_shares(total_amount: int, split_type: str, items: list[dict[str, Any]] | None = None) -> dict[str, int]:
    if split_type in {"full_daniel", "all_daniel"}:
        return {"share_ana": 0, "share_daniel": total_amount}
    if split_type in {"full_ana", "all_ana"}:
        return {"share_ana": total_amount, "share_daniel": 0}

    if split_type in {"items", "by_items"} and items:
        share_ana = 0
        share_daniel = 0
        for item in items:
            amount = int(item.get("amount") or 0)
            assigned = item.get("assigned_to") or item.get("assignedTo")
            if assigned == ANA:
                share_ana += amount
            elif assigned == DANIEL:
                share_daniel += amount
            else:
                split = split_equal(amount)
                share_ana += split["share_ana"]
                share_daniel += split["share_daniel"]

        remainder = total_amount - share_ana - share_daniel
        if remainder > 0:
            split = split_equal(remainder)
            share_ana += split["share_ana"]
            share_daniel += split["share_daniel"]
        return {"share_ana": share_ana, "share_daniel": share_daniel}

    return split_equal(total_amount)


def compute_balance(expenses: list[dict[str, Any]], settlements: list[dict[str, Any]]) -> dict[str, Any]:
    net = 0
    movements: list[dict[str, Any]] = []

    for expense in expenses:
        paid_by = expense.get("paid_by") or expense.get("paidBy")
        share_ana = int(expense.get("share_ana") or expense.get("shareAna") or 0)
        share_daniel = int(expense.get("share_daniel") or expense.get("shareDaniel") or 0)

        delta = 0
        if paid_by == DANIEL:
            delta = share_ana
        elif paid_by == ANA:
            delta = -share_daniel

        net += delta
        if delta:
            movements.append(
                {
                    "kind": "expense",
                    "id": expense.get("id"),
                    "date": expense.get("date"),
                    "title": expense.get("title"),
                    "delta": delta,
                    "amount": expense.get("total_amount") or expense.get("totalAmount"),
                }
            )

    for settlement in settlements:
        from_person = settlement.get("from_person") or settlement.get("fromPerson")
        to_person = settlement.get("to_person") or settlement.get("toPerson")
        amount = int(settlement.get("amount") or 0)
        if from_person == ANA and to_person == DANIEL:
            net -= amount
        elif from_person == DANIEL and to_person == ANA:
            net += amount

    if net > 0:
        owes = ANA
        owed = DANIEL
    elif net < 0:
        owes = DANIEL
        owed = ANA
    else:
        owes = None
        owed = None

    return {"net": net, "owes": owes, "owed": owed, "amount": abs(net), "movements": movements}


def account_delta(kind: str, tx_type: str, amount: int) -> int:
    if tx_type == "reconciliation":
        return amount
    if kind == "credit":
        if tx_type in {"expense", "transfer_out"}:
            return amount
        if tx_type in {"payment", "transfer_in", "income"}:
            return -amount
        return 0
    if tx_type in {"income", "transfer_in"}:
        return amount
    if tx_type in {"expense", "transfer_out", "payment"}:
        return -amount
    return 0
