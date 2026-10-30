# Cuentas Claras API

Backend Python/FastAPI para la APK de Ana y Daniel.

Arquitectura actual:

- FastAPI en Render.
- Render Postgres como base de datos.
- NVIDIA API para extraer facturas/comprobantes.
- La APK solo manda imagenes/datos y pinta la respuesta.
- No requiere Supabase.

## Local

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Variables requeridas:

```bash
NVIDIA_API_KEY=...
DATABASE_URL=postgresql://...
APP_TOKEN=...
```

Al arrancar, el backend aplica `app/schema.sql` de forma idempotente. Ese archivo crea las tablas y siembra los datos actuales de Daniel y Ana.

## Render

Crear un Web Service desde esta carpeta usando `render.yaml`.

Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## Endpoints añadidos desde Contador

Todos requieren el header `X-App-Token`.

| Endpoint | Que hace |
|---|---|
| `GET /api/categories` | Lista fija de categorias. |
| `POST /api/autocategorize` | `{description, amount}` -> categoria (IA NVIDIA si hay `NVIDIA_API_KEY`, si no reglas por palabras clave). |
| `POST /api/expenses/parse-text` | Texto libre ("pan 5000, cafe 3 mil") -> items `{description, amount, category}`. |
| `GET/POST /api/goals`, `PUT/DELETE /api/goals/{id}` | Objetivos de ahorro (tabla `goals`). |
| `GET /api/goals/{id}/projection?monthly_saving=` | Falta, meses restantes, aporte mensual necesario. |
| `GET /api/month-close?year=&month=` | Cierre de mes: total, por categoria, por persona, comparacion con el mes anterior. |

Pruebas: `pytest` (28 tests; los endpoints nuevos se prueban sin base de datos).
