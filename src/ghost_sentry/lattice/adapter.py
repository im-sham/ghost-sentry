from ghost_sentry.lattice.entities import LatticeTrack
from ghost_sentry.core import db, events

class LatticeConnector:
    """Publishes entities to Lattice (or local SQLite DB in dev mode)."""
    
    def __init__(self, mode: str = "dev"):
        self.mode = mode
        if self.mode == "dev":
            db.init_db()
    
    def publish_track(self, track: LatticeTrack) -> None:
        if self.mode == "dev":
            db.add_event("track", track.model_dump(), entity_id=track.entityId)
            events.publish(events.TrackEvent(entity_id=track.entityId, data=track.model_dump()))
        else:
            # TODO: Real Lattice SDK call
            raise NotImplementedError("Production mode requires Lattice SDK access")
    
    def publish_task(self, task: dict) -> None:
        if self.mode == "dev":
            import uuid
            task_id = str(uuid.uuid4())
            entity_id = task.get("target_entity_id")
            
            # Add to tasks table (new Phase 6 logic)
            db.add_task(
                task_id=task_id,
                entity_id=entity_id,
                task_type=task.get("type"),
                data=task,
                assigned_to=task.get("assigned_to")
            )
            
            # Also log to events for timeline and publish to bus
            task_event_data = {**task, "id": task_id, "state": "pending"}
            db.add_event("task", task_event_data, entity_id=entity_id)
            events.publish(events.TrackEvent(entity_id=entity_id, data={"type": "task", "task": task_event_data}))
