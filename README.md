# 🌾 Smart Irrigation System with Real-Time ML & Decision Engine

An end-to-end IoT and Machine Learning solution designed to optimize agricultural water usage. The system ingests telemetry from an ESP32 microcontroller, evaluates environmental conditions using a trained **Random Forest** model, applies safety override rules (e.g., dry reservoir detection), and actuates irrigation relays automatically while serving live diagnostics to a web dashboard.

---

## 🏗 System Architecture

```text
+-----------------------+      HTTP POST      +-------------------------------+
|  ESP32 Microcontroller | -----------------> |    FastAPI Cloud Backend      |
|  - Soil Moisture      |  /api/telemetry     |  - Features Parsing           |
|  - DHT22 (Temp/Hum)   |                     |  - Trained Model Prediction   |
|  - Light (LDR)        | <-----------------  |  - Safety Override Rules      |
|  - Water Tank Sensor  |     JSON Response   +---------------+---------------+
+-----------------------+     (Pump ON/OFF)                   |
                                                              |
                                                       Polls Dashboard
                                                       /api/dashboard
                                                              v
                                              +-------------------------------+
                                              |      Web Dashboard (HTML/JS)  |
                                              |  - Real-time Sensor Metrics   |
                                              |  - ML Inference & Diagnostics |
                                              |  - Safety Alerts              |
                                              +-------------------------------+
