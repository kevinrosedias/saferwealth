# par_engine.py
import os
from typing import List, Dict

import modelx as mx
import pandas as pd

BASE_DIR = os.path.dirname(__file__)
MODEL_DIR = os.path.join(BASE_DIR, "savings", "CashValue_SE")

# Load the model once
model = mx.read_model(MODEL_DIR)
Projection = model.Projection


def project_cash_value(point_id: int = 3, horizon_years: int = 30) -> List[Dict]:
    """
    Use lifelib's CashValue_SE model to build a yearly schedule.

    We reconstruct account value by cumulatively summing the "Change in AV"
    column from the monthly cashflows.
    """

    # 1) Select the model point
    Projection.point_id = point_id

    # 2) Get monthly cashflows
    cf = Projection.result_cf()

    # Bring the time index out as a column
    cf = cf.reset_index()  # index becomes a column, usually called 'index' or 't'

    # Work out which column is the time index
    if "t" in cf.columns:
        time_col = "t"
    elif "index" in cf.columns:
        time_col = "index"
    else:
        raise KeyError(f"No time index column found. Columns: {list(cf.columns)}")

    # 3) Confirm "Change in AV" exists and build cumulative AV
    if "Change in AV" not in cf.columns:
        raise KeyError(f"'Change in AV' column not found. Columns: {list(cf.columns)}")

    cf["cum_av"] = cf["Change in AV"].cumsum()

    schedule: List[Dict] = []

    # 4) Loop through each policy year and grab t = 12, 24, 36, ...
    for year in range(1, horizon_years + 1):
        t = year * 12  # month at end of policy year

        row = cf[cf[time_col] == t]
        if row.empty:
            # No more projection rows for this month
            break

        av = float(row["cum_av"].iloc[0])
        death_benefit = av * 1.10  # simple proxy; we’ll refine/calibrate later

        schedule.append({
            "policy_year": year,
            "cash_value": round(av, 2),
            "death_benefit": round(death_benefit, 2),
        })

    return schedule
