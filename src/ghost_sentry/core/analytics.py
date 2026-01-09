"""Behavioral analytics for track patterns."""
from ghost_sentry.core.track_state import get_positions
from shapely.geometry import Point
from typing import List, Tuple
import logging

LOITER_THRESHOLD_M = 50
LOITER_MIN_SAMPLES = 5

FORMATION_RADIUS_M = 500
FORMATION_MIN_TRACKS = 3


def detect_loitering(entity_id: str) -> bool:
    history = get_positions(entity_id)
    if len(history) < LOITER_MIN_SAMPLES:
        return False
        
    points = [Point(loc) for _, loc in history]
    
    avg_lat = sum(p.x for p in points) / len(points)
    avg_lon = sum(p.y for p in points) / len(points)
    centroid = Point(avg_lat, avg_lon)
    
    threshold_deg = LOITER_THRESHOLD_M / 111000.0
    
    is_loitering = all(p.distance(centroid) <= threshold_deg for p in points)
    
    if is_loitering:
        logging.info(f"Loitering behavior detected for entity: {entity_id}")
        
    return is_loitering


def detect_formation(tracks: List[dict]) -> List[dict]:
    """
    Detect formation patterns - clusters of tracks moving together.
    
    Returns list of formation candidates with member entity IDs.
    """
    if len(tracks) < FORMATION_MIN_TRACKS:
        return []
    
    formations = []
    radius_deg = FORMATION_RADIUS_M / 111000.0
    
    track_points: List[Tuple[str, Point]] = []
    for track in tracks:
        try:
            loc = track.get("location", {}).get("position", {})
            lat = loc.get("latitudeDegrees", 0)
            lon = loc.get("longitudeDegrees", 0)
            entity_id = track.get("entityId", "unknown")
            track_points.append((entity_id, Point(lat, lon)))
        except (KeyError, TypeError):
            continue
    
    if len(track_points) < FORMATION_MIN_TRACKS:
        return []
    
    used_entities = set()
    
    for i, (entity_id, point) in enumerate(track_points):
        if entity_id in used_entities:
            continue
            
        cluster_members = [(entity_id, point)]
        
        for j, (other_id, other_point) in enumerate(track_points):
            if i == j or other_id in used_entities:
                continue
            if point.distance(other_point) <= radius_deg:
                cluster_members.append((other_id, other_point))
        
        if len(cluster_members) >= FORMATION_MIN_TRACKS:
            member_ids = [m[0] for m in cluster_members]
            centroid_lat = sum(m[1].x for m in cluster_members) / len(cluster_members)
            centroid_lon = sum(m[1].y for m in cluster_members) / len(cluster_members)
            
            formations.append({
                "type": "FORMATION",
                "member_count": len(member_ids),
                "entity_ids": member_ids,
                "centroid": (centroid_lat, centroid_lon)
            })
            
            used_entities.update(member_ids)
            logging.info(f"Formation detected: {len(member_ids)} entities at ({centroid_lat:.4f}, {centroid_lon:.4f})")
    
    return formations
