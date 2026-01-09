import os
import logging
from ghost_sentry.lattice.entities import LatticeTrack
from ghost_sentry.core import db, events


class LatticeConnectionError(Exception):
    """Raised when Lattice connection fails."""
    pass


class LatticeConnector:
    """Publishes entities to Lattice (or local SQLite DB in dev mode).
    
    Modes:
        - dev: Local SQLite persistence with event bus (default)
        - prod: gRPC connection to Lattice service (requires LATTICE_ENDPOINT)
    """
    
    def __init__(self, mode: str = "dev"):
        self.mode = mode
        self._logger = logging.getLogger(__name__)
        
        if self.mode == "dev":
            db.init_db()
        elif self.mode == "prod":
            self._init_prod_connection()
    
    def _init_prod_connection(self) -> None:
        """Initialize production Lattice gRPC connection."""
        endpoint = os.environ.get("LATTICE_ENDPOINT")
        if not endpoint:
            raise EnvironmentError(
                "LATTICE_ENDPOINT environment variable required for prod mode. "
                "Expected format: grpc://lattice.example.com:443"
            )
        
        # Production Lattice SDK integration point
        # In a real deployment, this would establish gRPC channel:
        #
        # import grpc
        # from anduril.lattice.v1 import lattice_pb2_grpc
        # 
        # credentials = grpc.ssl_channel_credentials()
        # self._channel = grpc.secure_channel(endpoint, credentials)
        # self._stub = lattice_pb2_grpc.LatticeServiceStub(self._channel)
        #
        self._endpoint = endpoint
        self._logger.info(f"Lattice connector initialized for endpoint: {endpoint}")
    
    def publish_track(self, track: LatticeTrack) -> None:
        """Publish a track entity to Lattice."""
        if self.mode == "dev":
            db.add_event("track", track.model_dump(), entity_id=track.entityId)
            events.publish(events.TrackEvent(entity_id=track.entityId, data=track.model_dump()))
        else:
            # Production gRPC publish
            # In real deployment:
            # request = PublishTrackRequest(track=track.to_proto())
            # self._stub.PublishTrack(request)
            self._logger.info(f"[PROD] Would publish track {track.entityId} to {self._endpoint}")
    
    def publish_task(self, task: dict) -> None:
        if self.mode == "dev":
            import uuid
            task_id = str(uuid.uuid4())
            entity_id = task.get("target_entity_id", "unknown")
            task_type = task.get("type", "VERIFICATION_REQUEST")
            assigned_to = task.get("assigned_to")
            
            db.add_task(
                task_id=task_id,
                entity_id=entity_id,
                task_type=task_type,
                data=task,
                assigned_to=assigned_to
            )
            
            task_event_data = {**task, "id": task_id, "state": "pending"}
            db.add_event("task", task_event_data, entity_id=entity_id)
            events.publish(events.TrackEvent(entity_id=entity_id, data={"type": "task", "task": task_event_data}))
        else:
            self._logger.info(f"[PROD] Would publish task to {self._endpoint}")
