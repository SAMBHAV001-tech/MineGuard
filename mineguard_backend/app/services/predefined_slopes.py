# app/services/predefined_slopes.py

PREDEFINED_SLOPES = {
    # ---- Indian mines ----
    (22.5, 78.5): 12.0,  # Madhya Pradesh
    (22.5, 82.5): 18.0,  # Chhattisgarh
    (22.5, 84.5): 22.0,  # Odisha (bauxite/iron ore hills)
    (22.5, 85.5): 25.0,  # Odisha/Jharkhand
    (23.0, 86.5): 28.0,  # Jharia coalfield
    (24.0, 82.5): 15.0,  # MP/Jharkhand border
    (15.5, 76.5): 20.0,  # Karnataka (Bellary iron ore mines)

    # ---- Global mines ----
    (37.5, -81.5): 20.0, # West Virginia coal mines
    (51.5, 7.5): 10.0,   # Ruhr Valley Germany
    (-26.5, 27.5): 30.0, # South Africa gold mines
}

def get_slope(lat: float, lon: float) -> float:
    """
    Return predefined slope for a lat/lon if found,
    else return a safe default (15°).
    """
    key = (round(lat, 1), round(lon, 1))
    return PREDEFINED_SLOPES.get(key, 15.0)  # fallback slope
