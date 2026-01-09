"""Entity correlation and deduplication for multi-sensor fusion."""
from dataclasses import dataclass, field
from datetime import datetime, timedelta, UTC
from typing import Dict, List, Optional, Tuple
from enum import Enum
from shapely.geometry import Point
import uuid


class LifecycleState(Enum):
    TENTATIVE = "TENTATIVE"
    FIRM = "FIRM"
    STALE = "STALE"
    DROPPED = "DROPPED"


LIFECYCLE_TTL = {
    LifecycleState.TENTATIVE: timedelta(seconds=30),
    LifecycleState.FIRM: timedelta(minutes=5),
    LifecycleState.STALE: timedelta(minutes=10),
}

CORRELATION_RADIUS_M = 100
CORRELATION_TIME_WINDOW = timedelta(seconds=60)
FIRM_OBSERVATION_THRESHOLD = 2


@dataclass
class CorrelatedEntity:
    entity_id: str
    entity_type: str
    location: Tuple[float, float]
    confidence: float
    state: LifecycleState
    observation_count: int = 1
    first_seen: datetime = field(default_factory=lambda: datetime.now(UTC))
    last_seen: datetime = field(default_factory=lambda: datetime.now(UTC))
    sources: List[str] = field(default_factory=list)

    def update(self, location: Tuple[float, float], confidence: float, source: str) -> None:
        self.location = location
        self.confidence = max(self.confidence, confidence)
        self.observation_count += 1
        self.last_seen = datetime.now(UTC)
        if source not in self.sources:
            self.sources.append(source)
        self._update_lifecycle()

    def _update_lifecycle(self) -> None:
        if self.observation_count >= FIRM_OBSERVATION_THRESHOLD:
            self.state = LifecycleState.FIRM

    def check_staleness(self) -> None:
        now = datetime.now(UTC)
        age = now - self.last_seen
        
        if self.state == LifecycleState.DROPPED:
            return
            
        ttl = LIFECYCLE_TTL.get(self.state, timedelta(minutes=5))
        
        if age > ttl:
            if self.state == LifecycleState.TENTATIVE:
                self.state = LifecycleState.DROPPED
            elif self.state == LifecycleState.FIRM:
                self.state = LifecycleState.STALE
            elif self.state == LifecycleState.STALE:
                self.state = LifecycleState.DROPPED

    def to_dict(self) -> dict:
        return {
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "location": {"lat": self.location[0], "lon": self.location[1]},
            "confidence": self.confidence,
            "lifecycle_state": self.state.value,
            "observation_count": self.observation_count,
            "first_seen": self.first_seen.isoformat(),
            "last_seen": self.last_seen.isoformat(),
            "sources": self.sources
        }


class EntityMatcher:
    """
    Correlates detections across sensors to maintain unified entity tracks.
    
    Handles:
    - Spatial/temporal correlation
    - Lifecycle state management
    - Deduplication across observation sources
    """
    
    def __init__(self, radius_m: float = CORRELATION_RADIUS_M):
        self._entities: Dict[str, CorrelatedEntity] = {}
        self._radius_deg = radius_m / 111000.0
        self._time_window = CORRELATION_TIME_WINDOW

    def correlate(
        self, 
        entity_type: str, 
        location: Tuple[float, float], 
        confidence: float,
        source: str = "optical"
    ) -> CorrelatedEntity:
        """
        Attempt to correlate an observation with existing entities.
        Creates new entity if no match found.
        """
        self._prune_dropped()
        
        observation_point = Point(location)
        now = datetime.now(UTC)
        
        best_match: Optional[CorrelatedEntity] = None
        best_distance = float('inf')
        
        for entity in self._entities.values():
            if entity.state == LifecycleState.DROPPED:
                continue
                
            if entity.entity_type != entity_type:
                continue
                
            age = now - entity.last_seen
            if age > self._time_window:
                continue
            
            entity_point = Point(entity.location)
            distance = observation_point.distance(entity_point)
            
            if distance <= self._radius_deg and distance < best_distance:
                best_match = entity
                best_distance = distance
        
        if best_match:
            best_match.update(location, confidence, source)
            return best_match
        
        new_entity = CorrelatedEntity(
            entity_id=str(uuid.uuid4()),
            entity_type=entity_type,
            location=location,
            confidence=confidence,
            state=LifecycleState.TENTATIVE,
            sources=[source]
        )
        self._entities[new_entity.entity_id] = new_entity
        return new_entity

    def get_entity(self, entity_id: str) -> Optional[CorrelatedEntity]:
        return self._entities.get(entity_id)

    def get_active_entities(self) -> List[CorrelatedEntity]:
        self._update_all_staleness()
        return [e for e in self._entities.values() if e.state != LifecycleState.DROPPED]

    def get_firm_entities(self) -> List[CorrelatedEntity]:
        return [e for e in self.get_active_entities() if e.state == LifecycleState.FIRM]

    def _update_all_staleness(self) -> None:
        for entity in self._entities.values():
            entity.check_staleness()

    def _prune_dropped(self) -> None:
        dropped_ids = [
            eid for eid, entity in self._entities.items() 
            if entity.state == LifecycleState.DROPPED
        ]
        for eid in dropped_ids:
            del self._entities[eid]

    def entity_count(self) -> dict:
        self._update_all_staleness()
        counts = {state.value: 0 for state in LifecycleState}
        for entity in self._entities.values():
            counts[entity.state.value] += 1
        return counts
