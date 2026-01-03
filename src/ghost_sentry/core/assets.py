"""Asset management and assignment logic."""
from dataclasses import dataclass, asdict
from datetime import datetime, UTC
from typing import List, Optional, Tuple
from shapely.geometry import Point
import uuid

@dataclass
class Asset:
    """Represents a tactical asset (UAV, UGV, etc.) with telemetry."""
    id: str
    type: str          # "UAV", "UGV"
    location: Tuple[float, float]
    status: str = "idle"  # "idle", "tasked", "returning"
    domain: str = "air"
    battery: float = 1.0  # 0.0 - 1.0
    signal: float = 1.0   # 0.0 - 1.0
    current_task_id: Optional[str] = None
    last_heartbeat: Optional[datetime] = None

    def update_telemetry(self, lat: float, lon: float, battery: float, signal: float):
        self.location = (lat, lon)
        self.battery = battery
        self.signal = signal
        self.last_heartbeat = datetime.now(UTC)

    def to_dict(self):
        d = asdict(self)
        if self.last_heartbeat:
            d["last_heartbeat"] = self.last_heartbeat.isoformat()
        return d

# Initial mock fleet
MOCK_ASSETS = [
    Asset("drone-alpha", "UAV", (33.94, -118.41), domain="air"),
    Asset("drone-beta", "UAV", (33.95, -118.40), domain="air"),
    Asset("ugv-sierra", "UGV", (33.93, -118.42), domain="land"),
]

def score_asset(asset: Asset, target: Point) -> float:
    """
    Score an asset based on multi-criteria weighting.
    - Distance (40%)
    - Battery (30%)
    - Signal (30%)
    """
    distance = target.distance(Point(asset.location))
    # Normalize distance (max range ~11km / 0.1 deg for scoring)
    distance_score = max(0, 1 - (distance / 0.1))
    
    return (0.4 * distance_score) + (0.3 * asset.battery) + (0.3 * asset.signal)

def get_available_assets() -> List[Asset]:
    """Retrieve all idle assets."""
    return [a for a in MOCK_ASSETS if a.status == "idle"]

def assign_asset(target_loc: Tuple[float, float], assets: List[Asset]) -> Optional[Asset]:
    """
    Assign the best available asset to a target location using multi-criteria scoring.
    """
    if not assets:
        return None
        
    target = Point(target_loc)
    
    # Select the asset with the highest score
    best_asset = max(
        assets, 
        key=lambda a: score_asset(a, target)
    )
    
    return best_asset
