"""Behavioral analytics for track patterns."""
from ghost_sentry.core.track_state import get_positions
from shapely.geometry import Point
import logging

# Configuration for loitering detection
LOITER_THRESHOLD_M = 50  # Max distance in meters from centroid to be considered loitering
LOITER_MIN_SAMPLES = 5   # Minimum position samples required for analysis

def detect_loitering(entity_id: str) -> bool:
    """
    Detect if an entity is loitering (staying within a small area).
    Calculates centroid of recent positions and checks if all points are within threshold.
    """
    history = get_positions(entity_id)
    if len(history) < LOITER_MIN_SAMPLES:
        return False
        
    # Extract locations (lat, lon)
    points = [Point(loc) for _, loc in history]
    
    # Calculate centroid
    avg_lat = sum(p.x for p in points) / len(points)
    avg_lon = sum(p.y for p in points) / len(points)
    centroid = Point(avg_lat, avg_lon)
    
    # Check if all points are within threshold
    # 0.00001 degrees is approx 1.1 meters
    threshold_deg = LOITER_THRESHOLD_M / 111000.0
    
    is_loitering = all(p.distance(centroid) <= threshold_deg for p in points)
    
    if is_loitering:
        logging.info(f"Loitering behavior detected for entity: {entity_id}")
        
    return is_loitering

def detect_formation(tracks: list) -> list:
    """
    Placeholder for future formation detection logic.
    Identifies clusters of tracks moving in coordination.
    """
    return []
