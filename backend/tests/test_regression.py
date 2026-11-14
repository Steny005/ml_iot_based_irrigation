"""
Regression tests ensuring existing smart irrigation routes and new features function together.
"""
import sys
import os
import unittest
from fastapi.testclient import TestClient

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from main import app, ADMIN_SECRET_KEY


class TestRegressionAndEndpoints(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_root_endpoint(self):
        # Existing endpoint contract
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "online")
        self.assertIn("message", res.json())

    def test_dashboard_endpoint(self):
        # Existing endpoint contract
        res = self.client.get("/api/dashboard")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("soil_moisture", data)
        self.assertIn("temperature", data)
        self.assertIn("humidity", data)
        self.assertIn("light", data)
        self.assertIn("water_tank_level", data)
        self.assertIn("pump_status", data)
        self.assertIn("ml_recommendation", data)
        self.assertIn("override_reason", data)

    def test_telemetry_pipeline(self):
        # Existing endpoint contract: ESP32 telemetry ingestion
        payload = {
            "soil_moisture": 12.5,
            "temperature": 31.2,
            "humidity": 65.0,
            "light": 1,
            "time_since_irrigation": 1200,
            "moisture_drop_rate": 0.15,
            "water_tank_level": 85.0
        }
        res = self.client.post("/api/telemetry", json=payload)
        self.assertEqual(res.status_code, 200)
        result = res.json()
        # Verify exact response schema
        self.assertIn("pump_command", result)
        self.assertIn("ml_recommendation", result)
        self.assertIn("safety_override", result)
        self.assertIn("weather_override", result)
        self.assertIn("rain_probability", result)
        self.assertIn("rain_amount", result)
        self.assertIn("reason", result)

    def test_new_advisor_crops_endpoint(self):
        res = self.client.get("/api/advisor/crops")
        self.assertEqual(res.status_code, 200)
        crops = res.json()["crops"]
        self.assertGreaterEqual(len(crops), 4)

    def test_new_advisor_fertilizer_endpoint(self):
        req = {
            "crop_id": "paddy",
            "growth_stage": "Active Tillering (15-20 DAT)",
            "latitude": 9.50996,
            "longitude": 76.55067
        }
        res = self.client.post("/api/advisor/fertilizer", json=req)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("recommendations", data)
        self.assertIn("weather_context", data)
        self.assertIn("soil_context", data)

    def test_new_advisor_organic_recipe_endpoint(self):
        req = {
            "crop_id": "banana",
            "growth_stage": "Planting / Pit Preparation",
            "available_inputs": ["cow_dung", "vermicompost", "neem_cake"]
        }
        res = self.client.post("/api/advisor/organic-recipe", json=req)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("primary_recipe", data)
        self.assertIn("disclaimer", data)
        self.assertTrue(data.get("proportions_validated", True))

    def test_new_feed_endpoints(self):
        # GET /api/feed
        res = self.client.get("/api/feed?limit=5")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertGreaterEqual(len(data["cards"]), 1)

        # POST /api/feed/query
        res_q = self.client.post("/api/feed/query", json={"query": "നെല്ല് തണ്ടുതുരപ്പൻ", "top_k": 3})
        self.assertEqual(res_q.status_code, 200)
        data_q = res_q.json()
        self.assertEqual(data_q["status"], "success")

    def test_feed_refresh_admin_security(self):
        # 1. Unauthenticated request must be rejected with 401
        res_unauth = self.client.post("/api/feed/refresh")
        self.assertEqual(res_unauth.status_code, 401)
        self.assertIn("Unauthorized", res_unauth.json()["detail"])

        # 2. Invalid key must be rejected with 401
        res_invalid = self.client.post(
            "/api/feed/refresh",
            headers={"X-Admin-Key": "wrong_key"}
        )
        self.assertEqual(res_invalid.status_code, 401)

        # 3. Authorized request with valid admin key must succeed
        res_auth = self.client.post(
            "/api/feed/refresh",
            headers={"X-Admin-Key": ADMIN_SECRET_KEY}
        )
        self.assertEqual(res_auth.status_code, 200)
        self.assertEqual(res_auth.json()["status"], "success")
        self.assertGreaterEqual(res_auth.json()["total_cards"], 1)


if __name__ == "__main__":
    unittest.main()
