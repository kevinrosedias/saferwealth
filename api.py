# api.py
from typing import Dict, Any

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from par_engine import project_cash_value

app = FastAPI(title="SaferWealth lifelib Par Engine")

# 🔓 CORS so Wix can call your API from the browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # or lock down to ["https://www.saferwealth.com"] later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ProjectRequest(BaseModel):
    point_id: int = 3           # base product spec (still 3 for now)
    horizon_years: int = 30
    monthly_premium: float = 5000.0  # user’s monthly premium


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/project")
def project(req: ProjectRequest) -> Dict[str, Any]:
    # 1) Get base schedule from lifelib, which we treat as representing 5,000/month
    base_schedule = project_cash_value(
        point_id=req.point_id,
        horizon_years=req.horizon_years
    )

    # 2) Scale cash value & death benefit by the ratio of user premium to base premium
    BASE_PREMIUM = 5000.0  # this is your chosen base for point_id=3
    scale = req.monthly_premium / BASE_PREMIUM if BASE_PREMIUM else 1.0

    scaled_schedule = []
    for row in base_schedule:
        scaled_schedule.append({
            "policy_year": row["policy_year"],
            "cash_value": round(row["cash_value"] * scale, 2),
            "death_benefit": round(row["death_benefit"] * scale, 2),
        })

    return {
        "inputs": {
            "point_id": req.point_id,
            "horizon_years": req.horizon_years,
            "monthly_premium": req.monthly_premium,
        },
        "schedule": scaled_schedule,
    }


