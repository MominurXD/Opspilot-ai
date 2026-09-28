from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pandas as pd
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.analytics import detect_anomalies, forecast_revenue, generate_insights, summary_metrics, validate_frame

router = APIRouter()
DATA_PATH = Path(__file__).resolve().parents[3] / "data" / "sample_business_data.csv"


def load_sample() -> pd.DataFrame:
    return validate_frame(pd.read_csv(DATA_PATH))


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.get("/dashboard")
def dashboard() -> dict:
    frame = load_sample()
    return build_dashboard(frame)


@router.post("/dashboard/upload")
async def dashboard_upload(file: UploadFile = File(...)) -> dict:
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a CSV file.")

    try:
        content = await file.read()
        frame = validate_frame(pd.read_csv(BytesIO(content)))
        return build_dashboard(frame)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Could not parse the uploaded CSV.") from exc


def build_dashboard(frame: pd.DataFrame) -> dict:
    timeline = [
        {
            "date": row.date.date().isoformat(),
            "revenue": round(float(row.revenue), 2),
            "expenses": round(float(row.expenses), 2),
            "profit": round(float(row.profit), 2),
            "orders": int(row.orders),
        }
        for row in frame.tail(30).itertuples()
    ]

    return {
        "metrics": summary_metrics(frame),
        "timeline": timeline,
        "forecast": [point.__dict__ for point in forecast_revenue(frame)],
        "anomalies": detect_anomalies(frame),
        "insights": generate_insights(frame),
    }
