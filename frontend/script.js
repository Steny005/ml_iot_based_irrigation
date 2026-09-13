/* ==========================================================================
   Smart Irrigation Control Center — Dashboard logic
   Talks to the existing FastAPI backend at GET /api/dashboard.
   No pump control, no independent safety logic — the backend is authoritative.
   ========================================================================== */

const API_URL = "http://127.0.0.1:8000/api/dashboard";
const POLL_INTERVAL_MS = 3000;

// Backend safety threshold (mirrors backend/main.py — for VISUAL classification only).
const TANK_CRITICAL_THRESHOLD = 15;
const TANK_LOW_THRESHOLD = 35;

// Soil moisture ring geometry (r=50 -> circumference ~314.16)
const RING_CIRCUMFERENCE = 2 * Math.PI * 50;

// Rough working range for the raw LDR sensor (12-bit ADC on ESP32: 0–4095)
const LIGHT_MAX = 4095;

// Display-only ranges used to position the temperature/humidity range gauges.
// These do NOT affect any backend logic — purely for visual context.
const TEMP_GAUGE_MIN = 15;
const TEMP_GAUGE_MAX = 45;

let hasReceivedFirstReading = false;
let lastSuccessfulFetchAt = null;

// ------------------------------------------------------------------------
// DOM references
// ------------------------------------------------------------------------
const el = {
  connPill: document.getElementById("connPill"),
  connDot: document.getElementById("connDot"),
  connLabel: document.getElementById("connLabel"),
  lastUpdated: document.getElementById("lastUpdated"),

  loadingBanner: document.getElementById("loadingBanner"),
  offlineBanner: document.getElementById("offlineBanner"),

  pumpPanel: document.getElementById("pumpPanel"),
  pumpStateText: document.getElementById("pumpStateText"),
  pumpSubText: document.getElementById("pumpSubText"),

  soilRing: document.getElementById("soilRing"),
  soilValue: document.getElementById("soilValue"),

  tempValue: document.getElementById("tempValue"),
  tempGaugeFill: document.getElementById("tempGaugeFill"),
  tempGaugeMarker: document.getElementById("tempGaugeMarker"),

  humidityValue: document.getElementById("humidityValue"),
  humidityGaugeFill: document.getElementById("humidityGaugeFill"),
  humidityGaugeMarker: document.getElementById("humidityGaugeMarker"),

  tankCard: document.querySelector('.metric-card[data-metric="tank"]'),
  tankFill: document.getElementById("tankFill"),
  tankValue: document.getElementById("tankValue"),
  tankNote: document.getElementById("tankNote"),

  safetyAlert: document.getElementById("safetyAlert"),
  safetyNormal: document.getElementById("safetyNormal"),
  safetyReasonText: document.getElementById("safetyReasonText"),

  aiRecChip: document.getElementById("aiRecChip"),
  actionChip: document.getElementById("actionChip"),
  reasonText: document.getElementById("reasonText"),

  lightBar: document.getElementById("lightBar"),
  lightValue: document.getElementById("lightValue"),
  dropRateValue: document.getElementById("dropRateValue"),
  timeSinceValue: document.getElementById("timeSinceValue"),
};

// ------------------------------------------------------------------------
// Formatting helpers
// ------------------------------------------------------------------------

function formatNumber(value, decimals = 1) {
  if (typeof value !== "number" || Number.isNaN(value)) return "--";
  return value.toFixed(decimals);
}

// The backend's time_since_irrigation field is recorded in MINUTES since the
// last watering cycle (confirmed against the training dataset, where this
// value increments in step with 3-minute sensor intervals). Before any
// irrigation has ever been recorded, the field can be negative — we surface
// that plainly rather than inventing a fake duration.
function formatTimeSinceIrrigation(minutes) {
  if (typeof minutes !== "number" || Number.isNaN(minutes)) return "--";
  if (minutes < 0) return "No irrigation recorded yet";
  if (minutes < 60) return `${Math.round(minutes)} min ago`;
  const hours = Math.floor(minutes / 60);
  const rem = Math.round(minutes % 60);
  return `${hours}h ${rem}m ago`;
}

function classifyTankLevel(level) {
  if (level < TANK_CRITICAL_THRESHOLD) return "critical";
  if (level < TANK_LOW_THRESHOLD) return "low";
  return "normal";
}

function secondsAgoLabel(date) {
  if (!date) return "Waiting for first reading…";
  const secs = Math.max(0, Math.round((Date.now() - date.getTime()) / 1000));
  if (secs < 2) return "Last updated: just now";
  if (secs < 60) return `Last updated: ${secs} seconds ago`;
  const mins = Math.floor(secs / 60);
  return `Last updated: ${mins} min ago`;
}

// ------------------------------------------------------------------------
// Rendering
// ------------------------------------------------------------------------

function setConnectionState(state) {
  el.connPill.dataset.state = state; // "loading" | "online" | "offline"
  if (state === "online") {
    el.connLabel.textContent = "SYSTEM ONLINE";
  } else if (state === "offline") {
    el.connLabel.textContent = "SYSTEM OFFLINE";
  } else {
    el.connLabel.textContent = "CONNECTING…";
  }
}

function renderDashboard(data) {
  // --- Pump status (the primary operational indicator) ---
  const pumpOn = data.pump_status === "ON";
  el.pumpPanel.dataset.status = pumpOn ? "on" : "off";
  el.pumpStateText.textContent = pumpOn ? "🟢 PUMP ON" : "⚫ PUMP OFF";
  el.pumpSubText.textContent = pumpOn
    ? "Irrigation is actively running."
    : "Irrigation is currently inactive.";

  // --- Soil moisture ring ---
  const soil = Math.max(0, Math.min(100, data.soil_moisture));
  const offset = RING_CIRCUMFERENCE * (1 - soil / 100);
  el.soilRing.style.strokeDashoffset = offset;
  el.soilValue.textContent = formatNumber(data.soil_moisture, 1);

  // --- Temperature ---
  el.tempValue.textContent = formatNumber(data.temperature, 1);
  const tempPct = Math.max(
    0,
    Math.min(100, ((data.temperature - TEMP_GAUGE_MIN) / (TEMP_GAUGE_MAX - TEMP_GAUGE_MIN)) * 100)
  );
  el.tempGaugeFill.style.width = `${tempPct}%`;
  el.tempGaugeMarker.style.left = `${tempPct}%`;

  // --- Humidity ---
  el.humidityValue.textContent = formatNumber(data.humidity, 1);
  const humidityPct = Math.max(0, Math.min(100, data.humidity));
  el.humidityGaugeFill.style.width = `${humidityPct}%`;
  el.humidityGaugeMarker.style.left = `${humidityPct}%`;

  // --- Water reservoir ---
  const tankLevel = Math.max(0, Math.min(100, data.water_tank_level));
  const tankTier = classifyTankLevel(data.water_tank_level);
  el.tankCard.dataset.level = tankTier;
  el.tankFill.style.height = `${tankLevel}%`;
  el.tankValue.textContent = formatNumber(data.water_tank_level, 1);
  el.tankNote.textContent =
    tankTier === "critical"
      ? "Critical — below safety threshold"
      : tankTier === "low"
      ? "Running low"
      : "Reservoir healthy";

  // --- AI recommendation ---
  const irrigationNeeded = data.ml_recommendation === 1;
  el.aiRecChip.textContent = irrigationNeeded
    ? "1 — Irrigation Needed"
    : "0 — Irrigation Not Needed";
  el.aiRecChip.dataset.tone = irrigationNeeded ? "positive" : "neutral";

  // --- System action ---
  el.actionChip.textContent = pumpOn ? "Pump ON" : "Pump OFF";
  el.actionChip.dataset.tone = pumpOn ? "on" : "off";

  // --- Reason ---
  el.reasonText.textContent = data.override_reason || "—";
  el.reasonText.dataset.tone = data.safety_override ? "critical" : "normal";

  // --- Safety alert vs. normal indicator ---
  if (data.safety_override) {
    el.safetyAlert.hidden = false;
    el.safetyNormal.hidden = true;
    el.safetyReasonText.textContent = data.override_reason || "Safety override active";
  } else {
    el.safetyAlert.hidden = true;
    el.safetyNormal.hidden = false;
  }

  // --- Secondary sensors ---
  const lightPct = Math.max(0, Math.min(100, (data.light / LIGHT_MAX) * 100));
  el.lightBar.style.width = `${lightPct}%`;
  el.lightValue.textContent = `${data.light}`;

  const dropRate = data.moisture_drop_rate;
  const dropSign = dropRate > 0 ? "+" : "";
  el.dropRateValue.textContent = `${dropSign}${formatNumber(dropRate, 3)}`;

  el.timeSinceValue.textContent = formatTimeSinceIrrigation(data.time_since_irrigation);
}

function showLoadingState(isLoading) {
  el.loadingBanner.hidden = !isLoading;
}

function showOfflineWarning(isOffline) {
  el.offlineBanner.hidden = !isOffline;
}

// ------------------------------------------------------------------------
// Polling loop
// ------------------------------------------------------------------------

async function fetchDashboardData() {
  try {
    const response = await fetch(API_URL, { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();

    setConnectionState("online");
    showOfflineWarning(false);
    renderDashboard(data);

    hasReceivedFirstReading = true;
    lastSuccessfulFetchAt = new Date();
    showLoadingState(false);
  } catch (err) {
    setConnectionState("offline");
    // Only show the "unable to connect" warning once we've actually tried;
    // keep whatever values were last rendered on screen.
    if (hasReceivedFirstReading) {
      showOfflineWarning(true);
    }
  }
}

function tickLastUpdatedLabel() {
  el.lastUpdated.textContent = secondsAgoLabel(lastSuccessfulFetchAt);
}

// Initial state
setConnectionState("loading");
showLoadingState(true);

// Kick off polling immediately, then every 3 seconds.
fetchDashboardData();
setInterval(fetchDashboardData, POLL_INTERVAL_MS);

// Update the "last updated Xs ago" label every second, independent of fetches.
setInterval(tickLastUpdatedLabel, 1000);