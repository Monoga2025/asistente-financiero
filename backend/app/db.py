from __future__ import annotations

import base64
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from .finance import account_delta, compute_balance, compute_shares

LOCAL_STORE_PATH = Path(__file__).resolve().parent.parent / "cuentas_claras_local.json"


def _use_local_store() -> bool:
    url = (os.getenv("DATABASE_URL") or "").strip()
    return not url or url.lower() in {"local", "sqlite", "json"}


def _default_local_state() -> dict[str, Any]:
    return {
        "people": [
            {"id": 1, "slug": "ana", "name": "Silvia", "color": "#e0578e", "created_at": "2026-08-01T00:00:00"},
            {"id": 2, "slug": "daniel", "name": "Daniel", "color": "#2f6fed", "created_at": "2026-08-01T00:00:00"},
        ],
        "accounts": [
            {"id": 1, "person_id": 1, "name": "Nequi", "type": "nequi", "kind": "debit", "balance": 0, "is_default": True, "credit_limit": None, "cutoff_day": None, "due_day": None, "created_at": "2026-08-01T00:00:00"},
            {"id": 2, "person_id": 1, "name": "Nu Ahorros", "type": "nu_ahorros", "kind": "debit", "balance": 0, "is_default": False, "credit_limit": None, "cutoff_day": None, "due_day": None, "created_at": "2026-08-01T00:00:00"},
            {"id": 3, "person_id": 2, "name": "Nequi", "type": "nequi", "kind": "debit", "balance": 0, "is_default": True, "credit_limit": None, "cutoff_day": None, "due_day": None, "created_at": "2026-08-01T00:00:00"},
            {"id": 4, "person_id": 2, "name": "Nu Ahorros", "type": "nu_ahorros", "kind": "debit", "balance": 0, "is_default": False, "credit_limit": None, "cutoff_day": None, "due_day": None, "created_at": "2026-08-01T00:00:00"},
            {"id": 5, "person_id": 2, "name": "Nu Credito", "type": "nu_credito", "kind": "credit", "balance": 0, "is_default": False, "credit_limit": 1000000, "cutoff_day": 15, "due_day": 4, "created_at": "2026-08-01T00:00:00"},
        ],
        "expenses": [],
        "expense_items": [],
        "settlements": [],
        "account_transactions": [],
        "receipt_drafts": [],
        "receipt_blobs": [],
        "goals": [],
    }


def _load_local() -> dict[str, Any]:
    if not LOCAL_STORE_PATH.exists():
        state = _default_local_state()
        _save_local(state)
        return state
    try:
        return json.loads(LOCAL_STORE_PATH.read_text(encoding="utf-8"))
    except Exception:
        state = _default_local_state()
        _save_local(state)
        return state


def _save_local(state: dict[str, Any]) -> None:
    LOCAL_STORE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def _next_id(items: list[dict[str, Any]]) -> int:
    return max((int(item.get("id") or 0) for item in items), default=0) + 1


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
    if _use_local_store():
        _load_local()
        return
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
    people = _load_local()["people"] if _use_local_store() else fetch_all("select * from people order by id")
    by_id = {int(person["id"]): person for person in people}
    by_slug = {str(person["slug"]): person for person in people}
    if "ana" in by_slug and "silvia" not in by_slug:
        by_slug["silvia"] = by_slug["ana"]
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
        "date": str(expense["date"]),
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
        "createdAt": str(expense.get("created_at") or ""),
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
        "date": str(settlement["date"]),
        "note": settlement.get("note"),
        "createdAt": str(settlement.get("created_at") or ""),
    }


def get_expenses(people_by_id: dict[int, dict[str, Any]], limit: int = 200) -> list[dict[str, Any]]:
    if _use_local_store():
        state = _load_local()
        expenses = sorted(state["expenses"], key=lambda e: (str(e.get("date") or ""), int(e["id"])), reverse=True)[:limit]
        items_by_expense: dict[int, list[dict[str, Any]]] = {}
        for item in state["expense_items"]:
            items_by_expense.setdefault(int(item["expense_id"]), []).append(map_item(item))
        return [map_expense(expense, people_by_id, items_by_expense) for expense in expenses]

    expenses = fetch_all("select * from expenses order by date desc, id desc limit %s", (limit,))
    ids = [expense["id"] for expense in expenses]
    items_by_expense = {}
    if ids:
        items = fetch_all("select * from expense_items where expense_id = any(%s) order by id", (ids,))
        for item in items:
            items_by_expense.setdefault(int(item["expense_id"]), []).append(map_item(item))
    return [map_expense(expense, people_by_id, items_by_expense) for expense in expenses]


def get_settlements(people_by_id: dict[int, dict[str, Any]], limit: int = 200) -> list[dict[str, Any]]:
    if _use_local_store():
        state = _load_local()
        settlements = sorted(state["settlements"], key=lambda s: (str(s.get("date") or ""), int(s["id"])), reverse=True)[:limit]
        return [map_settlement(settlement, people_by_id) for settlement in settlements]

    settlements = fetch_all("select * from settlements order by date desc, id desc limit %s", (limit,))
    return [map_settlement(settlement, people_by_id) for settlement in settlements]


def get_account_transactions(account_id: int, limit: int = 100) -> list[dict[str, Any]]:
    if _use_local_store():
        state = _load_local()
        rows = [r for r in state["account_transactions"] if int(r["account_id"]) == int(account_id)]
        rows = sorted(rows, key=lambda r: (str(r.get("date") or ""), int(r["id"])), reverse=True)[:limit]
    else:
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
            "date": str(row.get("date") or ""),
            "createdAt": str(row.get("created_at") or ""),
            "relatedExpenseId": row.get("related_expense_id"),
        }
        for row in rows
    ]


def bootstrap() -> dict[str, Any]:
    people_by_id, _people_by_slug = people_maps()
    accounts = _load_local()["accounts"] if _use_local_store() else fetch_all("select * from accounts order by id")
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
    if _use_local_store():
        state = _load_local()
        blob_id = _next_id(state["receipt_blobs"])
        state["receipt_blobs"].append(
            {
                "id": blob_id,
                "content_type": mime_type,
                "data_b64": base64.b64encode(buffer).decode("ascii"),
                "created_at": datetime.now(UTC).isoformat(),
            }
        )
        _save_local(state)
        return f"/receipts/images/{blob_id}"
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
    if _use_local_store():
        state = _load_local()
        found = next((b for b in state["receipt_blobs"] if int(b["id"]) == int(image_id)), None)
        if not found:
            return None
        return {"content_type": found["content_type"], "data": base64.b64decode(found["data_b64"])}
    return fetch_one("select content_type, data from receipt_blobs where id = %s", (image_id,))


def create_receipt_draft(image_url: str | None, merchant: str | None, items: list[dict[str, Any]], ai_note: str | None) -> dict[str, Any]:
    if _use_local_store():
        state = _load_local()
        draft = {
            "id": _next_id(state["receipt_drafts"]),
            "image_url": image_url,
            "merchant_guess": merchant,
            "items": items,
            "ai_note": ai_note,
            "status": "pending",
            "created_at": datetime.now(UTC).isoformat(),
        }
        state["receipt_drafts"].append(draft)
        _save_local(state)
        return draft
    return execute_returning(
        """
        insert into receipt_drafts (image_url, merchant_guess, items, ai_note)
        values (%s, %s, %s::jsonb, %s)
        returning *
        """,
        (image_url, merchant, Jsonb(items), ai_note),
    )


def normalize_assignment(value: str | None) -> str:
    if value in {"ana", "silvia"}:
        return "ana"
    if value in {"daniel", "equal"}:
        return value
    if value == "half":
        return "equal"
    return "equal"


def update_account_for_transaction(client, account_id: int, tx_type: str, amount: int) -> None:
    if _use_local_store():
        state = _load_local()
        account = next((a for a in state["accounts"] if int(a["id"]) == int(account_id)), None)
        if not account:
            return
        delta = account_delta(str(account.get("kind")), tx_type, amount)
        account["balance"] = int(account.get("balance") or 0) + delta
        _save_local(state)
        return
    account = fetch_one("select * from accounts where id = %s", (account_id,))
    if not account:
        return
    delta = account_delta(str(account.get("kind")), tx_type, amount)
    execute_write("update accounts set balance = %s where id = %s", (int(account.get("balance") or 0) + delta, account_id))


def create_account(payload: dict[str, Any]) -> dict[str, Any]:
    person_id = int(payload.get("personId") or payload.get("person_id") or 0)
    if person_id not in {1, 2}:
        raise ValueError("Persona invalida.")
    name = str(payload.get("name") or "").strip()
    if not name:
        raise ValueError("Nombre de cuenta obligatorio.")
    kind = "credit" if payload.get("kind") == "credit" or payload.get("type") == "credit" else "debit"
    bank = str(payload.get("bank") or payload.get("type") or "nequi").strip().lower()
    db_type = "nu_credito" if kind == "credit" else ("nu_ahorros" if "nu" in bank else "nequi")
    balance = round(float(payload.get("balance") or 0))
    credit_limit = round(float(payload.get("creditLimit") or payload.get("credit_limit") or 0)) if kind == "credit" else None
    cutoff_day = int(payload.get("cutoffDay") or payload.get("cutoff_day") or 15) if kind == "credit" else None
    due_day = int(payload.get("dueDay") or payload.get("due_day") or 4) if kind == "credit" else None
    is_default = bool(payload.get("isDefault") or payload.get("is_default") or False)

    if _use_local_store():
        state = _load_local()
        row = {
            "id": _next_id(state["accounts"]),
            "person_id": person_id,
            "name": name,
            "type": db_type,
            "kind": kind,
            "balance": balance,
            "is_default": is_default,
            "credit_limit": credit_limit,
            "cutoff_day": cutoff_day,
            "due_day": due_day,
            "created_at": datetime.now(UTC).isoformat(),
        }
        state["accounts"].append(row)
        _save_local(state)
    else:
        row = execute_returning(
            """
            insert into accounts (person_id, name, type, kind, balance, is_default, credit_limit, cutoff_day, due_day)
            values (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            returning *
            """,
            (person_id, name, db_type, kind, balance, is_default, credit_limit, cutoff_day, due_day),
        )
    people_by_id, _ = people_maps()
    return map_account(row, people_by_id)


def update_account(account_id: int, payload: dict[str, Any]) -> dict[str, Any]:
    if _use_local_store():
        state = _load_local()
        existing = next((a for a in state["accounts"] if int(a["id"]) == int(account_id)), None)
        if not existing:
            raise ValueError("Cuenta no encontrada.")
        name = str(payload.get("name") if payload.get("name") is not None else existing["name"]).strip()
        if not name:
            raise ValueError("Nombre de cuenta obligatorio.")
        new_balance = round(float(payload["balance"])) if "balance" in payload and payload["balance"] is not None else int(existing["balance"])
        credit_limit = (
            round(float(payload["creditLimit"]))
            if "creditLimit" in payload and payload["creditLimit"] is not None
            else (round(float(payload["credit_limit"])) if "credit_limit" in payload and payload["credit_limit"] is not None else existing.get("credit_limit"))
        )
        cutoff_day = int(payload["cutoffDay"]) if "cutoffDay" in payload and payload["cutoffDay"] is not None else existing.get("cutoff_day")
        due_day = int(payload["dueDay"]) if "dueDay" in payload and payload["dueDay"] is not None else existing.get("due_day")
        old_balance = int(existing.get("balance") or 0)
        diff = new_balance - old_balance
        existing.update(name=name, balance=new_balance, credit_limit=credit_limit, cutoff_day=cutoff_day, due_day=due_day)
        if diff != 0:
            tx_date = str(payload.get("date") or datetime.now(UTC).date().isoformat())
            desc = str(payload.get("description") or ("Ajuste de cupo usado" if existing.get("kind") == "credit" else "Ajuste de saldo")).strip()
            tx_amount = -diff if existing.get("kind") == "credit" else diff
            state["account_transactions"].append(
                {
                    "id": _next_id(state["account_transactions"]),
                    "account_id": int(account_id),
                    "type": "reconciliation",
                    "amount": tx_amount,
                    "description": desc,
                    "date": tx_date,
                    "related_expense_id": None,
                    "created_at": datetime.now(UTC).isoformat(),
                }
            )
        _save_local(state)
        people_by_id, _ = people_maps()
        return map_account(existing, people_by_id)

    existing = fetch_one("select * from accounts where id = %s", (account_id,))
    if not existing:
        raise ValueError("Cuenta no encontrada.")

    name = str(payload.get("name") if payload.get("name") is not None else existing["name"]).strip()
    if not name:
        raise ValueError("Nombre de cuenta obligatorio.")
    new_balance = round(float(payload["balance"])) if "balance" in payload and payload["balance"] is not None else int(existing["balance"])
    credit_limit = (
        round(float(payload["creditLimit"]))
        if "creditLimit" in payload and payload["creditLimit"] is not None
        else (round(float(payload["credit_limit"])) if "credit_limit" in payload and payload["credit_limit"] is not None else existing.get("credit_limit"))
    )
    cutoff_day = int(payload["cutoffDay"]) if "cutoffDay" in payload and payload["cutoffDay"] is not None else existing.get("cutoff_day")
    due_day = int(payload["dueDay"]) if "dueDay" in payload and payload["dueDay"] is not None else existing.get("due_day")

    old_balance = int(existing.get("balance") or 0)
    diff = new_balance - old_balance

    row = execute_returning(
        """
        update accounts
        set name = %s, balance = %s, credit_limit = %s, cutoff_day = %s, due_day = %s
        where id = %s
        returning *
        """,
        (name, new_balance, credit_limit, cutoff_day, due_day, account_id),
    )

    if diff != 0:
        tx_date = str(payload.get("date") or datetime.now(UTC).date().isoformat())
        desc = str(payload.get("description") or ("Ajuste de cupo usado" if existing.get("kind") == "credit" else "Ajuste de saldo")).strip()
        tx_amount = -diff if existing.get("kind") == "credit" else diff
        execute_write(
            """
            insert into account_transactions (account_id, type, amount, description, date)
            values (%s, 'reconciliation', %s, %s, %s)
            """,
            (account_id, tx_amount, desc, tx_date),
        )

    people_by_id, _ = people_maps()
    return map_account(row, people_by_id)


def record_account_movement(account_id: int, payload: dict[str, Any]) -> dict[str, Any]:
    if _use_local_store():
        state = _load_local()
        existing = next((a for a in state["accounts"] if int(a["id"]) == int(account_id)), None)
        if not existing:
            raise ValueError("Cuenta no encontrada.")
        amount = round(float(payload.get("amount") or 0))
        if amount <= 0:
            raise ValueError("El monto debe ser mayor que cero.")
        tx_type = str(payload.get("type") or "income")
        if tx_type not in {"income", "expense", "payment"}:
            raise ValueError("Tipo de movimiento invalido.")
        description = str(payload.get("description") or ("Ingreso" if tx_type == "income" else "Movimiento")).strip()
        tx_date = str(payload.get("date") or datetime.now(UTC).date().isoformat())
        delta = account_delta(str(existing.get("kind")), tx_type, amount)
        existing["balance"] = int(existing.get("balance") or 0) + delta
        signed_amount = amount if tx_type == "income" else -amount
        state["account_transactions"].append(
            {
                "id": _next_id(state["account_transactions"]),
                "account_id": int(account_id),
                "type": tx_type,
                "amount": signed_amount,
                "description": description,
                "date": tx_date,
                "related_expense_id": None,
                "created_at": datetime.now(UTC).isoformat(),
            }
        )
        _save_local(state)
        people_by_id, _ = people_maps()
        return map_account(existing, people_by_id)

    existing = fetch_one("select * from accounts where id = %s", (account_id,))
    if not existing:
        raise ValueError("Cuenta no encontrada.")

    amount = round(float(payload.get("amount") or 0))
    if amount <= 0:
        raise ValueError("El monto debe ser mayor que cero.")
    tx_type = str(payload.get("type") or "income")
    if tx_type not in {"income", "expense", "payment"}:
        raise ValueError("Tipo de movimiento invalido.")
    description = str(payload.get("description") or ("Ingreso" if tx_type == "income" else "Movimiento")).strip()
    tx_date = str(payload.get("date") or datetime.now(UTC).date().isoformat())

    update_account_for_transaction(None, account_id, tx_type, amount)
    signed_amount = amount if tx_type == "income" else -amount
    execute_write(
        """
        insert into account_transactions (account_id, type, amount, description, date)
        values (%s, %s, %s, %s, %s)
        """,
        (account_id, tx_type, signed_amount, description, tx_date),
    )
    updated = fetch_one("select * from accounts where id = %s", (account_id,))
    people_by_id, _ = people_maps()
    return map_account(updated or existing, people_by_id)


def delete_expense(expense_id: int) -> bool:
    if _use_local_store():
        state = _load_local()
        expense = next((e for e in state["expenses"] if int(e["id"]) == int(expense_id)), None)
        if not expense:
            return False
        account_id = expense.get("account_id")
        total_amount = int(expense.get("total_amount") or 0)
        notes = str(expense.get("notes") or "")
        already_paid = notes.startswith("Historico:")
        if account_id and not already_paid and total_amount > 0:
            account = next((a for a in state["accounts"] if int(a["id"]) == int(account_id)), None)
            if account:
                reverse_delta = -account_delta(str(account.get("kind")), "expense", total_amount)
                account["balance"] = int(account.get("balance") or 0) + reverse_delta
            state["account_transactions"] = [t for t in state["account_transactions"] if t.get("related_expense_id") != int(expense_id)]
        state["expenses"] = [e for e in state["expenses"] if int(e["id"]) != int(expense_id)]
        state["expense_items"] = [i for i in state["expense_items"] if int(i["expense_id"]) != int(expense_id)]
        _save_local(state)
        return True

    expense = fetch_one("select * from expenses where id = %s", (expense_id,))
    if not expense:
        return False
    account_id = expense.get("account_id")
    total_amount = int(expense.get("total_amount") or 0)
    notes = str(expense.get("notes") or "")
    already_paid = notes.startswith("Historico:")

    if account_id and not already_paid and total_amount > 0:
        account = fetch_one("select * from accounts where id = %s", (int(account_id),))
        if account:
            reverse_delta = -account_delta(str(account.get("kind")), "expense", total_amount)
            execute_write(
                "update accounts set balance = %s where id = %s",
                (int(account.get("balance") or 0) + reverse_delta, int(account_id)),
            )
            execute_write("delete from account_transactions where related_expense_id = %s", (expense_id,))

    execute_write("delete from expenses where id = %s", (expense_id,))
    return True


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
        "all_silvia": "full_ana",
    }.get(split_type, split_type)
    share_items = [{"amount": item["amount"], "assigned_to": item["assigned_to"]} for item in items]
    shares = compute_shares(total_amount, db_split_type, share_items)

    if _use_local_store():
        state = _load_local()
        exp_id = _next_id(state["expenses"])
        inserted = {
            "id": exp_id,
            "title": title,
            "total_amount": total_amount,
            "date": expense_date,
            "paid_by_person_id": paid_by_person_id,
            "account_id": account_id,
            "split_type": db_split_type,
            "share_ana": shares["share_ana"],
            "share_daniel": shares["share_daniel"],
            "surcharge_amount": surcharge_amount,
            "surcharge_split_type": "equal",
            "notes": payload.get("note") or ("Historico: ya estaba pagado" if already_paid else None),
            "receipt_image_url": payload.get("imageUrl") or payload.get("image_url"),
            "source": source,
            "created_at": datetime.now(UTC).isoformat(),
        }
        state["expenses"].append(inserted)
        for item in items:
            state["expense_items"].append(
                {
                    "id": _next_id(state["expense_items"]),
                    "expense_id": exp_id,
                    "description": item["description"],
                    "amount": item["amount"],
                    "assigned_to": item["assigned_to"],
                }
            )
        if account_id and not already_paid:
            account = next((a for a in state["accounts"] if int(a["id"]) == int(account_id)), None)
            if account:
                delta = account_delta(str(account.get("kind")), "expense", total_amount)
                account["balance"] = int(account.get("balance") or 0) + delta
            state["account_transactions"].append(
                {
                    "id": _next_id(state["account_transactions"]),
                    "account_id": account_id,
                    "type": "expense",
                    "amount": -total_amount,
                    "description": title,
                    "date": expense_date,
                    "related_expense_id": exp_id,
                    "created_at": datetime.now(UTC).isoformat(),
                }
            )
        _save_local(state)
        return {"expenseId": exp_id, "totalAmount": total_amount}

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
    if _use_local_store():
        state = _load_local()
        draft = next((d for d in state["receipt_drafts"] if int(d["id"]) == draft_id), None)
    else:
        draft = fetch_one("select * from receipt_drafts where id = %s", (draft_id,))
    if not draft:
        raise ValueError("No se encontro la factura.")

    _people_by_id, people_by_slug = people_maps()
    paid_by_slug = "ana" if payload.get("paidBy") in {"ana", "silvia"} else "daniel"
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

    if _use_local_store():
        res = save_expense(
            {
                "title": title,
                "totalAmount": total_amount,
                "expenseDate": expense_date,
                "paidByPersonId": paid_by["id"],
                "accountId": account_id,
                "splitType": "by_items",
                "surchargeAmount": surcharge_amount,
                "imageUrl": draft.get("image_url"),
                "source": "scan",
                "items": items,
            }
        )
        state = _load_local()
        state["receipt_drafts"] = [d for d in state["receipt_drafts"] if int(d["id"]) != draft_id]
        _save_local(state)
        return res

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

    if _use_local_store():
        state = _load_local()
        settle_id = _next_id(state["settlements"])
        state["settlements"].append(
            {
                "id": settle_id,
                "from_person_id": int(payload.get("fromPersonId") or payload.get("from_person_id")),
                "to_person_id": int(payload.get("toPersonId") or payload.get("to_person_id")),
                "amount": amount,
                "from_account_id": account_id,
                "date": settlement_date,
                "note": payload.get("note"),
                "created_at": datetime.now(UTC).isoformat(),
            }
        )
        if account_id:
            account = next((a for a in state["accounts"] if int(a["id"]) == int(account_id)), None)
            if account:
                delta = account_delta(str(account.get("kind")), "payment", amount)
                account["balance"] = int(account.get("balance") or 0) + delta
            state["account_transactions"].append(
                {
                    "id": _next_id(state["account_transactions"]),
                    "account_id": account_id,
                    "type": "payment",
                    "amount": -amount,
                    "description": payload.get("note") or "Pago entre Silvia y Daniel",
                    "date": settlement_date,
                    "related_expense_id": None,
                    "created_at": datetime.now(UTC).isoformat(),
                }
            )
        _save_local(state)
        return {"settlementId": settle_id, "amount": amount}

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
            (account_id, -amount, payload.get("note") or "Pago entre Silvia y Daniel", settlement_date),
        )

    return {"settlementId": inserted["id"], "amount": amount}


GOAL_FREQUENCIES = {"una_vez", "semanal", "mensual", "anual"}


def map_goal(row: dict[str, Any]) -> dict[str, Any]:
    deadline = row.get("deadline")
    if hasattr(deadline, "isoformat"):
        deadline = deadline.isoformat()
    return {
        "id": row["id"],
        "name": row["name"],
        "target_amount": int(row["target_amount"]),
        "frequency": row["frequency"],
        "deadline": str(deadline) if deadline else None,
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
    if _use_local_store():
        return [map_goal(row) for row in _load_local()["goals"]]
    return [map_goal(row) for row in fetch_all("select * from goals order by id")]


def get_goal(goal_id: int) -> dict[str, Any] | None:
    if _use_local_store():
        found = next((g for g in _load_local()["goals"] if int(g["id"]) == int(goal_id)), None)
        return map_goal(found) if found else None
    row = fetch_one("select * from goals where id = %s", (goal_id,))
    return map_goal(row) if row else None


def create_goal(payload: dict[str, Any]) -> dict[str, Any]:
    if _use_local_store():
        state = _load_local()
        deadline = payload.get("deadline")
        row = {
            "id": _next_id(state["goals"]),
            "name": payload["name"],
            "target_amount": int(payload["target_amount"]),
            "frequency": payload["frequency"],
            "deadline": deadline.isoformat() if hasattr(deadline, "isoformat") else deadline,
            "current_saved": int(payload.get("current_saved", 0)),
            "notes": payload.get("notes"),
            "created_at": datetime.now(UTC).isoformat(),
        }
        state["goals"].append(row)
        _save_local(state)
        return map_goal(row)
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
    if _use_local_store():
        state = _load_local()
        found = next((g for g in state["goals"] if int(g["id"]) == int(goal_id)), None)
        if not found:
            return None
        for key in fields:
            val = payload[key]
            found[key] = val.isoformat() if hasattr(val, "isoformat") else val
        _save_local(state)
        return map_goal(found)
    assignments = ", ".join(f"{key} = %s" for key in fields)
    row = fetch_one_write(
        f"update goals set {assignments} where id = %s returning *",
        tuple(payload[key] for key in fields) + (goal_id,),
    )
    return map_goal(row) if row else None


def delete_goal(goal_id: int) -> bool:
    if _use_local_store():
        state = _load_local()
        before = len(state["goals"])
        state["goals"] = [g for g in state["goals"] if int(g["id"]) != int(goal_id)]
        _save_local(state)
        return len(state["goals"]) < before
    return fetch_one_write("delete from goals where id = %s returning id", (goal_id,)) is not None


def get_expenses_for_month(year: int, month: int) -> list[dict[str, Any]]:
    if _use_local_store():
        prefix = f"{year:04d}-{month:02d}-"
        return [e for e in _load_local()["expenses"] if str(e.get("date") or "").startswith(prefix)]
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
