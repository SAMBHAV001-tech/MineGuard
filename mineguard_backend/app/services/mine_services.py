# app/services/mine_services.py
import os
import rasterio
from app.services.dem import get_elevation_at, compute_local_slope_degrees

# Where your .tif files live
DATA_DIR = os.path.join(os.path.dirname(__file__), "../data")

# 👇 You can mix & match:
# - Either provide lat/lon directly
# - Or provide a tif filename (the code will use its center)
MINE_MAP = {
    "rourkela": {"tif": "n22_e078_1arc_v3.tif"},  # will read center of tif
    "mine_b": {"lat": 15.3, "lon": 76.2},          # direct lat/lon
    "mine_c": {"lat": 21.5, "lon": 83.1},
    # add more as you have them
}

def get_mine_data(name: str):
    """
    Return lat/lon, elevation and slope for a named mine.
    Will use tif center if 'tif' key is present, otherwise lat/lon.
    """
    key = name.lower()
    mine = MINE_MAP.get(key)
    if not mine:
        return {"error": f"{name} not configured in MINE_MAP"}

    # determine lat/lon
    if "tif" in mine:
        tif_file = os.path.join(DATA_DIR, mine["tif"])
        if not os.path.exists(tif_file):
            return {"error": f"TIF file not found for {name}"}
        with rasterio.open(tif_file) as src:
            bounds = src.bounds
            lon = (bounds.left + bounds.right) / 2
            lat = (bounds.top + bounds.bottom) / 2
    else:
        lat = mine["lat"]
        lon = mine["lon"]

    elevation = get_elevation_at(lat, lon)
    slope = compute_local_slope_degrees(lat, lon)

    return {
        "name": name,
        "lat": lat,
        "lon": lon,
        "elevation_m": elevation,
        "slope_deg": slope
    }
