import os
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Initialize FastAPI App
app = FastAPI(
    title="Smart Irrigation Decision Engine",
    version="1.0.0",
    description="API for real-time ESP32 telemetry processing and ML irrigation control."
)

# Enable CORS for Frontend Interaction
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Saved ML Model
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "ml", "saved_model.pkl")

try:
    model = joblib.load(MODEL_PATH)
    print(f"[INFO] ML Model loaded successfully from {MODEL_PATH}")
except Exception as e:
    model = None
    print(f"[ERROR] Could not load model: {e}")

# Global In-Memory State (For Dashboard Telemetry)
latest_system_state = {
    "soil_moisture": 0.0,
    "temperature": 0.0,
    "humidity": 0.0,
    "light": 0,
    "time_since_irrigation": 0,
    "moisture_drop_rate": 0.0,
    "water_tank_level": 100.0,
    "ml_recommendation": 0,
    "pump_status": "OFF",
    "safety_override": False,
    "override_reason": "None"
}


# Pydantic Input Schema
class TelemetryPayload(BaseModel):
    soil_moisture: float = Field(..., example=12.5)
    temperature: float = Field(..., example=31.2)
    humidity: float = Field(..., example=65.0)
    light: int = Field(..., example=24)
    time_since_irrigation: int = Field(..., example=1200)
    moisture_drop_rate: float = Field(..., example=0.15)
    water_tank_level: float = Field(..., example=85.0)


@app.get("/")
def root():
    return {"status": "online", "message": "Smart Irrigation API is running."}


@app.post("/api/telemetry")
def process_telemetry(data: TelemetryPayload):
    global latest_system_state

    if model is None:
        raise HTTPException(status_code=500, detail="ML Model is not loaded.")

    # 1. Format payload into DataFrame matching training features order
    input_data = pd.DataFrame([{
        "soil_moisture": data.soil_moisture,
        "temperature": data.temperature,
        "humidity": data.humidity,
        "light": data.light,
        "time_since_irrigation": data.time_since_irrigation,
        "moisture_drop_rate": data.moisture_drop_rate
    }])

    # 2. Generate ML Prediction (0 = OFF, 1 = ON)
    ml_pred = int(model.predict(input_data)[0])

    # 3. Apply Safety Rules Engine
    pump_status = "OFF"
    safety_override = False
    override_reason = "None"

    if ml_pred == 1:
        if data.water_tank_level < 15.0:
            # Tank dry safety rule: Do not turn pump ON
            pump_status = "OFF"
            safety_override = True
            override_reason = "Critical: Water Tank Level < 15%"
        else:
            pump_status = "ON"
            override_reason = "ML Triggered Irrigation"
    else:
        pump_status = "OFF"
        override_reason = "Soil Moisture Optimal"

    # 4. Update In-Memory State
    latest_system_state = {
        "soil_moisture": data.soil_moisture,
        "temperature": data.temperature,
        "humidity": data.humidity,
        "light": data.light,
        "time_since_irrigation": data.time_since_irrigation,
        "moisture_drop_rate": data.moisture_drop_rate,
        "water_tank_level": data.water_tank_level,
        "ml_recommendation": ml_pred,
        "pump_status": pump_status,
        "safety_override": safety_override,
        "override_reason": override_reason
    }

    # 5. Return Control Command to ESP32
    return {
        "pump_command": pump_status,
        "ml_recommendation": ml_pred,
        "safety_override": safety_override,
        "reason": override_reason
    }


@app.get("/api/dashboard")
def get_dashboard_data():
    return latest_system_state