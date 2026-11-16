const API_BASE = "http://127.0.0.1:8000";

const DASHBOARD_API = `${API_BASE}/api/dashboard`;
const WEATHER_API = `${API_BASE}/api/weather`;
const ADVISOR_CROPS_API = `${API_BASE}/api/advisor/crops`;
const ADVISOR_FERT_API = `${API_BASE}/api/advisor/fertilizer`;

// Update farm coordinates display (latitude & longitude)
function updateFarmCoordinates() {
  const latEl = document.getElementById('latValue');
  const lonEl = document.getElementById('lonValue');
  if (latEl && lonEl) {
    latEl.textContent = FARM_LAT.toFixed(5);
    lonEl.textContent = FARM_LON.toFixed(5);
  }
}

// Call on initial load and after successful dashboard fetch
window.addEventListener('load', updateFarmCoordinates);

const ADVISOR_ORGANIC_API = `${API_BASE}/api/advisor/organic-recipe`;
const ADVISOR_EXPLAIN_API = `${API_BASE}/api/advisor/explain`;
const FEED_API = `${API_BASE}/api/feed`;
const FEED_QUERY_API = `${API_BASE}/api/feed/query`;
const FEED_REFRESH_API = `${API_BASE}/api/feed/refresh`;

const POLL_MS = 3000;
const WEATHER_POLL_MS = 10 * 60 * 1000;

// Farm default coordinates (Kerala Agro-climatic zone)
const FARM_LAT = 9.50996;
const FARM_LON = 76.55067;

// ===============================
// EXISTING DASHBOARD ELEMENTS
// ===============================

const connDot = document.getElementById("connDot");
const connLabel = document.getElementById("connLabel");
const decisionTitle = document.getElementById("decisionTitle");
const decisionDescription = document.getElementById("decisionDescription");
const mlTag = document.getElementById("mlTag");
const weatherTag = document.getElementById("weatherTag");
const soilValue = document.getElementById("soilValue");
const tempValue = document.getElementById("tempValue");
const humidityValue = document.getElementById("humidityValue");
const lightValue = document.getElementById("lightValue");
const lightContext = document.getElementById("lightContext");
const aiRecommendation = document.getElementById("aiRecommendation");
const weatherDecision = document.getElementById("weatherDecision");
const finalDecision = document.getElementById("finalDecision");
const reasonText = document.getElementById("reasonText");
const dropRateValue = document.getElementById("dropRateValue");
const timeSinceValue = document.getElementById("timeSinceValue");
const weatherHeadline = document.getElementById("weatherHeadline");
const weatherDetail = document.getElementById("weatherDetail");
const rainProbability = document.getElementById("rainProbability");
const rainAmount = document.getElementById("rainAmount");
const nextRain = document.getElementById("nextRain");
const forecastStrip = document.getElementById("forecastStrip");

// Global state caches
let currentWeatherData = null;
let supportedCropsList = [];
let feedCardsList = [];
let currentSpeakingUtterance = null;
let currentSpeakingCardId = null;

// ===============================
// CONNECTION STATUS
// ===============================

function setConnected(connected) {
  connLabel.textContent = connected ? "System Online" : "Connecting";
  connDot.className = connected ? "connected" : "";
}

// ===============================
// TAB NAVIGATION
// ===============================

function switchTab(tabId) {
  // Update nav buttons
  document.querySelectorAll(".nav-btn").forEach((btn) => btn.classList.remove("active"));
  document.querySelectorAll(".tab-content").forEach((tab) => tab.classList.remove("active"));

  if (tabId === "irrigation") {
    document.getElementById("navIrrigationBtn").classList.add("active");
    document.getElementById("tabIrrigation").classList.add("active");
  } else if (tabId === "advisor") {
    document.getElementById("navAdvisorBtn").classList.add("active");
    document.getElementById("tabAdvisor").classList.add("active");
    if (!supportedCropsList.length) {
      loadAdvisorCrops();
    }
  } else if (tabId === "feed") {
    document.getElementById("navFeedBtn").classList.add("active");
    document.getElementById("tabFeed").classList.add("active");
    if (!feedCardsList.length) {
      fetchFeed();
    }
  }
}

// ===============================
// EXISTING DASHBOARD FETCH
// ===============================

async function fetchDashboard() {
  try {
    const response = await fetch(DASHBOARD_API, { cache: "no-store" });
    if (!response.ok) throw new Error("Dashboard error");

    const data = await response.json();
    const telemetry = data.latest_telemetry || data;

    const soil = Number(telemetry.soil_moisture ?? 0);
    const temperature = Number(telemetry.temperature ?? 0);
    const humidity = Number(telemetry.humidity ?? 0);
    const light = telemetry.light ?? 0;
    const dropRate = Number(telemetry.moisture_drop_rate ?? 0);
    const timeSince = Number(telemetry.time_since_irrigation ?? 0);

    soilValue.textContent = soil.toFixed(1);
    tempValue.textContent = temperature.toFixed(1);
    humidityValue.textContent = humidity.toFixed(1);

    const lightText = Number(light) === 1 ? "Good / Ample" : "Low";
    lightValue.textContent = lightText;
    lightContext.textContent = lightText;

    dropRateValue.textContent = dropRate.toFixed(2);
    timeSinceValue.textContent = `${timeSince} min`;

    const ml = Number(telemetry.ml_recommendation ?? telemetry.ml_prediction ?? 0);
    const irrigationNeeded = ml === 1;

    aiRecommendation.textContent = irrigationNeeded ? "Irrigation Needed" : "Irrigation Not Needed";
    mlTag.textContent = irrigationNeeded ? "AI: Irrigation Needed" : "AI: Irrigation Not Needed";

    const weatherBlocked = Boolean(telemetry.weather_override);
    if (weatherBlocked) {
      weatherDecision.textContent = "Rain expected";
      weatherTag.textContent = "Weather: Rain expected";
    } else {
      weatherDecision.textContent = "No immediate rain";
      weatherTag.textContent = "Weather: No immediate rain";
    }

    finalDecision.textContent = irrigationNeeded ? "Irrigation Needed" : "Irrigation Not Needed";
    decisionTitle.textContent = irrigationNeeded ? "Irrigation Needed" : "Irrigation Not Needed";
    decisionDescription.textContent = irrigationNeeded
      ? "The ML model recommends irrigation based on current field conditions."
      : "The ML model does not recommend irrigation under current field conditions.";

    reasonText.textContent = telemetry.reason || (irrigationNeeded ? "The ML model recommends irrigation." : "The ML model does not recommend irrigation.");

    setConnected(true);
  } catch (error) {
    console.error("Dashboard error:", error);
    setConnected(false);
    decisionTitle.textContent = "Waiting for field data";
    decisionDescription.textContent = "Unable to receive live telemetry from the controller.";
  }
}

// ===============================
// EXISTING WEATHER FETCH
// ===============================

async function fetchWeather() {
  try {
    const response = await fetch(WEATHER_API, { cache: "no-store" });
    if (!response.ok) throw new Error("Weather error");

    const data = await response.json();
    currentWeatherData = data;

    if (!data.hourly) return;

    const times = data.hourly.time || [];
    const probabilities = data.hourly.precipitation_probability || [];
    const rain = data.hourly.rain || [];
    const precipitation = data.hourly.precipitation || [];

    if (!times.length) return;

    const probability = Number(probabilities[0] ?? 0);
    const rainAmountValue = Number(precipitation[0] ?? rain[0] ?? 0);

    rainProbability.textContent = `${probability}%`;
    rainAmount.textContent = `${rainAmountValue.toFixed(1)} mm`;
    nextRain.textContent = `${probability}%`;

    const weatherStatusEl = document.getElementById("advisorWeatherStatus");
    if (weatherStatusEl) {
      weatherStatusEl.textContent = `${probability}% Rain chance (${rainAmountValue.toFixed(1)} mm)`;
    }

    if (probability >= 60) {
      weatherHeadline.textContent = "Rain expected soon";
      weatherDetail.textContent = `${probability}% chance of rain in the immediate forecast hour.`;
    } else {
      weatherHeadline.textContent = "No significant rain expected";
      weatherDetail.textContent = `${probability}% chance of rain in the immediate forecast hour.`;
    }

    forecastStrip.innerHTML = "";
    const count = Math.min(6, times.length);

    for (let i = 0; i < count; i++) {
      const time = new Date(times[i]);
      const hour = time.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
      const prob = Number(probabilities[i] ?? 0);
      const amount = Number(precipitation[i] ?? rain[i] ?? 0);

      const item = document.createElement("div");
      item.className = "forecast-item";
      item.innerHTML = `
        <small>${hour}</small>
        <strong>${prob}%</strong>
        <span>${amount.toFixed(1)} mm</span>
      `;
      forecastStrip.appendChild(item);
    }
  } catch (error) {
    console.error("Weather error:", error);
    weatherHeadline.textContent = "Weather unavailable";
  }
}

// ============================================================
// FEATURE 1: AI AGRICULTURAL ADVISOR
// ============================================================

async function loadAdvisorCrops() {
  try {
    const res = await fetch(ADVISOR_CROPS_API);
    if (!res.ok) throw new Error("Failed to load crops");
    const data = await res.json();
    supportedCropsList = data.crops || [];

    const cropSelect = document.getElementById("advisorCropSelect");
    cropSelect.innerHTML = "";
    supportedCropsList.forEach((c) => {
      const opt = document.createElement("option");
      opt.value = c.id;
      opt.textContent = c.name;
      cropSelect.appendChild(opt);
    });

    onAdvisorCropChange();
  } catch (e) {
    console.error("Error loading advisor crops:", e);
  }
}

function onAdvisorCropChange() {
  const cropId = document.getElementById("advisorCropSelect").value;
  const cropData = supportedCropsList.find((c) => c.id === cropId);
  const stageSelect = document.getElementById("advisorStageSelect");
  stageSelect.innerHTML = "";

  if (cropData && cropData.growth_stages) {
    cropData.growth_stages.forEach((stage) => {
      const opt = document.createElement("option");
      opt.value = stage;
      opt.textContent = stage;
      stageSelect.appendChild(opt);
    });
  }
}

function switchAdvisorSubTab(subTabId) {
  document.getElementById("subTabFertBtn").classList.remove("active");
  document.getElementById("subTabOrganicBtn").classList.remove("active");
  document.getElementById("subContentFertilizer").classList.remove("active");
  document.getElementById("subContentOrganic").classList.remove("active");

  if (subTabId === "fertilizer") {
    document.getElementById("subTabFertBtn").classList.add("active");
    document.getElementById("subContentFertilizer").classList.add("active");
  } else {
    document.getElementById("subTabOrganicBtn").classList.add("active");
    document.getElementById("subContentOrganic").classList.add("active");
  }
}

async function fetchFertilizerRecommendations() {
  const cropId = document.getElementById("advisorCropSelect").value;
  const stage = document.getElementById("advisorStageSelect").value;
  const soilPh = document.getElementById("soilPh").value;
  const soilType = document.getElementById("soilType").value;

  const soilData = soilPh ? { pH: parseFloat(soilPh), texture: soilType } : null;

  const listContainer = document.getElementById("fertilizerList");
  listContainer.innerHTML = `<div class="empty-state">Computing verified agronomic recommendations...</div>`;

  try {
    const res = await fetch(ADVISOR_FERT_API, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        crop_id: cropId,
        growth_stage: stage,
        latitude: FARM_LAT,
        longitude: FARM_LON,
        soil_data: soilData
      })
    });

    if (!res.ok) throw new Error("Fertilizer recommendation failed");
    const data = await res.json();
    renderFertilizerResults(data);

    // Fetch AI Explanation in parallel
    fetchAdvisorExplanation(data);
  } catch (e) {
    console.error("Error fetching fertilizer:", e);
    listContainer.innerHTML = `<div class="empty-state" style="color:#b02a2a;">Unable to load recommendations. Please check server status.</div>`;
  }
}

function renderFertilizerResults(data) {
  const listContainer = document.getElementById("fertilizerList");
  const weatherAlertBanner = document.getElementById("fertWeatherAlert");
  const soilNoticeBanner = document.getElementById("fertSoilNotice");

  // Weather safety banner
  const alerts = data.weather_context?.application_safety_alerts || [];
  if (alerts.length > 0) {
    const isHazard = alerts.some((a) => a.includes("RAIN HAZARD"));
    weatherAlertBanner.className = `weather-alert-banner ${isHazard ? "hazard" : "favorable"}`;
    weatherAlertBanner.innerHTML = `<strong>Agricultural Weather Alert:</strong> ${alerts.join("<br>")}`;
    weatherAlertBanner.style.display = "block";
  } else {
    weatherAlertBanner.style.display = "none";
  }

  // Soil guideline banner
  if (data.soil_context?.guideline_notice) {
    soilNoticeBanner.textContent = data.soil_context.guideline_notice;
    soilNoticeBanner.style.display = "block";
  }

  const recs = data.recommendations || [];
  if (recs.length === 0) {
    listContainer.innerHTML = `<div class="empty-state">No specific chemical fertilizer required for this stage.</div>`;
    return;
  }

  listContainer.innerHTML = "";
  recs.forEach((rec) => {
    const isOrganic = rec.fertilizer_type.toLowerCase().includes("organic");
    const typeBadgeClass = isOrganic ? "badge-organic" : "badge-chemical";

    const card = document.createElement("div");
    card.className = "fert-item-card";
    card.innerHTML = `
      <div class="fert-item-header">
        <h4>${rec.fertilizer_name}</h4>
        <div class="fert-badges">
          <span class="badge ${typeBadgeClass}">${rec.fertilizer_type}</span>
          ${rec.npk_composition ? `<span class="badge badge-npk">${rec.npk_composition}</span>` : ""}
        </div>
      </div>
      <p class="fert-desc">${rec.purpose}</p>
      <div class="fert-item-grid">
        <div class="fert-field">
          <small>Recommended Quantity</small>
          <strong>${rec.recommended_quantity}</strong>
        </div>
        <div class="fert-field">
          <small>Application Timing</small>
          <strong>${rec.application_timing}</strong>
        </div>
        <div class="fert-field">
          <small>Application Method</small>
          <strong>${rec.application_method}</strong>
        </div>
      </div>
      <div class="fert-precautions">
        <strong>⚠️ Precautions:</strong> ${rec.precautions}
      </div>
      <div class="fert-ref">
        Source: ${rec.reference}
      </div>
    `;
    listContainer.appendChild(card);
  });
}

async function fetchAdvisorExplanation(advisorData) {
  const cropName = advisorData.crop?.name || "Selected Crop";
  const stage = advisorData.selected_stage || "Current Stage";
  const weatherSummary = (advisorData.weather_context?.application_safety_alerts || []).join("; ");

  try {
    const res = await fetch(ADVISOR_EXPLAIN_API, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        crop_name: cropName,
        stage: stage,
        weather_summary: weatherSummary,
        recommendations: advisorData.recommendations || []
      })
    });

    if (!res.ok) return;
    const expl = await res.json();

    const box = document.getElementById("aiExplanationBox");
    document.getElementById("aiExplTitle").textContent = `Agronomic Advisory (${expl.source || "KAU Expert Engine"})`;
    document.getElementById("aiSummaryEn").textContent = expl.summary_en || "";
    document.getElementById("aiSummaryMl").textContent = expl.summary_ml || "";

    const tipsList = document.getElementById("aiActionTips");
    tipsList.innerHTML = "";
    (expl.farmer_action_tips || []).forEach((t) => {
      const li = document.createElement("li");
      li.textContent = t;
      tipsList.appendChild(li);
    });

    document.getElementById("aiSafetyAlert").textContent = expl.safety_alert || "";
    box.style.display = "block";
  } catch (e) {
    console.error("Explanation fetch error:", e);
  }
}

// Organic Manure Recipe Generator
async function fetchOrganicRecipe() {
  const cropId = document.getElementById("advisorCropSelect").value;
  const stage = document.getElementById("advisorStageSelect").value;

  const inputs = [];
  document.querySelectorAll(".inputs-checklist input:checked").forEach((chk) => {
    inputs.push(chk.value);
  });

  const container = document.getElementById("organicRecipeContainer");
  container.innerHTML = `<div class="empty-state">Formulating scientific organic recipe...</div>`;

  try {
    const res = await fetch(ADVISOR_ORGANIC_API, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        crop_id: cropId,
        growth_stage: stage,
        available_inputs: inputs
      })
    });

    if (!res.ok) throw new Error("Failed to generate recipe");
    const data = await res.json();
    renderOrganicRecipe(data);
  } catch (e) {
    console.error("Organic recipe error:", e);
    container.innerHTML = `<div class="empty-state" style="color:#b02a2a;">Unable to generate organic recipe.</div>`;
  }
}

function renderOrganicRecipe(data) {
  const container = document.getElementById("organicRecipeContainer");
  const rec = data.primary_recipe;
  if (!rec) {
    container.innerHTML = `<div class="empty-state">No matching organic recipe found.</div>`;
    return;
  }

  let ingRows = "";
  rec.ingredients.forEach((ing) => {
    ingRows += `
      <tr>
        <td><strong>${ing.item}</strong></td>
        <td>${ing.proportion}</td>
        <td>${ing.percentage ? ing.percentage + "%" : "--"}</td>
      </tr>
    `;
  });

  let stepItems = "";
  rec.preparation_instructions.forEach((s) => {
    stepItems += `<li>${s}</li>`;
  });

  container.innerHTML = `
    <div class="recipe-display-card">
      <h3 class="recipe-title">🌿 ${rec.name}</h3>
      <span class="recipe-type">${rec.recipe_type}</span>

      <table class="ingredients-table">
        <thead>
          <tr>
            <th>Ingredient (ഘടകങ്ങൾ)</th>
            <th>Proportion / Quantity</th>
            <th>Ratio</th>
          </tr>
        </thead>
        <tbody>
          ${ingRows}
        </tbody>
      </table>

      <div class="recipe-steps">
        <strong>Preparation Instructions (തയ്യാറാക്കുന്ന വിധം):</strong>
        <ol>${stepItems}</ol>
      </div>

      <div class="recipe-meta-box">
        <strong>Application Method & Stage:</strong>
        <p>${rec.application_method}</p>
        <p><em>Suitable Stage:</em> ${rec.suitable_application_stage}</p>
        <p><strong>Expected Benefits:</strong> ${rec.expected_benefits}</p>
      </div>

      <div class="recipe-precautions-box">
        <strong>⚠️ Biological Safety Precautions:</strong>
        <p>${rec.safety_precautions}</p>
      </div>

      <div class="disclaimer-box">
        ${data.disclaimer}
      </div>
    </div>
  `;
}

// ============================================================
// FEATURE 2: AI-POWERED FARMER FEED (MALAYALAM)
// ============================================================

async function fetchFeed(category = null) {
  const cardsWrapper = document.getElementById("feedCardsWrapper");
  cardsWrapper.innerHTML = `<div class="empty-state">കാർഷിക വിവരങ്ങൾ ശേഖരിക്കുന്നു... (Loading feed...)</div>`;

  let url = `${FEED_API}?limit=25`;
  if (category && category !== "all") {
    url += `&category=${encodeURIComponent(category)}`;
  }

  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error("Feed load failed");
    const data = await res.json();
    feedCardsList = data.cards || [];
    renderFeedCards(feedCardsList);
  } catch (e) {
    console.error("Error fetching feed:", e);
    cardsWrapper.innerHTML = `<div class="empty-state" style="color:#b02a2a;">ഫീഡ് ലഭ്യമാക്കാൻ സാധിച്ചില്ല. സെർവർ റൺ ചെയ്യുന്നുണ്ടെന്ന് ഉറപ്പുവരുത്തുക.</div>`;
  }
}

function filterFeedCategory(category, buttonEl) {
  document.querySelectorAll(".pill-btn").forEach((b) => b.classList.remove("active"));
  if (buttonEl) buttonEl.classList.add("active");
  fetchFeed(category);
}

async function searchFeed() {
  const query = document.getElementById("feedQueryInput").value.trim();
  if (!query) return;

  const cardsWrapper = document.getElementById("feedCardsWrapper");
  cardsWrapper.innerHTML = `<div class="empty-state">ആധികാരിക രേഖകളിൽ തിരയുന്നു... (RAG Searching...)</div>`;

  try {
    const res = await fetch(FEED_QUERY_API, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: query, top_k: 5 })
    });

    if (!res.ok) throw new Error("RAG Search failed");
    const data = await res.json();
    renderFeedCards(data.cards || []);

    // Render retrieved sources details
    const sourcesDetails = document.getElementById("ragSourcesDetails");
    const sourcesList = document.getElementById("ragSourcesList");
    if (data.retrieved_sources && data.retrieved_sources.length > 0) {
      sourcesList.innerHTML = "";
      data.retrieved_sources.forEach((s) => {
        const item = document.createElement("div");
        item.className = "rag-source-item";
        item.innerHTML = `
          <strong>${s.citation}</strong> [${s.crop}] - ${s.topic} (Relevance: ${s.relevance_score})
        `;
        sourcesList.appendChild(item);
      });
      sourcesDetails.style.display = "block";
      sourcesDetails.open = true;
    } else {
      sourcesDetails.style.display = "none";
    }
  } catch (e) {
    console.error("Error searching feed:", e);
    cardsWrapper.innerHTML = `<div class="empty-state" style="color:#b02a2a;">തിരച്ചിൽ പരാജയപ്പെട്ടു.</div>`;
  }
}

function resetFeed() {
  document.getElementById("feedQueryInput").value = "";
  document.getElementById("ragSourcesDetails").style.display = "none";
  fetchFeed();
}

function renderFeedCards(cards) {
  const cardsWrapper = document.getElementById("feedCardsWrapper");
  const countLabel = document.getElementById("feedCountLabel");
  countLabel.textContent = `ലഭ്യമായ കാർഡുകൾ: ${cards.length}`;

  if (!cards.length) {
    cardsWrapper.innerHTML = `<div class="empty-state">വിവരങ്ങൾ ഒന്നും ലഭ്യമല്ല.</div>`;
    return;
  }

  cardsWrapper.innerHTML = "";
  cards.forEach((c) => {
    const cardEl = document.createElement("article");
    cardEl.className = "feed-card";
    cardEl.id = `card_${c.id}`;

    cardEl.innerHTML = `
      <div class="feed-card-header">
        <div class="feed-card-badges">
          <span class="badge-feed-cat">${c.category}</span>
          <span class="badge-feed-crop">${c.crop}</span>
        </div>
      </div>

      <h3 class="feed-title">${c.title}</h3>
      ${c.title_en ? `<div class="feed-title-en">${c.title_en}</div>` : ""}

      <p class="feed-explanation">${c.explanation}</p>

      <div class="practical-tip-box">
        <span class="practical-tip-label">💡 പ്രായോഗിക കാർഷിക നിർദേശം (Practical Tip):</span>
        <p class="practical-tip-text">${c.practical_tip}</p>
      </div>

      <div class="audio-bar">
        <button id="btnListen_${c.id}" class="btn-listen" onclick="toggleListenAloud('${c.id}')">
          <span id="audioIcon_${c.id}">🔊</span>
          <span id="audioLabel_${c.id}">കേൾക്കുക (Listen Aloud)</span>
        </button>
        <div id="audioStatus_${c.id}" class="speaking-indicator" style="display: none;">
          <span>🔊 വായിക്കുന്നു...</span>
        </div>
      </div>

      <div class="feed-footer">
        <span class="source-tag">സ്രോതസ്സ്: <strong>${c.source_name}</strong></span>
        <span class="citation-tag">${c.source_citation}</span>
      </div>
    `;

    cardsWrapper.appendChild(cardEl);
  });
}

// ============================================================
// MALAYALAM TEXT-TO-SPEECH (TTS) LISTEN-ALOUD
// ============================================================

function toggleListenAloud(cardId) {
  if (!("speechSynthesis" in window)) {
    alert("ക്ഷമിക്കുക, നിങ്ങളുടെ ബ്രൗസറിൽ സ്പീച്ച് സിന്തസിസ് ലഭ്യമല്ല (Text-to-speech is not supported in this browser).");
    return;
  }

  // If already speaking this card, stop it
  if (currentSpeakingCardId === cardId) {
    stopSpeaking();
    return;
  }

  // If speaking another card, stop previous
  stopSpeaking();

  const card = feedCardsList.find((c) => c.id === cardId);
  if (!card) return;

  const textToSpeak = card.audio_text || `${card.title}. ${card.explanation}. ${card.practical_tip}`;

  const utterance = new SpeechSynthesisUtterance(textToSpeak);
  utterance.lang = "ml-IN"; // Prefer Malayalam
  utterance.rate = 0.9; // Slightly slower for clear comprehension
  utterance.pitch = 1.0;

  // Attempt to select a Malayalam voice if browser provides one
  const voices = window.speechSynthesis.getVoices();
  const mlVoice = voices.find((v) => v.lang.includes("ml") || v.name.toLowerCase().includes("malayalam"));
  if (mlVoice) {
    utterance.voice = mlVoice;
  }

  // Visual cues
  const btn = document.getElementById(`btnListen_${cardId}`);
  const icon = document.getElementById(`audioIcon_${cardId}`);
  const label = document.getElementById(`audioLabel_${cardId}`);
  const status = document.getElementById(`audioStatus_${cardId}`);
  const cardEl = document.getElementById(`card_${cardId}`);

  if (btn) btn.classList.add("speaking");
  if (icon) icon.textContent = "⏹️";
  if (label) label.textContent = "നിർത്തുക (Stop)";
  if (status) status.style.display = "flex";
  if (cardEl) cardEl.classList.add("speaking");

  currentSpeakingCardId = cardId;
  currentSpeakingUtterance = utterance;

  utterance.onend = () => {
    stopSpeaking();
  };

  utterance.onerror = (e) => {
    console.warn("TTS Error:", e);
    stopSpeaking();
  };

  window.speechSynthesis.speak(utterance);
}

function stopSpeaking() {
  if ("speechSynthesis" in window) {
    window.speechSynthesis.cancel();
  }

  if (currentSpeakingCardId) {
    const btn = document.getElementById(`btnListen_${currentSpeakingCardId}`);
    const icon = document.getElementById(`audioIcon_${currentSpeakingCardId}`);
    const label = document.getElementById(`audioLabel_${currentSpeakingCardId}`);
    const status = document.getElementById(`audioStatus_${currentSpeakingCardId}`);
    const cardEl = document.getElementById(`card_${currentSpeakingCardId}`);

    if (btn) btn.classList.remove("speaking");
    if (icon) icon.textContent = "🔊";
    if (label) label.textContent = "കേൾക്കുക (Listen Aloud)";
    if (status) status.style.display = "none";
    if (cardEl) cardEl.classList.remove("speaking");
  }

  currentSpeakingCardId = null;
  currentSpeakingUtterance = null;
}

function scrollFeedCard(delta) {
  const cards = document.querySelectorAll(".feed-card");
  if (!cards.length) return;

  const currentScroll = window.scrollY;
  let targetIndex = 0;

  for (let i = 0; i < cards.length; i++) {
    const rect = cards[i].getBoundingClientRect();
    if (rect.top >= 50) {
      targetIndex = i;
      break;
    }
  }

  let nextIndex = targetIndex + delta;
  if (nextIndex < 0) nextIndex = 0;
  if (nextIndex >= cards.length) nextIndex = cards.length - 1;

  cards[nextIndex].scrollIntoView({ behavior: "smooth", block: "start" });
}

// Pre-load voices if supported
if ("speechSynthesis" in window) {
  window.speechSynthesis.onvoiceschanged = () => {
    window.speechSynthesis.getVoices();
  };
}

// ===============================
// APP INITIALIZATION
// ===============================

fetchDashboard();
fetchWeather();

setInterval(fetchDashboard, POLL_MS);
setInterval(fetchWeather, WEATHER_POLL_MS);
