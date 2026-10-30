from __future__ import annotations

import math
from calendar import monthrange
from datetime import date
from typing import Any

from .categorize import categorize_by_rules
from .finance import DANIEL, ANA


def _months_until(deadline: date, today: date) -> int:
    if deadline <= today:
        return 0
    months = (deadline.year - today.year) * 12 + (deadline.month - today.month)
    if deadline.day > today.day:
        months += 1
    return max(months, 0)


def project_goal(
    target: int,
    saved: int,
    monthly_saving: int,
    deadline: date | None,
    today: date | None = None,
) -> dict[str, Any]:
    today = today or date.today()
    missing = max(0, int(target) - int(saved or 0))
    if missing == 0:
        return {"reached": True, "missing": 0, "months_left": 0, "needed_monthly": 0, "shortfall_monthly": 0, "on_track": True, "estimated_months": 0}

    monthly = max(0, int(monthly_saving or 0))
    result: dict[str, Any] = {
        "reached": False,
        "missing": missing,
        "months_left": None,
        "needed_monthly": None,
        "shortfall_monthly": 0,
        "on_track": False,
        "estimated_months": math.ceil(missing / monthly) if monthly > 0 else None,
    }
    if deadline is not None:
        months_left = _months_until(deadline, today)
        needed = round(missing / months_left) if months_left else missing
        result.update(
            months_left=months_left,
            needed_monthly=needed,
            shortfall_monthly=max(0, needed - monthly),
            on_track=monthly >= needed,
        )
    return result


def month_close_summary(
    expenses: list[dict[str, Any]],
    previous_expenses: list[dict[str, Any]],
    year: int,
    month: int,
) -> dict[str, Any]:
    total = 0
    by_category: dict[str, int] = {}
    by_person = {ANA: 0, DANIEL: 0}
    for expense in expenses:
        amount = int(expense.get("total_amount") or 0)
        total += amount
        category = categorize_by_rules(str(expense.get("title") or ""))
        by_category[category] = by_category.get(category, 0) + amount
        by_person[ANA] += int(expense.get("share_ana") or 0)
        by_person[DANIEL] += int(expense.get("share_daniel") or 0)

    by_category = dict(sorted(by_category.items(), key=lambda pair: pair[1], reverse=True))
    previous_total = sum(int(e.get("total_amount") or 0) for e in previous_expenses)
    change_pct = round((total - previous_total) / previous_total * 100, 1) if previous_total else None
    return {
        "year": year,
        "month": month,
        "total": total,
        "count": len(expenses),
        "by_category": by_category,
        "top_category": next(iter(by_category), None),
        "by_person": by_person,
        "previous_total": previous_total,
        "change_pct": change_pct,
        "daily_average": round(total / monthrange(year, month)[1]),
    }
