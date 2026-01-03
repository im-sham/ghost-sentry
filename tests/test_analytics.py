"""Unit tests for behavioral analytics."""
import pytest
from ghost_sentry.core import analytics, track_state
from shapely.geometry import Point

def test_loitering_detection_positive():
    """Test that loitering is detected when tracks are stationary."""
    entity_id = "test-loiterer"
    track_state.clear_cache()
    
    # Add 5 points in a tight 10m cluster (approx 0.0001 deg)
    base_loc = (33.9400, -118.4100)
    for _ in range(5):
        track_state.update_position(entity_id, base_loc)
        
    assert analytics.detect_loitering(entity_id) is True

def test_loitering_detection_negative_movement():
    """Test that loitering is NOT detected when entity is moving."""
    entity_id = "test-mover"
    track_state.clear_cache()
    
    # Add 5 points moving significantly (approx 200m each step)
    for i in range(5):
        loc = (33.9400 + (i * 0.002), -118.4100)
        track_state.update_position(entity_id, loc)
        
    assert analytics.detect_loitering(entity_id) is False

def test_loitering_detection_insufficient_data():
    """Test that loitering is NOT detected with too few samples."""
    entity_id = "test-new"
    track_state.clear_cache()
    
    track_state.update_position(entity_id, (33.94, -118.41))
    
    assert analytics.detect_loitering(entity_id) is False
