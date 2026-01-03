# Ghost Sentry: Unified Implementation Plan

> Reconciled plan incorporating Gemini's architecture review and Claude's refinements.

## Project Overview

**Name:** Ghost Sentry  
**Tagline:** Autonomous ISR & Anomaly Detection Pipeline for Lattice  
**Goal:** Portfolio project demonstrating geospatial AI + Lattice integration for Anduril application

---

## Delivery Strategy: Two Tracks

| Track | Purpose | Scope |
|-------|---------|-------|
| **The Demo** | Prove execution | Working end-to-end system with cached data |
| **The Design Doc** | Prove architecture | Full system design including future phases |

---

## Demo Scope (v1)

### Core Pipeline
```
[Cached Satellite Image] → [YOLO Inference] → [Track Generation] → [Lattice Adapter] → [Operator Console]
                                                      ↓
                                              [CoT XML Output]
```

### Components

#### 1. Data Layer
- **Source:** Pre-cached Sentinel-2 optical tiles (RGB + NIR)
- **Format:** GeoTIFF or PNG with georeference metadata
- **Scope:** 5-10 sample regions (include 1 military-relevant area like an airfield)

#### 2. Inference Engine
- **Model:** YOLOv8 fine-tuned on xView or DIOR dataset
- **Targets:** Vehicles, aircraft, buildings, ships
- **Output:** Bounding boxes with confidence scores + lat/lon

#### 3. Lattice Adapter
- **SDK:** `anduril-lattice-sdk` from PyPI
- **Interface:** Implement against real Protobuf types
- **Publishes:** 
  - `Track` entities (detected objects)
  - `Task` proposals (auto-generated cue requests)
- **Backend:** Configurable—local SQLite for dev, Lattice mesh for prod

#### 4. Autonomous Cueing
- **Logic:** When confidence > threshold, generate a `Task` to cue confirmation
- **Example:** "Vehicle detected at [lat,lon] with 85% confidence. Task: Request drone flyby for visual confirmation."

#### 5. Operator Console
- **Tech:** Terminal UI (Rich/Textual) or minimal web (FastAPI + HTMX)
- **Features:**
  - View pending Tracks
  - Confirm/reject detections
  - Manually trigger region scan
  - View generated Tasks

#### 6. CoT Output
- **Endpoint:** `/tracks/cot`
- **Format:** Standard Cursor-on-Target XML
- **Interop:** Compatible with ATAK and similar tactical tools

---

## Design Doc Scope

### Architecture Sections
1. **System Overview** — High-level data flow diagram
2. **Lattice Integration** — API contracts, entity schemas, adapter pattern
3. **Edge Deployment** — Docker constraints, offline operation, sync-on-reconnect
4. **Operator Workflow** — Human-machine teaming, confirmation loops
5. **Phase 2: SAR Integration** — Processing requirements, commercial partners
6. **Phase 3: Multi-Sensor Fusion** — Combining optical, SAR, ground sensors
7. **Failure Modes** — Network degradation, model uncertainty, fallback behaviors

---

## Repository Structure

```
ghost-sentry/
├── README.md
├── docs/
│   ├── ARCHITECTURE.md
│   ├── LATTICE_INTEGRATION.md
│   └── ROADMAP.md
├── data/
│   └── samples/              # Cached satellite tiles
├── src/
│   └── ghost_sentry/
│       ├── __init__.py
│       ├── core/
│       │   ├── detector.py   # YOLO inference
│       │   └── geo.py        # Coordinate transforms
│       ├── lattice/
│       │   ├── adapter.py    # Lattice SDK wrapper
│       │   ├── entities.py   # Track/Task builders
│       │   └── mock_backend.py
│       ├── output/
│       │   └── cot.py        # Cursor-on-Target generator
│       └── console/
│           └── app.py        # Operator UI
├── tests/
├── deploy/
│   ├── Dockerfile
│   ├── Dockerfile.edge       # Constrained resources
│   └── docker-compose.yml
├── Makefile
└── pyproject.toml
```

---

## Tech Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Language | Python 3.11+ | Lattice SDK available; CV ecosystem |
| ML Framework | PyTorch + Ultralytics | YOLOv8; better community than TF |
| Lattice SDK | `anduril-lattice-sdk` | Official Protobuf types |
| API | FastAPI | Async, modern, good for gRPC bridge |
| Console | Textual or HTMX | Minimal deps; impressive UX |
| Containerization | Docker | Edge deployment story |
| Geospatial | Rasterio + Shapely | Standard Python geo stack |

---

## Milestones

| Phase | Deliverable | Effort |
|-------|-------------|--------|
| 1 | Data caching + basic inference | 1-2 days |
| 2 | Lattice adapter (real SDK types) | 2-3 days |
| 3 | Autonomous Task generation | 1 day |
| 4 | CoT output endpoint | 0.5 day |
| 5 | Operator Console | 2-3 days |
| 6 | Design Doc | 1-2 days |
| 7 | Polish + README | 1 day |

**Total:** ~10-14 days of focused work

---

## Success Criteria

1. ✅ Demo runs end-to-end with cached data
2. ✅ Publishes valid Lattice Track entities using SDK types
3. ✅ Auto-generates Task proposals for high-confidence detections
4. ✅ Outputs valid CoT XML
5. ✅ Operator can view/confirm tracks via console
6. ✅ Design doc covers edge deployment and SAR roadmap
7. ✅ Code is clean, documented, and repository is professional
