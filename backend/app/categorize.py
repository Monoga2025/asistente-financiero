from __future__ import annotations

import os
import unicodedata
from typing import Any

import httpx


CATEGORIES = [
    "Alimentacion",
    "Transporte",
    "Vivienda",
    "Servicios",
    "Salud",
    "Ocio",
    "Compras",
    "Educacion",
    "Otros",
]

KEYWORDS: dict[str, tuple[str, ...]] = {
    "Alimentacion": ("almuerzo", "cena", "desayuno", "restaurante", "cafe", "pan", "mercado", "supermercado", "comida", "empanada", "pizza", "domicilio", "fruta"),
    "Transporte": ("uber", "taxi", "bus", "metro", "gasolina", "parqueadero", "peaje", "pasaje", "didi"),
    "Vivienda": ("arriendo", "alquiler", "administracion", "hipoteca", "reparacion", "ferreteria"),
    "Servicios": ("luz", "agua", "gas", "internet", "celular", "plan datos", "energia", "hostinger"),
    "Salud": ("farmacia", "medicina", "drogueria", "doctor", "medico", "odontologo", "eps", "consulta"),
    "Ocio": ("netflix", "spotify", "cine", "bar", "fiesta", "concierto", "juego", "entradas", "viaje"),
    "Compras": ("ropa", "zapatos", "tienda", "regalo", "amazon", "mercadolibre"),
    "Educacion": ("curso", "libro", "universidad", "matricula", "colegio", "clase"),
}


def _fold(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text or "")
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch)).lower().strip()


def categorize_by_rules(description: str) -> str:
    folded = _fold(description)
    if not folded:
        return "Otros"
    words = set(folded.replace(",", " ").replace(".", " ").split())
    for category, keywords in KEYWORDS.items():
        for keyword in keywords:
            if (" " in keyword and keyword in folded) or keyword in words:
                return category
    return "Otros"


def normalize_category(raw: str | None) -> str:
    folded = _fold(raw or "")
    for category in CATEGORIES:
        if _fold(category) in folded:
            return category
    return "Otros"


async def categorize_with_ai(description: str, amount: int | float = 0) -> str | None:
    """Ask the NVIDIA model for one category from the fixed list. Returns None when unavailable."""
    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key:
        return None
    model = os.getenv("NVIDIA_TEXT_MODEL", "meta/llama-3.1-8b-instruct")
    prompt = (
        f'Clasifica este gasto: "{description}" ({amount} COP). '
        f"Responde SOLO una categoria de esta lista, sin explicacion: {', '.join(CATEGORIES)}."
    )
    payload: dict[str, Any] = {
        "model": model,
        "temperature": 0,
        "max_tokens": 12,
        "messages": [{"role": "user", "content": prompt}],
    }
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                "https://integrate.api.nvidia.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json=payload,
            )
        if response.status_code >= 400:
            return None
        content = response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
    except (httpx.HTTPError, ValueError):
        return None
    return normalize_category(content)
