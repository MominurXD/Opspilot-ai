import pandas as pd

from app.services.analytics import forecast_revenue, summary_metrics, validate_frame


def sample_frame(days: int = 14) -> pd.DataFrame:
    frame = pd.DataFrame(
        {
            "date": pd.date_range("2026-01-01", periods=days),
            "revenue": [1000 + i * 20 for i in range(days)],
            "expenses": [600 + i * 5 for i in range(days)],
            "orders": [50 + i for i in range(days)],
        }
    )
    return validate_frame(frame)


def test_summary_metrics_are_consistent():
    metrics = summary_metrics(sample_frame())
    assert metrics["revenue"] > metrics["expenses"]
    assert metrics["profit"] == round(metrics["revenue"] - metrics["expenses"], 2)
    assert metrics["orders"] > 0


def test_forecast_returns_requested_days():
    points = forecast_revenue(sample_frame(), days=7)
    assert len(points) == 7
    assert all(point.predicted_revenue >= 0 for point in points)
