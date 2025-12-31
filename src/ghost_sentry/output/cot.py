"""Cursor-on-Target (CoT) XML generator."""
import uuid
from datetime import datetime, timezone, timedelta
from ghost_sentry.core.detector import Detection

COT_TEMPLATE = '''<?xml version="1.0" encoding="UTF-8"?>
<event version="2.0" uid="{uid}" type="{cot_type}" time="{time}" start="{time}" stale="{stale}" how="m-g">
  <point lat="{lat}" lon="{lon}" hae="0" ce="10" le="10"/>
  <detail>
    <contact callsign="{callsign}"/>
    <remarks>{remarks}</remarks>
  </detail>
</event>'''

COT_TYPE_MAP = {
    "airplane": "a-f-A",  # Assumed friendly air
    "truck": "a-u-G-E-V",  # Unknown ground vehicle
    "car": "a-u-G-E-V",
    "boat": "a-u-S",  # Unknown surface
}

def to_cursor_on_target(detection: Detection) -> str:
    """Convert a Detection to CoT XML."""
    lat, lon = detection.geo_location or (0.0, 0.0)
    now = datetime.now(timezone.utc)
    stale = now + timedelta(minutes=5)
    
    return COT_TEMPLATE.format(
        uid=str(uuid.uuid4()),
        cot_type=COT_TYPE_MAP.get(detection.label, "a-u-G"),
        time=now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        stale=stale.strftime("%Y-%m-%dT%H:%M:%SZ"),
        lat=lat,
        lon=lon,
        callsign=f"GS-{detection.label.upper()[:3]}",
        remarks=f"Detected {detection.label} (conf: {detection.confidence:.2f})"
    )
