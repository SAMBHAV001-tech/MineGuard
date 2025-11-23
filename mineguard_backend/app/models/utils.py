"""
utils.py
Helper functions for preprocessing and feature extraction
"""

def normalize(value, min_val, max_val):
    if max_val - min_val == 0:
        return 0
    return (value - min_val) / (max_val - min_val)

def compute_features(weather_data, slope, sensor_data):
    """
    weather_data: dict { 'rain', 'temperature', 'wind_speed' }
    slope: float (degrees)
    sensor_data: dict { 'displacement_rate', 'vibration' }
    """
    return {
        "rain": weather_data.get("rain", 0.0),
        "temperature": weather_data.get("temperature", 25.0),
        "slope": slope,
        "wind_speed": weather_data.get("wind_speed", 1.0),
        "displacement_rate": sensor_data.get("displacement_rate", 0.0),
        "vibration": sensor_data.get("vibration", 0.0)
    }