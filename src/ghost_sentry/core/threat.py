"""Threat classification based on track behavior and type."""
from enum import Enum
from typing import Optional
from ghost_sentry.core.correlation import CorrelatedEntity, LifecycleState
from ghost_sentry.core.analytics import detect_loitering


class ThreatLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


THREAT_PRIORITY_WEIGHTS = {
    ThreatLevel.CRITICAL: 100,
    ThreatLevel.HIGH: 75,
    ThreatLevel.MEDIUM: 50,
    ThreatLevel.LOW: 25,
}

HIGH_THREAT_TYPES = {"airplane", "Airplane", "AIRPLANE"}
MEDIUM_THREAT_TYPES = {"truck", "Truck", "TRUCK", "boat", "Boat", "BOAT"}


class ThreatClassifier:
    """
    Classifies tracks by threat level based on:
    - Entity type (aircraft > vehicles > other)
    - Behavioral patterns (loitering, formation)
    - Proximity to critical areas (future)
    """
    
    def __init__(self, confidence_threshold: float = 0.85):
        self._confidence_threshold = confidence_threshold

    def classify(
        self, 
        entity: CorrelatedEntity,
        is_loitering: bool = False,
        in_formation: bool = False
    ) -> ThreatLevel:
        entity_type = entity.entity_type
        confidence = entity.confidence
        
        if entity_type in HIGH_THREAT_TYPES:
            if is_loitering:
                return ThreatLevel.CRITICAL
            if confidence >= self._confidence_threshold:
                return ThreatLevel.HIGH
            return ThreatLevel.MEDIUM
        
        if entity_type in MEDIUM_THREAT_TYPES:
            if is_loitering or in_formation:
                return ThreatLevel.HIGH
            if confidence >= self._confidence_threshold:
                return ThreatLevel.MEDIUM
            return ThreatLevel.LOW
        
        if is_loitering or in_formation:
            return ThreatLevel.MEDIUM
            
        return ThreatLevel.LOW

    def classify_with_analytics(
        self, 
        entity: CorrelatedEntity,
        in_formation: bool = False
    ) -> ThreatLevel:
        is_loitering = detect_loitering(entity.entity_id)
        return self.classify(entity, is_loitering, in_formation)

    def get_priority_score(self, level: ThreatLevel) -> int:
        return THREAT_PRIORITY_WEIGHTS.get(level, 0)

    def should_auto_task(self, level: ThreatLevel) -> bool:
        return level in {ThreatLevel.HIGH, ThreatLevel.CRITICAL}


def classify_track_dict(track: dict, is_loitering: bool = False, in_formation: bool = False) -> ThreatLevel:
    """Convenience function for classifying raw track dicts."""
    entity_type = track.get("ontology", {}).get("platform_type", "unknown")
    confidence = track.get("confidence", 0.0)
    
    classifier = ThreatClassifier()
    
    from ghost_sentry.core.correlation import CorrelatedEntity, LifecycleState
    from datetime import datetime, UTC
    
    temp_entity = CorrelatedEntity(
        entity_id=track.get("entityId", "unknown"),
        entity_type=entity_type,
        location=(0.0, 0.0),
        confidence=confidence,
        state=LifecycleState.FIRM
    )
    
    return classifier.classify(temp_entity, is_loitering, in_formation)
