# app/main.py
from fastapi import FastAPI, Request
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import uvicorn
import yaml
import os

from app.services.weather import fetch_nasa_power, fetch_openweather
from app.services.dem import get_elevation_at
from app.services.sensors_mqtt import start_mqtt_client, get_latest_sensor_state
from app.models.predictor import predict as risk_score
from app.services.mine_services import get_mine_data
from app.services.predefined_slopes import get_slope

# ------------ APP ------------ #
app = FastAPI(
    title="MineGuard AI",
    description="Smart Rockfall Prediction & Safety System",
    version="1.0"
)

# Optional Swagger YAML loader
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    yaml_path = os.path.join(os.path.dirname(__file__), "swagger.yaml")
    if os.path.exists(yaml_path):
        with open(yaml_path, "r") as f:
            spec = yaml.safe_load(f)
        app.openapi_schema = spec
        return app.openapi_schema
    else:
        return get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )

app.openapi = custom_openapi

# ------------ CORS ------------ #
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*", 
        "https://mine-guard-theta.vercel.app",
      ],  # allow all during testing; restrict later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------ ROUTES ------------ #
@app.get("/")
async def root():
    return {"message": "MineGuard AI Backend running 🚀"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/weather/{lat}/{lon}")
async def weather(lat: float, lon: float):
    """Fetch combined weather data and return normalized fields."""
    nasa_data = fetch_nasa_power(lat, lon)
    owm_data = fetch_openweather(lat, lon)

    temperature = None
    humidity = None
    rainfall = None
    wind_speed = None

    # ---- Step 1: Prefer OpenWeather if available
    if owm_data:
        temperature = owm_data.get("temp")
        humidity = owm_data.get("humidity")

        # ✅ FIX: Handle multiple rain formats safely
        rain_data = owm_data.get("rain", {})
        if isinstance(rain_data, dict):
            rainfall = rain_data.get("1h") or (rain_data.get("3h", 0) / 3 if rain_data.get("3h") else 0)
        else:
            rainfall = 0

        # If still no rain info, fallback to 0.0
        rainfall = rainfall or 0.0
        wind_speed = owm_data.get("wind_speed")

    # ---- Step 2: NASA fallback if OpenWeather missing
    else:
        try:
            t2m = nasa_data["properties"]["parameter"].get("T2M", {})
            prect = nasa_data["properties"]["parameter"].get("PRECTOTCORR", {})
            ws = nasa_data["properties"]["parameter"].get("WS10M", {})

            if t2m:
                temperature = list(t2m.values())[-1]
            if prect:
                rainfall = list(prect.values())[-1]
            if ws:
                wind_speed = list(ws.values())[-1]
        except Exception:
            pass

    # ---- Step 3: Normalize values
    def as_number(v):
        try:
            return float(v) if v is not None else None
        except Exception:
            return None

    temperature = as_number(temperature)
    humidity = as_number(humidity)
    rainfall = as_number(rainfall)
    wind_speed = as_number(wind_speed)

    # ---- Step 4: Return normalized result
    return {
        "nasa_power": nasa_data,
        "openweather": owm_data,
        "summary": {
            "temperature": temperature,
            "humidity": humidity,
            "rainfall": rainfall,
            "wind_speed": wind_speed
        }
    }


@app.get("/srtm/{lat}/{lon}")
async def elevation(lat: float, lon: float):
    elev = get_elevation_at(lat, lon)
    slope = get_slope(lat, lon)
    return {"lat": lat, "lon": lon, "elevation_m": elev, "slope_deg": slope}

@app.on_event("startup")
async def startup_event():
    print("🚀 Starting MQTT client from FastAPI...")
    start_mqtt_client()

@app.get("/sensors/vibration")
async def vibration():
    state = get_latest_sensor_state()
    vib = state.get("vibration")
    try:
        vib_n = float(vib) if vib is not None else 0.0
    except Exception:
        vib_n = 0.0
    return {"vibration": vib_n}

@app.post("/predict")
async def predict(request: Request):
    """
    Robust predict endpoint.

    Behavior:
    - Accepts `{ "lat": ..., "lon": ... }` or `{ "latitude": ..., "longitude": ... }`.
    - Accepts optional features in the body and falls back to live weather or sensible defaults.
    - Uses demo_overrides for specific rounded coordinates (presentation/test).
    - Returns JSONResponse with features, prediction, and alert.
    """

    # 1) parse JSON safely
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON body"}, status_code=400)

    # 2) accept multiple coordinate key names
    lat = body.get("lat", body.get("latitude"))
    lon = body.get("lon", body.get("longitude"))

    # validate coords presence
    if lat is None or lon is None:
        return JSONResponse({"error": "Please provide 'lat' and 'lon' (or 'latitude' and 'longitude') in request body."}, status_code=400)

    # convert to floats safely
    try:
        lat = float(lat)
        lon = float(lon)
    except Exception:
        return JSONResponse({"error": "Latitude and longitude must be numeric"}, status_code=400)

    # 3) Try fetching live weather (protect against failures)
    weather_data = {}
    try:
        wd = fetch_openweather(lat, lon)
        if isinstance(wd, dict):
            weather_data = wd
    except Exception as e:
        # non-fatal: log and continue with defaults
        print("[PREDICT] fetch_openweather failed:", e)

    # small helper to coerce to float with fallback
    def _to_float(v, default=0.0):
        try:
            if v is None:
                return float(default)
            return float(v)
        except Exception:
            return float(default)

    # 4) build base feature set using body -> live weather -> defaults
    features = {
        "slope": body.get("slope"),  # try request first (may be None)
        "rainfall": body.get("rainfall", weather_data.get("rain_1h", body.get("rain", 10.0))),
        "temperature": body.get("temperature", weather_data.get("temp", 25.0)),
        "vibration": body.get("vibration", None),  # fill from sensors later if None
        "wind_speed": body.get("wind_speed", weather_data.get("wind_speed", 2.0)),
        "displacement_rate": body.get("displacement_rate", None)  # may compute later
    }

    # 5) demo overrides for presentation (rounded to 0.1 deg)
    demo_overrides = {
        (23.0, 86.5): {  # Jharia - force HIGH for demo
            "slope": 50,
            "rainfall": 70,
            "temperature": 35,
            "vibration": 3.5,
            "wind_speed": 10.0,
            "displacement_rate": 0.5
        },
        (22.3, 84.8): {  # Talcher - MODERATE
            "slope": 35,
            "rainfall": 40,
            "temperature": 30,
            "vibration": 1.5,
            "wind_speed": 6.0,
            "displacement_rate": 0.3
        },
        (23.8, 85.0): {  # Dhanbad - LOW
            "slope": 15,
            "rainfall": 10,
            "temperature": 25,
            "vibration": 0.2,
            "wind_speed": 2.0,
            "displacement_rate": 0.1
        }
    }

    # create demo key safely
    demo_key = (round(lat, 1), round(lon, 1))
    if demo_key in demo_overrides:
        features = demo_overrides[demo_key]
        print(f"[PREDICT] Using demo override for {demo_key}: {features}")
    else:
        # 6) If slope not supplied, try predefined lookup (get_slope) then fallback to default
        if features.get("slope") is None:
            try:
                slope_lookup = get_slope(lat, lon)
                if slope_lookup is not None:
                    features["slope"] = slope_lookup
                else:
                    features["slope"] = 30.0
            except Exception as e:
                print("[PREDICT] get_slope failed:", e)
                features["slope"] = 30.0

        # 7) If vibration not supplied, try latest sensor state
        if features.get("vibration") is None:
            try:
                sensor_state = get_latest_sensor_state()
                features["vibration"] = sensor_state.get("vibration", 0.0)
            except Exception as e:
                print("[PREDICT] get_latest_sensor_state failed:", e)
                features["vibration"] = 0.0

        # 8) compute displacement_rate if still missing (derive from slope as simple heuristic)
        if features.get("displacement_rate") is None:
            try:
                # If client provided 'displacement' use that; else derive from slope (1% per degree)
                disp = body.get("displacement")
                if disp is not None:
                    features["displacement_rate"] = float(disp)
                else:
                    features["displacement_rate"] = max(0.01, 0.01 * _to_float(features["slope"], 30.0))
            except Exception:
                features["displacement_rate"] = 0.01

    # 9) Coerce all features to numeric types (predictor expects numeric)
    features = {
        "rainfall": _to_float(features.get("rainfall", 10.0), 10.0),
        "temperature": _to_float(features.get("temperature", 25.0), 25.0),
        "slope": _to_float(features.get("slope", 30.0), 30.0),
        "wind_speed": _to_float(features.get("wind_speed", 2.0), 2.0),
        "displacement_rate": _to_float(features.get("displacement_rate", 0.01), 0.01),
        "vibration": _to_float(features.get("vibration", 0.0), 0.0)
    }

    print(f"[PREDICT] Final features: {features}")

    # 10) Run the model safely
    try:
        result = risk_score(features)
    except RuntimeError as re:
        print("[PREDICT] Model not loaded:", re)
        return JSONResponse({"error": "Model not loaded on server. Put trained model file in app/models and restart."}, status_code=503)
    except Exception as e:
        print("[PREDICT] Model prediction error:", e)
        return JSONResponse({"error": "Model prediction failed", "details": str(e)}, status_code=500)

    # 11) Normalize result to extract risk string and produce alert
    risk_level = ""
    try:
        if isinstance(result, dict):
            # try several possible keys
            risk_level = str(result.get("risk") or result.get("risk_level") or result.get("Risk") or "")
            prob = result.get("probability") or result.get("prob") or None
        else:
            risk_level = str(result)
            prob = None
    except Exception:
        risk_level = str(result)
        prob = None

    risk_level_l = risk_level.lower()

    if "high" in risk_level_l:
        alert = "⚠️ HIGH RISK of Rockfall detected! Immediate action required."
    elif "medium" in risk_level_l or "moderate" in risk_level_l:
        alert = "⚠️ MODERATE RISK — Monitor site closely."
    elif "low" in risk_level_l:
        alert = "✅ LOW RISK — Conditions stable."
    else:
        # fallback using probability if present
        try:
            p = float(prob) if prob is not None else None
            if p is not None:
                if p > 0.7:
                    alert = "⚠️ HIGH RISK of Rockfall detected! Immediate action required."
                elif p > 0.4:
                    alert = "⚠️ MODERATE RISK — Monitor site closely."
                else:
                    alert = "✅ LOW RISK — Conditions stable."
            else:
                alert = None
        except Exception:
            alert = None

    response = {
        "features": features,
        "prediction": result,
        "alert": alert
    }

    return JSONResponse(response, status_code=200)


@app.get("/mine/{name}")
async def mine(name: str):
    data = get_mine_data(name)
    if data is None:
        return {"error": f"No mine named '{name}' found"}
    return data

# ------------ LOCAL RUN ------------ #
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)





