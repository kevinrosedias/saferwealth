# peek_cf.py
import os
import modelx as mx

BASE_DIR = os.path.dirname(__file__)
MODEL_DIR = os.path.join(BASE_DIR, "savings", "CashValue_SE")

model = mx.read_model(MODEL_DIR)
Projection = model.Projection

Projection.point_id = 3  # same as before

cf = Projection.result_cf()
print("Columns:", list(cf.columns))
print("First few rows:")
print(cf.head())
