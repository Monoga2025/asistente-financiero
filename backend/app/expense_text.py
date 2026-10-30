from __future__ import annotations

import re


AMOUNT_RE = re.compile(r"\$?\s*(\d[\d.,]*)\s*(millones|millon|mil|k)?\b", re.IGNORECASE)
SPLIT_RE = re.compile(r"[\n;]|,(?!\d)|\s+y\s+", re.IGNORECASE)
MULTIPLIERS = {"mil": 1_000, "k": 1_000, "millon": 1_000_000, "millones": 1_000_000}


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
    """Parse Colombian-style amounts: 5000, $5.000, 3 mil, 2k, 1,5 millones."""
    match = AMOUNT_RE.fullmatch((text or "").strip())
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
    items: list[dict[str, int | str]] = []
    for fragment in SPLIT_RE.split(text or ""):
        fragment = fragment.strip()
        if not fragment:
            continue
        match = None
        for candidate in AMOUNT_RE.finditer(fragment):
            match = candidate
        if not match:
            continue
        amount = parse_amount(match.group(0))
        description = re.sub(r"\s+", " ", fragment[: match.start()] + " " + fragment[match.end():]).strip(" -:$")
        if amount and description:
            items.append({"description": description[:120], "amount": amount})
    return items
