# Ghost Sentry

**Autonomous ISR & Anomaly Detection Pipeline for Lattice**

> [!IMPORTANT]
> This project is a technical demonstration of geospatial AI and autonomous cueing within the Anduril Lattice ecosystem. It is designed for edge deployment and tactical interoperability.

---

## Overview

Ghost Sentry processes geospatial optical imagery (Sentinel-2) to detect tactical assets and autonomously generate cueing tasks. It acts as an "Autonomous Sentry" that bridges the gap between passive observation and active mission tasking.

### Key Features

| Capability | Description |
|------------|-------------|
| **Tactical Detection** | YOLOv8-based detection of aircraft, vehicles, and vessels |
| **Entity Correlation** | Multi-sensor fusion with spatial/temporal track correlation |
| **Threat Classification** | Behavioral threat assessment (loitering, formation detection) |
| **Track Lifecycle** | TENTATIVE → FIRM → STALE → DROPPED state management |
| **Autonomous Cueing** | Auto-generates verification tasks with multi-criteria asset assignment |
| **Lattice-Ready** | SDK-compatible entity schemas with dev/prod adapter pattern |
| **Tactical Interop** | Real-time CoT XML streaming for ATAK/WinTAK |
| **Edge UI** | Lightweight Textual TUI for constrained environments |

---

## Tech Stack

- **AI**: PyTorch + Ultralytics (YOLOv8)
- **Framework**: FastAPI (REST + WebSocket)
- **Lattice**: SDK-compatible adapter pattern
- **Geospatial**: Rasterio + Shapely
- **TUI**: Textual
- **CI/CD**: GitHub Actions

---

## Quick Start

### Prerequisites
- Python 3.11+
- Virtual environment

### Setup
```bash
cd ghost-sentry
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Run Tests
```bash
pytest tests/ -v
```

### Run Detection Demo (Mock Mode)
```bash
python -m ghost_sentry.cli dummy.jpg --mock
```

### Start API & CoT Stream
```bash
uvicorn ghost_sentry.api:app --reload

# View tracks
curl http://localhost:8000/v1/tracks

# View CoT XML
curl http://localhost:8000/v1/tracks/cot
```

### Launch Operator Console
```bash
python -m ghost_sentry.console.app
```

---

## API Reference

### REST Endpoints (v1)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/v1/tracks` | All current tracks |
| GET | `/v1/tracks/{id}/history` | Track position history |
| GET | `/v1/tracks/cot` | Tracks as CoT XML |
| GET | `/v1/tasks` | Task queue |
| PATCH | `/v1/tasks/{id}/state` | Update task state |
| POST | `/v1/tasks/{id}/ack` | Acknowledge task |
| GET | `/v1/assets` | Available assets |
| GET | `/v1/timeline` | Unified event timeline |

### WebSocket Streams

| Endpoint | Description |
|----------|-------------|
| `/ws/tracks` | Real-time track/task JSON stream |
| `/ws/cot` | Real-time CoT XML stream |

---

## Repository Structure

```text
ghost-sentry/
├── docs/                 # Architecture, Integration, Roadmap
│   ├── ARCHITECTURE.md
│   ├── INTEGRATION.md
│   └── ROADMAP.md
├── src/ghost_sentry/
│   ├── core/
│   │   ├── detector.py      # YOLOv8 detection
│   │   ├── correlation.py   # Entity matching & lifecycle
│   │   ├── threat.py        # Threat classification
│   │   ├── analytics.py     # Loitering & formation detection
│   │   ├── sentry.py        # Autonomous cueing logic
│   │   └── assets.py        # Asset management
│   ├── lattice/
│   │   ├── adapter.py       # Lattice SDK adapter
│   │   └── entities.py      # Track/Task schemas
│   ├── output/
│   │   └── cot.py           # Cursor-on-Target XML
│   ├── console/
│   │   └── app.py           # Textual TUI
│   └── api.py               # FastAPI application
├── tests/                    # 51 test cases
├── .github/workflows/        # CI/CD
└── docker-compose.yml        # Container deployment
```

---

## Documentation

- [Architecture](docs/ARCHITECTURE.md) - System design and component flow
- [Integration](docs/INTEGRATION.md) - Lattice SDK integration guide
- [Roadmap](docs/ROADMAP.md) - Future development plans

---

## License

MIT License - See [LICENSE](LICENSE)

---

*Ghost Sentry - Automating the Edge for National Security.*
