from __future__ import annotations

import re
import unicodedata
from typing import Any


AMOUNT_RE = re.compile(r"\$?\s*(\d[\d.,]*)\s*(millones|millon|mil|k|lucas)?\b", re.IGNORECASE)
SPLIT_RE = re.compile(r"[\n;]|,(?!\d)|\s+y\s+(?=[a-záéíóúñ]+\s+\$?\d)", re.IGNORECASE)
MULTIPLIERS = {
    "mil": 1_000,
    "k": 1_000,
    "lucas": 1_000,
    "millon": 1_000_000,
    "millones": 1_000_000,
}

WORD_UNITS = {
    "un": 1,
    "uno": 1,
    "una": 1,
    "dos": 2,
    "tres": 3,
    "cuatro": 4,
    "cinco": 5,
    "seis": 6,
    "siete": 7,
    "ocho": 8,
    "nueve": 9,
    "diez": 10,
    "once": 11,
    "doce": 12,
    "trece": 13,
    "catorce": 14,
    "quince": 15,
    "dieciseis": 16,
    "diecisiete": 17,
    "dieciocho": 18,
    "diecinueve": 19,
    "veinte": 20,
    "veintiun": 21,
    "veintiuno": 21,
    "veintidos": 22,
    "veintitres": 23,
    "veinticuatro": 24,
    "veinticinco": 25,
    "veintiseis": 26,
    "veintisiete": 27,
    "veintiocho": 28,
    "veintinueve": 29,
    "treinta": 30,
    "cuarenta": 40,
    "cincuenta": 50,
    "sesenta": 60,
    "setenta": 70,
    "ochenta": 80,
    "noventa": 90,
    "cien": 100,
    "ciento": 100,
    "doscientos": 200,
    "trescientos": 300,
    "cuatrocientos": 400,
    "quinientos": 500,
    "seiscientos": 600,
    "setecientos": 700,
    "ochocientos": 800,
    "novecientos": 900,
}


def _strip_accents(value: str) -> str:
    return "".join(ch for ch in unicodedata.normalize("NFD", value) if unicodedata.category(ch) != "Mn")


def _parse_small_spanish_number(tokens: list[str]) -> int | None:
    total = 0
    matched = False
    for token in tokens:
        clean = _strip_accents(token.lower())
        if clean == "y":
            continue
        if clean in WORD_UNITS:
            total += WORD_UNITS[clean]
            matched = True
        else:
            return None
    return total if matched and total > 0 else None


def normalize_spanish_numbers(text: str) -> str:
    """Convert spoken Spanish number phrases (e.g. 'cinco mil', 'tres mil quinientos', 'cuarenta y cinco mil') into digits."""
    if not text:
        return ""
    s = re.sub(r"\bmedio\s+mill[oó]n\b", "500000", text, flags=re.IGNORECASE)
    s = re.sub(r"\bun\s+mill[oó]n\b", "1000000", s, flags=re.IGNORECASE)

    num_words = "|".join(sorted(WORD_UNITS.keys(), key=len, reverse=True))
    pattern = re.compile(
        rf"\b((?:(?:{num_words})(?:\s+y\s+|\s+))*?(?:{num_words}))\s+mil(?:\s+((?:{num_words})(?:\s+y\s+(?:{num_words}))?))?\b",
        re.IGNORECASE,
    )

    def _replace_thousands(match: re.Match[str]) -> str:
        prefix_tokens = match.group(1).split()
        suffix_tokens = match.group(2).split() if match.group(2) else []
        thousands = _parse_small_spanish_number(prefix_tokens)
        if thousands is None:
            return match.group(0)
        remainder = _parse_small_spanish_number(suffix_tokens) if suffix_tokens else 0
        return str(thousands * 1000 + (remainder or 0))

    s = pattern.sub(_replace_thousands, s)
    s = re.sub(r"\bmil\s+quinientos\b", "1500", s, flags=re.IGNORECASE)
    return s


def _to_number(raw: str, has_suffix: bool) -> float | None:
    raw = raw.rstrip(".,")
    if not raw:
        return None
    if has_suffix:
        normalized = raw.replace(",", ".")
        return float(normalized) if normalized.count(".") <= 1 else None
    if re.fullmatch(r"\d{1,3}([.,]\d{3})+", raw):
        return float(re.sub(r"[.,]", "", raw))
    if re.fullmatch(r"\d+([.,]\d{1,2})?", raw):
        return float(raw.replace(",", "."))
    return None


def parse_amount(text: str) -> int | None:
    """Parse Colombian-style amounts: 5000, $5.000, 3 mil, 2k, 1,5 millones, cinco mil."""
    normalized = normalize_spanish_numbers(text or "")
    match = AMOUNT_RE.fullmatch(normalized.strip())
    if not match:
        return None
    suffix = (match.group(2) or "").lower()
    value = _to_number(match.group(1), bool(suffix))
    if value is None:
        return None
    amount = round(value * MULTIPLIERS.get(suffix, 1))
    return amount if amount > 0 else None


def parse_expenses_text(text: str) -> list[dict[str, int | str]]:
    """Extract {description, amount} items from free text (dictated or pasted)."""
    normalized = normalize_spanish_numbers(text or "")
    items: list[dict[str, int | str]] = []
    for fragment in SPLIT_RE.split(normalized):
        fragment = fragment.strip()
        if not fragment:
            continue
        match = None
        for candidate in AMOUNT_RE.finditer(fragment):
            match = candidate
        if not match:
            continue
        amount = parse_amount(match.group(0))
        description = re.sub(r"\s+", " ", fragment[: match.start()] + " " + fragment[match.end() :]).strip(" -:$.,")
        if amount and description:
            items.append({"description": description[:120], "amount": amount})
    return items


METADATA_PHRASES_RE = re.compile(
    r"\b(?:pag[oó]\s+(?:silvia|ana|daniel)|pagado\s+por\s+(?:silvia|ana|daniel)|con\s+(?:nequi|nu\s+cr[eé]dito|nu\s+ahorros|tarjeta|nu)|mitad\s+y\s+mitad|a\s+medias|todo\s+(?:silvia|ana|daniel)|para\s+(?:silvia|ana|daniel))\b",
    re.IGNORECASE,
)


def parse_voice_expense_command(text: str) -> dict[str, Any]:
    """Parse a full voice/chat command including payer, split type, account hint, and items."""
    raw = (text or "").strip()
    lower = _strip_accents(raw.lower())

    paid_by = None
    if re.search(r"\b(pago\s+silvia|pagado\s+por\s+silvia|pago\s+ana|de\s+silvia)\b", lower):
        paid_by = "silvia"
    elif re.search(r"\b(pago\s+daniel|pagado\s+por\s+daniel|de\s+daniel)\b", lower):
        paid_by = "daniel"

    split_type = None
    if re.search(r"\b(todo\s+silvia|todo\s+ana|solo\s+silvia|para\s+silvia)\b", lower):
        split_type = "all_ana"
    elif re.search(r"\b(todo\s+daniel|solo\s+daniel|para\s+daniel)\b", lower):
        split_type = "all_daniel"
    elif re.search(r"\b(mitad\s+y\s+mitad|a\s+medias|mitad|compartido)\b", lower):
        split_type = "half"

    bank_hint = None
    if "nequi" in lower:
        bank_hint = "nequi"
    elif "credito" in lower or "tarjeta" in lower:
        bank_hint = "nu_credito"
    elif "nu" in lower:
        bank_hint = "nu_ahorros"

    cleaned_for_items = METADATA_PHRASES_RE.sub(" ", raw)
    items = parse_expenses_text(cleaned_for_items)
    if not items:
        items = parse_expenses_text(raw)

    total_amount = sum(int(item["amount"]) for item in items)
    title = str(items[0]["description"]).capitalize() if len(items) == 1 else ("Compra por voz" if items else "")

    return {
        "title": title,
        "totalAmount": total_amount,
        "paidBy": paid_by,
        "splitType": split_type,
        "bankHint": bank_hint,
        "items": items,
    }
