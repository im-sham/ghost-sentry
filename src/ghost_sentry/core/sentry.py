from datetime import datetime, timedelta, UTC
from ghost_sentry.core.detector import Detection
from ghost_sentry.lattice.entities import TrackBuilder
from ghost_sentry.lattice.adapter import LatticeConnector

# Tactical labels from COCO that warrant autonomous cueing
HIGH_PRIORITY_LABELS = {"airplane", "truck", "boat"}
CONFIDENCE_THRESHOLD = 0.85

# Debounce configuration
DEBOUNCE_WINDOW = timedelta(minutes=10)
_recent_tasks: dict[str, datetime] = {}

def should_task(entity_id: str) -> bool:
    """Check if an entity should be tasked (debounced)."""
    now = datetime.now(UTC)
    if entity_id in _recent_tasks:
        if now - _recent_tasks[entity_id] < DEBOUNCE_WINDOW:
            return False
    _recent_tasks[entity_id] = now
    return True

from ghost_sentry.core import track_state, analytics, assets

def process_detections(
    detections: list[Detection],
    connector: LatticeConnector
) -> dict:
    """Process detections and generate Tracks + Tasks."""
    stats = {"tracks": 0, "tasks": 0}
    
    for detection in detections:
        # Always publish track
        track = TrackBuilder.from_detection(detection)
        connector.publish_track(track)
        stats["tracks"] += 1
        
        # Update in-memory state for analytics
        if detection.geo_location:
            track_state.update_position(track.entityId, detection.geo_location)
        
        # Check for loitering behavior
        is_loitering = analytics.detect_loitering(track.entityId)
        
        # Auto-cue for high-priority detections or anomalies
        is_high_priority = (detection.label in HIGH_PRIORITY_LABELS and 
                           detection.confidence >= CONFIDENCE_THRESHOLD)
        
        if (is_high_priority or is_loitering) and should_task(track.entityId):
            # Proximity-based asset assignment
            assigned_asset = assets.assign_asset(
                detection.geo_location or (0.0, 0.0),
                assets.get_available_assets()
            )
            
            task = {
                "type": "VERIFICATION_REQUEST" if not is_loitering else "ANOMALY_VERIFICATION",
                "target_entity_id": track.entityId,
                "description": f"Confirm {detection.label} at {detection.geo_location}",
                "priority": "HIGH" if detection.label == "airplane" or is_loitering else "MEDIUM",
                "assigned_to": assigned_asset.id if assigned_asset else "DISPATCH_PENDING"
            }
            connector.publish_task(task)
            stats["tasks"] += 1
    
    return stats
