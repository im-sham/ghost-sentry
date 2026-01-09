# Ghost Sentry Architecture

## System Overview

Ghost Sentry is an autonomous ISR (Intelligence, Surveillance, Reconnaissance) pipeline designed for integration with Anduril's Lattice ecosystem. It processes geospatial imagery to detect tactical assets and autonomously generates cueing tasks for verification.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           GHOST SENTRY PIPELINE                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌────────────┐ │
│  │   SENSORS    │───▶│  DETECTION   │───▶│   FUSION     │───▶│  LATTICE   │ │
│  │              │    │   ENGINE     │    │   ENGINE     │    │  ADAPTER   │ │
│  │ • Optical    │    │              │    │              │    │            │ │
│  │ • SAR        │    │ • YOLOv8     │    │ • Optical+SAR│    │ • Tracks   │ │
│  │ • AIS/ADS-B  │    │ • Tactical   │    │ • Correlation│    │ • Tasks    │ │
│  │              │    │   Filtering  │    │ • Dedup      │    │ • Events   │ │
│  └──────────────┘    └──────────────┘    └──────────────┘    └─────┬──────┘ │
│                                                                     │        │
│  ┌──────────────────────────────────────────────────────────────────┼──────┐ │
│  │                        AUTONOMOUS CUEING                         │      │ │
│  │  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐            │      │ │
│  │  │  ANALYTICS  │   │   THREAT    │   │    ASSET    │◀───────────┘      │ │
│  │  │             │   │ CLASSIFIER  │   │  ASSIGNMENT │                   │ │
│  │  │ • Loitering │   │             │   │             │                   │ │
│  │  │ • Formation │   │ • Behavior  │   │ • Proximity │                   │ │
│  │  │ • Anomaly   │   │ • Type      │   │ • Battery   │                   │ │
│  │  └─────────────┘   └─────────────┘   └─────────────┘                   │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────────┐│
│  │                           OUTPUT LAYER                                   ││
│  │  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐  ││
│  │  │  REST API   │   │  WebSocket  │   │  CoT/ATAK   │   │  TUI Console│  ││
│  │  │  /v1/*      │   │  /ws/tracks │   │  /ws/cot    │   │  Textual    │  ││
│  │  └─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘  ││
│  └──────────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Detection Engine (`core/detector.py`)

YOLOv8-based object detection with tactical class filtering.

```python
TACTICAL_CLASSES = {"airplane", "truck", "car", "boat", "bus"}
```

**Key Features:**
- Real-time inference on imagery
- Confidence scoring per detection
- Bounding box extraction for geo-registration

### 2. Fusion Engine (`core/fusion.py`)

Multi-modal sensor fusion combining optical and SAR detections.

**Fusion Logic:**
- Optical detections above confidence threshold are prioritized
- SAR detections provide all-weather/all-day capability
- Source provenance is preserved for audit

### 3. Entity Correlation (`core/correlation.py`)

Track correlation and deduplication across sensor observations.

**Correlation Criteria:**
- Spatial proximity (configurable radius)
- Temporal window (track freshness)
- Type matching with confidence weighting

**Entity Lifecycle:**
```
TENTATIVE ──▶ FIRM ──▶ STALE ──▶ DROPPED
    │           │         │
    └───────────┴─────────┴──── (observations refresh state)
```

### 4. Threat Classifier (`core/threat.py`)

Behavioral threat assessment based on track patterns.

**Threat Levels:**
| Level | Criteria |
|-------|----------|
| CRITICAL | Aircraft + loitering + near critical infrastructure |
| HIGH | High-priority type + high confidence |
| MEDIUM | Loitering behavior OR formation detected |
| LOW | Standard detection, no anomalies |

### 5. Lattice Adapter (`lattice/adapter.py`)

Abstraction layer for Lattice SDK integration.

**Modes:**
- `dev`: SQLite persistence + event bus
- `prod`: gRPC to Lattice service (requires credentials)

**Published Entities:**
- `Track`: Detected object with location, ontology, confidence
- `Task`: Verification request with priority and assignment

### 6. Asset Management (`core/assets.py`)

Multi-criteria asset assignment for task execution.

**Scoring Formula:**
```
score = 0.4 * distance_score + 0.3 * battery + 0.3 * signal
```

### 7. Analytics (`core/analytics.py`)

Behavioral pattern detection.

- **Loitering**: Entity stays within 50m radius for 5+ observations
- **Formation**: Cluster of 3+ entities moving with similar heading

## Data Flow

### Detection → Track Pipeline

```
1. Image ingested (optical/SAR)
2. YOLOv8 inference → raw detections
3. Geo-registration (pixel → lat/lon)
4. Fusion engine merges sources
5. Entity correlation (new vs. existing track)
6. Lifecycle state update
7. Threat classification
8. Lattice Track published
```

### Track → Task Pipeline

```
1. Track meets cueing criteria:
   - High-priority type + confidence ≥ 0.85
   - Loitering behavior detected
   - Formation detected
   - Threat level ≥ MEDIUM
2. Debounce check (10-min window)
3. Asset assignment (best available)
4. Task published to Lattice
5. Operator notification via TUI/WebSocket
```

## Database Schema

### Events Table (Audit Log)
```sql
CREATE TABLE events (
    id INTEGER PRIMARY KEY,
    type TEXT,           -- 'track' or 'task'
    entity_id TEXT,
    data TEXT,           -- JSON blob
    created_at TIMESTAMP
);
```

### Tasks Table (State Machine)
```sql
CREATE TABLE tasks (
    id TEXT PRIMARY KEY,
    entity_id TEXT,
    type TEXT,
    state TEXT,          -- pending/assigned/in_progress/completed/cancelled
    assigned_to TEXT,
    data TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

## API Design

See [INTEGRATION.md](./INTEGRATION.md) for full API reference.

### Key Endpoints
- `GET /v1/tracks` - All current tracks
- `GET /v1/tasks` - Task queue with filtering
- `PATCH /v1/tasks/{id}/state` - State transitions
- `POST /v1/tasks/{id}/ack` - Operator acknowledgment
- `WS /ws/tracks` - Real-time track feed
- `WS /ws/cot` - CoT XML stream for ATAK

## Deployment

### Docker Compose
```yaml
services:
  api:
    build: .
    ports: ["8000:8000"]
  
  web:
    build: ./web
    ports: ["5173:5173"]
```

### Edge Deployment
- Designed for constrained environments
- SQLite for zero-dependency persistence
- Textual TUI for low-bandwidth operators

## Security Considerations

- All credentials via environment variables
- CORS origins configurable
- No PII in track data
- Audit log for all state changes
