# OpsPilot AI

**Operations intelligence for small businesses turn daily sales and cost data into forecasts, anomaly alerts and practical decisions.**

OpsPilot AI is a full-stack analytics project built to demonstrate production-minded software engineering, data analysis and applied machine learning in a business setting.

## Why this project exists

Small businesses often have sales and expense data but limited time to analyse it. OpsPilot AI turns a simple daily CSV export into a decision dashboard that answers four questions:

1. How is the business performing right now?
2. What changed compared with the previous period?
3. Is anything unusual happening?
4. What does the next week look like if current trends continue?

## Features

- KPI dashboard for revenue, expenses, profit, margin, orders and average order value
- CSV upload and validation
- 7-day revenue forecasting using scikit-learn
- Statistical anomaly detection across revenue, expenses and orders
- Automatically generated operational insights
- Responsive React + TypeScript dashboard
- FastAPI REST API with Swagger/OpenAPI docs
- Unit/API tests with pytest
- Dockerised frontend and backend
- GitHub Actions CI for tests and frontend builds
- Architecture documentation and production roadmap

## Tech stack

| Layer | Technology |
| --- | --- |
| Frontend | React, TypeScript, Vite, Recharts |
| Backend | Python, FastAPI, Pydantic |
| Analytics | Pandas, NumPy, scikit-learn |
| Testing | pytest, FastAPI TestClient |
| DevOps | Docker, Docker Compose, GitHub Actions |

## Demo data format

Upload a CSV with these columns:

```csv
date,revenue,expenses,orders
2026-08-01,2450.50,1510.20,112
2026-08-02,2610.00,1575.40,121
```

At least seven valid daily rows are required. A generated sample dataset is included in `data/sample_business_data.csv`.

## Run locally

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
PYTHONPATH=. uvicorn app.main:app --reload
```

API: `http://localhost:8000`  
Swagger docs: `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Dashboard: `http://localhost:5173`

### Tests

```bash
cd backend
PYTHONPATH=. pytest -q
```

### Docker

```bash
docker compose up --build
```

## API endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/api/v1/health` | Service health check |
| GET | `/api/v1/dashboard` | Analyse bundled demo data |
| POST | `/api/v1/dashboard/upload` | Analyse a user-uploaded CSV |

## Engineering decisions

The first version intentionally uses interpretable analytics rather than hiding logic behind a third-party AI API. Forecasts, anomaly thresholds and insight rules can be inspected, tested and discussed in an interview. The architecture is designed so the analytics layer can later be replaced by more sophisticated forecasting models without changing the frontend contract.

See [`docs/architecture.md`](docs/architecture.md) for the system design and production roadmap.

## Future improvements

- PostgreSQL persistence and organisation accounts
- Authentication and role-based access control
- POS/accounting integrations
- Forecast back-testing and model comparison
- Inventory reorder predictions
- Staff demand recommendations
- AWS ECS/RDS deployment and Terraform infrastructure
- Observability, structured logging and audit events

## Licence

MIT
