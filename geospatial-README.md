# 🗺️ Geospatial Marketplace Simulator

> Predicting ride demand per city block, per hour, fast enough that a dispatcher could actually use the answer.

A ride-hailing marketplace has to decide where vehicles should be before riders
open the app. That is a forecasting problem with a latency constraint attached:
a prediction that arrives in two seconds is not a dispatch input, it is a
report. This project builds the model and the serving path together.

Built on 1.5M NYC high-volume for-hire vehicle trip records.

---

## 🔗 Links

- **Dashboard:** [Streamlit console](https://ashwapoo-geospatial-marketplace-simulator-dashboard-wt4aqn.streamlit.app/)
- The hosted dashboard runs on simulated data so the 3D rendering works without a backend. The FastAPI service runs locally.

---

## 🧭 The approach

**Hexagons instead of coordinates.** Raw pickup latitude and longitude are
continuous, which makes "demand here" undefined. Trips are aggregated onto
Uber's H3 hexagonal grid at resolution 8, roughly a few city blocks. Hexagons
beat a square grid because every neighbor is equidistant, so spatial features
do not depend on whether a cell is adjacent edge-to-edge or corner-to-corner.

**Split the pipeline at the latency boundary.** Aggregation, feature building,
and training run offline in PySpark on Databricks, with MLflow tracking runs
and versioning artifacts. Only the trained weights cross into the serving
path, which is a FastAPI process doing H3 indexing, validation, and inference
and nothing else. Everything expensive happens before the request arrives.

---

## 📊 Results

| Metric | Value |
|---|---|
| Model | LightGBM regressor |
| RMSE | 0.84 rides per hexagon-hour |
| Improvement over naive lag baseline | 88.8% |
| Inference latency | ~2.6ms, measured under simulated morning peak |
| R² | 0.9994 |

**On that R².** It is not the number to judge this by. Hourly demand in a
fixed hexagon is strongly autocorrelated, so a model with lag features
explains almost all the variance before it does anything clever. The honest
measure is the 88.8% RMSE improvement over a naive lag baseline, which is
what the model adds on top of "tomorrow looks like today." I am reporting the
R² because leaving it out would be worse, not because it means what a 0.9994
usually means.

---

## ⚠️ What is simulated

- **The feature store.** Features are computed in-process at request time. A
  production version puts them in Redis and the service reads rather than
  computes. The architecture is shaped for that substitution but does not
  implement it.
- **The hosted dashboard.** Streamlit Cloud has no backend to call, so the
  public version generates plausible demand surfaces to exercise the
  rendering. Real predictions require running the API locally.

The architecture is production-oriented. It is not production-deployed, and
the difference matters.

---

## 🛠️ Repository

| File | What it does |
|---|---|
| `appmain.py` | FastAPI service: Pydantic schema validation, coordinate boundary checks, H3 indexing, inference |
| `dashboard.py` | Streamlit and PyDeck 3D console rendering demand across Manhattan, JFK, and Brooklyn |
| `requirements.txt` | Dependencies |

---

## ▶️ Run it locally

```bash
pip install -r requirements.txt

# backend
python appmain.py

# dashboard, in a second terminal
streamlit run dashboard.py
```

---

## 🧱 Stack

PySpark, Databricks, MLflow, H3, LightGBM, FastAPI, Streamlit, PyDeck.
