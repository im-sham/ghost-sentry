"""Tests for threat classification module."""
import pytest

from ghost_sentry.core.threat import (
    ThreatClassifier,
    ThreatLevel,
    classify_track_dict,
)
from ghost_sentry.core.correlation import CorrelatedEntity, LifecycleState


class TestThreatClassifier:
    
    def test_aircraft_high_confidence_is_high_threat(self):
        classifier = ThreatClassifier()
        entity = CorrelatedEntity(
            entity_id="test-1",
            entity_type="airplane",
            location=(33.94, -118.40),
            confidence=0.92,
            state=LifecycleState.FIRM
        )
        
        level = classifier.classify(entity)
        
        assert level == ThreatLevel.HIGH

    def test_aircraft_loitering_is_critical(self):
        classifier = ThreatClassifier()
        entity = CorrelatedEntity(
            entity_id="test-1",
            entity_type="airplane",
            location=(33.94, -118.40),
            confidence=0.92,
            state=LifecycleState.FIRM
        )
        
        level = classifier.classify(entity, is_loitering=True)
        
        assert level == ThreatLevel.CRITICAL

    def test_truck_high_confidence_is_medium(self):
        classifier = ThreatClassifier()
        entity = CorrelatedEntity(
            entity_id="test-2",
            entity_type="truck",
            location=(34.0, -117.0),
            confidence=0.90,
            state=LifecycleState.FIRM
        )
        
        level = classifier.classify(entity)
        
        assert level == ThreatLevel.MEDIUM

    def test_truck_loitering_is_high(self):
        classifier = ThreatClassifier()
        entity = CorrelatedEntity(
            entity_id="test-2",
            entity_type="truck",
            location=(34.0, -117.0),
            confidence=0.90,
            state=LifecycleState.FIRM
        )
        
        level = classifier.classify(entity, is_loitering=True)
        
        assert level == ThreatLevel.HIGH

    def test_unknown_type_is_low(self):
        classifier = ThreatClassifier()
        entity = CorrelatedEntity(
            entity_id="test-3",
            entity_type="bicycle",
            location=(34.0, -117.0),
            confidence=0.95,
            state=LifecycleState.FIRM
        )
        
        level = classifier.classify(entity)
        
        assert level == ThreatLevel.LOW

    def test_formation_elevates_threat(self):
        classifier = ThreatClassifier()
        entity = CorrelatedEntity(
            entity_id="test-4",
            entity_type="car",
            location=(34.0, -117.0),
            confidence=0.80,
            state=LifecycleState.FIRM
        )
        
        level = classifier.classify(entity, in_formation=True)
        
        assert level == ThreatLevel.MEDIUM

    def test_should_auto_task(self):
        classifier = ThreatClassifier()
        
        assert classifier.should_auto_task(ThreatLevel.CRITICAL) is True
        assert classifier.should_auto_task(ThreatLevel.HIGH) is True
        assert classifier.should_auto_task(ThreatLevel.MEDIUM) is False
        assert classifier.should_auto_task(ThreatLevel.LOW) is False

    def test_priority_scores(self):
        classifier = ThreatClassifier()
        
        assert classifier.get_priority_score(ThreatLevel.CRITICAL) == 100
        assert classifier.get_priority_score(ThreatLevel.HIGH) == 75
        assert classifier.get_priority_score(ThreatLevel.MEDIUM) == 50
        assert classifier.get_priority_score(ThreatLevel.LOW) == 25


class TestClassifyTrackDict:
    
    def test_classify_airplane_track(self):
        track = {
            "entityId": "abc-123",
            "ontology": {"platform_type": "Airplane"},
            "confidence": 0.92
        }
        
        level = classify_track_dict(track)
        
        assert level == ThreatLevel.HIGH

    def test_classify_unknown_type(self):
        track = {
            "entityId": "abc-123",
            "ontology": {"platform_type": "Unknown"},
            "confidence": 0.50
        }
        
        level = classify_track_dict(track)
        
        assert level == ThreatLevel.LOW
