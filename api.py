# api.py
from typing import Dict, Any

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from par_engine import project_cash_value_sean_baseline

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
    horizon_years: int = 30
    monthly_premium: float = 5000.0
    point_id: int = 3  # kept for metadata for now



@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}

@app.post("/project")
def project(req: ProjectRequest) -> Dict[str, Any]:
    # 1) Get calibrated baseline for Sean’s case (30M NS, 5k/month)
    base_schedule = project_cash_value_sean_baseline(horizon_years=req.horizon_years)

    # 2) Scale schedule by user’s premium vs baseline
    BASE_PREMIUM = 5000.0
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
            "horizon_years": req.horizon_years,
            "monthly_premium": req.monthly_premium,
            "point_id": req.point_id,
        },
        "schedule": scaled_schedule,
    }


