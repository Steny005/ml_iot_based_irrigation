"""
Verified Agricultural Crop Knowledge Base
Derived from Kerala Agricultural University (KAU) Package of Practices Recommendations: Crops (2024 Edition)
and ICAR Crop Specific Guides.
Preserves official institutional citations, exact section references, and verified page numbers.
"""

CROPS_DATABASE = {
    "paddy": {
        "id": "paddy",
        "name": "Paddy / Rice (നെല്ല്)",
        "scientific_name": "Oryza sativa",
        "category": "Cereals",
        "soil_suitability": "Clayey loam, alluvial wetland soils with high moisture retention. pH 5.0 - 6.5",
        "growth_stages": [
            "Basal / Land Preparation",
            "Active Tillering (15-20 DAT)",
            "Panicle Initiation (35-40 DAT)",
            "Flowering & Grain Filling",
            "Maturity & Harvesting"
        ],
        "fertilizer_recommendations": {
            "Basal / Land Preparation": [
                {
                    "fertilizer_name": "Factamfos (20:20:0:13) or SSP + Urea",
                    "fertilizer_type": "Chemical (Compound)",
                    "npk_composition": "20:20:0:13 (N:P:K:S)",
                    "purpose": "Promotes early root development and seedling vigor through readily available phosphorus and sulfur.",
                    "recommended_quantity": "35-40 kg per acre",
                    "application_method": "Soil incorporation / broadcast uniformly during final puddling before transplanting",
                    "application_timing": "At final puddling / transplanting",
                    "precautions": "Incorporate well into soil. Drain excess water before application so fertilizer is not washed away.",
                    "reference": "KAU Package of Practices: Crops 2024 (Rice Chapter, Section 3.4, Page 22)"
                },
                {
                    "fertilizer_name": "Well-rotted Farmyard Manure (FYM) or Compost",
                    "fertilizer_type": "Organic",
                    "npk_composition": "0.5-0.8% N, 0.2-0.4% P, 0.5-0.8% K (Typical non-guaranteed)",
                    "purpose": "Improves soil organic carbon, water retention, and beneficial microbial activity in paddy wetlands.",
                    "recommended_quantity": "2 tonnes per acre",
                    "application_method": "Even broadcast during initial field preparation",
                    "application_timing": "10-15 days prior to transplanting or direct sowing",
                    "precautions": "Ensure manure is completely decomposed to avoid anaerobic toxicity to young roots.",
                    "reference": "KAU Package of Practices: Crops 2024 (Rice Organic Management, Page 24)"
                },
                {
                    "fertilizer_name": "Agricultural Lime or Dolomite",
                    "fertilizer_type": "Soil Amendment",
                    "npk_composition": "CaCO3 / MgCO3 (Neutralizing agent)",
                    "purpose": "Corrects soil acidity typical of Kerala paddy soils (Kuttanad/Palakkad/Kole lands) and provides Calcium/Magnesium.",
                    "recommended_quantity": "100-150 kg per acre (based on soil pH test; omit if pH > 6.5)",
                    "application_method": "Broadcast evenly across dry or drained field during first ploughing",
                    "application_timing": "2 weeks prior to basal fertilizer application",
                    "precautions": "NEVER apply lime together with nitrogenous or phosphate fertilizers. Maintain at least a 10-14 day interval.",
                    "reference": "KAU Soil Health & Acidity Management Guidelines 2024 (Page 18)"
                }
            ],
            "Active Tillering (15-20 DAT)": [
                {
                    "fertilizer_name": "Neem Coated Urea",
                    "fertilizer_type": "Chemical (Nitrogenous)",
                    "npk_composition": "46% Nitrogen",
                    "purpose": "Boosts vegetative tillering, chlorophyll formation, and canopy expansion.",
                    "recommended_quantity": "20-25 kg per acre",
                    "application_method": "Top dressing. Drain standing water leaving thin moisture layer; re-irrigate after 24-48 hours.",
                    "application_timing": "Early morning or late afternoon when dew has dried off foliage",
                    "precautions": "Do not top dress during heavy rainfall or when standing water exceeds 5 cm. Splitting nitrogen prevents leaching.",
                    "reference": "KAU Package of Practices: Crops 2024 (Nutrient Split Schedule for Rice, Page 23)"
                },
                {
                    "fertilizer_name": "Muriate of Potash (MOP)",
                    "fertilizer_type": "Chemical (Potassic)",
                    "npk_composition": "60% K2O",
                    "purpose": "Strengthens culm against lodging and confers resistance against stem borer and blast.",
                    "recommended_quantity": "12-15 kg per acre (1st split)",
                    "application_method": "Top dressing alongside urea",
                    "application_timing": "15-20 days after transplanting",
                    "precautions": "Apply with adequate soil moisture. Avoid standing flood water.",
                    "reference": "KAU Package of Practices: Crops 2024 (Rice Section 3.4.2, Page 23)"
                }
            ],
            "Panicle Initiation (35-40 DAT)": [
                {
                    "fertilizer_name": "Neem Coated Urea + Muriate of Potash (MOP)",
                    "fertilizer_type": "Chemical (Split Dose)",
                    "npk_composition": "Urea (46% N) + MOP (60% K2O)",
                    "purpose": "Supports panicle primordial development, spikelet count, and uniform earhead emergence.",
                    "recommended_quantity": "15-20 kg Urea + 12-15 kg MOP per acre",
                    "application_method": "Top dress after draining ponded water",
                    "application_timing": "At flag leaf emergence / panicle initiation",
                    "precautions": "Excess nitrogen at this stage invites neck blast and sheath blight. Stick to the recommended dosage.",
                    "reference": "ICAR-NRRI & KAU Joint Rice Advisory 2024 (Page 26)"
                }
            ],
            "Flowering & Grain Filling": [
                {
                    "fertilizer_name": "Water Soluble 19:19:19 or 13:0:45 (Potassium Nitrate)",
                    "fertilizer_type": "Foliar Fertilizer",
                    "npk_composition": "19:19:19 or 13:0:45",
                    "purpose": "Enhances grain filling, test weight, and reduces chaffy grains.",
                    "recommended_quantity": "5-10 grams per litre of water (approx. 1-1.5 kg per acre spray volume)",
                    "application_method": "Fine foliar spray onto panicles and flag leaves",
                    "application_timing": "Late afternoon during milking / soft dough stage",
                    "precautions": "Do not spray during bright midday sun or imminent rainfall. Do not exceed 1% concentration.",
                    "reference": "KAU Foliar Nutrition Guidelines for Cereals 2024 (Page 31)"
                }
            ],
            "Maturity & Harvesting": [
                {
                    "fertilizer_name": "No Chemical Fertilizer Required",
                    "fertilizer_type": "Management Guideline",
                    "npk_composition": "N/A",
                    "purpose": "Allows natural translocation of stored starches to grains and permits crop maturation.",
                    "recommended_quantity": "0 kg",
                    "application_method": "Withhold all fertilizers and drain field 10 days before harvest",
                    "application_timing": "Terminal ripening stage",
                    "precautions": "Applying nitrogen now causes green vegetative regrowth, delayed maturity, and grain spoilage.",
                    "reference": "KAU Harvest Management Protocol 2024 (Page 33)"
                }
            ]
        }
    },

    "banana": {
        "id": "banana",
        "name": "Banana / Plantain (വാഴ - Nendran/Robusta)",
        "scientific_name": "Musa paradisiaca",
        "category": "Fruits",
        "soil_suitability": "Deep, well-drained loamy soil with rich organic matter. pH 6.0 - 7.5",
        "growth_stages": [
            "Planting / Pit Preparation",
            "Early Vegetative (2nd Month)",
            "Active Growth (4th Month)",
            "Shooting / Bunch Emergence (7-8th Month)",
            "Bunch Development & Harvest"
        ],
        "fertilizer_recommendations": {
            "Planting / Pit Preparation": [
                {
                    "fertilizer_name": "Composted Farmyard Manure or Vermicompost",
                    "fertilizer_type": "Organic",
                    "npk_composition": "FYM (0.5-0.8% N), Vermicompost (1.5-2.0% N, 1% P, 1.5% K)",
                    "purpose": "Provides basal organic cushion, promotes feeder root emergence, and prevents pit soil hardening.",
                    "recommended_quantity": "10-15 kg FYM or 5 kg Vermicompost per pit",
                    "application_method": "Mix thoroughly with topsoil in the bottom two-thirds of planting pit (60cm x 60cm x 60cm)",
                    "application_timing": "At pit filling, 7-10 days before suckering",
                    "precautions": "Do not use unfermented dung as heat of decomposition and grubs will attack the corm.",
                    "reference": "KAU Package of Practices: Fruits 2024 (Banana Section 4.2, Page 48)"
                },
                {
                    "fertilizer_name": "Rock Phosphate / Mussoriephos",
                    "fertilizer_type": "Mineral Phosphate",
                    "npk_composition": "18-20% Citric Acid Soluble P2O5",
                    "purpose": "Slow-release phosphorus for deep anchor and feeder root development.",
                    "recommended_quantity": "150-200 grams per pit",
                    "application_method": "Mix into the planting pit soil mix",
                    "application_timing": "At basal pit preparation",
                    "precautions": "Works best in slightly acidic soils of Kerala; incorporate evenly.",
                    "reference": "ICAR-National Research Centre for Banana (NRCB Technical Bulletin, Page 12)"
                },
                {
                    "fertilizer_name": "Neem Cake Powder",
                    "fertilizer_type": "Bio-organic / Nematicide",
                    "npk_composition": "5.2% N, 1.0% P, 1.4% K (Typical)",
                    "purpose": "Wards off banana rhizome weevil and burrowing nematodes while slowly releasing nitrogen.",
                    "recommended_quantity": "500 grams to 1 kg per pit",
                    "application_method": "Mix in ring around the corm zone in the pit",
                    "application_timing": "Basal pit filling",
                    "precautions": "Ensure powdered form is free of mold. Keep 5 cm away from direct contact with tender bud.",
                    "reference": "KAU Bio-pesticides & Bio-fertilizers Handbook (Page 64)"
                }
            ],
            "Early Vegetative (2nd Month)": [
                {
                    "fertilizer_name": "Urea + Muriate of Potash (MOP)",
                    "fertilizer_type": "Chemical",
                    "npk_composition": "Urea (46% N), MOP (60% K2O)",
                    "purpose": "Accelerates pseudo-stem height and broad leaf emergence.",
                    "recommended_quantity": "50g Urea + 60g MOP per plant",
                    "application_method": "Ring application 30-40 cm away from pseudo-stem, lightly forked and watered",
                    "application_timing": "60 days after planting",
                    "precautions": "Never pile fertilizer against pseudo-stem. Always irrigate immediately after application.",
                    "reference": "KAU Package of Practices: Fruits 2024 (Banana NPK Split Schedule, Page 49)"
                }
            ],
            "Active Growth (4th Month)": [
                {
                    "fertilizer_name": "Urea + MOP (2nd Top Dress)",
                    "fertilizer_type": "Chemical",
                    "npk_composition": "Urea (46% N), MOP (60% K2O)",
                    "purpose": "Enhances leaf area index and prepares plant corm for flower bud differentiation.",
                    "recommended_quantity": "65g Urea + 100g MOP per plant",
                    "application_method": "Ring application at 50 cm distance from stem; cover with soil mulch",
                    "application_timing": "120 days after planting",
                    "precautions": "Ensure soil is damp. Avoid applying just before forecasted torrential downpours.",
                    "reference": "KAU Package of Practices: Fruits 2024 (Banana Nutrition, Page 50)"
                }
            ],
            "Shooting / Bunch Emergence (7-8th Month)": [
                {
                    "fertilizer_name": "Muriate of Potash (MOP) + Magnesium Sulphate",
                    "fertilizer_type": "Chemical & Micronutrient",
                    "npk_composition": "MOP (60% K2O), MgSO4 (9.6% Mg, 12% S)",
                    "purpose": "Potassium is decisive for finger filling, fruit curvature, sugar accumulation, and bunch weight.",
                    "recommended_quantity": "100g MOP + 25g MgSO4 per plant",
                    "application_method": "Soil ring application followed by earthing up and mulching",
                    "application_timing": "At flower bud emergence / bunch shooting",
                    "precautions": "Cease nitrogen application after bunch emergence to prevent fruit drop and finger tip rot.",
                    "reference": "KAU Package of Practices: Fruits 2024 (Page 52)"
                }
            ],
            "Bunch Development & Harvest": [
                {
                    "fertilizer_name": "Sulphate of Potash (0:0:50) Foliar Bunch Spray",
                    "fertilizer_type": "Foliar Fertilizer",
                    "npk_composition": "0:0:50 + 17.5% Sulfur",
                    "purpose": "Improves fruit luster, skin thickness, and shelf life.",
                    "recommended_quantity": "5 grams per litre of water (spray directly on developing bunch after removing male bud)",
                    "application_method": "Direct bunch spray using fine nozzle; cover bunch with perforated polythene or dried leaves",
                    "application_timing": "15 days after bunch opening",
                    "precautions": "Spray during calm weather. Do not apply chemical pesticides at harvest approach.",
                    "reference": "ICAR-NRCB Post-Harvest Protocol (Page 19)"
                }
            ]
        }
    },

    "coconut": {
        "id": "coconut",
        "name": "Coconut (തെങ്ങ് - WCT/Komadan)",
        "scientific_name": "Cocos nucifera",
        "category": "Plantation",
        "soil_suitability": "Laterite, sandy, red sandy loam. pH 5.5 - 7.0 with good drainage.",
        "growth_stages": [
            "Seedling (1-3 Years)",
            "Pre-Bearing (4-7 Years)",
            "Bearing Adult Palm (Pre-Monsoon / May-June)",
            "Bearing Adult Palm (Post-Monsoon / Sep-Oct)"
        ],
        "fertilizer_recommendations": {
            "Bearing Adult Palm (Pre-Monsoon / May-June)": [
                {
                    "fertilizer_name": "Urea + Rock Phosphate + Muriate of Potash (1/3rd split)",
                    "fertilizer_type": "Chemical Blend",
                    "npk_composition": "Annual Adult Palm Dose: 500g N, 320g P2O5, 1200g K2O",
                    "purpose": "Replenishes depleted reserves after dry season and triggers floral primordia in the leaf axils.",
                    "recommended_quantity": "350g Urea + 500g Rock Phosphate + 700g MOP per palm",
                    "application_method": "Circular basin 1.8 to 2 metres away from trunk; lightly fork into top 10 cm soil",
                    "application_timing": "May - June with onset of southwest pre-monsoon showers",
                    "precautions": "Do not apply if basin is waterlogged. Open circular drainage trenches in heavy soil.",
                    "reference": "KAU Package of Practices: Plantation Crops 2024 (Coconut Section 2.3, Page 84)"
                },
                {
                    "fertilizer_name": "Green Manure / Sunnhemp / Cowpea in palm basin",
                    "fertilizer_type": "Organic / Bio-enrichment",
                    "npk_composition": "Organic biomass providing 20-25 kg green manure",
                    "purpose": "Suppresses weeds, adds 15-20 kg organic matter per palm, and conserves basin moisture.",
                    "recommended_quantity": "100g seeds sown in circular basin around palm",
                    "application_method": "Sow with pre-monsoon showers and slash down at 50% flowering; incorporate into basin",
                    "application_timing": "May sowing, August incorporation",
                    "precautions": "Cut before seed setting to avoid nutrient depletion.",
                    "reference": "ICAR-CPCRI Integrated Nutrient Management Bulletin (Page 15)"
                }
            ],
            "Bearing Adult Palm (Post-Monsoon / Sep-Oct)": [
                {
                    "fertilizer_name": "Urea + Muriate of Potash (2/3rd split)",
                    "fertilizer_type": "Chemical",
                    "npk_composition": "Urea (46% N), MOP (60% K2O)",
                    "purpose": "Major nutrient burst sustaining developing nut bunches and female flower button retention.",
                    "recommended_quantity": "700g Urea + 1300g MOP + 500g Magnesium Sulphate per palm",
                    "application_method": "Circular basin application (2m radius); incorporate and cover with dry coconut frond mulch",
                    "application_timing": "September - October during retreating northeast monsoon",
                    "precautions": "Crucial to irrigate if rains cease early. Magnesium prevents yellowing of older fronds.",
                    "reference": "KAU Package of Practices: Plantation Crops 2024 (Coconut Section 2.3, Page 86)"
                },
                {
                    "fertilizer_name": "Agricultural Dolomite / Lime",
                    "fertilizer_type": "Soil Conditioner",
                    "npk_composition": "Calcium & Magnesium Carbonate",
                    "purpose": "Neutralizes acidity in laterite root zones and prevents crown choking.",
                    "recommended_quantity": "1 kg per adult palm annually",
                    "application_method": "Broadcast in circular basin",
                    "application_timing": "April-May (1 month before chemical fertilizer application)",
                    "precautions": "Never mix directly with chemical fertilizers.",
                    "reference": "KAU Coconut Management Handbook (Page 38)"
                }
            ],
            "Seedling (1-3 Years)": [
                {
                    "fertilizer_name": "Young Palm Starter NPK Blend",
                    "fertilizer_type": "Chemical + Organic",
                    "npk_composition": "1/4th to 1/3rd of adult dose",
                    "purpose": "Builds robust root crown and rapid leaf production.",
                    "recommended_quantity": "10 kg Compost + 150g Urea + 200g Rock Phosphate + 300g MOP per seedling/year",
                    "application_method": "Apply in 1m radius basin away from seedling collar",
                    "application_timing": "Two splits (June and September)",
                    "precautions": "Protect collar from soil piling and water stagnancy.",
                    "reference": "ICAR-CPCRI Seedling Care Manual (Page 8)"
                }
            ]
        }
    },

    "pepper": {
        "id": "pepper",
        "name": "Black Pepper (കുരുമുളക് - Panniyur varieties)",
        "scientific_name": "Piper nigrum",
        "category": "Spices",
        "soil_suitability": "Well-drained laterite or red loam rich in humus. pH 5.5 - 6.5.",
        "growth_stages": [
            "Establishment / Planting",
            "Pre-Monsoon Active Flush (May-June)",
            "Berry Development (August-September)",
            "Post-Harvest / Winter (December-January)"
        ],
        "fertilizer_recommendations": {
            "Pre-Monsoon Active Flush (May-June)": [
                {
                    "fertilizer_name": "NPK 140:55:270 g per standard vine (1st split)",
                    "fertilizer_type": "Chemical",
                    "npk_composition": "Urea + Rock Phosphate + MOP",
                    "purpose": "Supports flush growth, spike emergence, and lateral branch development.",
                    "recommended_quantity": "75g Urea + 130g Rock Phosphate + 225g MOP per vine (half dose)",
                    "application_method": "Circular band 30 cm around standard vine, covered with loose soil and organic mulch",
                    "application_timing": "May - June with early monsoon rains",
                    "precautions": "Do not damage delicate feeder roots in the top 15 cm soil. Apply after weeding.",
                    "reference": "KAU Package of Practices: Spices 2024 (Black Pepper Section 1.4, Page 114)"
                },
                {
                    "fertilizer_name": "Trichoderma-enriched Farmyard Manure / Neem Cake",
                    "fertilizer_type": "Bio-organic Protection",
                    "npk_composition": "FYM + Neem Cake (10:1 ratio) colonized with Trichoderma harzianum",
                    "purpose": "Prevents catastrophic foot rot (quick wilt caused by Phytophthora capsici) while nourishing the vine.",
                    "recommended_quantity": "5 kg enriched FYM + 500g Neem cake per vine",
                    "application_method": "Basin surface mulch around vine collar",
                    "application_timing": "May before continuous heavy rain begins",
                    "precautions": "Do not apply chemical fungicides in the same root zone within 14 days of Trichoderma application.",
                    "reference": "ICAR-IISR Black Pepper Health Manual (Page 22)"
                }
            ],
            "Berry Development (August-September)": [
                {
                    "fertilizer_name": "Urea + MOP (2nd split)",
                    "fertilizer_type": "Chemical",
                    "npk_composition": "Urea (46% N), MOP (60% K2O)",
                    "purpose": "Promotes berry sizing, prevents spike shedding, and improves Piperine content.",
                    "recommended_quantity": "75g Urea + 225g MOP per vine",
                    "application_method": "Surface incorporation in 30 cm radius under leaf mulch",
                    "application_timing": "Late August - September",
                    "precautions": "Maintain adequate soil moisture; protect basins from erosion on slope terrains.",
                    "reference": "KAU Package of Practices: Spices 2024 (Page 116)"
                }
            ]
        }
    },

    "vegetables": {
        "id": "vegetables",
        "name": "Vegetables / Bhindi / Solanaceous (പച്ചക്കറികൾ / വെണ്ട / വഴുതന)",
        "scientific_name": "Abelmoschus esculentus / Solanum melongena",
        "category": "Vegetables",
        "soil_suitability": "Rich friable loam with high organic matter. pH 6.0 - 7.0.",
        "growth_stages": [
            "Basal / Bed Preparation",
            "Vegetative Growth (15-20 DAS)",
            "Flowering & First Picking (35-40 DAS)",
            "Peak Harvest / Continuous Picking"
        ],
        "fertilizer_recommendations": {
            "Basal / Bed Preparation": [
                {
                    "fertilizer_name": "Compost / Vermicompost + Neem Cake",
                    "fertilizer_type": "Organic Base",
                    "npk_composition": "Vermicompost + Neem cake (9:1)",
                    "purpose": "Conditions rhizosphere, enhances beneficial nematodes suppression, and provides continuous slow nutrition.",
                    "recommended_quantity": "8-10 tonnes FYM or 3 tonnes Vermicompost + 200 kg Neem cake per acre",
                    "application_method": "Broadcast and incorporate into raised beds during final tilling",
                    "application_timing": "7 days prior to seed sowing or seedling planting",
                    "precautions": "Ensure compost is well cured and cool to touch.",
                    "reference": "KAU Package of Practices: Vegetables 2024 (Section 6.1, Page 142)"
                },
                {
                    "fertilizer_name": "Factamfos (20:20:0:13) + MOP",
                    "fertilizer_type": "Chemical Basal",
                    "npk_composition": "20:20:0:13 + 60% K2O",
                    "purpose": "Full phosphorus basal dose along with starter nitrogen and potassium.",
                    "recommended_quantity": "50 kg Factamfos + 20 kg MOP per acre",
                    "application_method": "Band placement 5 cm below seed or seedling row",
                    "application_timing": "At time of sowing / planting",
                    "precautions": "Do not let germinating seeds touch concentrated chemical granules directly.",
                    "reference": "KAU Vegetable Recommendation Chart 2024 (Page 144)"
                }
            ],
            "Vegetative Growth (15-20 DAS)": [
                {
                    "fertilizer_name": "Urea (1st Top Dressing)",
                    "fertilizer_type": "Chemical",
                    "npk_composition": "46% Nitrogen",
                    "purpose": "Promotes rapid branching, leaf node formation, and strong root anchor.",
                    "recommended_quantity": "25 kg Urea per acre",
                    "application_method": "Side dressing along plant rows followed by weeding and hoeing",
                    "application_timing": "15-20 days after germination",
                    "precautions": "Apply when soil is moist. Avoid hot midday hours.",
                    "reference": "KAU Package of Practices: Vegetables 2024 (Page 145)"
                }
            ],
            "Flowering & First Picking (35-40 DAS)": [
                {
                    "fertilizer_name": "Urea + MOP (2nd Top Dressing) & 19:19:19 Foliar",
                    "fertilizer_type": "Chemical + Foliar",
                    "npk_composition": "Urea + MOP + Soluble 19:19:19",
                    "purpose": "Prevents flower drop, accelerates fruit set, and enhances continuous fruit picking.",
                    "recommended_quantity": "25 kg Urea + 15 kg MOP per acre soil; 5g/L 19:19:19 foliar spray",
                    "application_method": "Soil side dressing followed by irrigation; foliar spray on foliage",
                    "application_timing": "At commencement of flowering and every 15 days during harvest",
                    "precautions": "Observe pre-harvest intervals if combined with plant protection sprays.",
                    "reference": "KAU Vegetable Cultivation Guidelines 2024 (Page 146)"
                }
            ]
        }
    }
}
