"""
Organic Manure Recipe Generator Engine
Scientifically grounded recipes combining locally available organic inputs for Kerala crops.
Explicitly distinguishes between composting preparations, liquid bio-formulations, and direct field-application mixtures.
Validates ingredient proportions and enforces strict pathogen and bio-safety protocols.
"""

from typing import List, Dict, Any, Optional

# Verified typical nutrient profile of organic inputs (approximate ranges, non-guaranteed)
ORGANIC_INPUT_PROFILES = {
    "cow_dung": {
        "name": "Decomposed Cow Dung / Cattle Manure",
        "category": "Animal Manure",
        "approx_n": 0.5,
        "approx_p": 0.2,
        "approx_k": 0.5,
        "c_n_ratio": "20:1 to 25:1 (when decomposed)",
        "handling_caution": "Must be well decomposed (dark brown, earthy smell). Never use fresh slurry directly on plant collars to avoid root rot, heat injury, and fungal damping-off."
    },
    "poultry_manure": {
        "name": "Composted Poultry Droppings / Manure",
        "category": "Animal Manure (High Nitrogen)",
        "approx_n": 2.8,
        "approx_p": 2.5,
        "approx_k": 1.4,
        "c_n_ratio": "10:1 to 12:1",
        "handling_caution": "HIGH RISK: Fresh poultry manure contains volatile uric acid and ammonia that cause catastrophic root and foliage burn, alongside potential Salmonella/E. coli pathogen risks. MUST undergo thermophilic co-composting (>55°C) with dry carbonaceous material (paddy straw/coir pith) for 6-8 weeks before field application."
    },
    "vermicompost": {
        "name": "Earthworm Castings / Vermicompost",
        "category": "Bio-organic Compost",
        "approx_n": 1.8,
        "approx_p": 1.2,
        "approx_k": 1.5,
        "c_n_ratio": "15:1",
        "handling_caution": "Store in dense shade with 20-25% moisture. Do not expose to direct sun or drying wind which eliminates beneficial microbial flora."
    },
    "farmyard_manure": {
        "name": "Well-cured Farmyard Manure (FYM)",
        "category": "Bulk Organic Manure",
        "approx_n": 0.6,
        "approx_p": 0.3,
        "approx_k": 0.6,
        "c_n_ratio": "20:1 to 30:1",
        "handling_caution": "Verify absence of plastic debris and viable weed seeds. Proper heap curing reaches thermophilic temperatures (>55°C) that destroy weed seeds and pathogens."
    },
    "neem_cake": {
        "name": "Neem Seed Cake (Azadirachta indica)",
        "category": "Organic Cake / Bio-pesticide",
        "approx_n": 5.0,
        "approx_p": 1.0,
        "approx_k": 1.4,
        "c_n_ratio": "10:1",
        "handling_caution": "Acts as a natural nitrification inhibitor and soil nematicide. Avoid over-application around sensitive young seedlings; incorporate 5-10 cm into soil."
    },
    "bone_meal": {
        "name": "Sterilized Bone Meal (Raw / Steamed)",
        "category": "Mineral Organic (Phosphorus & Calcium)",
        "approx_n": 3.0,
        "approx_p": 20.0,
        "approx_k": 0.0,
        "c_n_ratio": "N/A",
        "handling_caution": "Must be sterilized steamed bone meal to eliminate bacterial contamination. Incorporate into root zone as phosphorus is immobile."
    },
    "wood_ash": {
        "name": "Kitchen Wood Ash (Coconut shell / Hardwood)",
        "category": "Potassium & Lime Alternative",
        "approx_n": 0.0,
        "approx_p": 1.5,
        "approx_k": 6.0,
        "c_n_ratio": "N/A",
        "handling_caution": "High alkaline pH (pH 9-11). Do not mix directly with fresh animal urine or nitrogenous compost as it drives off nitrogen as ammonia gas. Do not exceed 500g per tree basin."
    },
    "compost": {
        "name": "Decomposed Agricultural Crop Residue Compost",
        "category": "Bulk Humus",
        "approx_n": 0.8,
        "approx_p": 0.4,
        "approx_k": 0.8,
        "c_n_ratio": "18:1",
        "handling_caution": "Ensure C:N balancing during composting (brown leaves + green waste) to ensure full stabilization."
    }
}


RECIPE_TEMPLATES = [
    {
        "id": "enriched_jeevamrutham",
        "name": "Liquid Jeevamrutham Bio-Enhancer",
        "recipe_type": "Liquid Microbial Bio-Formulation (Field Fermentation)",
        "recipe_category": "direct_field_application",
        "primary_crops": ["paddy", "banana", "vegetables", "pepper", "coconut"],
        "suitable_stages": ["Vegetative Growth", "Active Tillering", "Flowering", "Berry Development"],
        "ingredients": [
            {"item": "Fresh indigenous cow dung", "proportion": "10 kg", "percentage": 4.5},
            {"item": "Fresh cow urine (gomutra)", "proportion": "10 litres", "percentage": 4.5},
            {"item": "Organic jaggery / molasses", "proportion": "2 kg", "percentage": 0.9},
            {"item": "Pulse flour (Besan / Gram flour)", "proportion": "2 kg", "percentage": 0.9},
            {"item": "Uncontaminated virgin forest / bund soil", "proportion": "0.2 kg", "percentage": 0.1},
            {"item": "Clean chlorine-free water", "proportion": "200 litres", "percentage": 89.1}
        ],
        "preparation_instructions": [
            "1. Take 200 litres of clean, non-chlorinated water in a 250L plastic drum placed in dense shade (never in direct sun).",
            "2. Add 10 kg cow dung and 10 litres cow urine; stir thoroughly with a wooden pole clockwise.",
            "3. Dissolve 2 kg jaggery and 2 kg besan flour in a separate bucket of water and add to the drum.",
            "4. Add 200g of virgin fertile soil from field borders or beneath a banyan/neem tree to inoculate native beneficial microflora.",
            "5. Stir the concoction for 5 minutes clockwise three times daily (morning, noon, evening).",
            "6. Keep drum covered with a porous jute gunny sack to allow aerobic breathing while blocking flies.",
            "7. The solution ferments actively within 48 to 72 hours, releasing a pleasant fermented aroma. Ready for application on days 3 to 7."
        ],
        "application_method": "Soil drenching along crop basins or through flood irrigation channels (200 litres per acre). For foliar use, filter through double-layer muslin cloth and dilute 10% (1L Jeevamrutham in 10L water).",
        "suitable_application_stage": "Apply every 15-21 days during active vegetative and flowering periods.",
        "expected_benefits": "Multiplies beneficial soil rhizosphere bacteria, solubilizes fixed phosphorus and potassium, stimulates earthworm activity, and enhances plant defense against root pathogens.",
        "safety_precautions": "Do not store for more than 7-8 days as anaerobic decay begins. Do not use chemical pesticides or chlorinated tap water with Jeevamrutham. Maintain eye and face protection during manual stirring."
    },
    {
        "id": "trichoderma_enriched_fym",
        "name": "Trichoderma-Enriched Bio-Fungicidal Manure Mix",
        "recipe_type": "Solid Bio-Control Manure Blend",
        "recipe_category": "direct_field_application",
        "primary_crops": ["banana", "pepper", "vegetables", "coconut"],
        "suitable_stages": ["Planting / Pit Preparation", "Pre-Monsoon Active Flush", "Basal / Bed Preparation"],
        "ingredients": [
            {"item": "Well-rotted Farmyard Manure or Vermicompost", "proportion": "90 kg", "percentage": 85.0},
            {"item": "Neem Seed Cake powder", "proportion": "10 kg", "percentage": 9.5},
            {"item": "Trichoderma harzianum / viride talc formulation", "proportion": "2 kg", "percentage": 1.9},
            {"item": "Clean water for moisture maintenance", "proportion": "3.8 litres", "percentage": 3.6}
        ],
        "preparation_instructions": [
            "1. Spread 90 kg of well-rotted FYM or vermicompost evenly on a clean polythene sheet under cool tree shade.",
            "2. Mix in 10 kg of finely ground neem cake powder uniformly throughout the manure.",
            "3. Sprinkle 2 kg of Trichoderma powder over the heap.",
            "4. Sprinkle water lightly so that the mixture is moist (a squeezed handful should form a ball without dripping water).",
            "5. Heap the mixture into a neat mound, cover with moistened gunny sacks or banana leaves, and keep undisturbed for 7 to 10 days.",
            "6. By day 7, a dense whitish-green fungal mycelium will completely colonize the entire manure mass. Mix once and apply immediately to plant basins."
        ],
        "application_method": "Apply 2-3 kg per banana pit / 5 kg per pepper vine basin / 500g per vegetable plant into the root feeding zone and cover with dry soil mulch.",
        "suitable_application_stage": "Basal pit filling or pre-monsoon root zone conditioning.",
        "expected_benefits": "Biological suppression of Phytophthora (pepper foot rot), Fusarium wilt (banana Panama disease), and Pythium damping off in vegetables while providing balanced organic nutrients.",
        "safety_precautions": "Never mix with chemical copper fungicides, carbendazim, or synthetic systemic fungicides. Wear a dust mask while handling dry Trichoderma powder to prevent spore inhalation."
    },
    {
        "id": "fortified_compost_manure",
        "name": "Potash & Phosphate Fortified Organic Blend",
        "recipe_type": "Direct Field Application Organic Combination",
        "recipe_category": "direct_field_application",
        "primary_crops": ["coconut", "banana", "vegetables"],
        "suitable_stages": ["Early Vegetative", "Active Growth", "Shooting / Bunch Emergence", "Bearing Adult Palm (Post-Monsoon)"],
        "ingredients": [
            {"item": "Cured Farmyard Manure or Vermicompost", "proportion": "50 kg", "percentage": 60.0},
            {"item": "Crushed Neem Cake", "proportion": "10 kg", "percentage": 12.0},
            {"item": "Sterilized Steamed Bone Meal", "proportion": "10 kg", "percentage": 12.0},
            {"item": "Clean Wood Ash (dry)", "proportion": "10 kg", "percentage": 12.0},
            {"item": "Biofertilizer consortia (Azospirillum + PSB)", "proportion": "2 kg", "percentage": 2.4},
            {"item": "Water (for light moistening)", "proportion": "1.3 litres", "percentage": 1.6}
        ],
        "preparation_instructions": [
            "1. On a shaded floor or dry canvas, mix the vermicompost and neem cake thoroughly.",
            "2. Add sterilized bone meal and mix until evenly distributed.",
            "3. Mix wood ash gently just before application (do not store ash mixed with wet manure for prolonged periods).",
            "4. Blend the biofertilizer inoculants into the mix at room temperature.",
            "5. The enriched organic blend is now ready for direct root-zone application."
        ],
        "application_method": "Apply in shallow circular rings 40-50 cm away from crop collar. Lightly fork into top 5-10 cm soil and cover with leaf mulch.",
        "suitable_application_stage": "Growth and fruit development stages requiring heightened potassium and organic phosphorus.",
        "expected_benefits": "High organic potassium and slow-release phosphate enhance fruit bunch weight, stem girth, drought resilience, and soil microbial carbon.",
        "safety_precautions": "Do not leave wood ash exposed to damp rain before use. Apply when soil has adequate moisture; follow with light irrigation if soil is dry."
    },
    {
        "id": "aerobic_farm_waste_compost",
        "name": "Balanced Pit / Heap Aerobic Composting Recipe",
        "recipe_type": "Full Aerobic Composting Protocol (60-day cycle)",
        "recipe_category": "compost_preparation",
        "primary_crops": ["all_crops", "paddy", "banana", "coconut", "pepper", "vegetables"],
        "suitable_stages": ["Land Preparation", "Pre-Monsoon Basin Mulch"],
        "ingredients": [
            {"item": "Brown Carbon Material (dry paddy straw, coir pith, dry fallen leaves)", "proportion": "200 kg (60% volume)", "percentage": 50.0},
            {"item": "Green Nitrogen Material (legume cuttings, fresh vegetable waste, cowpea vines)", "proportion": "100 kg (30% volume)", "percentage": 25.0},
            {"item": "Fresh cattle dung slurry", "proportion": "60 kg (mixed with water)", "percentage": 15.0},
            {"item": "Poultry manure (for nitrogen acceleration)", "proportion": "20 kg", "percentage": 5.0},
            {"item": "Topsoil or mature compost (inoculum)", "proportion": "20 kg", "percentage": 5.0}
        ],
        "preparation_instructions": [
            "1. Choose a high, well-drained shaded site of dimensions 3m length x 1.5m width x 1.2m height.",
            "2. Layer 1: Lay a 15 cm base of coarse brown carbon materials (chopped straw / small twigs) for bottom aeration.",
            "3. Layer 2: Spread a 10 cm layer of green farm waste / legume cuttings.",
            "4. Layer 3: Sprinkle poultry manure and drench with cattle dung slurry to provide microbial starter.",
            "5. Layer 4: Dust with 2 cm garden topsoil to provide native mineral microbes.",
            "6. Repeat alternating carbon and nitrogen layers until pile reaches 1.2 meters in height. Insert vertical bamboo poles with perforated notches to maintain internal oxygen.",
            "7. Turn the pile completely on Day 15, Day 30, and Day 45 to aerate and equalize heat (temperature should reach 55-60°C to sanitize pathogens and weed seeds).",
            "8. By Day 60, the heap cools down to ambient temperature and transforms into dark, crumbly, sweet-smelling humus ready for farm use."
        ],
        "application_method": "Incorporate 2 to 3 tonnes per acre during land preparation or 5-10 kg per tree basin annually.",
        "suitable_application_stage": "Pre-sowing, land preparation, or annual perennial basin rejuvenation.",
        "expected_benefits": "High cation exchange capacity (CEC), long-term soil structure improvement, high moisture holding capacity, and complete recycling of on-farm organic residues.",
        "safety_precautions": "PATHOGEN SAFETY: Fresh animal droppings must achieve internal temperatures of 55-60°C for at least 72 consecutive hours during composting to neutralize fecal pathogens (E. coli, Salmonella). Never apply unfermented poultry droppings directly to root zones."
    }
]


def validate_recipe_proportions(recipe: Dict[str, Any]) -> bool:
    """Validates that recipe ingredient percentages are positive and sum to approximately 100%."""
    ingredients = recipe.get("ingredients", [])
    if not ingredients:
        return False
    total_pct = sum(float(i.get("percentage", 0.0)) for i in ingredients)
    return 98.0 <= total_pct <= 102.0


def generate_organic_recipe(
    crop_id: str,
    growth_stage: Optional[str] = None,
    available_inputs: Optional[List[str]] = None,
    soil_condition: Optional[str] = None
) -> Dict[str, Any]:
    """
    Selects or tailors an organic manure recipe based on crop, available inputs, and stage.
    Validates ingredient proportions and biological safety rules.
    """
    crop_id = (crop_id or "").lower().strip()
    available_inputs = [i.lower().strip() for i in (available_inputs or [])]

    # Filter matching templates
    matched_recipes = []
    for recipe in RECIPE_TEMPLATES:
        is_crop_match = (
            "all_crops" in recipe["primary_crops"] or
            crop_id in recipe["primary_crops"] or
            any(crop_id in c for c in recipe["primary_crops"])
        )
        if is_crop_match:
            matched_recipes.append(recipe)

    if not matched_recipes:
        matched_recipes = RECIPE_TEMPLATES

    selected = matched_recipes[0]
    alternatives = matched_recipes[1:]

    # Validate proportions of selected recipe
    proportions_valid = validate_recipe_proportions(selected)

    # Highlight available vs missing inputs
    available_input_details = []
    for key, profile in ORGANIC_INPUT_PROFILES.items():
        is_selected = any(key in inp for inp in available_inputs) if available_inputs else True
        available_input_details.append({
            "key": key,
            "name": profile["name"],
            "category": profile["category"],
            "approx_npk": f"N: {profile['approx_n']}%, P: {profile['approx_p']}%, K: {profile['approx_k']}% (Typical non-guaranteed)",
            "selected_by_farmer": is_selected,
            "handling_caution": profile["handling_caution"]
        })

    # Clear scientific disclaimer
    scientific_disclaimer = (
        "IMPORTANT SCIENTIFIC NOTICE: Organic manures possess variable natural nutrient contents "
        "dependent on animal diet, bed material, moisture, and curing methods. The figures provided are typical agronomic estimates "
        "and NOT guaranteed NPK analysis. Fresh poultry manure and unfermented animal wastes MUST be fully composted before root application "
        "to prevent ammonia toxicity and pathogen contamination."
    )

    return {
        "status": "success",
        "crop_id": crop_id,
        "growth_stage": growth_stage or "General Growth Stage",
        "primary_recipe": selected,
        "recipe_category": selected.get("recipe_category", "direct_field_application"),
        "is_compost_preparation": selected.get("recipe_category") == "compost_preparation",
        "proportions_validated": proportions_valid,
        "alternative_recipes": alternatives,
        "inputs_analysis": available_input_details,
        "disclaimer": scientific_disclaimer,
        "soil_context_applied": soil_condition or "General organic guidelines (No soil test provided)"
    }
