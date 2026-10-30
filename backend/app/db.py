from __future__ import annotations

import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from .finance import account_delta, compute_balance, compute_shares


def get_database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL es obligatorio.")
    parsed = urlsplit(url)
    query = []
    for key, value in parse_qsl(parsed.query, keep_blank_values=True):
        if key in {"pgbouncer", "connection_limit"}:
            continue
        if key == "sslmode" and value == "no-verify":
            value = "require"
        query.append((key, value))
    return urlunsplit(parsed._replace(query=urlencode(query)))


def init_database() -> None:
    schema_path = Path(__file__).with_name("schema.sql")
    schema_sql = schema_path.read_text(encoding="utf-8")
    with psycopg.connect(get_database_url(), row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(schema_sql)
            conn.commit()


def fetch_all(sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    with psycopg.connect(get_database_url(), row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return list(cur.fetchall())


def fetch_one(sql: str, params: tuple[Any, ...] = ()) -> dict[str, Any] | None:
    with psycopg.connect(get_database_url(), row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchone()


def execute_returning(sql: str, params: tuple[Any, ...] = ()) -> dict[str, Any]:
    with psycopg.connect(get_database_url(), row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            result = cur.fetchone()
            conn.commit()
            if result is None:
                raise RuntimeError("La operacion no devolvio resultado.")
            return result


def execute_write(sql: str, params: tuple[Any, ...] = ()) -> None:
    with psycopg.connect(get_database_url(), row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            conn.commit()


def people_maps() -> tuple[dict[int, dict[str, Any]], dict[str, dict[str, Any]]]:
    people = fetch_all("select * from people order by id")
    by_id = {int(person["id"]): person for person in people}
    by_slug = {str(person["slug"]): person for person in people}
    return by_id, by_slug


def account_available(account: dict[str, Any]) -> int:
    if account.get("kind") == "credit":
        return max(int(account.get("credit_limit") or 0) - int(account.get("balance") or 0), 0)
    return int(account.get("balance") or 0)


def map_account(account: dict[str, Any], people_by_id: dict[int, dict[str, Any]]) -> dict[str, Any]:
    person = people_by_id.get(int(account["person_id"]), {})
    return {
        "id": account["id"],
        "name": account["name"],
        "type": account["type"],
        "kind": account["kind"],
        "balance": int(account.get("balance") or 0),
        "available": account_available(account),
        "creditLimit": account.get("credit_limit"),
        "cutoffDay": account.get("cutoff_day"),
        "dueDay": account.get("due_day"),
        "personSlug": person.get("slug"),
        "personName": person.get("name"),
        "isDefault": account.get("is_default"),
    }


def map_item(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": item["id"],
        "expenseId": item["expense_id"],
        "description": item["description"],
        "amount": int(item.get("amount") or 0),
        "assignedTo": item.get("assigned_to"),
    }


def map_expense(
    expense: dict[str, Any],
    people_by_id: dict[int, dict[str, Any]],
    items_by_expense: dict[int, list[dict[str, Any]]],
) -> dict[str, Any]:
    paid_by = people_by_id.get(int(expense["paid_by_person_id"]), {})
    return {
        "id": expense["id"],
        "title": expense["title"],
        "date": expense["date"],
        "totalAmount": int(expense.get("total_amount") or 0),
        "paidByPersonId": expense["paid_by_person_id"],
        "paidBy": paid_by.get("slug"),
        "paidByName": paid_by.get("name"),
        "accountId": expense.get("account_id"),
        "shareAna": int(expense.get("share_ana") or 0),
        "shareDaniel": int(expense.get("share_daniel") or 0),
        "surchargeAmount": int(expense.get("surcharge_amount") or 0),
        "receiptImageUrl": expense.get("receipt_image_url"),
        "source": expense.get("source"),
        "splitType": expense.get("split_type"),
        "createdAt": expense.get("created_at"),
        "items": items_by_expense.get(int(expense["id"]), []),
    }


def map_settlement(settlement: dict[str, Any], people_by_id: dict[int, dict[str, Any]]) -> dict[str, Any]:
    from_person = people_by_id.get(int(settlement["from_person_id"]), {})
    to_person = people_by_id.get(int(settlement["to_person_id"]), {})
    return {
        "id": settlement["id"],
        "fromPersonId": settlement["from_person_id"],
        "toPersonId": settlement["to_person_id"],
        "fromPerson": from_person.get("slug"),
        "toPerson": to_person.get("slug"),
        "amount": int(settlement.get("amount") or 0),
        "date": settlement["date"],
        "note": settlement.get("note"),
        "createdAt": settlement.get("created_at"),
    }


def get_expenses(people_by_id: dict[int, dict[str, Any]], limit: int = 200) -> list[dict[str, Any]]:
    expenses = fetch_all("select * from expenses order by date desc, id desc limit %s", (limit,))
    ids = [expense["id"] for expense in expenses]
    items_by_expense: dict[int, list[dict[str, Any]]] = {}
    if ids:
        items = fetch_all("select * from expense_items where expense_id = any(%s) order by id", (ids,))
        for item in items:
            items_by_expense.setdefault(int(item["expense_id"]), []).append(map_item(item))
    return [map_expense(expense, people_by_id, items_by_expense) for expense in expenses]


def get_settlements(people_by_id: dict[int, dict[str, Any]], limit: int = 200) -> list[dict[str, Any]]:
    settlements = fetch_all("select * from settlements order by date desc, id desc limit %s", (limit,))
    return [map_settlement(settlement, people_by_id) for settlement in settlements]


def get_account_transactions(account_id: int, limit: int = 100) -> list[dict[str, Any]]:
    rows = fetch_all(
        """
        select *
        from account_transactions
        where account_id = %s
        order by date desc, id desc
        limit %s
        """,
        (account_id, limit),
    )
    return [
        {
            "id": row["id"],
            "accountId": row["account_id"],
            "type": row["type"],
            "amount": int(row.get("amount") or 0),
            "description": row.get("description"),
            "date": row.get("date"),
            "createdAt": row.get("created_at"),
            "relatedExpenseId": row.get("related_expense_id"),
        }
        for row in rows
    ]


def bootstrap() -> dict[str, Any]:
    people_by_id, _people_by_slug = people_maps()
    accounts = fetch_all("select * from accounts order by id")
    expenses = get_expenses(people_by_id)
    settlements = get_settlements(people_by_id)
    balance = compute_balance(
        [
            {
                "id": expense["id"],
                "title": expense["title"],
                "date": expense["date"],
                "total_amount": expense["totalAmount"],
                "paid_by": expense["paidBy"],
                "share_ana": expense["shareAna"],
                "share_daniel": expense["shareDaniel"],
            }
            for expense in expenses
        ],
        [
            {
                "from_person": settlement["fromPerson"],
                "to_person": settlement["toPerson"],
                "amount": settlement["amount"],
            }
            for settlement in settlements
        ],
    )
    return {
        "ok": True,
        "balance": balance,
        "accounts": [map_account(account, people_by_id) for account in accounts],
        "expenses": expenses,
        "settlements": settlements,
    }


def upload_receipt_image(buffer: bytes, mime_type: str) -> str | None:
    try:
        inserted = execute_returning(
            """
            insert into receipt_blobs (content_type, data)
            values (%s, %s)
            returning id
            """,
            (mime_type, buffer),
        )
        return f"/receipts/images/{inserted['id']}"
    except Exception:
        return None


def get_receipt_blob(image_id: int) -> dict[str, Any] | None:
    return fetch_one("select content_type, data from receipt_blobs where id = %s", (image_id,))


def create_receipt_draft(image_url: str | None, merchant: str | None, items: list[dict[str, Any]], ai_note: str | None) -> dict[str, Any]:
    return execute_returning(
        """
        insert into receipt_drafts (image_url, merchant_guess, items, ai_note)
        values (%s, %s, %s::jsonb, %s)
        returning *
        """,
        (image_url, merchant, Jsonb(items), ai_note),
    )


def normalize_assignment(value: str | None) -> str:
    if value in {"ana", "daniel", "equal"}:
        return value
    if value == "half":
        return "equal"
    return "equal"


def update_account_for_transaction(client, account_id: int, tx_type: str, amount: int) -> None:
    account = fetch_one("select * from accounts where id = %s", (account_id,))
    if not account:
        return
    delta = account_delta(str(account.get("kind")), tx_type, amount)
    execute_write("update accounts set balance = %s where id = %s", (int(account.get("balance") or 0) + delta, account_id))


def save_expense(payload: dict[str, Any]) -> dict[str, Any]:
    title = str(payload.get("title") or "").strip()
    total_amount = round(float(payload.get("totalAmount") or payload.get("total_amount") or 0))
    paid_by_person_id = int(payload.get("paidByPersonId") or payload.get("paid_by_person_id") or 0)
    account_id = payload.get("accountId") or payload.get("account_id")
    account_id = int(account_id) if account_id else None
    expense_date = str(payload.get("expenseDate") or payload.get("date") or datetime.now(UTC).date().isoformat())
    split_type = str(payload.get("splitType") or payload.get("split_type") or "half")
    surcharge_amount = round(float(payload.get("surchargeAmount") or payload.get("surcharge_amount") or 0))
    already_paid = bool(payload.get("alreadyPaid") or payload.get("already_paid"))
    source = "receipt" if payload.get("source") == "scan" else str(payload.get("source") or "manual")

    items = []
    for item in payload.get("items") or []:
        description = str(item.get("description") or item.get("name") or "").strip()[:120]
        amount = round(float(item.get("amount") or 0))
        assigned_to = normalize_assignment(item.get("assignedTo") or item.get("assigned_to"))
        if description and amount > 0:
            items.append({"description": description, "amount": amount, "assigned_to": assigned_to})

    if not title:
        raise ValueError("Falta el titulo.")
    if total_amount <= 0:
        raise ValueError("Monto invalido.")

    db_split_type = {
        "half": "equal",
        "by_items": "items",
        "all_daniel": "full_daniel",
        "all_ana": "full_ana",
    }.get(split_type, split_type)
    share_items = [{"amount": item["amount"], "assigned_to": item["assigned_to"]} for item in items]
    shares = compute_shares(total_amount, db_split_type, share_items)

    inserted = execute_returning(
        """
        insert into expenses
          (title, total_amount, date, paid_by_person_id, account_id, split_type,
           share_ana, share_daniel, surcharge_amount, surcharge_split_type,
           notes, receipt_image_url, source)
        values (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'equal', %s, %s, %s)
        returning *
        """,
        (
            title,
            total_amount,
            expense_date,
            paid_by_person_id,
            account_id,
            db_split_type,
            shares["share_ana"],
            shares["share_daniel"],
            surcharge_amount,
            payload.get("note") or ("Historico: ya estaba pagado" if already_paid else None),
            payload.get("imageUrl") or payload.get("image_url"),
            source,
        ),
    )

    if items:
        with psycopg.connect(get_database_url(), row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                cur.executemany(
                    "insert into expense_items (expense_id, description, amount, assigned_to) values (%s, %s, %s, %s)",
                    [(inserted["id"], item["description"], item["amount"], item["assigned_to"]) for item in items],
                )
                conn.commit()

    if account_id and not already_paid:
        update_account_for_transaction(None, account_id, "expense", total_amount)
        execute_write(
            """
            insert into account_transactions (account_id, type, amount, description, date, related_expense_id)
            values (%s, 'expense', %s, %s, %s, %s)
            """,
            (account_id, -total_amount, title, expense_date, inserted["id"]),
        )

    return {"expenseId": inserted["id"], "totalAmount": total_amount}


def confirm_receipt(payload: dict[str, Any]) -> dict[str, Any]:
    draft_id = int(payload.get("draftId") or payload.get("draft_id") or 0)
    draft = fetch_one("select * from receipt_drafts where id = %s", (draft_id,))
    if not draft:
        raise ValueError("No se encontro la factura.")

    _people_by_id, people_by_slug = people_maps()
    paid_by_slug = "ana" if payload.get("paidBy") == "ana" else "daniel"
    paid_by = people_by_slug.get(paid_by_slug)
    if not paid_by:
        raise ValueError("Persona invalida.")

    raw_items = payload.get("items") or []
    items = []
    for item in raw_items:
        description = str(item.get("description") or "").strip()[:120]
        amount = round(float(item.get("amount") or 0))
        assigned_to = normalize_assignment(item.get("assignedTo") or item.get("assigned_to"))
        if description and amount > 0:
            items.append({"description": description, "amount": amount, "assigned_to": assigned_to})
    if not items:
        raise ValueError("Faltan conceptos para guardar.")

    subtotal = sum(item["amount"] for item in items)
    surcharge_percent = float(payload.get("surchargePercent") or 0) if payload.get("addSurcharge") else 0
    surcharge_amount = round((subtotal * surcharge_percent) / 100)
    if surcharge_amount > 0:
        items_for_shares = [{"amount": item["amount"], "assigned_to": item["assigned_to"]} for item in items]
        items_for_shares.append({"amount": surcharge_amount, "assigned_to": "equal"})
    else:
        items_for_shares = [{"amount": item["amount"], "assigned_to": item["assigned_to"]} for item in items]
    total_amount = subtotal + surcharge_amount
    shares = compute_shares(total_amount, "items", items_for_shares)

    account_id = int(payload["accountId"]) if payload.get("accountId") else None
    expense_date = str(payload.get("date") or datetime.now(UTC).date().isoformat())
    title = str(payload.get("title") or draft.get("merchant_guess") or "Factura").strip()
    inserted = execute_returning(
        """
        insert into expenses
          (title, total_amount, date, paid_by_person_id, account_id, split_type,
           share_ana, share_daniel, surcharge_amount, surcharge_split_type,
           receipt_image_url, source)
        values (%s, %s, %s, %s, %s, 'items', %s, %s, %s, 'equal', %s, 'receipt')
        returning *
        """,
        (
            title,
            total_amount,
            expense_date,
            paid_by["id"],
            account_id,
            shares["share_ana"],
            shares["share_daniel"],
            surcharge_amount,
            draft.get("image_url"),
        ),
    )

    with psycopg.connect(get_database_url(), row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.executemany(
                "insert into expense_items (expense_id, description, amount, assigned_to) values (%s, %s, %s, %s)",
                [(inserted["id"], item["description"], item["amount"], item["assigned_to"]) for item in items],
            )
            conn.commit()

    if account_id:
        update_account_for_transaction(None, account_id, "expense", total_amount)
        execute_write(
            """
            insert into account_transactions (account_id, type, amount, description, date, related_expense_id)
            values (%s, 'expense', %s, %s, %s, %s)
            """,
            (account_id, -total_amount, inserted["title"], inserted["date"], inserted["id"]),
        )

    execute_write("delete from receipt_drafts where id = %s", (draft_id,))
    return {"expenseId": inserted["id"], "totalAmount": total_amount}


def save_settlement(payload: dict[str, Any]) -> dict[str, Any]:
    amount = round(float(payload.get("amount") or 0))
    if amount <= 0:
        raise ValueError("Monto invalido.")
    account_id = payload.get("accountId") or payload.get("account_id")
    account_id = int(account_id) if account_id else None
    settlement_date = str(payload.get("date") or datetime.now(UTC).date().isoformat())

    inserted = execute_returning(
        """
        insert into settlements (from_person_id, to_person_id, amount, from_account_id, date, note)
        values (%s, %s, %s, %s, %s, %s)
        returning *
        """,
        (
            int(payload.get("fromPersonId") or payload.get("from_person_id")),
            int(payload.get("toPersonId") or payload.get("to_person_id")),
            amount,
            account_id,
            settlement_date,
            payload.get("note"),
        ),
    )

    if account_id:
        update_account_for_transaction(None, account_id, "payment", amount)
        execute_write(
            """
            insert into account_transactions (account_id, type, amount, description, date)
            values (%s, 'payment', %s, %s, %s)
            """,
            (account_id, -amount, payload.get("note") or "Pago entre Ana y Daniel", settlement_date),
        )

    return {"settlementId": inserted["id"], "amount": amount}


GOAL_FREQUENCIES = {"una_vez", "semanal", "mensual", "anual"}


def map_goal(row: dict[str, Any]) -> dict[str, Any]:
    deadline = row.get("deadline")
    return {
        "id": row["id"],
        "name": row["name"],
        "target_amount": int(row["target_amount"]),
        "frequency": row["frequency"],
        "deadline": deadline.isoformat() if deadline else None,
        "current_saved": int(row.get("current_saved") or 0),
        "notes": row.get("notes"),
    }


def fetch_one_write(sql: str, params: tuple[Any, ...] = ()) -> dict[str, Any] | None:
    with psycopg.connect(get_database_url(), row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            result = cur.fetchone()
            conn.commit()
            return result


def list_goals() -> list[dict[str, Any]]:
    return [map_goal(row) for row in fetch_all("select * from goals order by id")]


def get_goal(goal_id: int) -> dict[str, Any] | None:
    row = fetch_one("select * from goals where id = %s", (goal_id,))
    return map_goal(row) if row else None


def create_goal(payload: dict[str, Any]) -> dict[str, Any]:
    row = execute_returning(
        """
        insert into goals (name, target_amount, frequency, deadline, current_saved, notes)
        values (%s, %s, %s, %s, %s, %s)
        returning *
        """,
        (
            payload["name"],
            payload["target_amount"],
            payload["frequency"],
            payload.get("deadline"),
            payload.get("current_saved", 0),
            payload.get("notes"),
        ),
    )
    return map_goal(row)


def update_goal(goal_id: int, payload: dict[str, Any]) -> dict[str, Any] | None:
    allowed = ("name", "target_amount", "frequency", "deadline", "current_saved", "notes")
    fields = [key for key in allowed if key in payload]
    if not fields:
        return get_goal(goal_id)
    assignments = ", ".join(f"{key} = %s" for key in fields)
    row = fetch_one_write(
        f"update goals set {assignments} where id = %s returning *",
        tuple(payload[key] for key in fields) + (goal_id,),
    )
    return map_goal(row) if row else None


def delete_goal(goal_id: int) -> bool:
    return fetch_one_write("delete from goals where id = %s returning id", (goal_id,)) is not None


def get_expenses_for_month(year: int, month: int) -> list[dict[str, Any]]:
    return fetch_all(
        """
        select id, title, total_amount, date, share_ana, share_daniel
        from expenses
        where date >= make_date(%s, %s, 1)
          and date < make_date(%s, %s, 1) + interval '1 month'
        order by date, id
        """,
        (year, month, year, month),
    )
