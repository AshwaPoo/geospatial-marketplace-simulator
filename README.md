# Spatiotemporal Marketplace Optimization Engine

A production-grade, low-latency geospatial demand forecasting system for high-throughput ride-hailing marketplace dispatch. This system translates continuous spatial coordinates into optimized discrete hexagonal grids to predict market-space vehicle demand fluctuations.

## 🔗 Live Links
* **Source Code Repository:** [https://github.com/AshwaPoo/geospatial-marketplace-simulator](https://github.com/AshwaPoo/geospatial-marketplace-simulator)
* **Interactive Web Dashboard:** [https://ashwapoo-geospatial-marketplace-simulator-dashboard-wt4aqn.streamlit.app/]

> **Note:** The public web application hosted on Streamlit Cloud runs in high-fidelity fallback simulation mode to showcase the frontend 3D rendering. The full, low-latency FastAPI backend microservice runs locally for live, high-throughput engineering demonstrations.

## 🏗️ Architecture Overview

The system architecture is bifurcated into two core phases: an offline heavy data engineering/modeling pipeline and an online low-latency inference delivery network.

1. **Upstream Heavy Logistics (Databricks & PySpark):** Aggregated and analyzed massive spatiotemporal datasets utilizing PySpark. Maintained feature pipelines, executed spatial aggregation onto **Uber H3 Hexagonal Grids (Resolution 8)**, and managed model tracking, hyperparameter validation, and artifact versioning via **MLflow**.
2. **Downstream Production Serving (FastAPI & Streamlit):** Deployed the optimized machine learning model weights into an isolated, high-performance **FastAPI microservice** achieving an exceptional **inference latency of ~2.5ms**. Built a 3D **Streamlit & PyDeck console** to visualize real-time marketplace dispatch allocation across major operational hubs (e.g., Manhattan Core, JFK Airport, Brooklyn).

## 📊 Model Performance Metrics
* **Architecture:** LightGBM Regressor
* **R² Score:** 0.9994
* **Root Mean Squared Error (RMSE):** 0.84 rides
* **Inference Latency:** < 3.0 ms (Production Benchmark: ~2.59 ms under simulated peak morning rush hour workloads)

## 🛠️ Repository Structure
* `appmain.py`: Production-ready FastAPI implementation featuring schema validation (Pydantic), geospatial coordinate boundary checks, and real-time H3 spatial indexing.
* `dashboard.py`: Frontend Streamlit console rendering 3D interactive hexagonal demand distributions over vector map projections.
* `requirements.txt`: Declarative environment dependencies file for automated continuous deployment pipelines.

## 🚀 Local Deployment & Execution

To spin up the ecosystem locally on your machine, clone the repository and execute the following:

```bash
# Install required dependencies
pip install -r requirements.txt

# Launch the FastAPI backend server (Terminal Tab 1)
python appmain.py

# Launch the interactive Streamlit 3D Dashboard (Terminal Tab 2)
streamlit run dashboard.py
