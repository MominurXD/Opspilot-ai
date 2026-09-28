from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


REQUIRED_COLUMNS = {"date", "revenue", "expenses", "orders"}


@dataclass
class ForecastPoint:
    date: str
    predicted_revenue: float


def validate_frame(frame: pd.DataFrame) -> pd.DataFrame:
    missing = REQUIRED_COLUMNS - set(frame.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

    cleaned = frame.copy()
    cleaned["date"] = pd.to_datetime(cleaned["date"], errors="coerce")
    for column in ["revenue", "expenses", "orders"]:
        cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")

    cleaned = cleaned.dropna(subset=["date", "revenue", "expenses", "orders"]).sort_values("date")
    if len(cleaned) < 7:
        raise ValueError("At least 7 valid daily records are required.")

    cleaned["profit"] = cleaned["revenue"] - cleaned["expenses"]
    cleaned["margin"] = np.where(cleaned["revenue"] > 0, cleaned["profit"] / cleaned["revenue"], 0.0)
    return cleaned


def summary_metrics(frame: pd.DataFrame) -> dict:
    current = frame.tail(7)
    previous = frame.iloc[-14:-7] if len(frame) >= 14 else frame.head(0)

    revenue = float(current["revenue"].sum())
    expenses = float(current["expenses"].sum())
    profit = float(current["profit"].sum())
    orders = int(current["orders"].sum())
    margin = (profit / revenue * 100) if revenue else 0.0
    aov = revenue / orders if orders else 0.0

    previous_revenue = float(previous["revenue"].sum()) if not previous.empty else revenue
    revenue_change = ((revenue - previous_revenue) / previous_revenue * 100) if previous_revenue else 0.0

    return {
        "revenue": round(revenue, 2),
        "expenses": round(expenses, 2),
        "profit": round(profit, 2),
        "orders": orders,
        "margin_percent": round(margin, 1),
        "average_order_value": round(aov, 2),
        "revenue_change_percent": round(revenue_change, 1),
    }


def detect_anomalies(frame: pd.DataFrame) -> list[dict]:
    recent = frame.tail(min(30, len(frame))).copy()
    anomalies: list[dict] = []

    for metric in ["revenue", "expenses", "orders"]:
        mean = recent[metric].mean()
        std = recent[metric].std(ddof=0)
        if std == 0 or np.isnan(std):
            continue
        recent[f"{metric}_z"] = (recent[metric] - mean) / std
        flagged = recent[recent[f"{metric}_z"].abs() >= 1.8]
        for _, row in flagged.iterrows():
            direction = "above" if row[f"{metric}_z"] > 0 else "below"
            anomalies.append(
                {
                    "date": row["date"].date().isoformat(),
                    "metric": metric,
                    "value": round(float(row[metric]), 2),
                    "severity": "high" if abs(row[f"{metric}_z"]) >= 2.5 else "medium",
                    "message": f"{metric.title()} was unusually {direction} its recent baseline.",
                }
            )

    return sorted(anomalies, key=lambda item: item["date"], reverse=True)[:8]


def forecast_revenue(frame: pd.DataFrame, days: int = 7) -> list[ForecastPoint]:
    history = frame.tail(min(60, len(frame))).copy()
    x = np.arange(len(history)).reshape(-1, 1)
    y = history["revenue"].to_numpy()
    model = LinearRegression().fit(x, y)

    future_x = np.arange(len(history), len(history) + days).reshape(-1, 1)
    predictions = np.maximum(model.predict(future_x), 0)
    last_date = history["date"].max()

    return [
        ForecastPoint(
            date=(last_date + pd.Timedelta(days=index + 1)).date().isoformat(),
            predicted_revenue=round(float(value), 2),
        )
        for index, value in enumerate(predictions)
    ]


def generate_insights(frame: pd.DataFrame) -> list[dict]:
    current = frame.tail(7)
    previous = frame.iloc[-14:-7] if len(frame) >= 14 else current

    current_revenue = float(current["revenue"].sum())
    previous_revenue = float(previous["revenue"].sum())
    current_expense = float(current["expenses"].sum())
    previous_expense = float(previous["expenses"].sum())
    current_margin = float(current["profit"].sum() / current_revenue * 100) if current_revenue else 0

    revenue_delta = ((current_revenue - previous_revenue) / previous_revenue * 100) if previous_revenue else 0
    expense_delta = ((current_expense - previous_expense) / previous_expense * 100) if previous_expense else 0

    insights = []
    if revenue_delta >= 5:
        insights.append({"type": "positive", "title": "Revenue momentum", "detail": f"Revenue is up {revenue_delta:.1f}% versus the previous 7-day period."})
    elif revenue_delta <= -5:
        insights.append({"type": "warning", "title": "Revenue slowdown", "detail": f"Revenue is down {abs(revenue_delta):.1f}% versus the previous 7-day period. Review order volume and average order value."})
    else:
        insights.append({"type": "neutral", "title": "Revenue stable", "detail": f"Revenue moved {revenue_delta:.1f}% versus the previous 7-day period."})

    if expense_delta > revenue_delta + 5:
        insights.append({"type": "warning", "title": "Costs growing faster than sales", "detail": f"Expenses changed {expense_delta:.1f}% while revenue changed {revenue_delta:.1f}%. Supplier or staffing costs may need review."})
    else:
        insights.append({"type": "positive", "title": "Cost control", "detail": f"Expenses changed {expense_delta:.1f}% against revenue growth of {revenue_delta:.1f}%."})

    margin_type = "positive" if current_margin >= 20 else "warning"
    insights.append({"type": margin_type, "title": "Operating margin", "detail": f"The latest 7-day operating margin is {current_margin:.1f}%."})

    best = frame.loc[frame["revenue"].idxmax()]
    insights.append({"type": "neutral", "title": "Best trading day", "detail": f"{best['date'].strftime('%A')} {best['date'].date().isoformat()} generated £{best['revenue']:.0f} revenue from {int(best['orders'])} orders."})
    return insights
