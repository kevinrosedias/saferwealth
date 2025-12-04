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
    point_id: int = 3
    horizon_years: int = 30


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/project")
def project(req: ProjectRequest) -> Dict[str, Any]:
    schedule = project_cash_value(
        point_id=req.point_id,
        horizon_years=req.horizon_years
    )
    return {"schedule": schedule}
