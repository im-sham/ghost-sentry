import os
import logging
import asyncio
from typing import List, Optional, Literal

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, APIRouter
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ghost_sentry.core.detector import Detection
from ghost_sentry.core import db, events
from ghost_sentry.lattice.adapter import LatticeConnector
from ghost_sentry.output.cot import to_cursor_on_target

logger = logging.getLogger(__name__)

app = FastAPI(title="Ghost Sentry", version="0.2.0")

v1_router = APIRouter(prefix="/v1")


class Geometry(BaseModel):
    type: Literal["polygon", "linestring", "point"]
    coords: List[List[float]]
    label: str


class CreateMission(BaseModel):
    name: str
    geometries: List[Geometry]


_track_subscribers: List[asyncio.Queue] = []
_cot_subscribers: List[asyncio.Queue] = []


async def broadcast_track(event: events.TrackEvent):
    for queue in _track_subscribers:
        await queue.put(event.data)


async def broadcast_cot(cot_xml: str):
    for queue in _cot_subscribers:
        await queue.put(cot_xml)


def _schedule_broadcast(event: events.TrackEvent):
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(broadcast_track(event))
    except RuntimeError:
        pass


@app.on_event("startup")
def startup_event():
    db.init_db()
    events.subscribe(_schedule_broadcast)


CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:5173,http://localhost:5174").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

connector = LatticeConnector()


@app.get("/")
def root():
    return {
        "name": "Ghost Sentry",
        "version": "0.2.0",
        "description": "Autonomous ISR & Anomaly Detection Pipeline for Lattice",
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "tracks": "/v1/tracks",
            "tasks": "/v1/tasks",
            "assets": "/v1/assets",
            "timeline": "/v1/timeline",
            "cot": "/v1/tracks/cot",
            "websocket_tracks": "/ws/tracks",
            "websocket_cot": "/ws/cot"
        }
    }


@app.get("/health")
def health():
    return {"status": "ok", "version": "0.2.0"}


@app.websocket("/ws/tracks")
async def websocket_tracks(websocket: WebSocket):
    await websocket.accept()
    queue: asyncio.Queue = asyncio.Queue()
    _track_subscribers.append(queue)
    try:
        tracks = db.get_tracks()
        for track in tracks:
            await websocket.send_json(track)
        
        from ghost_sentry.core import assets
        for asset in assets.MOCK_ASSETS:
            await websocket.send_json({"type": "asset_telemetry", **asset.to_dict()})
            
        while True:
            data = await queue.get()
            await websocket.send_json(data)
    except WebSocketDisconnect:
        logger.debug("WebSocket client disconnected from /ws/tracks")
    except Exception as e:
        logger.warning(f"WebSocket error on /ws/tracks: {e}")
    finally:
        _track_subscribers.remove(queue)


@app.websocket("/ws/cot")
async def websocket_cot(websocket: WebSocket):
    await websocket.accept()
    queue: asyncio.Queue = asyncio.Queue()
    _cot_subscribers.append(queue)
    try:
        tracks = db.get_tracks()
        for track in tracks:
            cot_xml = _track_to_cot(track)
            if cot_xml:
                await websocket.send_text(cot_xml)
        
        while True:
            cot_xml = await queue.get()
            await websocket.send_text(cot_xml)
    except WebSocketDisconnect:
        logger.debug("WebSocket client disconnected from /ws/cot")
    except Exception as e:
        logger.warning(f"WebSocket error on /ws/cot: {e}")
    finally:
        _cot_subscribers.remove(queue)


def _track_to_cot(track: dict) -> Optional[str]:
    try:
        d = Detection(
            label=track["ontology"]["platform_type"].lower(),
            confidence=track.get("confidence", 0.9),
            bbox=(0, 0, 0, 0),
            geo_location=(
                track["location"]["position"]["latitudeDegrees"],
                track["location"]["position"]["longitudeDegrees"]
            )
        )
        return to_cursor_on_target(d)
    except (KeyError, TypeError):
        return None


@v1_router.get("/tracks")
def get_tracks():
    return db.get_tracks()


@v1_router.get("/tracks/{entity_id}/history")
def get_track_history(entity_id: str, limit: int = 10):
    return db.get_track_history(entity_id, limit=limit)


@v1_router.get("/tracks/cot", response_class=Response)
def get_tracks_cot():
    tracks = db.get_tracks()
    cot_events = [cot for t in tracks if (cot := _track_to_cot(t)) is not None]
    return Response(content="\n".join(cot_events), media_type="application/xml")


@v1_router.get("/tasks")
def get_tasks(state: Optional[str] = None):
    return db.get_tasks(state=state)


@v1_router.patch("/tasks/{task_id}/state")
def update_task_state(task_id: str, state: str):
    db.update_task_state(task_id, state)
    all_tasks = db.get_tasks()
    task = next((t for t in all_tasks if t["id"] == task_id), None)
    if task and task.get("entity_id"):
        events.publish(events.TrackEvent(
            entity_id=task["entity_id"],
            data={"type": "task_update", "task_id": task_id, "state": state}
        ))
    return {"status": "updated", "task_id": task_id, "state": state}


@v1_router.post("/tasks/{task_id}/ack")
def acknowledge_task(task_id: str, operator_id: Optional[str] = None):
    all_tasks = db.get_tasks()
    task = next((t for t in all_tasks if t["id"] == task_id), None)
    if not task:
        return {"status": "error", "message": "Task not found"}
    
    if task["state"] == "pending":
        db.update_task_state(task_id, "assigned")
    
    if task.get("entity_id"):
        events.publish(events.TrackEvent(
            entity_id=task["entity_id"],
            data={
                "type": "task_ack",
                "task_id": task_id,
                "operator_id": operator_id or "unknown",
                "acknowledged_at": __import__("datetime").datetime.now(__import__("datetime").UTC).isoformat()
            }
        ))
    
    return {"status": "acknowledged", "task_id": task_id}


@v1_router.get("/timeline")
def get_timeline():
    return db.get_latest_events(limit=100)


@v1_router.get("/assets")
def get_assets():
    from ghost_sentry.core import assets
    return [a.to_dict() for a in assets.MOCK_ASSETS]


@v1_router.post("/assets/telemetry")
async def update_asset_telemetry(asset_id: str, lat: float, lon: float, battery: float, signal: float):
    from ghost_sentry.core import assets
    asset = next((a for a in assets.MOCK_ASSETS if a.id == asset_id), None)
    if not asset:
        return {"status": "error", "message": "Asset not found"}
    
    asset.update_telemetry(lat, lon, battery, signal)
    
    events.publish(events.TrackEvent(
        entity_id=asset_id,
        data={"type": "asset_telemetry", **asset.to_dict()}
    ))
    
    return {"status": "ok"}


@v1_router.get("/missions")
def get_missions():
    return db.get_missions()


@v1_router.post("/missions")
def create_mission(mission: CreateMission):
    import uuid
    mission_id = str(uuid.uuid4())
    geometries_dict = [g.model_dump() for g in mission.geometries]
    db.add_mission(mission_id, mission.name, geometries_dict)
    return {"status": "ok", "mission_id": mission_id}


app.include_router(v1_router)


@app.get("/tracks")
def get_tracks_legacy():
    return db.get_tracks()


@app.get("/tasks")
def get_tasks_legacy(state: Optional[str] = None):
    return db.get_tasks(state=state)


@app.patch("/tasks/{task_id}/state")
def update_task_state_legacy(task_id: str, state: str):
    return update_task_state(task_id, state)


@app.get("/timeline")
def get_timeline_legacy():
    return db.get_latest_events(limit=100)


@app.get("/assets")
def get_assets_legacy():
    from ghost_sentry.core import assets
    return [a.to_dict() for a in assets.MOCK_ASSETS]


@app.get("/missions")
def get_missions_legacy():
    return db.get_missions()


@app.get("/tracks/cot", response_class=Response)
def get_tracks_cot_legacy():
    return get_tracks_cot()
