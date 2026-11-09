import json
from pathlib import Path

p = Path(r"C:\Users\lady\.gemini\antigravity\scratch\cuentas-claras\backend\cuentas_claras_local.json")
data = json.loads(p.read_text("utf-8"))
print("=== BASE DE DATOS LOCAL ACTUAL ===")
print("Personas:", [p["name"] for p in data["people"]])
print("\nCuentas:")
for a in data["accounts"]:
    person = "Silvia" if a["person_id"] == 1 else "Daniel"
    print(f"  • ID {a['id']}: {a['name']} ({person}) | Saldo: ${a['balance']:,}")

print(f"\nGastos registrados ({len(data['expenses'])}):")
for e in data["expenses"]:
    print(f"  • {e['date']} - {e['title']}: ${e['total_amount']:,}")

print(f"\nGastos fijos ({len(data['recurring_expenses'])}):")
for r in data["recurring_expenses"]:
    payer = "Silvia" if r["paid_by_person_id"] == 1 else "Daniel"
    print(f"  • {r['title']} (Día {r['day_of_month']}): ${r['amount']:,} (Paga {payer})")

print(f"\nTransferencias de saldo ({len(data['settlements'])}):")
for s in data["settlements"]:
    print(f"  • {s}")
