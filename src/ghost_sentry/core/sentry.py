"""Ghost Sentry autonomous decision engine."""
from ghost_sentry.core.detector import Detection
from ghost_sentry.lattice.entities import TrackBuilder
from ghost_sentry.lattice.adapter import LatticeConnector

# Tactical labels from COCO that warrant autonomous cueing
HIGH_PRIORITY_LABELS = {"airplane", "truck", "boat"}
CONFIDENCE_THRESHOLD = 0.85

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
        
        # Auto-cue for high-priority, high-confidence detections
        if (detection.label in HIGH_PRIORITY_LABELS and 
            detection.confidence >= CONFIDENCE_THRESHOLD):
            task = {
                "type": "VERIFICATION_REQUEST",
                "target_entity_id": track.entityId,
                "description": f"Confirm {detection.label} at {detection.geo_location}",
                "priority": "HIGH" if detection.label == "airplane" else "MEDIUM"
            }
            connector.publish_task(task)
            stats["tasks"] += 1
    
    return stats
