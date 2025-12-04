import os
import pandas as pd
import modelx as mx

# Base directory = folder where this script lives
BASE_DIR = os.path.dirname(__file__)

# Path to the CashValue_SE model folder we just copied with lifelib.create
MODEL_DIR = os.path.join(BASE_DIR, "savings", "CashValue_SE")

# Read the model
model = mx.read_model(MODEL_DIR)

# The model has a single UserSpace called Projection
Projection = model.Projection

# --- Choose a model point ---

# By default, there are 4 sample model points (A, B, C, D).
# A/B = single premium products, C/D = level premium whole life style. 
# The selected model point is controlled by Projection.point_id (1–4).
# For now, let's use point_id = 3 (spec C: level premium WL-type).
Projection.point_id = 3

# Get the cashflow schedule for that model point
cf = Projection.result_cf()   # DataFrame of monthly cashflows
pv = Projection.result_pv()   # DataFrame of present values

# For sanity, print a few lines
print("=== Cashflows (head) ===")
print(cf.head())

print("\n=== Present Values (tail) ===")
print(pv.tail())

# Optionally, save to CSV for inspection
output_dir = os.path.join(BASE_DIR, "outputs")
os.makedirs(output_dir, exist_ok=True)

cf.to_csv(os.path.join(output_dir, "cashflows_point3.csv"), index=True)
pv.to_csv(os.path.join(output_dir, "present_values_point3.csv"), index=True)

print(f"\nSaved CSVs into: {output_dir}")
