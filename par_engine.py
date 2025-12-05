# par_engine.py
import os
from typing import List, Dict

import modelx as mx
import pandas as pd

from typing import List, Dict

CALIBRATION_FACTORS_CV_30M_NS_5K: Dict[int, float] = {
    # paste your 70 CV lines here
}

CALIBRATION_FACTORS_DB_30M_NS_5K: Dict[int, float] = {
    # paste your 70 DB lines here
}


def _apply_calibration_30M_NS_5K(schedule: List[Dict]) -> List[Dict]:
    """Apply per-year calibration to lifelib schedule for Sean baseline (Years 1–70)."""
    calibrated: List[Dict] = []
    for row in schedule:
        year = row["policy_year"]
        f_cv = CALIBRATION_FACTORS_CV_30M_NS_5K.get(year, 1.0)
        f_db = CALIBRATION_FACTORS_DB_30M_NS_5K.get(year, 1.0)

        calibrated.append({
            "policy_year": year,
            "cash_value": round(row["cash_value"] * f_cv, 2),
            "death_benefit": round(row["death_benefit"] * f_db, 2),
        })
    return calibrated


BASE_DIR = os.path.dirname(__file__)
MODEL_DIR = os.path.join(BASE_DIR, "savings", "CashValue_SE")

# Load the model once
model = mx.read_model(MODEL_DIR)
Projection = model.Projection


def project_cash_value(point_id: int = 3, horizon_years: int = 30) -> List[Dict]:
    """Base raw lifelib projection, no calibration or premium scaling."""
    _ensure_model_loaded()
    proj = _Projection
    proj.point_id = point_id

    cf = proj.result_cf().reset_index()

    if "t" in cf.columns:
        time_col = "t"
    elif "index" in cf.columns:
        time_col = "index"
    else:
        raise KeyError(f"No time index column found. Columns: {list(cf.columns)}")

    if "Change in AV" not in cf.columns:
        raise KeyError(f"'Change in AV' column not found. Columns: {list(cf.columns)}")

    cf["cum_av"] = cf["Change in AV"].cumsum()

    schedule: List[Dict] = []

    for year in range(1, horizon_years + 1):
        t = year * 12
        row = cf[cf[time_col] == t]
        if row.empty:
            break

        av = float(row["cum_av"].iloc[0])
        death_benefit = av * 1.10  # your current proxy

        schedule.append({
            "policy_year": year,
            "cash_value": av,
            "death_benefit": death_benefit,
        })

    return schedule

def project_cash_value_sean_baseline(horizon_years: int = 30) -> List[Dict]:
    """
    Baseline: Male 30, NS, 5k/month scenario using point_id=3,
    calibrated to official par illustration for Years 1–70.
    """
    raw = project_cash_value(point_id=3, horizon_years=horizon_years)
    return _apply_calibration_30M_NS_5K(raw)


