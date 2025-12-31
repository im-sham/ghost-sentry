"""Lattice connection adapter."""
import json
from pathlib import Path
from ghost_sentry.lattice.entities import LatticeTrack

class LatticeConnector:
    """Publishes entities to Lattice (or local log in dev mode)."""
    
    def __init__(self, mode: str = "dev", log_path: str = "lattice_events.jsonl"):
        self.mode = mode
        self.log_path = Path(log_path)
    
    def publish_track(self, track: LatticeTrack) -> None:
        if self.mode == "dev":
            with self.log_path.open("a") as f:
                f.write(json.dumps({"type": "track", "data": track.model_dump()}) + "\n")
        else:
            # TODO: Real Lattice SDK call
            raise NotImplementedError("Production mode requires Lattice SDK access")
    
    def publish_task(self, task: dict) -> None:
        if self.mode == "dev":
            with self.log_path.open("a") as f:
                f.write(json.dumps({"type": "task", "data": task}) + "\n")
