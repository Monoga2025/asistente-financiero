from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import date
from typing import Any

from fastapi import Depends, FastAPI, File, HTTPException, Query, Request, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .auth import require_app_token
from .categorize import CATEGORIES, categorize_by_rules, categorize_with_ai
from .db import (
    GOAL_FREQUENCIES,
    bootstrap,
    confirm_receipt,
    create_goal,
    create_receipt_draft,
    delete_goal,
    get_account_transactions,
    get_expenses_for_month,
    get_goal,
    get_receipt_blob,
    init_database,
    list_goals,
    save_expense,
    save_settlement,
    update_goal,
    upload_receipt_image,
)
from .expense_text import parse_expenses_text
from .goals import month_close_summary, project_goal
from .receipts import scan_receipt_with_nvidia


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_database()
    yield


def parse_goal_payload(payload: dict[str, Any], partial: bool) -> dict[str, Any]:
    goal: dict[str, Any] = {}
    if not partial or "name" in payload:
        name = str(payload.get("name") or "").strip()
        if not name:
            raise HTTPException(status_code=400, detail="El objetivo necesita un nombre.")
        goal["name"] = name
    if not partial or "target_amount" in payload:
        try:
            target = int(payload.get("target_amount"))
        except (TypeError, ValueError):
            target = 0
        if target <= 0:
            raise HTTPException(status_code=400, detail="La meta debe ser mayor a cero.")
        goal["target_amount"] = target
    if not partial or "frequency" in payload:
        frequency = str(payload.get("frequency") or "una_vez")
        if frequency not in GOAL_FREQUENCIES:
            raise HTTPException(status_code=400, detail="Frecuencia invalida.")
        goal["frequency"] = frequency
    if "deadline" in payload:
        try:
            goal["deadline"] = date.fromisoformat(payload["deadline"]) if payload["deadline"] else None
        except (TypeError, ValueError) as exc:
            raise HTTPException(status_code=400, detail="Fecha limite invalida (AAAA-MM-DD).") from exc
    if "current_saved" in payload:
        try:
            goal["current_saved"] = max(0, int(payload["current_saved"]))
        except (TypeError, ValueError) as exc:
            raise HTTPException(status_code=400, detail="Ahorro actual invalido.") from exc
    if "notes" in payload:
        goal["notes"] = str(payload["notes"] or "").strip() or None
    return goal


def create_app() -> FastAPI:
    app = FastAPI(title="Cuentas Claras API", version="1.0.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health() -> dict[str, Any]:
        return {"ok": True, "service": "cuentas-claras-api"}

    @app.get("/mobile/bootstrap", dependencies=[Depends(require_app_token)])
    def mobile_bootstrap() -> dict[str, Any]:
        return bootstrap()

    @app.get("/mobile/expenses", dependencies=[Depends(require_app_token)])
    def mobile_expenses() -> dict[str, Any]:
        data = bootstrap()
        return {"ok": True, "expenses": data["expenses"]}

    @app.get("/mobile/settlements", dependencies=[Depends(require_app_token)])
    def mobile_settlements() -> dict[str, Any]:
        data = bootstrap()
        return {"ok": True, "settlements": data["settlements"]}

    @app.get("/api/mobile/accounts/{account_id}/transactions", dependencies=[Depends(require_app_token)])
    def mobile_account_transactions(account_id: int, limit: int = Query(default=100, ge=1, le=300)) -> dict[str, Any]:
        return {"ok": True, "transactions": get_account_transactions(account_id, limit)}

    @app.get("/receipts/images/{image_id}")
    def receipt_image(image_id: int) -> Response:
        blob = get_receipt_blob(image_id)
        if not blob:
            raise HTTPException(status_code=404, detail="Imagen no encontrada.")
        return Response(content=bytes(blob["data"]), media_type=blob["content_type"])

    @app.post("/expenses", dependencies=[Depends(require_app_token)])
    def create_expense(payload: dict[str, Any]) -> dict[str, Any]:
        try:
            result = save_expense(payload)
            return {"ok": True, **result}
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/mobile/expenses/save", dependencies=[Depends(require_app_token)])
    def create_mobile_expense(payload: dict[str, Any]) -> dict[str, Any]:
        try:
            result = save_expense(payload)
            return {"ok": True, **result}
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/settlements", dependencies=[Depends(require_app_token)])
    def create_settlement(payload: dict[str, Any]) -> dict[str, Any]:
        try:
            result = save_settlement(payload)
            return {"ok": True, **result}
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/mobile/settlements/save", dependencies=[Depends(require_app_token)])
    def create_mobile_settlement(payload: dict[str, Any]) -> dict[str, Any]:
        try:
            result = save_settlement(payload)
            return {"ok": True, **result}
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/receipts/scan", dependencies=[Depends(require_app_token)])
    async def scan_receipt(request: Request, image: UploadFile = File(...)) -> dict[str, Any]:
        buffer = await image.read()
        mime_type = image.content_type or "image/jpeg"
        image_url = upload_receipt_image(buffer, mime_type)
        if image_url and image_url.startswith("/"):
            image_url = f"{str(request.base_url).rstrip('/')}{image_url}"
        parsed = await scan_receipt_with_nvidia(buffer, mime_type)
        draft = create_receipt_draft(image_url, parsed["merchant"], parsed["items"], parsed.get("aiNote"))
        return {
            "ok": True,
            "draftId": draft["id"],
            "draft": {
                "id": draft["id"],
                "imageUrl": draft.get("image_url"),
                "merchantGuess": draft.get("merchant_guess"),
                "items": draft.get("items") or [],
                "aiNote": draft.get("ai_note"),
            },
        }

    @app.post("/api/receipts/scan", dependencies=[Depends(require_app_token)])
    async def scan_receipt_compat(request: Request, image: UploadFile = File(...)) -> dict[str, Any]:
        return await scan_receipt(request, image)

    @app.post("/receipts/confirm", dependencies=[Depends(require_app_token)])
    def confirm_scanned_receipt(payload: dict[str, Any]) -> dict[str, Any]:
        try:
            result = confirm_receipt(payload)
            return {"ok": True, **result}
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/mobile/receipts/save", dependencies=[Depends(require_app_token)])
    def confirm_mobile_scanned_receipt(payload: dict[str, Any]) -> dict[str, Any]:
        try:
            result = confirm_receipt(payload)
            return {"ok": True, **result}
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/api/categories", dependencies=[Depends(require_app_token)])
    def list_categories() -> dict[str, Any]:
        return {"ok": True, "categories": CATEGORIES}

    @app.post("/api/autocategorize", dependencies=[Depends(require_app_token)])
    async def autocategorize(payload: dict[str, Any]) -> dict[str, Any]:
        description = str(payload.get("description") or "").strip()
        if not description:
            raise HTTPException(status_code=400, detail="Falta la descripcion.")
        ai_category = await categorize_with_ai(description, payload.get("amount") or 0)
        if ai_category:
            return {"ok": True, "category": ai_category, "source": "ai"}
        return {"ok": True, "category": categorize_by_rules(description), "source": "rules"}

    @app.post("/api/expenses/parse-text", dependencies=[Depends(require_app_token)])
    def parse_expenses_from_text(payload: dict[str, Any]) -> dict[str, Any]:
        text = str(payload.get("text") or "").strip()
        if not text:
            raise HTTPException(status_code=400, detail="Falta el texto.")
        items = [{**item, "category": categorize_by_rules(str(item["description"]))} for item in parse_expenses_text(text)]
        return {"ok": True, "items": items}

    @app.get("/api/goals", dependencies=[Depends(require_app_token)])
    def get_goals() -> dict[str, Any]:
        return {"ok": True, "goals": list_goals()}

    @app.post("/api/goals", dependencies=[Depends(require_app_token)])
    def post_goal(payload: dict[str, Any]) -> dict[str, Any]:
        return {"ok": True, "goal": create_goal(parse_goal_payload(payload, partial=False))}

    @app.put("/api/goals/{goal_id}", dependencies=[Depends(require_app_token)])
    def put_goal(goal_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        goal = update_goal(goal_id, parse_goal_payload(payload, partial=True))
        if not goal:
            raise HTTPException(status_code=404, detail="Objetivo no encontrado.")
        return {"ok": True, "goal": goal}

    @app.delete("/api/goals/{goal_id}", dependencies=[Depends(require_app_token)])
    def remove_goal(goal_id: int) -> dict[str, Any]:
        if not delete_goal(goal_id):
            raise HTTPException(status_code=404, detail="Objetivo no encontrado.")
        return {"ok": True}

    @app.get("/api/goals/{goal_id}/projection", dependencies=[Depends(require_app_token)])
    def goal_projection(goal_id: int, monthly_saving: int = Query(default=0, ge=0)) -> dict[str, Any]:
        goal = get_goal(goal_id)
        if not goal:
            raise HTTPException(status_code=404, detail="Objetivo no encontrado.")
        deadline = date.fromisoformat(goal["deadline"]) if goal.get("deadline") else None
        projection = project_goal(goal["target_amount"], goal["current_saved"], monthly_saving, deadline)
        return {"ok": True, "goal": goal, "projection": projection}

    @app.get("/api/month-close", dependencies=[Depends(require_app_token)])
    def month_close(
        year: int | None = Query(default=None, ge=2000, le=2100),
        month: int | None = Query(default=None, ge=1, le=12),
    ) -> dict[str, Any]:
        today = date.today()
        if year is None or month is None:
            year, month = (today.year - 1, 12) if today.month == 1 else (today.year, today.month - 1)
        prev_year, prev_month = (year - 1, 12) if month == 1 else (year, month - 1)
        summary = month_close_summary(
            get_expenses_for_month(year, month),
            get_expenses_for_month(prev_year, prev_month),
            year,
            month,
        )
        return {"ok": True, "summary": summary}

    return app


app = create_app()
