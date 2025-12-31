"""Ghost Sentry REST API."""
from fastapi import FastAPI
from fastapi.responses import Response
from ghost_sentry.core.detector import ObjectDetector, Detection
from ghost_sentry.core.sentry import process_detections
from ghost_sentry.lattice.adapter import LatticeConnector
from ghost_sentry.output.cot import to_cursor_on_target
import json
from pathlib import Path

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Ghost Sentry", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
connector = LatticeConnector()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/tracks")
def get_tracks():
    """Return all published tracks from the log."""
    log = Path("lattice_events.jsonl")
    if not log.exists():
        return []
    tracks = []
    for line in log.read_text().splitlines():
        event = json.loads(line)
        if event["type"] == "track":
            tracks.append(event["data"])
    return tracks

@app.get("/tracks/cot", response_class=Response)
def get_tracks_cot():
    """Return tracks as CoT XML."""
    tracks = get_tracks()
    cot_events = []
    for track in tracks:
        d = Detection(
            label=track["ontology"]["platform_type"].lower(),
            confidence=track.get("confidence", 0.9),
            bbox=(0,0,0,0),
            geo_location=(
                track["location"]["position"]["latitudeDegrees"],
                track["location"]["position"]["longitudeDegrees"]
            )
        )
        cot_events.append(to_cursor_on_target(d))
    return Response(content="\n".join(cot_events), media_type="application/xml")
