import json
from pathlib import Path
from datetime import datetime, timezone

db_path = Path(r"C:\Users\lady\.gemini\antigravity\scratch\cuentas-claras\backend\cuentas_claras_local.json")

# Current timestamp
now = datetime.now(timezone.utc).isoformat()

data = {
    "people": [
        {"id": 1, "slug": "ana", "name": "Silvia", "color": "#e0578e", "created_at": "2026-08-01T00:00:00"},
        {"id": 2, "slug": "daniel", "name": "Daniel", "color": "#2f6fed", "created_at": "2026-08-01T00:00:00"}
    ],
    "accounts": [
        {
            "id": 1,
            "person_id": 1,
            "name": "Nequi Silvia",
            "type": "nequi",
            "kind": "debit",
            "balance": 1543896,
            "is_default": True,
            "credit_limit": None,
            "cutoff_day": None,
            "due_day": None,
            "created_at": "2026-08-01T00:00:00"
        },
        {
            "id": 2,
            "person_id": 1,
            "name": "Nu Ahorros Silvia",
            "type": "nu_ahorros",
            "kind": "debit",
            "balance": 555313,
            "is_default": False,
            "credit_limit": None,
            "cutoff_day": None,
            "due_day": None,
            "created_at": "2026-08-01T00:00:00"
        },
        {
            "id": 3,
            "person_id": 2,
            "name": "Nequi Daniel",
            "type": "nequi",
            "kind": "debit",
            "balance": 655394,
            "is_default": True,
            "credit_limit": None,
            "cutoff_day": None,
            "due_day": None,
            "created_at": "2026-08-01T00:00:00"
        },
        {
            "id": 4,
            "person_id": 2,
            "name": "Nu Ahorros Daniel",
            "type": "nu_ahorros",
            "kind": "debit",
            "balance": 0,
            "is_default": False,
            "credit_limit": None,
            "cutoff_day": None,
            "due_day": None,
            "created_at": "2026-08-01T00:00:00"
        },
        {
            "id": 5,
            "person_id": 2,
            "name": "Nu Crédito Daniel",
            "type": "nu_credito",
            "kind": "credit",
            "balance": 0,
            "is_default": False,
            "credit_limit": 1000000,
            "cutoff_day": 15,
            "due_day": 4,
            "created_at": "2026-08-01T00:00:00"
        },
        {
            "id": 6,
            "person_id": 1,
            "name": "Nu Crédito Silvia",
            "type": "nu_credito",
            "kind": "credit",
            "balance": 0,
            "is_default": False,
            "credit_limit": 1000000,
            "cutoff_day": 15,
            "due_day": 4,
            "created_at": "2026-11-03T22:00:38"
        }
    ],
    "expenses": [
        {
            "id": 1,
            "title": "Arriendo Apartamento",
            "total_amount": 700000,
            "date": "2026-11-01",
            "paid_by_person_id": 2,
            "split_type": "proportional",
            "share_ana": 0,
            "share_daniel": 700000,
            "daniel_pct": 100,
            "surcharge_applied": False,
            "already_paid": False,
            "source": "manual",
            "account_id": 3,
            "note": "Arriendo del hogar pagado por Daniel (100% asumido mientras Silvia está desempleada)",
            "created_at": "2026-11-01T10:00:00"
        },
        {
            "id": 2,
            "title": "Aseo Hogar",
            "total_amount": 35000,
            "date": "2026-11-01",
            "paid_by_person_id": 2,
            "split_type": "half",
            "share_ana": 17500,
            "share_daniel": 17500,
            "daniel_pct": 50,
            "surcharge_applied": False,
            "already_paid": False,
            "source": "manual",
            "account_id": 3,
            "note": "Aseo del hogar (planilla Daniel)",
            "created_at": "2026-11-01T11:00:00"
        },
        {
            "id": 3,
            "title": "Ropa Daniel (comprada por Silvia)",
            "total_amount": 374400,
            "date": "2026-11-02",
            "paid_by_person_id": 1,
            "split_type": "all_daniel",
            "share_ana": 0,
            "share_daniel": 374400,
            "daniel_pct": 100,
            "surcharge_applied": False,
            "already_paid": False,
            "source": "manual",
            "account_id": 1,
            "note": "Silvia pagó la ropa de Daniel de su bolsillo (Daniel se lo debe reembolsar)",
            "created_at": "2026-11-02T15:00:00"
        },
        {
            "id": 4,
            "title": "Dollar City (Compras hogar)",
            "total_amount": 17500,
            "date": "2026-11-03",
            "paid_by_person_id": 1,
            "split_type": "half",
            "share_ana": 8750,
            "share_daniel": 8750,
            "daniel_pct": 50,
            "surcharge_applied": False,
            "already_paid": False,
            "source": "manual",
            "account_id": 1,
            "note": "Artículos del hogar pagados por Silvia",
            "created_at": "2026-11-03T16:00:00"
        },
        {
            "id": 5,
            "title": "Miniso (Compras hogar)",
            "total_amount": 93700,
            "date": "2026-11-03",
            "paid_by_person_id": 1,
            "split_type": "half",
            "share_ana": 46850,
            "share_daniel": 46850,
            "daniel_pct": 50,
            "surcharge_applied": False,
            "already_paid": False,
            "source": "manual",
            "account_id": 1,
            "note": "Compras del hogar pagadas por Silvia",
            "created_at": "2026-11-03T17:00:00"
        },
        {
            "id": 6,
            "title": "Rappi Comida",
            "total_amount": 24490,
            "date": "2026-11-04",
            "paid_by_person_id": 1,
            "split_type": "half",
            "share_ana": 12245,
            "share_daniel": 12245,
            "daniel_pct": 50,
            "surcharge_applied": False,
            "already_paid": False,
            "source": "manual",
            "account_id": 1,
            "note": "Comida compartida pagada por Silvia",
            "created_at": "2026-11-04T13:00:00"
        },
        {
            "id": 7,
            "title": "Gasolina compartida",
            "total_amount": 33588,
            "date": "2026-11-04",
            "paid_by_person_id": 1,
            "split_type": "half",
            "share_ana": 16794,
            "share_daniel": 16794,
            "daniel_pct": 50,
            "surcharge_applied": False,
            "already_paid": False,
            "source": "manual",
            "account_id": 1,
            "note": "Gasolina pagada por Silvia",
            "created_at": "2026-11-04T18:00:00"
        }
    ],
    "expense_items": [],
    "settlements": [
        {
            "id": 1,
            "from_person_id": 2,
            "to_person_id": 1,
            "amount": 50000,
            "account_id": 3,
            "to_account_id": 1,
            "date": "2026-11-01",
            "note": "Daniel le da a Silvia ($50.000 registrados en planilla de Silvia)",
            "created_at": "2026-11-01T12:00:00"
        }
    ],
    "account_transactions": [
        {
            "id": 1,
            "account_id": 3,
            "type": "reconciliation",
            "amount": 655394,
            "description": "Saldo real en Nequi Daniel",
            "date": "2026-11-01",
            "related_expense_id": None,
            "created_at": "2026-11-01T00:00:00"
        },
        {
            "id": 2,
            "account_id": 1,
            "type": "reconciliation",
            "amount": 1543896,
            "description": "Saldo real en Nequi Silvia",
            "date": "2026-11-01",
            "related_expense_id": None,
            "created_at": "2026-11-01T00:00:00"
        },
        {
            "id": 3,
            "account_id": 2,
            "type": "reconciliation",
            "amount": 555313,
            "description": "Saldo real en Nu Ahorros Silvia",
            "date": "2026-11-01",
            "related_expense_id": None,
            "created_at": "2026-11-01T00:00:00"
        }
    ],
    "receipt_drafts": [],
    "receipt_blobs": [],
    "goals": [
        {
            "id": 1,
            "name": "Fondo de Emergencia Familiar",
            "target_amount": 2000000,
            "frequency": "mensual",
            "deadline": "2027-12-31",
            "current_saved": 500000,
            "notes": "Ahorro de respaldo del hogar",
            "created_at": "2026-11-01T00:00:00"
        },
        {
            "id": 2,
            "name": "Seguro y Llantas Moto",
            "target_amount": 800000,
            "frequency": "anual",
            "deadline": "2027-08-01",
            "current_saved": 200000,
            "notes": "Provisión anual moto Daniel",
            "created_at": "2026-11-01T00:00:00"
        }
    ],
    "recurring_expenses": [
        {
            "id": 1,
            "title": "Arriendo Apartamento",
            "amount": 700000,
            "day_of_month": 1,
            "paid_by_person_id": 2,
            "split_type": "proportional",
            "daniel_pct": 100,
            "category": "Vivienda"
        },
        {
            "id": 2,
            "title": "Internet Hogar (Fibra)",
            "amount": 95000,
            "day_of_month": 5,
            "paid_by_person_id": 2,
            "split_type": "proportional",
            "daniel_pct": 100,
            "category": "Vivienda"
        },
        {
            "id": 3,
            "title": "Servicios Públicos (Luz y Agua)",
            "amount": 180000,
            "day_of_month": 15,
            "paid_by_person_id": 1,
            "split_type": "half",
            "daniel_pct": 50,
            "category": "Vivienda"
        },
        {
            "id": 4,
            "title": "Aseo Hogar",
            "amount": 35000,
            "day_of_month": 1,
            "paid_by_person_id": 2,
            "split_type": "half",
            "daniel_pct": 50,
            "category": "Vivienda"
        }
    ]
}

db_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("SUCCESS: cuentas_claras_local.json populated with exact real data from both Excels!")
