# Cuentas Claras

**A shared-finance assistant for two people: scan a receipt, split it item by item, and always know who owes whom.**

Built for a real household in Colombia, with an Android build. It tracks bank accounts (Nequi, Nu, credit cards with cut-off and due dates), turns receipt photos into itemized expenses with a vision model, and keeps a running balance between the two people.

## Screenshots

<table>
  <tr>
    <td align="center"><img src="docs/screenshots/home.png" width="300" alt="Home screen with the balance between both people, quick actions and account summary"></td>
    <td align="center"><img src="docs/screenshots/balance.png" width="300" alt="Balance screen with the expense history and how each expense moved the balance"></td>
  </tr>
  <tr>
    <td align="center"><em>Home: current balance, quick actions and accounts</em></td>
    <td align="center"><em>Balance: every expense and how it moved the debt</em></td>
  </tr>
</table>

*All data in the screenshots is fictional sample data.*

## What it does

- **Receipt scanning with AI.** Take a photo of a receipt; the backend sends it to a vision model (NVIDIA NIM) and returns the merchant and line items, ready to assign.
- **Item-level splitting.** Each line can belong to one person or be shared, so a single supermarket receipt is split fairly.
- **Running balance.** Every expense and every payment updates who owes whom, with a full history.
- **Accounts.** Debit and credit accounts per person, including credit limit, cut-off day and due day.
- **Natural-language expenses.** Type `pan 5000, cafe 3 mil` or `1,5 millones` and the parser turns it into amounts.
- **Auto-categorization.** Keyword rules with an optional AI fallback.
- **Goals and month close.** Savings goals with a monthly projection, and a month-close summary by category and person compared with the previous month.

## Architecture

```mermaid
flowchart LR
  App["Expo app (Android + web)<br/>React Native, expo-router"] -- "X-App-Token" --> API["FastAPI backend"]
  API --> DB[("PostgreSQL")]
  API --> Vision["NVIDIA NIM<br/>vision model"]
```

| Layer | Stack |
|---|---|
| App | Expo, React Native, expo-router, TypeScript (`app/`, `components/`, `lib/`) |
| API | Python, FastAPI, psycopg with raw SQL (`backend/app/`) |
| Data | PostgreSQL; schema and sample seed in `backend/app/schema.sql` |
| AI | NVIDIA NIM vision model for receipts; optional AI categorization |
| Deploy | Render blueprint (`backend/render.yaml`); Android build with Expo |

Every private endpoint requires the `X-App-Token` header; the API refuses to start serving them if `APP_TOKEN` is not set.

## Run it locally

Backend:

```bash
cd backend
pip install -r requirements.txt
export DATABASE_URL=postgresql://user:password@localhost:5432/cuentas_claras
export APP_TOKEN=change-me
export NVIDIA_API_KEY=...   # only needed for receipt scanning
uvicorn app.main:app --reload
python -m pytest
```

App:

```bash
npm install
cp .env.example .env        # EXPO_PUBLIC_API_BASE_URL and EXPO_PUBLIC_APP_TOKEN
npm run dev                 # Expo dev server (press w for web, a for Android)
npm run typecheck
```

API endpoints are documented in [`backend/README.md`](backend/README.md).

## Status

- 🟢 Backend: 28 tests passing (`python -m pytest`), including splitting, balance, receipts, goals, month close and the text parser.
- 🟢 App: type-checks cleanly (`npm run typecheck`).
- 🟡 The goals and month-close SQL has not yet been run against a real PostgreSQL instance; it is covered by tests with a mocked database layer.
- 🟡 Built for two people by design (the people and split types are fixed in the schema).

---

Built by [Daniel Monoga](https://github.com/Monoga2025) · MIT licensed.
