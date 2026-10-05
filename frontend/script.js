const DASHBOARD_API =
  "http://127.0.0.1:8000/api/dashboard";

const WEATHER_API =
  "http://127.0.0.1:8000/api/weather";

const POLL_MS = 3000;
const WEATHER_POLL_MS = 10 * 60 * 1000;


// ===============================
// ELEMENTS
// ===============================

const connDot = document.getElementById("connDot");
const connLabel = document.getElementById("connLabel");

const decisionTitle =
  document.getElementById("decisionTitle");

const decisionDescription =
  document.getElementById("decisionDescription");

const mlTag =
  document.getElementById("mlTag");

const weatherTag =
  document.getElementById("weatherTag");

const soilValue =
  document.getElementById("soilValue");

const tempValue =
  document.getElementById("tempValue");

const humidityValue =
  document.getElementById("humidityValue");

const lightValue =
  document.getElementById("lightValue");

const lightContext =
  document.getElementById("lightContext");

const aiRecommendation =
  document.getElementById("aiRecommendation");

const weatherDecision =
  document.getElementById("weatherDecision");

const finalDecision =
  document.getElementById("finalDecision");

const reasonText =
  document.getElementById("reasonText");

const dropRateValue =
  document.getElementById("dropRateValue");

const timeSinceValue =
  document.getElementById("timeSinceValue");

const weatherHeadline =
  document.getElementById("weatherHeadline");

const weatherDetail =
  document.getElementById("weatherDetail");

const rainProbability =
  document.getElementById("rainProbability");

const rainAmount =
  document.getElementById("rainAmount");

const nextRain =
  document.getElementById("nextRain");

const forecastStrip =
  document.getElementById("forecastStrip");


// ===============================
// CONNECTION STATUS
// ===============================

function setConnected(connected) {

  connLabel.textContent =
    connected
      ? "System Online"
      : "Connecting";

  connDot.className =
    connected
      ? "connected"
      : "";

}


// ===============================
// DASHBOARD
// ===============================

async function fetchDashboard() {

  try {

    const response = await fetch(
      DASHBOARD_API,
      {
        cache: "no-store"
      }
    );

    if (!response.ok) {
      throw new Error("Dashboard error");
    }

    const data =
      await response.json();

    const telemetry =
      data.latest_telemetry || data;


    // ===========================
    // SENSOR VALUES
    // ===========================

    const soil =
      Number(
        telemetry.soil_moisture ?? 0
      );

    const temperature =
      Number(
        telemetry.temperature ?? 0
      );

    const humidity =
      Number(
        telemetry.humidity ?? 0
      );

    const light =
      telemetry.light ?? 0;

    const dropRate =
      Number(
        telemetry.moisture_drop_rate ?? 0
      );

    const timeSince =
      Number(
        telemetry.time_since_irrigation ?? 0
      );


    // ===========================
    // DISPLAY SENSOR VALUES
    // ===========================

    soilValue.textContent =
      soil.toFixed(1);

    tempValue.textContent =
      temperature.toFixed(1);

    humidityValue.textContent =
      humidity.toFixed(1);


    // ===========================
    // LIGHT
    // ===========================

    const lightText =
      Number(light) === 1
        ? "Good / Ample"
        : "Low";

    lightValue.textContent =
      lightText;

    lightContext.textContent =
      lightText;


    // ===========================
    // FIELD BEHAVIOUR
    // ===========================

    dropRateValue.textContent =
      dropRate.toFixed(2);

    timeSinceValue.textContent =
      `${timeSince} min`;


    // ===========================
    // ML RECOMMENDATION
    // ===========================

    const ml =
      Number(
        telemetry.ml_recommendation ??
        telemetry.ml_prediction ??
        0
      );

    const irrigationNeeded =
      ml === 1;


    // ===========================
    // AI RECOMMENDATION
    // ===========================

    aiRecommendation.textContent =
      irrigationNeeded
        ? "Irrigation Needed"
        : "Irrigation Not Needed";


    mlTag.textContent =
      irrigationNeeded
        ? "AI: Irrigation Needed"
        : "AI: Irrigation Not Needed";


    // ===========================
    // WEATHER INFORMATION ONLY
    // ===========================

    const weatherBlocked =
      Boolean(
        telemetry.weather_override
      );

    if (weatherBlocked) {

      weatherDecision.textContent =
        "Rain expected";

      weatherTag.textContent =
        "Weather: Rain expected";

    } else {

      weatherDecision.textContent =
        "No immediate rain";

      weatherTag.textContent =
        "Weather: No immediate rain";
    }


    // ===========================
    // FINAL DECISION
    // DIRECTLY FROM ML
    // ===========================

    finalDecision.textContent =
      irrigationNeeded
        ? "Irrigation Needed"
        : "Irrigation Not Needed";


    decisionTitle.textContent =
      irrigationNeeded
        ? "Irrigation Needed"
        : "Irrigation Not Needed";


    decisionDescription.textContent =
      irrigationNeeded
        ? "The ML model recommends irrigation based on the current field conditions."
        : "The ML model does not recommend irrigation under the current field conditions.";


    // ===========================
    // REASON
    // ===========================

    reasonText.textContent =
      telemetry.reason ||
      (
        irrigationNeeded
          ? "The ML model recommends irrigation."
          : "The ML model does not recommend irrigation."
      );


    // ===========================
    // CONNECTION
    // ===========================

    setConnected(true);

  }

  catch (error) {

    console.error(
      "Dashboard error:",
      error
    );

    setConnected(false);

    decisionTitle.textContent =
      "Waiting for field data";

    decisionDescription.textContent =
      "Unable to receive live telemetry from the controller.";

  }

}


// ===============================
// WEATHER
// ===============================

async function fetchWeather() {

  try {

    const response =
      await fetch(
        WEATHER_API,
        {
          cache: "no-store"
        }
      );

    if (!response.ok) {
      throw new Error("Weather error");
    }

    const data =
      await response.json();

    if (!data.hourly) {
      return;
    }


    // ===========================
    // WEATHER DATA
    // ===========================

    const times =
      data.hourly.time || [];

    const probabilities =
      data.hourly.precipitation_probability || [];

    const rain =
      data.hourly.rain || [];

    const precipitation =
      data.hourly.precipitation || [];


    if (!times.length) {
      return;
    }


    // ===========================
    // NEXT HOUR
    // ===========================

    const probability =
      Number(
        probabilities[0] ?? 0
      );

    const rainAmountValue =
      Number(
        precipitation[0] ??
        rain[0] ??
        0
      );


    rainProbability.textContent =
      `${probability}%`;

    rainAmount.textContent =
      `${rainAmountValue.toFixed(1)} mm`;

    nextRain.textContent =
      `${probability}%`;


    // ===========================
    // WEATHER STATUS
    // ===========================

    if (probability >= 60) {

      weatherHeadline.textContent =
        "Rain expected soon";

      weatherDetail.textContent =
        `${probability}% chance of rain in the immediate forecast hour.`;

    } else {

      weatherHeadline.textContent =
        "No significant rain expected";

      weatherDetail.textContent =
        `${probability}% chance of rain in the immediate forecast hour.`;
    }


    // ===========================
    // FORECAST STRIP
    // ===========================

    forecastStrip.innerHTML = "";

    const count =
      Math.min(
        6,
        times.length
      );


    for (
      let i = 0;
      i < count;
      i++
    ) {

      const time =
        new Date(times[i]);

      const hour =
        time.toLocaleTimeString(
          [],
          {
            hour: "2-digit",
            minute: "2-digit"
          }
        );

      const prob =
        Number(
          probabilities[i] ?? 0
        );

      const amount =
        Number(
          precipitation[i] ??
          rain[i] ??
          0
        );


      const item =
        document.createElement("div");

      item.className =
        "forecast-item";


      item.innerHTML = `
        <small>${hour}</small>
        <strong>${prob}%</strong>
        <span>${amount.toFixed(1)} mm</span>
      `;


      forecastStrip.appendChild(
        item
      );
    }

  }

  catch (error) {

    console.error(
      "Weather error:",
      error
    );

    weatherHeadline.textContent =
      "Weather unavailable";

  }

}


// ===============================
// START
// ===============================

fetchDashboard();

fetchWeather();


setInterval(
  fetchDashboard,
  POLL_MS
);


setInterval(
  fetchWeather,
  WEATHER_POLL_MS
);