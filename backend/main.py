import os
import sys
import joblib
import pandas as pd
import requests

# Ensure backend directory is in python path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from fastapi import FastAPI, HTTPException, Query, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from advisor.crops_data import CROPS_DATABASE
from advisor.fertilizer_engine import get_available_crops, recommend_fertilizer
from advisor.organic_engine import generate_organic_recipe, ORGANIC_INPUT_PROFILES
from advisor.ai_explainer import generate_advisor_explanation
from feed.rag_engine import RAGEngine
from feed.store import FeedStore


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

# ============================================================
# RAG Engine & Farmer Feed Storage Initialization
# ============================================================

DOCS_DIR = os.path.join(CURRENT_DIR, "knowledge", "documents")
FEED_DATA_FILE = os.path.join(CURRENT_DIR, "data", "feed_cards.json")
rag_engine = RAGEngine(DOCS_DIR)
feed_store = FeedStore(FEED_DATA_FILE, rag_engine)


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

# ============================================================
# Pydantic Schemas for AI Advisor & Feed
# ============================================================

class FertilizerRequest(BaseModel):
    crop_id: str = Field(..., example="paddy")
    growth_stage: Optional[str] = Field(None, example="Active Tillering (15-20 DAT)")
    latitude: float = Field(9.50996, example=9.50996)
    longitude: float = Field(76.55067, example=76.55067)
    soil_data: Optional[Dict[str, Any]] = None


class OrganicRecipeRequest(BaseModel):
    crop_id: str = Field(..., example="banana")
    growth_stage: Optional[str] = Field(None, example="Early Vegetative")
    available_inputs: Optional[List[str]] = Field(default_factory=list, example=["cow_dung", "vermicompost", "neem_cake"])
    soil_condition: Optional[str] = None


class ExplainRequest(BaseModel):
    crop_name: str
    stage: str
    weather_summary: str = "Clear weather"
    recommendations: List[Dict[str, Any]] = []


class FeedQueryRequest(BaseModel):
    query: str = Field(..., example="കുരുമുളക് വാട്ടരോഗം")
    top_k: int = Field(5, example=5)


# ============================================================
# AI AGRICULTURAL ADVISOR ENDPOINTS
# ============================================================

@app.get("/api/advisor/crops")
def list_crops():
    """Returns supported crops, scientific names, and their growth stages."""
    return {
        "status": "success",
        "crops": get_available_crops()
    }


@app.post("/api/advisor/fertilizer")
def get_fertilizer_recommendation(payload: FertilizerRequest):
    """Computes verified fertilizer recommendations incorporating stage, coordinates, and weather."""
    weather_info = None
    try:
        rain_expected, rain_prob, rain_amt = check_rain_next_hour()
        weather_info = {
            "rain_probability": rain_prob,
            "rain_amount": rain_amt
        }
    except Exception as e:
        weather_info = {"rain_probability": 0, "rain_amount": 0.0}

    return recommend_fertilizer(
        crop_id=payload.crop_id,
        growth_stage=payload.growth_stage,
        latitude=payload.latitude,
        longitude=payload.longitude,
        weather_info=weather_info,
        soil_data=payload.soil_data
    )


@app.post("/api/advisor/organic-recipe")
def get_organic_recipe(payload: OrganicRecipeRequest):
    """Generates scientific organic manure recipe based on available farm inputs."""
    return generate_organic_recipe(
        crop_id=payload.crop_id,
        growth_stage=payload.growth_stage,
        available_inputs=payload.available_inputs,
        soil_condition=payload.soil_condition
    )


@app.get("/api/advisor/organic-inputs")
def list_organic_inputs():
    """Returns verified list of organic manure inputs and nutrient profiles."""
    return {
        "status": "success",
        "inputs": ORGANIC_INPUT_PROFILES
    }


@app.post("/api/advisor/explain")
def get_explanation(payload: ExplainRequest):
    """Generates AI farmer-friendly explanation grounded in KAU guidelines."""
    return generate_advisor_explanation(
        crop_name=payload.crop_name,
        stage=payload.stage,
        weather_summary=payload.weather_summary,
        recommendations_summary=payload.recommendations
    )


# ============================================================
# Admin Authorization for Feed Management
# ============================================================

ADMIN_SECRET_KEY = os.environ.get("ADMIN_SECRET_KEY", "admin_secure_irrigation_2026")

def verify_admin_authorization(
    x_admin_key: Optional[str] = Header(None, alias="X-Admin-Key"),
    authorization: Optional[str] = Header(None)
):
    token = x_admin_key or (authorization.replace("Bearer ", "").strip() if authorization else None)
    if not token or token != ADMIN_SECRET_KEY:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized: Valid administrative key required to trigger feed refresh."
        )
    return True

# ============================================================
# AI-POWERED FARMER FEED ENDPOINTS
# ============================================================

@app.get("/api/feed")
def get_farmer_feed(
    category: Optional[str] = Query(None),
    crop: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=50)
):
    """Retrieves swipeable agricultural cards in Malayalam with category and crop filters."""
    cards = feed_store.get_cards(category=category, crop=crop, limit=limit)
    return {
        "status": "success",
        "count": len(cards),
        "cards": cards
    }


@app.post("/api/feed/query")
def query_feed(payload: FeedQueryRequest):
    """RAG-powered semantic search across agricultural documents in English and Malayalam."""
    if not payload.query or len(payload.query.strip()) < 2:
        raise HTTPException(status_code=400, detail="Query string is too short.")
    return feed_store.query_rag_feed(query=payload.query, top_k=payload.top_k)


@app.post("/api/feed/refresh")
def refresh_feed(authorized: bool = Depends(verify_admin_authorization)):
    """Re-indexes agricultural documents (.pdf, .txt, .md) and refreshes feed cards (Admin protected)."""
    total = feed_store.refresh()
    return {
        "status": "success",
        "message": "Successfully re-indexed agricultural documents and refreshed feed cards.",
        "total_cards": total
    }
