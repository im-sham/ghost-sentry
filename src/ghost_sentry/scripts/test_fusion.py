"""Test script for FusionEngine."""
import json
from pathlib import Path
from ghost_sentry.core.detector import Detection
from ghost_sentry.core.fusion import FusionEngine

def test_fusion():
    # Mock Optical detections (low confidence/empty for cloudy day)
    optical = []
    
    # Mock SAR detections
    sar_data = [
        {"label": "tank", "confidence": 0.82, "bbox": [0,0,0,0], "geo_location": [33.95, -118.42], "sensor": "SAR"},
        {"label": "truck", "confidence": 0.91, "bbox": [0,0,0,0], "geo_location": [33.94, -118.41], "sensor": "SAR"}
    ]
    sar = [Detection(**d) for d in sar_data]
    
    engine = FusionEngine()
    fused = engine.fuse(optical, sar)
    
    print(f"Fused Detections: {len(fused)}")
    for d in fused:
        print(f"- {d.label} at {d.geo_location} (Confidence: {d.confidence})")

if __name__ == "__main__":
    test_fusion()
