# Ghost Sentry

**Autonomous ISR & Anomaly Detection Pipeline for Lattice**

> [!IMPORTANT]
> This project is a technical demonstration of geospatial AI and autonomous cueing within the Anduril Lattice ecosystem. It is designed for edge deployment and tactical interoperability.

---

## 🚀 Overview

Ghost Sentry process geospatial optical imagery (Sentinel-2) to detect tactical assets and autonomously generate cueing tasks. It acts as an "Autonomous Sentry" that bridge the gap between passive observation and active mission tasking.

### Key Features
- **Tactical Detection**: YOLOv8-based detection of aircraft, vehicles, and vessels.
- **Lattice-Ready**: Built using the `anduril-lattice-sdk` (v4.0.0) and Lattice Data Schemas.
- **Autonomous Cueing**: Automatically generates verification tasks for high-confidence detections.
- **Tactical Interop**: Real-time Cursor-on-Target (CoT) XML output for ATAK/WinTAK.
- **Edge UI**: Lightweight TUI console for operators in constrained environments.

---

## 🛠️ Tech Stack
- **AI**: PyTorch + Ultralytics (YOLOv8)
- **Framework**: FastAPI (REST/CoT)
- **Lattice**: `anduril-lattice-sdk`
- **Geospatial**: Rasterio + Shapely
- **TUI**: Textual

---

## 🏃 Quick Start

### 1. Prerequisites
- Python 3.11+
- Virtual environment support

### 2. Setup
```bash
# Clone the repository (if applicable)
cd ghost-sentry

# Initialize environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"
```

### 3. Run Detection Demo (Mock Mode)
```bash
python -m ghost_sentry.cli dummy.jpg --mock
```

### 4. Start API & CoT Stream
```bash
uvicorn ghost_sentry.api:app --reload
# View CoT output:
curl http://localhost:8000/tracks/cot
```

### 5. Launch Operator Console
```bash
python -m ghost_sentry.console.app
```

---

## 📂 Repository Structure
```text
ghost-sentry/
├── docs/                 # Architecture, Integration, Roadmap
├── src/ghost_sentry/
│   ├── core/             # Detection & Sentry logic
│   ├── lattice/          # Lattice Adapter & Entities
│   ├── output/           # CoT & XML generation
│   └── console/          # Textual TUI
├── data/samples/         # Sample imagery & mock data
└── tests/                # Verification suite
```

---

## 🗺️ Roadmap
See [ROADMAP.md](docs/ROADMAP.md) for future directions, including SAR integration and multi-platform cueing.

---

*Ghost Sentry - Automating the Edge for National Security.*
