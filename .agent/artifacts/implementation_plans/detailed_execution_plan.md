# Detailed Execution Plan: Ghost Sentry

**Role**: Executor (Gemini Flash)
**Context**: This plan breaks down the `implementation_plan.md` into atomic, verifiable steps.
**Framework Reference**: Follow `.agent/workflows/feature-development.md` or `AGENTIC_FRAMEWORK.md`.

---

## Phase 0: Scaffolding & Environment Setup
**Goal**: Initialize repository, dependency management, and environment.

### Step 0.1: Repository Structure
Create the following directory tree inside the workspace root:
```text
ghost-sentry/
├── data/samples/
├── docs/
├── src/ghost_sentry/
│   ├── core/
│   ├── lattice/
│   ├── output/
│   ├── console/
│   └── scripts/
├── tests/
└── deploy/
```
**Action**: 
```bash
mkdir -p ghost-sentry/{data/samples,docs,tests,deploy}
mkdir -p ghost-sentry/src/ghost_sentry/{core,lattice,output,console,scripts}
```

### Step 0.2: Create `__init__.py` Files
```bash
touch ghost-sentry/src/ghost_sentry/__init__.py
touch ghost-sentry/src/ghost_sentry/core/__init__.py
touch ghost-sentry/src/ghost_sentry/lattice/__init__.py
touch ghost-sentry/src/ghost_sentry/output/__init__.py
touch ghost-sentry/src/ghost_sentry/console/__init__.py
touch ghost-sentry/src/ghost_sentry/scripts/__init__.py
```

### Step 0.3: Virtual Environment
```bash
cd ghost-sentry
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### Step 0.4: Python Configuration
Create `ghost-sentry/pyproject.toml`:
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "ghost-sentry"
version = "0.1.0"
dependencies = [
    "fastapi>=0.109.0",
    "uvicorn>=0.27.0",
    "typer>=0.9.0",
    "rich>=13.0.0",
    "textual>=0.47.0",
    "rasterio>=1.3.0",
    "shapely>=2.0.0",
    "ultralytics>=8.1.0",
    "pydantic>=2.5.0",
]

[project.optional-dependencies]
dev = ["pytest", "black", "isort", "mypy"]

[tool.hatch.build.targets.wheel]
packages = ["src/ghost_sentry"]
```

### Step 0.5: Git Init
```bash
git init
```
Create `.gitignore`:
```text
.venv/
__pycache__/
*.pyc
.mypy_cache/
data/samples/*.tif
data/samples/*.jpg
data/samples/*.png
*.pt
.DS_Store
```

### Step 0.6: Install Dependencies
```bash
pip install -e ".[dev]"
```

**Phase 0 Verification**:
```bash
python -c "import ghost_sentry; print('OK')"
```

---

## Phase 1: Data Layer & Basic Inference
**Goal**: Load an image and detect objects using YOLOv8.

### Step 1.1: Sample Data Strategy
Create `data/samples/README.md`:
```markdown
# Sample Data

For demo purposes, place satellite/aerial images here.

**Quick Option**: Download a free sample from Wikimedia Commons:
- Search "satellite view airport" or "aerial view military base"

**For Testing Without Images**: Phase 1.3 includes a mock mode.
```

Create `data/samples/mock_detections.json` for downstream testing:
```json
[
  {"label": "airplane", "confidence": 0.92, "bbox": [100, 150, 200, 250], "geo_location": [33.9425, -118.4081]},
  {"label": "truck", "confidence": 0.78, "bbox": [300, 400, 380, 460], "geo_location": [33.9430, -118.4075]},
  {"label": "car", "confidence": 0.88, "bbox": [500, 200, 560, 240], "geo_location": [33.9428, -118.4090]}
]
```

### Step 1.2: Detection Model (`core/detector.py`)
**Model**: Use `yolov8n.pt` (nano, 6MB) for fast iteration. Upgrade to `yolov8m.pt` for production.

**COCO Classes to Watch**: `airplane`, `truck`, `car`, `boat`, `bus` (these map to tactical targets).

```python
"""Object detection using YOLOv8."""
from pathlib import Path
from typing import Optional
from pydantic import BaseModel
from ultralytics import YOLO

class Detection(BaseModel):
    """A single detected object."""
    label: str
    confidence: float
    bbox: tuple[int, int, int, int]  # x1, y1, x2, y2
    geo_location: Optional[tuple[float, float]] = None  # lat, lon

class ObjectDetector:
    """YOLOv8-based object detector."""
    
    TACTICAL_CLASSES = {"airplane", "truck", "car", "boat", "bus"}
    
    def __init__(self, model_path: str = "yolov8n.pt"):
        self.model = YOLO(model_path)
    
    def detect(self, image_path: str) -> list[Detection]:
        """Run detection on an image."""
        results = self.model(image_path)
        detections = []
        for result in results:
            for box in result.boxes:
                label = result.names[int(box.cls)]
                if label in self.TACTICAL_CLASSES:
                    detections.append(Detection(
                        label=label,
                        confidence=float(box.conf),
                        bbox=tuple(map(int, box.xyxy[0].tolist())),
                        geo_location=None  # Populated by geo module if available
                    ))
        return detections
```

### Step 1.3: Geo Utilities (`core/geo.py`)
```python
"""Geospatial coordinate utilities."""
from pathlib import Path
from typing import Optional
import rasterio
from rasterio.transform import xy

def pixel_to_latlon(
    image_path: str, 
    pixel_x: int, 
    pixel_y: int
) -> Optional[tuple[float, float]]:
    """Convert pixel coordinates to lat/lon if image has CRS metadata."""
    try:
        with rasterio.open(image_path) as src:
            if src.crs is None:
                return None
            lon, lat = xy(src.transform, pixel_y, pixel_x)
            return (lat, lon)
    except Exception:
        return None

# Mock coordinates for demo (LAX airport area)
MOCK_CENTER = (33.9425, -118.4081)

def mock_geo_location() -> tuple[float, float]:
    """Return mock coordinates for testing."""
    import random
    lat = MOCK_CENTER[0] + random.uniform(-0.01, 0.01)
    lon = MOCK_CENTER[1] + random.uniform(-0.01, 0.01)
    return (lat, lon)
```

### Step 1.4: CLI Demo (`cli.py`)
```python
"""Ghost Sentry CLI."""
import json
import typer
from pathlib import Path
from ghost_sentry.core.detector import ObjectDetector, Detection
from ghost_sentry.core.geo import mock_geo_location

app = typer.Typer()

@app.command()
def detect(
    image_path: str = typer.Argument(..., help="Path to image"),
    mock: bool = typer.Option(False, help="Use mock detections for testing")
):
    """Detect objects in an image."""
    if mock:
        # Load pre-made mock data
        mock_file = Path(__file__).parent.parent.parent.parent / "data/samples/mock_detections.json"
        if mock_file.exists():
            data = json.loads(mock_file.read_text())
            typer.echo(json.dumps(data, indent=2))
            return
    
    detector = ObjectDetector()
    detections = detector.detect(image_path)
    
    # Add mock geo if not available
    for d in detections:
        if d.geo_location is None:
            d.geo_location = mock_geo_location()
    
    typer.echo(json.dumps([d.model_dump() for d in detections], indent=2))

if __name__ == "__main__":
    app()
```

**Phase 1 Verification**:
```bash
# Test mock mode (no image needed)
python -m ghost_sentry.cli detect dummy.jpg --mock

# Test real detection (requires image)
python -m ghost_sentry.cli detect data/samples/test.jpg
```

---

## Phase 2: Lattice Adapter
**Goal**: Wrap detections in Lattice SDK data structures.

### Step 2.1: SDK Setup
```bash
pip install anduril-lattice-sdk
```
**Contingency**: If this fails (404 or access denied), proceed to Step 2.2 using Pydantic stubs. Do not block.

### Step 2.2: Lattice Stubs (`lattice/entities.py`)
Create Pydantic models mirroring Lattice schemas:
```python
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
            provenance=LatticeProvenance()
        )
```

### Step 2.3: Adapter (`lattice/adapter.py`)
```python
"""Lattice connection adapter."""
import json
from pathlib import Path
from ghost_sentry.lattice.entities import LatticeTrack

class LatticeConnector:
    """Publishes entities to Lattice (or local log in dev mode)."""
    
    def __init__(self, mode: str = "dev", log_path: str = "lattice_events.jsonl"):
        self.mode = mode
        self.log_path = Path(log_path)
    
    def publish_track(self, track: LatticeTrack) -> None:
        if self.mode == "dev":
            with self.log_path.open("a") as f:
                f.write(json.dumps({"type": "track", "data": track.model_dump()}) + "\n")
        else:
            # TODO: Real Lattice SDK call
            raise NotImplementedError("Production mode requires Lattice SDK access")
    
    def publish_task(self, task: dict) -> None:
        if self.mode == "dev":
            with self.log_path.open("a") as f:
                f.write(json.dumps({"type": "task", "data": task}) + "\n")
```

**Phase 2 Verification**:
```bash
python -c "
from ghost_sentry.core.detector import Detection
from ghost_sentry.lattice.entities import TrackBuilder
from ghost_sentry.lattice.adapter import LatticeConnector

d = Detection(label='airplane', confidence=0.9, bbox=(0,0,100,100), geo_location=(33.94, -118.40))
track = TrackBuilder.from_detection(d)
connector = LatticeConnector()
connector.publish_track(track)
print('Track published to lattice_events.jsonl')
"
```

---

## Phase 3: Autonomous Cueing Logic
**Goal**: Auto-generate Tasks for high-confidence detections.

### Step 3.1: Sentry Logic (`core/sentry.py`)
```python
"""Ghost Sentry autonomous decision engine."""
from ghost_sentry.core.detector import Detection
from ghost_sentry.lattice.entities import TrackBuilder
from ghost_sentry.lattice.adapter import LatticeConnector

# Tactical labels from COCO that warrant autonomous cueing
HIGH_PRIORITY_LABELS = {"airplane", "truck", "boat"}
CONFIDENCE_THRESHOLD = 0.85

def process_detections(
    detections: list[Detection],
    connector: LatticeConnector
) -> dict:
    """Process detections and generate Tracks + Tasks."""
    stats = {"tracks": 0, "tasks": 0}
    
    for detection in detections:
        # Always publish track
        track = TrackBuilder.from_detection(detection)
        connector.publish_track(track)
        stats["tracks"] += 1
        
        # Auto-cue for high-priority, high-confidence detections
        if (detection.label in HIGH_PRIORITY_LABELS and 
            detection.confidence >= CONFIDENCE_THRESHOLD):
            task = {
                "type": "VERIFICATION_REQUEST",
                "target_entity_id": track.entityId,
                "description": f"Confirm {detection.label} at {detection.geo_location}",
                "priority": "HIGH" if detection.label == "airplane" else "MEDIUM"
            }
            connector.publish_task(task)
            stats["tasks"] += 1
    
    return stats
```

**Phase 3 Verification**:
```bash
python -c "
from ghost_sentry.core.detector import Detection
from ghost_sentry.core.sentry import process_detections
from ghost_sentry.lattice.adapter import LatticeConnector

detections = [
    Detection(label='airplane', confidence=0.92, bbox=(0,0,100,100), geo_location=(33.94, -118.40)),
    Detection(label='car', confidence=0.75, bbox=(0,0,50,50), geo_location=(33.95, -118.41)),
]
connector = LatticeConnector()
stats = process_detections(detections, connector)
print(f'Published {stats[\"tracks\"]} tracks, {stats[\"tasks\"]} tasks')
"
```

---

## Phase 4: CoT & Output APIs

### Step 4.1: CoT Generator (`output/cot.py`)
```python
"""Cursor-on-Target (CoT) XML generator."""
import uuid
from datetime import datetime, timezone
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
    stale = now.replace(minute=now.minute + 5)
    
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
```

### Step 4.2: FastAPI Backend (`api.py`)
```python
"""Ghost Sentry REST API."""
from fastapi import FastAPI
from fastapi.responses import Response
from ghost_sentry.core.detector import ObjectDetector, Detection
from ghost_sentry.core.sentry import process_detections
from ghost_sentry.lattice.adapter import LatticeConnector
from ghost_sentry.output.cot import to_cursor_on_target
import json
from pathlib import Path

app = FastAPI(title="Ghost Sentry", version="0.1.0")
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
            confidence=0.9,
            bbox=(0,0,0,0),
            geo_location=(
                track["location"]["position"]["latitudeDegrees"],
                track["location"]["position"]["longitudeDegrees"]
            )
        )
        cot_events.append(to_cursor_on_target(d))
    return Response(content="\n".join(cot_events), media_type="application/xml")
```

**Phase 4 Verification**:
```bash
uvicorn ghost_sentry.api:app --reload &
curl http://localhost:8000/health
curl http://localhost:8000/tracks
curl http://localhost:8000/tracks/cot
```

---

## Phase 5: Operator Console

### Step 5.1: Textual TUI (`console/app.py`)
Build a terminal UI showing live events. (Detailed implementation deferred — create placeholder that reads from log.)

```python
"""Ghost Sentry Operator Console."""
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Log
from textual.containers import Horizontal
import json
from pathlib import Path

class SentryConsole(App):
    """The Ghost Sentry operator console."""
    
    BINDINGS = [("q", "quit", "Quit"), ("r", "refresh", "Refresh")]
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            DataTable(id="tracks"),
            Log(id="logs"),
        )
        yield Footer()
    
    def on_mount(self) -> None:
        table = self.query_one("#tracks", DataTable)
        table.add_columns("ID", "Label", "Confidence", "Location")
        self.load_tracks()
    
    def load_tracks(self) -> None:
        table = self.query_one("#tracks", DataTable)
        log_widget = self.query_one("#logs", Log)
        log = Path("lattice_events.jsonl")
        if log.exists():
            for line in log.read_text().splitlines():
                event = json.loads(line)
                if event["type"] == "track":
                    t = event["data"]
                    table.add_row(
                        t["entityId"][:8],
                        t["ontology"]["platform_type"],
                        "0.9",
                        f"{t['location']['position']['latitudeDegrees']:.4f}"
                    )
                elif event["type"] == "task":
                    log_widget.write_line(f"[TASK] {event['data']['description']}")
    
    def action_refresh(self) -> None:
        self.load_tracks()

def main():
    app = SentryConsole()
    app.run()

if __name__ == "__main__":
    main()
```

**Phase 5 Verification**:
```bash
python -m ghost_sentry.console.app
```

---

## Execution Instructions for Flash

1. **Read this plan strictly.** One phase at a time.
2. **Verify after every phase.** Run the verification commands.
3. **If SDK install fails**: Use the Pydantic stubs immediately. Do not block.
4. **Log Decisions**: If you make an architectural choice (e.g., change model size), append to `.agent/traces/decision_log.jsonl`:
   ```json
   {"timestamp": "...", "context": "...", "decision": "...", "model": "Gemini Flash"}
   ```
5. **Update active_context.md** before stopping work with current status and next steps.
