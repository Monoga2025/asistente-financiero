from datetime import date

from app.goals import month_close_summary, project_goal


def test_project_goal_reached():
    result = project_goal(target=1000, saved=1000, monthly_saving=0, deadline=None, today=date(2026, 1, 15))
    assert result["reached"] is True
    assert result["missing"] == 0


def test_project_goal_with_deadline_computes_needed_monthly():
    result = project_goal(target=1_200_000, saved=0, monthly_saving=100_000, deadline=date(2026, 12, 20), today=date(2026, 1, 15))

    assert result["missing"] == 1_200_000
    assert result["months_left"] == 12
    assert result["needed_monthly"] == 100_000
    assert result["on_track"] is True


def test_project_goal_off_track_reports_shortfall():
    result = project_goal(target=1_200_000, saved=0, monthly_saving=50_000, deadline=date(2026, 12, 20), today=date(2026, 1, 15))

    assert result["on_track"] is False
    assert result["shortfall_monthly"] == 50_000


def test_project_goal_without_deadline_estimates_months():
    result = project_goal(target=300_000, saved=0, monthly_saving=100_000, deadline=None, today=date(2026, 1, 15))

    assert result["months_left"] is None
    assert result["estimated_months"] == 3


def test_month_close_summary_totals_categories_and_comparison():
    current = [
        {"title": "Pago arriendo", "total_amount": 700_000, "share_ana": 350_000, "share_daniel": 350_000},
        {"title": "Almuerzo restaurante", "total_amount": 50_000, "share_ana": 25_000, "share_daniel": 25_000},
    ]
    previous = [{"title": "Almuerzo restaurante", "total_amount": 250_000, "share_ana": 125_000, "share_daniel": 125_000}]

    summary = month_close_summary(current, previous, 2026, 7)

    assert summary["total"] == 750_000
    assert summary["count"] == 2
    assert summary["by_category"] == {"Vivienda": 700_000, "Alimentacion": 50_000}
    assert summary["top_category"] == "Vivienda"
    assert summary["by_person"] == {"ana": 375_000, "daniel": 375_000}
    assert summary["previous_total"] == 250_000
    assert summary["change_pct"] == 200.0
    assert summary["daily_average"] == round(750_000 / 31)


def test_month_close_summary_empty_month():
    summary = month_close_summary([], [], 2026, 2)

    assert summary["total"] == 0
    assert summary["top_category"] is None
    assert summary["change_pct"] is None
