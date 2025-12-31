"""Lattice entity builders (SDK-compatible stubs)."""
import uuid
from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field
from ghost_sentry.core.detector import Detection

class LatticeLocation(BaseModel):
    latitudeDegrees: float
    longitudeDegrees: float
    altitudeHaeMeters: float = 0.0

class LatticeOntology(BaseModel):
    template: str = "TEMPLATE_TRACK"
    platform_type: Optional[str] = None

class LatticeMilView(BaseModel):
    disposition: str = "DISPOSITION_UNKNOWN"
    environment: str = "ENVIRONMENT_LAND"

class LatticeProvenance(BaseModel):
    integrationName: str = "ghost-sentry"
    dataType: str = "detection"
    sourceUpdateTime: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class LatticeTrack(BaseModel):
    """A Lattice-compatible Track entity."""
    entityId: str = Field(default_factory=lambda: str(uuid.uuid4()))
    description: str
    ontology: LatticeOntology
    location: dict  # {"position": LatticeLocation}
    milView: LatticeMilView
    provenance: LatticeProvenance
    confidence: float = 0.0  # Detection confidence score
    isLive: bool = True
    createdTime: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    expiryTime: Optional[str] = None

class TrackBuilder:
    """Builds Lattice Track entities from Detections."""
    
    @staticmethod
    def from_detection(detection: Detection) -> LatticeTrack:
        lat, lon = detection.geo_location or (0.0, 0.0)
        return LatticeTrack(
            description=f"Detected {detection.label}",
            ontology=LatticeOntology(platform_type=detection.label.capitalize()),
            location={"position": LatticeLocation(
                latitudeDegrees=lat,
                longitudeDegrees=lon
            ).model_dump()},
            milView=LatticeMilView(
                disposition="DISPOSITION_UNKNOWN",
                environment="ENVIRONMENT_AIR" if detection.label == "airplane" else "ENVIRONMENT_LAND"
            ),
            provenance=LatticeProvenance(),
            confidence=detection.confidence
        )
