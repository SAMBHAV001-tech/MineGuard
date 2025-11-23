import os
import math
import rasterio
import requests
import math
import numpy as np
import rasterio.windows
from rasterio.enums import Resampling

# Path to local DEM data folder
DATA_DIR = os.path.join(os.path.dirname(__file__), "../data")  # adjust if needed

# ---------- Find Local DEM Tile ----------
def find_tile_for_latlon(lat: float, lon: float) -> str:
    """
    Try to find a local GeoTIFF DEM tile for the given lat/lon.
    Adjust tile naming convention as per your dataset.
    """
    tile_name = f"N{int(lat)}E{int(lon)}.tif"
    path = os.path.join(DATA_DIR, tile_name)
    if os.path.exists(path):
        return path
    raise FileNotFoundError(f"No local DEM tile found for lat={lat}, lon={lon}")

# ---------- Elevation ----------
def get_elevation_at(lat: float, lon: float) -> float:
    """
    Return elevation at given lat/lon.
    Tries local DEM first, then falls back to OpenTopoData API.
    """
    try:
        # Try local DEM first
        path = find_tile_for_latlon(lat, lon)
        with rasterio.open(path) as dem:
            row, col = dem.index(lon, lat)
            elevation = dem.read(1)[row, col]
        return float(elevation)
    except FileNotFoundError:
        # Fallback to online API
        print(f"No local DEM tile found, fetching online for lat={lat}, lon={lon}")
        url = f"https://api.opentopodata.org/v1/srtm90m?locations={lat},{lon}"
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            data = r.json()
            if "results" in data and len(data["results"]) > 0:
                return float(data["results"][0]["elevation"])
            else:
                print("❌ No elevation data in API response")
                return None
        except Exception as e:
            print("❌ Error fetching elevation from OpenTopoData:", e)
            return None

# ---------- Slope Calculation ----------
def compute_local_slope_degrees(lat: float, lon: float) -> float:
    """
    Compute slope at a point directly from local DEM using rasterio & numpy.
    Returns slope in degrees or None if no data.
    """
    try:
        path = find_tile_for_latlon(lat, lon)
    except FileNotFoundError:
        return None

    with rasterio.open(path) as dem:
        row, col = dem.index(lon, lat)
        window = rasterio.windows.Window(col_off=col-1, row_off=row-1, width=3, height=3)
        data = dem.read(1, window=window, resampling=Resampling.bilinear, boundless=True, fill_value=np.nan)

        nodata = dem.nodata
        if nodata is not None:
            data = np.where(data == nodata, np.nan, data)

        if np.isnan(data).sum() > 4:
            return None

        # pixel size in degrees
        xres_deg = dem.transform.a
        yres_deg = -dem.transform.e

        # convert to metres
        lat_rad = math.radians(lat)
        m_per_deg_lat = 111132.954 - 559.822 * math.cos(2*lat_rad) + 1.175 * math.cos(4*lat_rad)
        m_per_deg_lon = 111132.954 * math.cos(lat_rad)

        xres = xres_deg * m_per_deg_lon
        yres = yres_deg * m_per_deg_lat

        dzdx = ((data[0,2] + 2*data[1,2] + data[2,2]) - (data[0,0] + 2*data[1,0] + data[2,0])) / (8 * xres)
        dzdy = ((data[2,0] + 2*data[2,1] + data[2,2]) - (data[0,0] + 2*data[0,1] + data[0,2])) / (8 * yres)

        slope_rad = np.arctan(np.sqrt(dzdx**2 + dzdy**2))
        slope_deg = np.degrees(slope_rad)
        return float(slope_deg)



# ---------- Example Usage ----------
if __name__ == "__main__":
    lat, lon = 20.5, 85.8
    elevation = get_elevation_at(lat, lon)
    slope = compute_local_slope_degrees(lat, lon)
    print(f"Elevation at ({lat},{lon}): {elevation} m")
    print(f"Slope at ({lat},{lon}): {slope}°")