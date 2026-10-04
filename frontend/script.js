const DASHBOARD_API =
  "http://127.0.0.1:8000/api/dashboard";

const WEATHER_API =
  "http://127.0.0.1:8000/api/weather";

const POLL_MS = 3000;

const WEATHER_POLL_MS =
  10 * 60 * 1000;


// ============================================================
// DOM HELPER
// ============================================================

const $ = (id) =>
  document.getElementById(id);


// ============================================================
// DOM REFERENCES
// ============================================================

const el = {

  connPill: $("connPill"),
  connDot: $("connDot"),
  connLabel: $("connLabel"),
  lastUpdated: $("lastUpdated"),

  loading: $("loadingBanner"),
  offline: $("offlineBanner"),

  hero: $("decisionHero"),
  title: $("decisionTitle"),
  description: $("decisionDescription"),
  mark: $("decisionMark"),

  mlTag: $("mlTag"),
  weatherTag: $("weatherTag"),
  tankTag: $("tankTag"),

  pumpOrb: $("pumpOrb"),
  pumpStatus: $("pumpStatusText"),
  pumpSub: $("pumpSubText"),
  pumpCommand: $("pumpCommand"),
  overrideState: $("overrideState"),

  weatherIcon: $("weatherIcon"),
  weatherHeadline: $("weatherHeadline"),
  weatherDetail: $("weatherDetail"),
  rainProbability: $("rainProbability"),
  rainAmount: $("rainAmount"),
  forecastStrip: $("forecastStrip"),

  soil: $("soilValue"),
  soilBar: $("soilBar"),
  soilNote: $("soilNote"),

  temp: $("tempValue"),
  tempBar: $("tempBar"),

  humidity: $("humidityValue"),
  humidityBar: $("humidityBar"),

  tank: $("tankValue"),
  tankBar: $("tankBar"),
  tankNote: $("tankNote"),

  ai: $("aiRecommendation"),
  weatherDecision: $("weatherDecision"),
  finalAction: $("finalAction"),
  reason: $("reasonText"),

  light: $("lightValue"),
  drop: $("dropRateValue"),
  time: $("timeSinceValue"),
  safety: $("safetyValue")

};


// ============================================================
// RUNTIME STATE
// ============================================================

let hasData = false;

let lastUpdated = null;


// ============================================================
// HELPERS
// ============================================================

function num(value, fallback = null) {

  const n = Number(value);

  return Number.isFinite(n)
    ? n
    : fallback;
}


function clamp(value, min, max) {

  return Math.min(
    Math.max(value, min),
    max
  );

}


function setText(node, value) {

  if (node) {

    node.textContent = value;

  }

}


function formatTimeSince(minutes) {

  if (minutes == null) {

    return "--";

  }

  if (minutes < 60) {

    return `${Math.round(minutes)} min`;

  }

  return `${Math.floor(minutes / 60)}h ${
    Math.round(minutes % 60)
  }m`;

}


function setTag(
  node,
  text,
  tone = "neutral"
) {

  if (!node) return;

  node.textContent = text;

  node.className =
    `tag ${tone}`;

}


// ============================================================
// CONNECTION
// ============================================================

function connection(state) {

  if (!el.connPill) return;

  el.connPill.dataset.state =
    state;

  if (state === "online") {

    setText(
      el.connLabel,
      "SYSTEM ONLINE"
    );

  }

  else if (state === "offline") {

    setText(
      el.connLabel,
      "SYSTEM OFFLINE"
    );

  }

  else {

    setText(
      el.connLabel,
      "CONNECTING"
    );

  }

}


// ============================================================
// SOIL DESCRIPTION
// ============================================================

function soilLabel(value) {

  if (value < 20) {

    return "Critically dry";

  }

  if (value < 40) {

    return "Dry";

  }

  if (value <= 70) {

    return "Optimal range";

  }

  return "Moist / wet";

}


// ============================================================
// WEATHER ICON
// ============================================================

function weatherIcon(code) {

  if (code == null) {

    return "☁";

  }

  if (code >= 95) {

    return "⛈";

  }

  if (code >= 80) {

    return "🌦";

  }

  if (code >= 61) {

    return "🌧";

  }

  if (code >= 51) {

    return "🌦";

  }

  if (code >= 45) {

    return "☁";

  }

  if (code >= 1) {

    return "🌤";

  }

  return "☀";

}


// ============================================================
// DASHBOARD RENDER
// ============================================================

function renderDashboard(data) {

  if (
    !data ||
    typeof data !== "object"
  ) {

    return;

  }


  hasData = true;

  el.loading.hidden = true;

  el.offline.hidden = true;

  connection("online");

  lastUpdated = new Date();


  // ----------------------------------------------------------
  // PUMP
  // ----------------------------------------------------------

  const pump =
    String(
      data.pump_status ??
      data.pump_command ??
      "OFF"
    ).toUpperCase() === "ON";


  // ----------------------------------------------------------
  // ML
  // ----------------------------------------------------------

  const ml =
    num(
      data.ml_recommendation ??
      data.ml_prediction,
      0
    ) === 1;


  // ----------------------------------------------------------
  // SAFETY
  // ----------------------------------------------------------

  const safety =
    data.safety_override === true;


  // ----------------------------------------------------------
  // WEATHER OVERRIDE
  // ----------------------------------------------------------

  const weatherOverride =
    data.weather_override === true;


  // ----------------------------------------------------------
  // WEATHER
  // ----------------------------------------------------------

  const rainProb =
    num(
      data.rain_probability,
      0
    );


  const rainAmount =
    num(
      data.rain_amount,
      0
    );


  // ----------------------------------------------------------
  // WATER TANK
  // ----------------------------------------------------------

  const tank =
    clamp(
      num(
        data.water_tank_level ??
        data.water_level,
        0
      ),
      0,
      100
    );


  // ----------------------------------------------------------
  // BACKEND REASON
  // ----------------------------------------------------------

  const reason =
    data.override_reason ??
    data.reason ??
    "No decision reason available";


  // ==========================================================
  // DETERMINE HERO STATE
  // ==========================================================

  let state = "standby";


  if (safety) {

    state = "safety";

  }

  else if (weatherOverride) {

    state = "weather";

  }

  else if (pump) {

    state = "active";

  }


  el.hero.dataset.state =
    state;


  el.pumpOrb.dataset.state =
    pump
      ? "on"
      : "off";


  // ==========================================================
  // HERO CONTENT
  // ==========================================================

  if (safety) {

    setText(
      el.title,
      "Irrigation locked for safety"
    );

    setText(
      el.description,
      "The AI requested irrigation, but the reservoir is below the safe operating threshold."
    );

    setText(
      el.mark,
      "!"
    );

  }

  else if (weatherOverride) {

    setText(
      el.title,
      "Irrigation postponed"
    );

    setText(
      el.description,
      "Rain is expected soon, so the system is conserving water instead of starting a watering cycle."
    );

    setText(
      el.mark,
      "☂"
    );

  }

  else if (pump) {

    setText(
      el.title,
      "Irrigation active"
    );

    setText(
      el.description,
      "The AI recommends watering and no immediate weather or safety condition is blocking the cycle."
    );

    setText(
      el.mark,
      "⌁"
    );

  }

  else {

    setText(
      el.title,
      "Irrigation not required"
    );

    setText(
      el.description,
      "Current field conditions do not require the pump to run."
    );

    setText(
      el.mark,
      "✓"
    );

  }


  // ==========================================================
  // DECISION TAGS
  // ==========================================================

  setTag(
    el.mlTag,

    ml
      ? "AI · Irrigation needed"
      : "AI · No irrigation",

    ml
      ? "positive"
      : "neutral"
  );


  setTag(
    el.weatherTag,

    weatherOverride
      ? `Rain · ${rainProb}%`
      : `Weather · ${rainProb}%`,

    weatherOverride
      ? "warning"
      : "neutral"
  );


  setTag(

    el.tankTag,

    tank < 15
      ? "Tank · Critical"
      : tank < 35
        ? "Tank · Low"
        : "Tank · Healthy",

    tank < 15
      ? "danger"
      : tank < 35
        ? "warning"
        : "positive"

  );


  // ==========================================================
  // PUMP CARD
  // ==========================================================

  setText(
    el.pumpStatus,
    pump
      ? "Running"
      : "Standby"
  );


  setText(

    el.pumpSub,

    pump
      ? "Pump command is ON"

      : safety
        ? "Blocked by tank safety"

        : weatherOverride
          ? "Waiting for safer weather window"

          : "No watering cycle active"

  );


  setText(
    el.pumpCommand,
    pump
      ? "ON"
      : "OFF"
  );


  setText(

    el.overrideState,

    safety
      ? "Safety"
      : weatherOverride
        ? "Weather"
        : "None"

  );


  // ==========================================================
  // SOIL
  // ==========================================================

  const soil =
    num(data.soil_moisture);


  if (soil != null) {

    setText(
      el.soil,
      soil.toFixed(1)
    );

    el.soilBar.style.width =
      `${clamp(soil, 0, 100)}%`;

    setText(
      el.soilNote,
      soilLabel(soil)
    );

  }


  // ==========================================================
  // TEMPERATURE
  // ==========================================================

  const temperature =
    num(data.temperature);


  if (temperature != null) {

    setText(
      el.temp,
      temperature.toFixed(1)
    );

    const percentage =
      clamp(
        ((temperature - 15) / 30) * 100,
        0,
        100
      );

    el.tempBar.style.width =
      `${percentage}%`;

  }


  // ==========================================================
  // HUMIDITY
  // ==========================================================

  const humidity =
    num(data.humidity);


  if (humidity != null) {

    setText(
      el.humidity,
      humidity.toFixed(1)
    );

    el.humidityBar.style.width =
      `${clamp(humidity, 0, 100)}%`;

  }


  // ==========================================================
  // WATER TANK
  // ==========================================================

  setText(
    el.tank,
    tank.toFixed(1)
  );

  el.tankBar.style.width =
    `${tank}%`;


  setText(

    el.tankNote,

    tank < 15

      ? "Critical — pump protection active"

      : tank < 35
        ? "Running low"
        : "Reservoir healthy"

  );


  // ==========================================================
  // DECISION TRACE
  // ==========================================================

  setText(

    el.ai,

    ml
      ? "Irrigation needed"
      : "Irrigation not needed"

  );


  setText(

    el.weatherDecision,

    weatherOverride
      ? `Postponed · ${rainProb}% rain`
      : `Clear gate · ${rainProb}% rain`

  );


  setText(

    el.finalAction,

    pump
      ? "Pump ON"
      : "Pump OFF"

  );


  setText(
    el.reason,
    reason
  );


  // ==========================================================
  // SECONDARY CONTEXT
  // ==========================================================

  setText(

    el.light,

    data.light == null
      ? "--"
      : Math.round(
          Number(data.light)
        )

  );


  const drop =
    num(
      data.moisture_drop_rate
    );


  setText(

    el.drop,

    drop == null
      ? "--"
      : `${drop > 0 ? "+" : ""}${drop.toFixed(3)}`

  );


  setText(

    el.time,

    formatTimeSince(
      num(
        data.time_since_irrigation
      )
    )

  );


  setText(

    el.safety,

    safety
      ? "ACTIVE"
      : "Normal"

  );

}


// ============================================================
// WEATHER RENDER
// ============================================================

function renderWeather(data) {

  if (!data?.hourly) {

    return;

  }


  const hourly =
    data.hourly;


  const times =
    hourly.time || [];


  const probabilities =
    hourly.precipitation_probability || [];


  const rain =
    hourly.rain || [];


  const codes =
    hourly.weather_code || [];


  const probability =
    num(
      probabilities[0],
      0
    );


  const rainAmount =
    num(
      rain[0],
      0
    );


  // ==========================================================
  // CURRENT WEATHER
  // ==========================================================

  setText(
    el.rainProbability,
    `${Math.round(probability)}%`
  );


  setText(
    el.rainAmount,
    `${rainAmount.toFixed(1)} mm`
  );


  setText(
    el.weatherIcon,
    weatherIcon(codes[0])
  );


  if (
    probability >= 60 &&
    rainAmount >= 0.1
  ) {

    setText(
      el.weatherHeadline,
      "Rain expected soon"
    );

  }

  else {

    setText(
      el.weatherHeadline,
      "No significant rain expected"
    );

  }


  setText(

    el.weatherDetail,

    `${Math.round(probability)}% probability · ${rainAmount.toFixed(1)} mm in the immediate forecast hour`

  );


  // ==========================================================
  // FORECAST STRIP
  // ==========================================================

  el.forecastStrip.innerHTML = "";


  times
    .slice(0, 6)
    .forEach(
      (time, index) => {

        const date =
          new Date(time);


        const hour =
          date.toLocaleTimeString(
            [],
            {
              hour: "2-digit",
              minute: "2-digit"
            }
          );


        const probabilityValue =
          num(
            probabilities[index],
            0
          );


        const rainValue =
          num(
            rain[index],
            0
          );


        const item =
          document.createElement(
            "div"
          );


        item.className =
          "forecast-item";


        item.innerHTML = `

          <span>${hour}</span>

          <b>
            ${Math.round(
              probabilityValue
            )}%
          </b>

          <small>
            ${rainValue.toFixed(1)} mm
          </small>

        `;


        el.forecastStrip
          .appendChild(item);

      }
    );

}


// ============================================================
// FETCH DASHBOARD
// ============================================================

async function fetchDashboard() {

  try {

    const response =
      await fetch(
        `${DASHBOARD_API}?t=${Date.now()}`,
        {
          cache: "no-store"
        }
      );


    if (!response.ok) {

      throw new Error(
        `HTTP ${response.status}`
      );

    }


    const data =
      await response.json();


    renderDashboard(data);

  }

  catch (error) {

    console.error(
      "Dashboard API error:",
      error
    );


    connection("offline");


    if (hasData) {

      el.offline.hidden =
        false;

    }

  }

}


// ============================================================
// FETCH WEATHER
// ============================================================

async function fetchWeather() {

  try {

    const response =
      await fetch(
        `${WEATHER_API}?t=${Date.now()}`,
        {
          cache: "no-store"
        }
      );


    if (!response.ok) {

      throw new Error(
        `HTTP ${response.status}`
      );

    }


    const data =
      await response.json();


    renderWeather(data);

  }

  catch (error) {

    console.error(
      "Weather API error:",
      error
    );


    setText(
      el.weatherHeadline,
      "Weather unavailable"
    );


    setText(
      el.weatherDetail,
      "The dashboard will continue using the backend decision state."
    );

  }

}


// ============================================================
// LAST UPDATED
// ============================================================

function tick() {

  if (!el.lastUpdated) {

    return;

  }


  if (!lastUpdated) {

    el.lastUpdated.textContent =
      "Waiting for first reading…";

    return;

  }


  const seconds =
    Math.max(
      0,
      Math.round(
        (
          Date.now() -
          lastUpdated.getTime()
        ) / 1000
      )
    );


  el.lastUpdated.textContent =
    `Last updated: ${seconds}s ago`;

}


// ============================================================
// INITIALIZE
// ============================================================

connection("loading");

el.loading.hidden = false;

fetchDashboard();

fetchWeather();


// Dashboard every 3 seconds

setInterval(
  fetchDashboard,
  POLL_MS
);


// Weather every 10 minutes

setInterval(
  fetchWeather,
  WEATHER_POLL_MS
);


// Update timestamp every second

setInterval(
  tick,
  1000
);