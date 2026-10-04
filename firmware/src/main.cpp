#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <DHT.h>

// Sensor Pin Definitions
#define SOIL_PIN 34    // ADC pin for Soil Moisture Sensor
#define DHT_PIN 4      // Digital pin for DHT22 / DHT11
#define LDR_PIN 32     // ADC pin for LDR Light Sensor
#define RELAY_PIN 26   // Output pin for Relay (Pump Control)
#define DHT_TYPE DHT11 // Change to DHT22 if using a DHT22 sensor

// Wi-Fi Credentials
const char* ssid = "Stenyyay";
const char* password = "stenythisthat";

// FastAPI Server Telemetry Endpoint (Your PC's Wi-Fi IP address)
const char* serverUrl = "http://172.20.10.5:8000/api/telemetry";

// Soil Moisture ADC Calibration (Dry vs Wet raw values)
const int SOIL_DRY_ADC = 3500;
const int SOIL_WET_ADC = 1200;

DHT dht(DHT_PIN, DHT_TYPE);

unsigned long lastIrrigationTime = 0;
float previousMoisture = 50.0;
unsigned long previousMillis = 0;
const unsigned long TELEMETRY_INTERVAL_MS = 5000; // Send telemetry every 5 seconds

void setup() {
  Serial.begin(115200);
  
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW); // Keep pump OFF initially

  dht.begin();

  // Connect to Wi-Fi
  Serial.print("Connecting to Wi-Fi: ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWi-Fi Connected successfully!");
  Serial.print("ESP32 IP Address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  unsigned long currentMillis = millis();

  // Send telemetry every 5 seconds
  if (currentMillis - previousMillis >= TELEMETRY_INTERVAL_MS) {
    previousMillis = currentMillis;

    // 1. Read Raw Physical Sensors
    int rawSoil = analogRead(SOIL_PIN);
    float temp = dht.readTemperature();
    float hum = dht.readHumidity();
    int ldrValue = analogRead(LDR_PIN); // Read LDR as analog value (0 - 4095)

    // 2. Map Soil Raw ADC to Percentage (0% - 100%)
    float soilMoisture = ((float)(rawSoil - SOIL_DRY_ADC) / (float)(SOIL_WET_ADC - SOIL_DRY_ADC)) * 100.0f;
    soilMoisture = constrain(soilMoisture, 0.0f, 100.0f);

    // 3. Calculate Derived Features required by ML model
    // Time since last irrigation in MINUTES
    int timeSinceIrrigation = (lastIrrigationTime == 0) 
                              ? (currentMillis / 60000) 
                              : ((currentMillis - lastIrrigationTime) / 60000);
                              
    float moistureDropRate = previousMoisture - soilMoisture;
    previousMoisture = soilMoisture;

    // DHT sensor fallback if sensor reading fails temporarily
    if (isnan(temp)) temp = 25.0;
    if (isnan(hum)) hum = 50.0;

    // 4. Construct JSON Payload
    JsonDocument doc;
    doc["soil_moisture"] = soilMoisture;
    doc["temperature"] = temp;
    doc["humidity"] = hum;
    doc["light"] = ldrValue;
    doc["time_since_irrigation"] = timeSinceIrrigation;
    doc["moisture_drop_rate"] = moistureDropRate;
    doc["water_tank_level"] = 100.0; // Simulated tank level (100% full)

    String jsonPayload;
    serializeJson(doc, jsonPayload);

    // 5. Send HTTP POST to FastAPI Backend
    if (WiFi.status() == WL_CONNECTED) {
      HTTPClient http;
      http.begin(serverUrl);
      http.addHeader("Content-Type", "application/json");

      int httpResponseCode = http.POST(jsonPayload);

      if (httpResponseCode == 200) {
        String response = http.getString();
        JsonDocument respDoc;
        deserializeJson(respDoc, response);

        const char* pumpCommand = respDoc["pump_command"];
        bool safetyOverride = respDoc["safety_override"];
        const char* reason = respDoc["reason"];

        Serial.printf("[HTTP 200] Sent -> Soil: %.1f%% | Temp: %.1fC | Hum: %.1f%% | Light: %d\n",
                      soilMoisture, temp, hum, ldrValue);
        Serial.printf("           Action -> Pump: %s | Safety Override: %s | Reason: %s\n",
                      pumpCommand, safetyOverride ? "YES" : "NO", reason);

        // Actuate Relay Pin based on backend decision
        if (String(pumpCommand) == "ON") {
          digitalWrite(RELAY_PIN, HIGH);
          lastIrrigationTime = currentMillis;
        } else {
          digitalWrite(RELAY_PIN, LOW);
        }
      } else {
        Serial.printf("[ERROR] HTTP POST failed! Error code: %d\n", httpResponseCode);
      }
      http.end();
    } else {
      Serial.println("[WARNING] Wi-Fi Disconnected! Reconnecting...");
      WiFi.reconnect();
    }
  }
}