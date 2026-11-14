"""
Unit tests for AI Agricultural Advisor
"""
import sys
import os
import unittest

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from advisor.fertilizer_engine import get_available_crops, recommend_fertilizer
from advisor.organic_engine import generate_organic_recipe, ORGANIC_INPUT_PROFILES
from advisor.ai_explainer import generate_advisor_explanation


class TestAgriculturalAdvisor(unittest.TestCase):

    def test_get_available_crops(self):
        crops = get_available_crops()
        self.assertGreaterEqual(len(crops), 4)
        crop_ids = [c["id"] for c in crops]
        self.assertIn("paddy", crop_ids)
        self.assertIn("banana", crop_ids)
        self.assertIn("coconut", crop_ids)

    def test_fertilizer_recommendation_paddy(self):
        rec = recommend_fertilizer(
            crop_id="paddy",
            growth_stage="Active Tillering (15-20 DAT)",
            latitude=9.50996,
            longitude=76.55067
        )
        self.assertEqual(rec["status"], "success")
        self.assertEqual(rec["crop"]["id"], "paddy")
        self.assertGreater(len(rec["recommendations"]), 0)
        # Verify NPK composition and verified reference presence
        first_rec = rec["recommendations"][0]
        self.assertIn("fertilizer_name", first_rec)
        self.assertIn("recommended_quantity", first_rec)
        self.assertIn("reference", first_rec)
        self.assertTrue(first_rec["is_verified_agronomic"])

    def test_fertilizer_weather_safety_warning(self):
        # When rain probability is high (>= 50%), check that rain warning is emitted
        weather_rain = {"rain_probability": 75, "rain_amount": 12.0}
        rec = recommend_fertilizer(
            crop_id="banana",
            growth_stage="Early Vegetative (2nd Month)",
            weather_info=weather_rain
        )
        alerts = rec["weather_context"]["application_safety_alerts"]
        self.assertGreater(len(alerts), 0)
        self.assertTrue(any("RAIN HAZARD" in a for a in alerts))

    def test_no_soil_data_guideline_notice(self):
        rec = recommend_fertilizer(crop_id="coconut")
        self.assertFalse(rec["soil_context"]["has_soil_test"])
        self.assertIn("GENERAL GUIDELINE NOTICE", rec["soil_context"]["guideline_notice"])

    def test_organic_recipe_generation(self):
        recipe_data = generate_organic_recipe(
            crop_id="banana",
            growth_stage="Planting / Pit Preparation",
            available_inputs=["cow_dung", "vermicompost", "neem_cake"]
        )
        self.assertEqual(recipe_data["status"], "success")
        primary = recipe_data["primary_recipe"]
        self.assertIn("name", primary)
        self.assertIn("ingredients", primary)
        self.assertIn("preparation_instructions", primary)
        self.assertIn("safety_precautions", primary)
        self.assertIn("disclaimer", recipe_data)

    def test_ai_explainer_fallback(self):
        explanation = generate_advisor_explanation(
            crop_name="Paddy / Rice",
            stage="Active Tillering",
            weather_summary="Sunny with 10% rain",
            recommendations_summary=[{"name": "Urea", "qty": "20 kg/acre"}]
        )
        self.assertIn("summary_en", explanation)
        self.assertIn("summary_ml", explanation)
        self.assertIn("farmer_action_tips", explanation)
        self.assertIn("safety_alert", explanation)


if __name__ == "__main__":
    unittest.main()
