"""Tests for entity correlation module."""
import pytest
from datetime import datetime, timedelta, UTC

from ghost_sentry.core.correlation import (
    EntityMatcher,
    CorrelatedEntity,
    LifecycleState,
    CORRELATION_RADIUS_M,
)


class TestCorrelatedEntity:
    
    def test_entity_creation(self):
        entity = CorrelatedEntity(
            entity_id="test-123",
            entity_type="airplane",
            location=(33.94, -118.40),
            confidence=0.92,
            state=LifecycleState.TENTATIVE
        )
        assert entity.entity_id == "test-123"
        assert entity.entity_type == "airplane"
        assert entity.observation_count == 1
        assert entity.state == LifecycleState.TENTATIVE

    def test_entity_update_increments_observations(self):
        entity = CorrelatedEntity(
            entity_id="test-123",
            entity_type="airplane",
            location=(33.94, -118.40),
            confidence=0.80,
            state=LifecycleState.TENTATIVE
        )
        
        entity.update((33.95, -118.41), 0.95, "sar")
        
        assert entity.observation_count == 2
        assert entity.confidence == 0.95
        assert "sar" in entity.sources

    def test_entity_becomes_firm_after_threshold(self):
        entity = CorrelatedEntity(
            entity_id="test-123",
            entity_type="truck",
            location=(34.0, -117.0),
            confidence=0.85,
            state=LifecycleState.TENTATIVE
        )
        
        entity.update((34.01, -117.01), 0.90, "optical")
        
        assert entity.state == LifecycleState.FIRM

    def test_entity_to_dict(self):
        entity = CorrelatedEntity(
            entity_id="test-123",
            entity_type="boat",
            location=(33.5, -118.0),
            confidence=0.88,
            state=LifecycleState.FIRM,
            sources=["optical", "sar"]
        )
        
        d = entity.to_dict()
        
        assert d["entity_id"] == "test-123"
        assert d["lifecycle_state"] == "FIRM"
        assert d["location"]["lat"] == 33.5


class TestEntityMatcher:
    
    def test_new_observation_creates_entity(self):
        matcher = EntityMatcher()
        
        entity = matcher.correlate("airplane", (33.94, -118.40), 0.92, "optical")
        
        assert entity.entity_type == "airplane"
        assert entity.state == LifecycleState.TENTATIVE
        assert len(matcher.get_active_entities()) == 1

    def test_nearby_observation_correlates(self):
        matcher = EntityMatcher()
        
        entity1 = matcher.correlate("airplane", (33.94, -118.40), 0.85, "optical")
        entity2 = matcher.correlate("airplane", (33.9401, -118.4001), 0.90, "sar")
        
        assert entity1.entity_id == entity2.entity_id
        assert entity1.observation_count == 2
        assert len(matcher.get_active_entities()) == 1

    def test_distant_observation_creates_new_entity(self):
        matcher = EntityMatcher()
        
        entity1 = matcher.correlate("airplane", (33.94, -118.40), 0.85, "optical")
        entity2 = matcher.correlate("airplane", (34.50, -117.00), 0.90, "optical")
        
        assert entity1.entity_id != entity2.entity_id
        assert len(matcher.get_active_entities()) == 2

    def test_different_type_creates_new_entity(self):
        matcher = EntityMatcher()
        
        entity1 = matcher.correlate("airplane", (33.94, -118.40), 0.85, "optical")
        entity2 = matcher.correlate("truck", (33.9401, -118.4001), 0.90, "optical")
        
        assert entity1.entity_id != entity2.entity_id

    def test_get_firm_entities(self):
        matcher = EntityMatcher()
        
        entity = matcher.correlate("airplane", (33.94, -118.40), 0.85, "optical")
        assert len(matcher.get_firm_entities()) == 0
        
        matcher.correlate("airplane", (33.9401, -118.4001), 0.90, "sar")
        assert len(matcher.get_firm_entities()) == 1

    def test_entity_count_by_state(self):
        matcher = EntityMatcher()
        
        matcher.correlate("airplane", (33.94, -118.40), 0.85, "optical")
        matcher.correlate("truck", (34.0, -117.0), 0.80, "optical")
        matcher.correlate("airplane", (33.9401, -118.4001), 0.90, "sar")
        
        counts = matcher.entity_count()
        
        assert counts["TENTATIVE"] == 1
        assert counts["FIRM"] == 1
