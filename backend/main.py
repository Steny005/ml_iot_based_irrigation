import os
import joblib
import pandas as pd
import requests

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


# ============================================================
# Initialize FastAPI App
# ============================================================

app = FastAPI(
    title="Smart Irrigation Decision Engine",
    version="1.0.0",
    description="API for real-time ESP32 telemetry processing and ML irrigation control."
)


# ============================================================
# Enable CORS for Frontend Interaction
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Load Saved ML Model
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "ml", "saved_model.pkl")

try:
    model = joblib.load(MODEL_PATH)
    print(f"[INFO] ML Model loaded successfully from {MODEL_PATH}")

except Exception as e:
    model = None
    print(f"[ERROR] Could not load model: {e}")


# ============================================================
# Global In-Memory State
# ============================================================

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

    "weather_override": False,
    "rain_probability": 0,
    "rain_amount": 0.0,

    "override_reason": "None"
}


# ============================================================
# Pydantic Input Schema
# ============================================================

class TelemetryPayload(BaseModel):

    soil_moisture: float = Field(..., example=12.5)

    temperature: float = Field(..., example=31.2)

    humidity: float = Field(..., example=65.0)

    light: int = Field(..., example=24)

    time_since_irrigation: int = Field(..., example=1200)

    moisture_drop_rate: float = Field(..., example=0.15)

    water_tank_level: float = Field(..., example=85.0)


# ============================================================
# Root Endpoint
# ============================================================

@app.get("/")
def root():

    return {
        "status": "online",
        "message": "Smart Irrigation API is running."
    }


# ============================================================
# Weather API
# ============================================================

@app.get("/api/weather")
def get_weather():

    url = (
        "https://api.open-meteo.com/v1/forecast"
        "?latitude=9.50996"
        "&longitude=76.55067"
        "&hourly=precipitation_probability,rain,precipitation,weather_code"
        "&forecast_hours=6"
        "&timezone=auto"
    )

    try:

        response = requests.get(
            url,
            timeout=10
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as e:

        raise HTTPException(
            status_code=503,
            detail=f"Weather API unavailable: {str(e)}"
        )


# ============================================================
# Check Rain for Immediate Irrigation Decision
# ============================================================

def check_rain_next_hour():

    """
    Checks whether rain is expected during the
    immediate forecast period.

    Returns:

        rain_expected
        rain_probability
        rain_amount
    """

    url = (
        "https://api.open-meteo.com/v1/forecast"
        "?latitude=9.50996"
        "&longitude=76.55067"
        "&hourly=precipitation_probability,rain,precipitation,weather_code"
        "&forecast_hours=2"
        "&timezone=auto"
    )

    try:

        response = requests.get(
            url,
            timeout=10
        )

        response.raise_for_status()

        weather = response.json()

        hourly = weather["hourly"]

        # First forecast hour
        rain_probability = hourly["precipitation_probability"][0]

        rain_amount = hourly["rain"][0]

        # Rain decision threshold
        rain_expected = (
            rain_probability >= 60
            and rain_amount >= 0.1
        )

        print(
            f"[WEATHER] Rain probability: "
            f"{rain_probability}% | "
            f"Rain: {rain_amount} mm | "
            f"Expected: {rain_expected}"
        )

        return (
            rain_expected,
            rain_probability,
            rain_amount
        )

    except Exception as e:

        print(
            f"[WARNING] Weather API failed: {e}"
        )

        # If weather API fails,
        # do not block the existing ML system.
        return (
            False,
            0,
            0.0
        )


# ============================================================
# ESP32 Telemetry + Irrigation Decision
# ============================================================

@app.post("/api/telemetry")
def process_telemetry(
    data: TelemetryPayload
):

    global latest_system_state

    # --------------------------------------------------------
    # Check ML Model
    # --------------------------------------------------------

    if model is None:

        raise HTTPException(
            status_code=500,
            detail="ML Model is not loaded."
        )


    # --------------------------------------------------------
    # 1. Format Telemetry for ML Model
    # --------------------------------------------------------

    input_data = pd.DataFrame([{

        "soil_moisture": data.soil_moisture,

        "temperature": data.temperature,

        "humidity": data.humidity,

        "light": data.light,

        "time_since_irrigation": data.time_since_irrigation,

        "moisture_drop_rate": data.moisture_drop_rate

    }])


    # --------------------------------------------------------
    # 2. Generate ML Prediction
    #
    # 0 = Irrigation NOT required
    # 1 = Irrigation required
    # --------------------------------------------------------

    ml_pred = int(
        model.predict(input_data)[0]
    )


    # --------------------------------------------------------
    # 3. Initialize Decision Variables
    # --------------------------------------------------------

    pump_status = "OFF"

    safety_override = False

    weather_override = False

    override_reason = "None"

    rain_probability = 0

    rain_amount = 0.0


    # ========================================================
    # 4. IRRIGATION DECISION ENGINE
    # ========================================================

    if ml_pred == 1:

        # ----------------------------------------------------
        # PRIORITY 1:
        # WATER TANK SAFETY
        # ----------------------------------------------------

        if data.water_tank_level < 15.0:

            pump_status = "OFF"

            safety_override = True

            override_reason = (
                "Critical: Water Tank Level < 15%"
            )


        else:

            # ------------------------------------------------
            # PRIORITY 2:
            # WEATHER CHECK
            # ------------------------------------------------

            (
                rain_expected,
                rain_probability,
                rain_amount
            ) = check_rain_next_hour()


            if rain_expected:

                # --------------------------------------------
                # Rain expected → DO NOT IRRIGATE
                # --------------------------------------------

                pump_status = "OFF"

                weather_override = True

                override_reason = (
                    f"Rain expected soon "
                    f"({rain_probability}% probability, "
                    f"{rain_amount} mm)"
                )


            else:

                # --------------------------------------------
                # No significant rain expected
                # → Allow ML irrigation decision
                # --------------------------------------------

                pump_status = "ON"

                override_reason = (
                    "ML Triggered Irrigation"
                )


    else:

        # ----------------------------------------------------
        # ML says irrigation is NOT required
        # ----------------------------------------------------

        pump_status = "OFF"

        override_reason = (
            "Soil Moisture Optimal"
        )


    # ========================================================
    # 5. Update Dashboard State
    # ========================================================

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

        "weather_override": weather_override,


        "rain_probability": rain_probability,

        "rain_amount": rain_amount,


        "override_reason": override_reason
    }


    # ========================================================
    # 6. Return Control Command to ESP32
    # ========================================================

    return {

        "pump_command": pump_status,

        "ml_recommendation": ml_pred,

        "safety_override": safety_override,

        "weather_override": weather_override,

        "rain_probability": rain_probability,

        "rain_amount": rain_amount,

        "reason": override_reason
    }


# ============================================================
# Dashboard Endpoint
# ============================================================

@app.get("/api/dashboard")
def get_dashboard_data():

    return latest_system_state