import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import h3
import mlflow
import pandas as pd
import numpy as np

app = FastAPI(
    title="Chrono-Spatial Marketplace Dispatch Engine",
    description="Production-grade latency engine for predicting spatiotemporal ride-hailing demand.",
    version="1.0.0"
)

# Load the trained model from MLflow Model Registry
MODEL_NAME = "workspace.default.geospatial_demand_engine"
MODEL_VERSION = "1"
model = None

try:
    model = mlflow.pyfunc.load_model(f"models:/{MODEL_NAME}/{MODEL_VERSION}")
    print(f"✅ Loaded model: {MODEL_NAME} version {MODEL_VERSION}")
except Exception as e:
    print(f"⚠️  Warning: Could not load model - {e}")
    print("Using fallback predictions")

# Define the structured Request Payload mimicking an app user or dispatch ping
class PredictionPayload(BaseModel):
    latitude: float
    longitude: float

# Define the Response Payload format
class PredictionResponse(BaseModel):
    h3_index: str
    target_resolution: int
    predicted_demand_next_15m: float
    inference_latency_ms: float

RESOLUTION = 8

@app.get("/")
def health_check():
    model_status = "loaded" if model else "fallback"
    return {
        "status": "online",
        "engine": "Geospatial_Demand_Engine",
        "version": "1.0.0",
        "model_status": model_status
    }

@app.post("/predict", response_model=PredictionResponse)
def predict_demand(payload: PredictionPayload):
    start_time = datetime.datetime.now()
    
    # Validate geographic bounds roughly matching NYC territory
    if not (40.4 <= payload.latitude <= 40.9) or not (-74.3 <= payload.longitude <= -73.6):
        raise HTTPException(status_code=400, detail="Coordinates out of bounds for the NYC marketplace simulation framework.")
    
    # 1. Convert continuous raw coordinates to H3 Spatial Index on the fly
    try:
        spatial_hex = h3.latlng_to_cell(payload.latitude, payload.longitude, RESOLUTION)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Spatial indexing failed: {str(e)}")
    
    # 2. Extract current Temporal features from system clock
    now = datetime.datetime.now()
    current_hour = now.hour
    day_of_week = now.isoweekday()  # 1-7 Mon-Sun
    is_weekend = 1 if day_of_week in [6, 7] else 0
    is_rush_hour = 1 if current_hour in [7, 8, 9, 17, 18, 19] else 0
    
    # 3. Simulate Feature Store Lookup
    # In a fully deployed cloud system, you would query an online store (e.g., Feast or Redis) 
    # to pull the actual lag features for this hex address. 
    # Here, we simulate a standard baseline state lookup.
    mock_current_volume = 42.0
    mock_lag_15m = 38.0
    mock_lag_30m = 35.0
    mock_lag_60m = 33.0
    
    # 4. Execute Model Prediction with correct schema
    if model:
        # Build feature vector matching the trained model schema
        features = {
            "supply_volume": np.int64(35),
            "supply_demand_ratio": 0.85,
            "demand_lag_15min": np.int64(int(mock_lag_15m)),
            "demand_lag_30min": float(mock_lag_30m),
            "demand_lag_60min": float(mock_lag_60m),
            "demand_rolling_avg_1h": (mock_lag_15m + mock_lag_30m + mock_lag_60m) / 3.0,
            "demand_momentum": 0.05,
            "neighbor_avg_demand": 40.0,
            "neighbor_total_demand": np.int64(240),
            "spatial_demand_gradient": 0.0,
            "hour_of_day": np.int32(current_hour),
            "day_of_week": np.int32(day_of_week),
            "is_weekend": np.int32(is_weekend),
            "is_rush_hour": np.int32(is_rush_hour)
        }
        
        input_df = pd.DataFrame([features])
        prediction = float(model.predict(input_df)[0])
    else:
        # Fallback prediction
        prediction = (mock_current_volume * 0.95) + (current_hour * 0.1) if current_hour in [8, 9, 17, 18, 21] else (mock_current_volume * 0.7)
    
    end_time = datetime.datetime.now()
    latency_ms = (end_time - start_time).total_seconds() * 1000.0
    
    return PredictionResponse(
        h3_index=spatial_hex,
        target_resolution=RESOLUTION,
        predicted_demand_next_15m=round(max(0.0, prediction), 2),
        inference_latency_ms=round(latency_ms, 3)
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("appmain:app", host="0.0.0.0", port=8000, reload=True)
