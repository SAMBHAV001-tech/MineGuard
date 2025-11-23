import os
import requests
from typing import Optional
import datetime
from dotenv import load_dotenv

# ---------- Load Environment Variables ----------
load_dotenv()

# Pull API key from environment (.env) or fallback (not recommended for production)
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "696253a0d17b6f0775f5bd8a01d5dd95")

# ---------- NASA POWER (No API Key Needed) ----------
POWER_URL_TEMPLATE = (
    "https://power.larc.nasa.gov/api/temporal/daily/point"
    "?parameters={params}&community=AG&longitude={lon}&latitude={lat}&start={start}&end={end}&format=JSON"
)

def fetch_nasa_power(lat: float, lon: float, params: str = "T2M,PRECTOTCORR,WS10M", days: int = 7) -> dict:
    """
    Fetch daily weather data (temperature, precipitation, wind speed, etc.)
    from NASA POWER API for the last `days`.
    """
    end = datetime.date.today()
    start = end - datetime.timedelta(days=days)
    start_str = start.strftime("%Y%m%d")
    end_str = end.strftime("%Y%m%d")

    url = POWER_URL_TEMPLATE.format(params=params, lon=lon, lat=lat, start=start_str, end=end_str)
    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print("❌ Exception in fetch_nasa_power:", e)
        return {}


# ---------- OpenWeatherMap ----------
OWM_CURRENT_URL = "https://api.openweathermap.org/data/2.5/weather"

def fetch_openweather(lat: float, lon: float) -> Optional[dict]:
    """
    Fetch current weather data from OpenWeatherMap.
    Normalizes output to a minimal dictionary.
    """
    if not OPENWEATHER_API_KEY:
        print("❌ No OpenWeather API key found")
        return None

    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric",
    }

    try:
        r = requests.get(OWM_CURRENT_URL, params=params, timeout=10)
        if r.status_code != 200:
            print("❌ OpenWeather request failed:", r.text)
            return None

        data = r.json()
        return {
            "temp": data.get("main", {}).get("temp"),
            "humidity": data.get("main", {}).get("humidity"),
            "rain_1h": data.get("rain", {}).get("1h", 0),
            "wind_speed": data.get("wind", {}).get("speed", 0),
        }
    except Exception as e:
        print("❌ Exception in fetch_openweather:", e)
        return None
