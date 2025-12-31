"""Geospatial coordinate utilities."""
from pathlib import Path
from typing import Optional
import rasterio
from rasterio.transform import xy

def pixel_to_latlon(
    image_path: str, 
    pixel_x: int, 
    pixel_y: int
) -> Optional[tuple[float, float]]:
    """Convert pixel coordinates to lat/lon if image has CRS metadata."""
    try:
        with rasterio.open(image_path) as src:
            if src.crs is None:
                return None
            lon, lat = xy(src.transform, pixel_y, pixel_x)
            return (lat, lon)
    except Exception:
        return None

# Mock coordinates for demo (LAX airport area)
MOCK_CENTER = (33.9425, -118.4081)

def mock_geo_location() -> tuple[float, float]:
    """Return mock coordinates for testing."""
    import random
    lat = MOCK_CENTER[0] + random.uniform(-0.01, 0.01)
    lon = MOCK_CENTER[1] + random.uniform(-0.01, 0.01)
    return (lat, lon)
