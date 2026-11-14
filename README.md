# 🌾 Smart Irrigation System with Real-Time ML & AI Agricultural Advisory Hub

An end-to-end agricultural IoT, Machine Learning, and AI Advisory solution designed to optimize farm water usage and empower farmers with verified agronomic guidance and Malayalam knowledge feeds.

The system ingests real-time telemetry from an ESP32 microcontroller, predicts irrigation needs using a trained **Random Forest** model, evaluates immediate local rainfall forecasts (via Open-Meteo), manages safety overrides (e.g. low water reservoir alerts), and serves interactive diagnostics, a **Location-Based AI Agricultural Advisor**, and an **AI-Powered Malayalam Farmer Feed** on the web dashboard.

---

## 🏗 System Architecture

```text
+-----------------------+      HTTP POST      +-------------------------------+
|  ESP32 Microcontroller | -----------------> |    FastAPI Cloud Backend      |
|  - Soil Moisture      |  /api/telemetry     |  - Features Parsing           |
|  - DHT22 (Temp/Hum)   |                     |  - Trained Model Prediction   |
|  - Light (LDR)        | <-----------------  |  - Safety Override Rules      |
|  - Water Tank Sensor  |     JSON Response   |  - Rain Forecast Check        |
+-----------------------+     (Pump ON/OFF)   +---------------+---------------+
                                                              |
                                                       Polls Dashboard / API
                                                              v
+-----------------------------------------------------------------------------+
|                          Web Dashboard & Advisory Hub                       |
|  1. 💧 Field Control & Sensors       2. 🌾 AI Agricultural Advisor          |
|     - Live Sensor Telemetry             - Crop & Growth Stage Schedules     |
|     - ML Inference Diagnostics          - Rain Leaching Safety Alerts       |
|     - Weather Forecast Strip            - Organic Manure Recipe Generator   |
|     - Safety Reservoir Warnings         - Agronomic AI Insights             |
|                                                                             |
|  3. 📰 AI Farmer Feed (കർഷക ഫീഡ്)                                           |
|     - RAG Document Retrieval (KAU / ICAR Official Publications)             |
|     - Natural Malayalam Agricultural Knowledge Cards                        |
|     - Practical Remedies & Disease / Pest Prevention                        |
|     - Listen-Aloud Audio (Web Speech TTS in Malayalam)                      |
+-----------------------------------------------------------------------------+
```

---

## 🌟 New Features Overview

### 1. 🌾 AI Agricultural Advisor
- **Location-Based Fertilizer Recommendation Engine**: Recommends fertilizer schedules tailored to the selected crop and growth stage, calibrated with **Kerala Agricultural University (KAU) Package of Practices** and **ICAR** guidelines.
- **Weather-Conditioned Safety Guardrails**: Proactively alerts the farmer if imminent heavy rain or high precipitation probability threatens fertilizer runoff, preventing financial loss and groundwater leaching.
- **Organic Manure Recipe Generator**: Allows farmers to select available farm inputs (decomposed cow dung, vermicompost, neem cake, farmyard manure, bone meal, wood ash, poultry manure) to generate scientific organic fertilizer recipes with step-by-step preparation, application timing, biological safety cautions (e.g., composting poultry manure to prevent ammonia burning), and transparent non-guaranteed NPK disclaimers.
- **AI Agronomic Explainer**: Connects to Gemini API (or structured KAU expert rule-based fallback) to generate clear bilingual farmer summaries in English and simple Malayalam.

### 2. 📰 AI-Powered Farmer Feed (മലയാളം കർഷക ഫീഡ്)
- **Authoritative RAG Pipeline**: Ingests, processes, chunks, indexes, and retrieves official publications from Kerala Agricultural University (KAU) and ICAR institutes (CPCRI, IISR, NRCB).
- **Practical Malayalam Knowledge Cards**: Each card contains a clear Malayalam title, simple explanation, practical actionable tip, crop/category badge, and verified institutional citation.
- **Natural Malayalam Text-to-Speech (TTS) Listen-Aloud**: Integrated Web Speech API audio player with Play/Stop toggles, speaking indicators, and language-targeted synthesis (`ml-IN`), accessible to farmers regardless of literacy levels.
- **Semantic RAG Search & Category Filters**: Search by symptom or topic (e.g., "ഇലകളിൽ ദ്വാരങ്ങൾ", "കുരുമുളക് വാട്ടരോഗം", "തണ്ടുതുരപ്പൻ പുഴു", "വെള്ളീച്ച") with citations.

---

## 📁 Repository Structure

```text
ml_iot_based_irrigation/
├── backend/
│   ├── main.py                     # FastAPI application with IoT, Advisor & Feed endpoints
│   ├── requirements.txt            # Python dependencies
│   ├── advisor/                    # AI Agricultural Advisor module
│   │   ├── crops_data.py           # Verified KAU/ICAR crop nutrient & stage database
│   │   ├── fertilizer_engine.py    # Location & weather-conditioned fertilizer engine
│   │   ├── organic_engine.py       # Organic manure recipe generator & input profiles
│   │   └── ai_explainer.py         # AI explanation module with Gemini & KAU fallback
│   ├── feed/                       # AI Farmer Feed & RAG module
│   │   ├── rag_engine.py           # Document chunking, TF-IDF vector indexing & retrieval
│   │   ├── generator.py            # Malayalam card generator with verified grounding
│   │   └── store.py                # Card caching, category filtering & persistence
│   ├── knowledge/
│   │   └── documents/              # Official KAU & ICAR agricultural reference documents
│   ├── data/
│   │   └── feed_cards.json         # Cached knowledge feed cards
│   └── tests/                      # Automated test suite
│       ├── test_advisor.py         # Unit tests for Advisor & organic recipes
│       ├── test_feed_rag.py        # Unit tests for RAG pipeline & Malayalam feed
│       └── test_regression.py      # End-to-end regression tests
├── frontend/
│   ├── index.html                  # Tabbed UI (Field Control, Advisor, Farmer Feed)
│   ├── style.css                   # Responsive agricultural styling & Malayalam typography
│   └── script.js                   # Telemetry polling, Advisor logic & Malayalam TTS
├── ml/
│   ├── saved_model.pkl             # Trained Random Forest model
│   ├── train.py                    # ML model training pipeline
│   └── eda_clean.py                # Dataset cleaning & exploration
├── dataset/                        # Agricultural sensor datasets
└── firmware/                       # ESP32 PlatformIO firmware
```

---

## 🚀 API Endpoints

### Core Smart Irrigation (Preserved)
- `GET /` — Health check
- `GET /api/dashboard` — Live telemetry, pump state, ML prediction, safety flags
- `GET /api/weather` — Open-Meteo hourly precipitation forecast for farm coordinates
- `POST /api/telemetry` — ESP32 telemetry ingestion and ML pump actuation decision

### AI Agricultural Advisor (New)
- `GET /api/advisor/crops` — List supported crops and their growth stages
- `POST /api/advisor/fertilizer` — Compute weather-conditioned fertilizer recommendations
- `POST /api/advisor/organic-recipe` — Generate scientific organic manure recipes
- `GET /api/advisor/organic-inputs` — List available organic inputs and handling cautions
- `POST /api/advisor/explain` — Generate bilingual AI agronomic explanations

### AI-Powered Farmer Feed (New)
- `GET /api/feed` — Retrieve Malayalam cards with optional `category`, `crop`, and `limit`
- `POST /api/feed/query` — RAG semantic search across official agricultural publications
- `POST /api/feed/refresh` — Re-index documents and refresh cached cards

---

## ⚙️ Configuration & Environment Variables

Create a `.env` file in the project root or configure your shell environment:

```env
# Optional: External LLM API key for dynamic generation (Gemini)
# If omitted, system seamlessly runs on the verified KAU Package of Practices engine.
GEMINI_API_KEY=your_gemini_api_key_here

# Farm Coordinates (Default: Central Kerala Agro-Climatic Zone)
FARM_LATITUDE=9.50996
FARM_LONGITUDE=76.55067
```

> **Note:** The application is designed to be completely functional even without external LLM API keys. When no key is provided, all fertilizer recommendations, organic recipes, and Malayalam feed cards are served from the verified KAU/ICAR knowledge base.

---

## 🏃 Local Setup & Execution

### 1. Prerequisites
- Python 3.10+
- Modern Web Browser (Chrome, Edge, Firefox, Safari)

### 2. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 3. Start the FastAPI Backend
```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```
API Documentation will be accessible at: `http://127.0.0.1:8000/docs`

### 4. Launch the Web Frontend
Open `frontend/index.html` directly in your browser or serve using Python's HTTP server:
```bash
cd frontend
python -m http.server 3000
```
Access the application at `http://127.0.0.1:3000`.

---

## 🧪 Running Automated Tests

Run the full automated test suite covering unit tests and regression testing:

```bash
python -m unittest discover -s backend/tests -v
```

All 18 tests will verify:
- Sensor telemetry processing and ML model predictions
- Crop selection and stage-specific fertilizer recommendations
- Weather-conditioned rain hazard warnings
- Organic manure formulation and bio-safety cautions
- RAG document indexing and semantic retrieval
- Malayalam text presence and audio script structure
- Backward compatibility of all existing smart irrigation endpoints

---

## 📖 How to Add New Agricultural Documents

1. Place the new official reference document (`.txt` or `.md`) in `backend/knowledge/documents/`.
2. Format the header with metadata tags:
   ```text
   TITLE: Document Title
   INSTITUTION: Publishing Organization (e.g., KAU / ICAR)
   CROP: Target Crop
   TOPIC: Agronomic Topic / Section
   
   1. Symptom / Practice Name
   Symptoms: ...
   Management & Remedy: ...
   Citation: ...
   ```
3. Trigger re-indexing by calling `POST /api/feed/refresh` or restarting the backend server. The RAG engine will automatically chunk, index, and surface the new guidance in the Farmer Feed.

---

## 🛡 Agricultural Safety & Limitations

- **Software-Only Guidance**: The AI Agricultural Advisor provides advisory guidance and does not tamper with or override automated irrigation hardware safety relays.
- **No Hallucinated Dosages**: The system uses verified dosages from the Kerala Agricultural University Package of Practices. If soil testing is unavailable, it explicitly marks dosages as regional guidelines rather than soil-specific prescriptions.
- **Organic Bio-Safety**: Organic recipes strictly caution against uncomposted poultry manure and emphasize thermophilic curing to prevent pathogen risks and weed seed germination.
