from dotenv import load_dotenv
import os


load_dotenv()


# OpenWeatherMap
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")


# SRTM GeoTIFF path (local)
SRTM_PATH = os.getenv("SRTM_PATH", "data/srtm_tile.tif")


# MQTT
MQTT_BROKER = os.getenv("MQTT_BROKER", "broker.hivemq.com")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "sih2025/mineguard/sensors")


# Prediction threshold for alerts
ALERT_THRESHOLD = float(os.getenv("ALERT_THRESHOLD", 0.7))


# Model path
MODEL_PATH = os.getenv("MODEL_PATH", "app/models/rockfall_model.pkl")