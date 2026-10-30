from __future__ import annotations

import base64
import json
import os
import re
from typing import Any

import httpx


RECEIPT_SYSTEM_PROMPT = """Eres un asistente que lee facturas, tickets y comprobantes de compra en Colombia (COP) a partir de una foto.
Devuelve SOLO JSON valido con esta forma exacta:
{"merchant":"nombre del establecimiento o null","items":[{"description":"string corto","amount":number}]}
Reglas obligatorias:
- "items" debe contener unicamente productos o conceptos individuales comprados.
- EXCLUYE totales, subtotal, IVA/impuestos, propina, descuento general, cambio, efectivo recibido, formas de pago, transferencia, tarjeta, Nequi, datafono, voucher, garantia y textos legales.
- Si una linea resume la factura completa, no la incluyas aunque tenga valor.
- Los montos son pesos colombianos enteros sin puntos, comas ni simbolo de moneda.
- No inventes productos que no aparezcan en la imagen.
- Si no puedes leer productos claros, devuelve items como arreglo vacio."""

SUMMARY_LINE_RE = re.compile(
    r"\b(total|totales|subtotal|iva|impuesto|propina|descuento|cambio|efectivo|recibido|transferencia|tarj|tarjeta|credito|cr[eé]dito|debito|d[eé]bito|nequi|dat[aá]fono|datafono|voucher|garant[ií]a|son:?)\b",
    re.IGNORECASE,
)


def sanitize_receipt_items(items: Any) -> list[dict[str, Any]]:
    if not isinstance(items, list):
        return []
    cleaned: list[dict[str, Any]] = []
    for raw in items:
        if not isinstance(raw, dict):
            continue
        description = re.sub(r"\s+", " ", str(raw.get("description") or raw.get("name") or "")).strip()[:120]
        try:
            amount = round(float(raw.get("amount") or 0))
        except (TypeError, ValueError):
            amount = 0
        if description and amount > 0 and not SUMMARY_LINE_RE.search(description):
            cleaned.append({"description": description, "amount": amount})
    return cleaned


def parse_model_json(content: str) -> dict[str, Any]:
    text = content.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return json.loads(text or "{}")


async def scan_receipt_with_nvidia(buffer: bytes, mime_type: str) -> dict[str, Any]:
    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key:
        return {
            "merchant": None,
            "items": [],
            "aiNote": "La lectura automatica no esta configurada. Falta NVIDIA_API_KEY.",
        }

    model = os.getenv("NVIDIA_RECEIPT_MODEL", "meta/llama-3.2-11b-vision-instruct")
    image_data = base64.b64encode(buffer).decode("ascii")
    payload = {
        "model": model,
        "temperature": 0,
        "max_tokens": 1200,
        "messages": [
            {"role": "system", "content": RECEIPT_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Extrae solo los productos individuales de esta factura."},
                    {"type": "image_url", "image_url": {"url": f"data:{mime_type or 'image/jpeg'};base64,{image_data}"}},
                ],
            },
        ],
    }

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            "https://integrate.api.nvidia.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json=payload,
        )

    if response.status_code >= 400:
        return {
            "merchant": None,
            "items": [],
            "aiNote": f"No se pudo leer la factura automaticamente ({response.status_code}).",
        }

    data = response.json()
    content = data.get("choices", [{}])[0].get("message", {}).get("content", "{}")
    parsed = parse_model_json(content)
    merchant = parsed.get("merchant")
    if isinstance(merchant, str):
        merchant = merchant.strip()[:120] or None
    else:
        merchant = None
    items = sanitize_receipt_items(parsed.get("items"))
    return {
        "merchant": merchant,
        "items": items,
        "aiNote": None if items else "No se detectaron productos automaticamente. Agregalos manualmente.",
    }
