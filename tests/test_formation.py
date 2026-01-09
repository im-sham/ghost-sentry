"""Tests for formation detection in analytics module."""
import pytest

from ghost_sentry.core.analytics import detect_formation, FORMATION_MIN_TRACKS


class TestFormationDetection:
    
    def test_no_formation_with_insufficient_tracks(self):
        tracks = [
            {"entityId": "t1", "location": {"position": {"latitudeDegrees": 33.94, "longitudeDegrees": -118.40}}}
        ]
        
        formations = detect_formation(tracks)
        
        assert formations == []

    def test_no_formation_with_scattered_tracks(self):
        tracks = [
            {"entityId": "t1", "location": {"position": {"latitudeDegrees": 33.0, "longitudeDegrees": -118.0}}},
            {"entityId": "t2", "location": {"position": {"latitudeDegrees": 34.0, "longitudeDegrees": -117.0}}},
            {"entityId": "t3", "location": {"position": {"latitudeDegrees": 35.0, "longitudeDegrees": -116.0}}},
        ]
        
        formations = detect_formation(tracks)
        
        assert formations == []

    def test_formation_detected_with_clustered_tracks(self):
        tracks = [
            {"entityId": "t1", "location": {"position": {"latitudeDegrees": 33.940, "longitudeDegrees": -118.400}}},
            {"entityId": "t2", "location": {"position": {"latitudeDegrees": 33.941, "longitudeDegrees": -118.401}}},
            {"entityId": "t3", "location": {"position": {"latitudeDegrees": 33.942, "longitudeDegrees": -118.402}}},
        ]
        
        formations = detect_formation(tracks)
        
        assert len(formations) == 1
        assert formations[0]["type"] == "FORMATION"
        assert formations[0]["member_count"] == 3
        assert "t1" in formations[0]["entity_ids"]
        assert "t2" in formations[0]["entity_ids"]
        assert "t3" in formations[0]["entity_ids"]

    def test_formation_has_centroid(self):
        tracks = [
            {"entityId": "t1", "location": {"position": {"latitudeDegrees": 33.940, "longitudeDegrees": -118.400}}},
            {"entityId": "t2", "location": {"position": {"latitudeDegrees": 33.941, "longitudeDegrees": -118.401}}},
            {"entityId": "t3", "location": {"position": {"latitudeDegrees": 33.942, "longitudeDegrees": -118.402}}},
        ]
        
        formations = detect_formation(tracks)
        
        assert "centroid" in formations[0]
        centroid = formations[0]["centroid"]
        assert 33.940 < centroid[0] < 33.943
        assert -118.403 < centroid[1] < -118.400

    def test_multiple_formations(self):
        tracks = [
            {"entityId": "t1", "location": {"position": {"latitudeDegrees": 33.940, "longitudeDegrees": -118.400}}},
            {"entityId": "t2", "location": {"position": {"latitudeDegrees": 33.941, "longitudeDegrees": -118.401}}},
            {"entityId": "t3", "location": {"position": {"latitudeDegrees": 33.942, "longitudeDegrees": -118.402}}},
            {"entityId": "t4", "location": {"position": {"latitudeDegrees": 35.000, "longitudeDegrees": -117.000}}},
            {"entityId": "t5", "location": {"position": {"latitudeDegrees": 35.001, "longitudeDegrees": -117.001}}},
            {"entityId": "t6", "location": {"position": {"latitudeDegrees": 35.002, "longitudeDegrees": -117.002}}},
        ]
        
        formations = detect_formation(tracks)
        
        assert len(formations) == 2

    def test_handles_malformed_tracks(self):
        tracks = [
            {"entityId": "t1"},
            {"entityId": "t2", "location": {}},
            {"entityId": "t3", "location": {"position": {"latitudeDegrees": 33.94}}},
        ]
        
        formations = detect_formation(tracks)
        
        assert formations == []
