from fastapi import FastAPI, WebSocket
from fastapi.responses import Response
from ghost_sentry.core.detector import ObjectDetector, Detection
from ghost_sentry.core import db, sentry, events
from ghost_sentry.lattice.adapter import LatticeConnector
from ghost_sentry.output.cot import to_cursor_on_target
import json
import asyncio
from typing import List
from pathlib import Path

from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Literal

app = FastAPI(title="Ghost Sentry", version="0.1.0")

class Geometry(BaseModel):
    """Schema for mission geometry (polygon, linestring, point)."""
    type: Literal["polygon", "linestring", "point"]
    coords: List[List[float]]
    label: str

class CreateMission(BaseModel):
    name: str
    geometries: List[Geometry]

# In-memory pub/sub for WebSockets
_subscribers: List[asyncio.Queue] = []

async def broadcast(event: events.TrackEvent):
    """Broadcast an event to all connected WebSocket clients."""
    for queue in _subscribers:
        await queue.put(event.data)

@app.on_event("startup")
def startup_event():
    db.init_db()
    # Subscribe the broadcast function to core events
    # We use a wrapper to handle the async call from the sync bus
    events.subscribe(lambda e: asyncio.create_task(broadcast(e)))

@app.websocket("/ws/tracks")
async def websocket_endpoint(websocket: WebSocket):
    """Real-time tactical feed via WebSocket."""
    await websocket.accept()
    queue = asyncio.Queue()
    _subscribers.append(queue)
    try:
        # Send initial state (current tracks)
        tracks = db.get_tracks()
        for track in tracks:
            await websocket.send_json(track)
        
        # Send initial assets for consistency
        from ghost_sentry.core import assets
        for asset in assets.MOCK_ASSETS:
            await websocket.send_json({"type": "asset_telemetry", **asset.to_dict()})
            
        while True:
            # Wait for new events from the bus
            data = await queue.get()
            await websocket.send_json(data)
    except Exception:
        pass
    finally:
        _subscribers.remove(queue)

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
    """Return all published tracks from the database."""
    return db.get_tracks()

@app.get("/tasks")
def get_tasks(state: str = None):
    """Retrieve all tasks from the database."""
    return db.get_tasks(state=state)

@app.patch("/tasks/{task_id}/state")
def update_task_state(task_id: str, state: str):
    """Update the state of a task and broadcast change."""
    db.update_task_state(task_id, state)
    # Broadcast state change via event bus if matching an entity
    # (Simplified: find entity_id from task list)
    all_tasks = db.get_tasks()
    task = next((t for t in all_tasks if t["id"] == task_id), None)
    if task:
        events.publish(events.TrackEvent(
            entity_id=task["entity_id"], 
            data={"type": "task_update", "task_id": task_id, "state": state}
        ))
    return {"status": "updated", "task_id": task_id, "state": state}

@app.get("/timeline")
def get_timeline():
    """Retrieve a unified event timeline (tracks + tasks)."""
    return db.get_latest_events(limit=100)

@app.get("/assets")
def get_assets():
    """Retrieve full asset status and utilization."""
    from ghost_sentry.core import assets
    return [a.to_dict() for a in assets.MOCK_ASSETS]

@app.post("/assets/telemetry")
async def update_asset_telemetry(asset_id: str, lat: float, lon: float, battery: float, signal: float):
    """Update asset telemetry and broadcast to clients."""
    from ghost_sentry.core import assets
    asset = next((a for a in assets.MOCK_ASSETS if a.id == asset_id), None)
    if not asset:
        return {"status": "error", "message": "Asset not found"}
    
    asset.update_telemetry(lat, lon, battery, signal)
    
    # Broadcast via event bus
    events.publish(events.TrackEvent(
        entity_id=asset_id,
        data={"type": "asset_telemetry", **asset.to_dict()}
    ))
    
    return {"status": "ok"}

@app.get("/missions")
def get_missions():
    """Retrieve all mission configurations."""
    return db.get_missions()

@app.post("/missions")
def create_mission(mission: CreateMission):
    """Save a new mission configuration."""
    import uuid
    mission_id = str(uuid.uuid4())
    db.add_mission(mission_id, mission.name, mission.geometries)
    return {"status": "ok", "mission_id": mission_id}

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
