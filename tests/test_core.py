"""Tests for Ghost Sentry core modules."""
import pytest
from ghost_sentry.core.detector import Detection, ObjectDetector
from ghost_sentry.core.sentry import process_detections, HIGH_PRIORITY_LABELS, CONFIDENCE_THRESHOLD
from ghost_sentry.lattice.entities import TrackBuilder, LatticeTrack
from ghost_sentry.lattice.adapter import LatticeConnector
from ghost_sentry.output.cot import to_cursor_on_target
import tempfile
import json
from pathlib import Path


class TestDetection:
    """Tests for the Detection model."""
    
    def test_detection_creation(self):
        """Test that Detection can be created with valid data."""
        d = Detection(
            label="airplane",
            confidence=0.92,
            bbox=(100, 150, 200, 250),
            geo_location=(33.9425, -118.4081)
        )
        assert d.label == "airplane"
        assert d.confidence == 0.92
        assert d.bbox == (100, 150, 200, 250)
        assert d.geo_location == (33.9425, -118.4081)
    
    def test_detection_without_geo(self):
        """Test that Detection works without geo_location."""
        d = Detection(
            label="truck",
            confidence=0.78,
            bbox=(0, 0, 50, 50)
        )
        assert d.geo_location is None


class TestTrackBuilder:
    """Tests for the TrackBuilder."""
    
    def test_track_from_detection(self):
        """Test that TrackBuilder creates valid LatticeTrack."""
        d = Detection(
            label="airplane",
            confidence=0.92,
            bbox=(0, 0, 100, 100),
            geo_location=(33.94, -118.40)
        )
        track = TrackBuilder.from_detection(d)
        
        assert isinstance(track, LatticeTrack)
        assert track.ontology.platform_type == "Airplane"
        assert track.milView.environment == "ENVIRONMENT_AIR"
        assert track.confidence == 0.92
        assert track.location["position"]["latitudeDegrees"] == 33.94
    
    def test_ground_vehicle_environment(self):
        """Test that ground vehicles get ENVIRONMENT_LAND."""
        d = Detection(
            label="truck",
            confidence=0.85,
            bbox=(0, 0, 50, 50),
            geo_location=(34.0, -117.0)
        )
        track = TrackBuilder.from_detection(d)
        assert track.milView.environment == "ENVIRONMENT_LAND"


class TestSentryLogic:
    """Tests for the autonomous cueing logic."""
    
    @pytest.fixture(autouse=True)
    def setup_test_db(self, monkeypatch, tmp_path):
        """Setup a test database for each test."""
        from ghost_sentry.core import db, sentry
        test_db = tmp_path / "test_sentry.db"
        monkeypatch.setattr(db, "DB_PATH", test_db)
        # Reset the debounce cache for each test
        sentry._recent_tasks.clear()
        db.init_db()
        yield
    
    def test_high_priority_cueing(self):
        """Test that high-priority, high-confidence detections generate tasks."""
        detections = [
            Detection(label="airplane", confidence=0.92, bbox=(0,0,100,100), geo_location=(33.94, -118.40)),
        ]
        
        connector = LatticeConnector()
        stats = process_detections(detections, connector)
        
        assert stats["tracks"] == 1
        assert stats["tasks"] == 1  # Airplane with 0.92 > 0.85 threshold
    
    def test_low_confidence_no_task(self):
        """Test that low-confidence detections don't generate tasks."""
        detections = [
            Detection(label="airplane", confidence=0.70, bbox=(0,0,100,100), geo_location=(33.94, -118.40)),
        ]
        
        connector = LatticeConnector()
        stats = process_detections(detections, connector)
        
        assert stats["tracks"] == 1
        assert stats["tasks"] == 0  # 0.70 < 0.85 threshold
    
    def test_low_priority_no_task(self):
        """Test that low-priority labels don't generate tasks even with high confidence."""
        detections = [
            Detection(label="car", confidence=0.95, bbox=(0,0,50,50), geo_location=(33.94, -118.40)),
        ]
        
        connector = LatticeConnector()
        stats = process_detections(detections, connector)
        
        assert stats["tracks"] == 1
        assert stats["tasks"] == 0  # car is not in HIGH_PRIORITY_LABELS


class TestCoTGeneration:
    """Tests for CoT XML generation."""
    
    def test_cot_output_format(self):
        """Test that CoT XML has correct structure."""
        d = Detection(
            label="airplane",
            confidence=0.90,
            bbox=(0, 0, 100, 100),
            geo_location=(33.94, -118.40)
        )
        xml = to_cursor_on_target(d)
        
        assert '<?xml version="1.0"' in xml
        assert 'type="a-f-A"' in xml  # airplane type
        assert 'lat="33.94"' in xml
        assert 'lon="-118.4"' in xml
        assert 'callsign="GS-AIR"' in xml
    
    def test_cot_truck_type(self):
        """Test that trucks get correct CoT type."""
        d = Detection(
            label="truck",
            confidence=0.85,
            bbox=(0, 0, 50, 50),
            geo_location=(34.0, -117.0)
        )
        xml = to_cursor_on_target(d)
        
        assert 'type="a-u-G-E-V"' in xml  # ground vehicle type


class TestFusionEngine:
    """Tests for the multi-modal fusion engine."""
    
    def test_fuse_combines_sources(self):
        """Test that FusionEngine merges Optical and SAR sources."""
        from ghost_sentry.core.fusion import FusionEngine
        engine = FusionEngine()
        optical = [Detection(label="tank", confidence=0.9, bbox=(0,0,0,0), geo_location=(33.94, -118.4))]
        sar = [Detection(label="truck", confidence=0.85, bbox=(0,0,0,0), geo_location=(33.95, -118.41))]
        
        fused = engine.fuse(optical, sar)
        assert len(fused) == 2
        assert "(Optical)" in fused[0].label
        assert "(SAR)" in fused[1].label

    def test_fuse_filters_low_confidence_optical(self):
        """Test that FusionEngine filters out optical detections below threshold."""
        from ghost_sentry.core.fusion import FusionEngine
        # Set threshold high to filter out common detections
        engine = FusionEngine(optical_threshold=0.8)
        
        optical = [
            Detection(label="car", confidence=0.5, bbox=(0,0,0,0), geo_location=(33.1, -118.1)),  # Should be filtered
            Detection(label="truck", confidence=0.9, bbox=(0,0,0,0), geo_location=(33.2, -118.2))  # Should stay
        ]
        sar = [
            Detection(label="boat", confidence=0.7, bbox=(0,0,0,0), geo_location=(33.3, -118.3)) # Should always stay
        ]
        
        fused = engine.fuse(optical, sar)
        # Should have truck (Optical) and boat (SAR). car (Optical) filtered.
        assert len(fused) == 2
        labels = [d.label for d in fused]
        assert "truck (Optical)" in labels
        assert "boat (SAR)" in labels
        assert "car (Optical)" not in labels
