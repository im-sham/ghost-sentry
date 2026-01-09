# Lattice Integration Guide

This document describes how Ghost Sentry integrates with Anduril's Lattice ecosystem.

## Overview

Ghost Sentry acts as an **autonomous sensor node** within the Lattice mesh. It:
1. Ingests imagery from various sources
2. Produces `Track` entities for detected objects
3. Generates `Task` entities for operator verification
4. Streams Cursor-on-Target (CoT) for ATAK/WinTAK interoperability

## Lattice SDK Compatibility

### Entity Model

Ghost Sentry entities follow Lattice SDK v4.0.0 schemas:

```python
class LatticeTrack:
    entityId: str           # UUID
    description: str        # Human-readable
    ontology: {
        template: "TEMPLATE_TRACK"
        platform_type: str  # "Airplane", "Truck", etc.
    }
    location: {
        position: {
            latitudeDegrees: float
            longitudeDegrees: float
            altitudeHaeMeters: float
        }
    }
    milView: {
        disposition: str    # DISPOSITION_UNKNOWN/FRIENDLY/HOSTILE
        environment: str    # ENVIRONMENT_AIR/LAND/SURFACE
    }
    provenance: {
        integrationName: "ghost-sentry"
        dataType: "detection"
        sourceUpdateTime: str  # ISO 8601
    }
    lifecycleState: str     # TENTATIVE/FIRM/STALE/DROPPED
    confidence: float       # 0.0 - 1.0
    isLive: bool
```

### Adapter Pattern

The `LatticeConnector` class abstracts SDK communication:

```python
from ghost_sentry.lattice.adapter import LatticeConnector

# Development mode (local SQLite)
connector = LatticeConnector(mode="dev")

# Production mode (requires LATTICE_ENDPOINT env var)
connector = LatticeConnector(mode="prod")

# Publish entities
connector.publish_track(track)
connector.publish_task(task)
```

### Production Configuration

For production Lattice integration, set these environment variables:

```bash
# Required for prod mode
LATTICE_ENDPOINT=grpc://lattice.example.com:443
LATTICE_API_KEY=your-api-key

# Optional
LATTICE_TLS_CERT=/path/to/cert.pem
LATTICE_INTEGRATION_NAME=ghost-sentry
```

## API Reference

### REST Endpoints

All endpoints are prefixed with `/v1/` for versioning.

#### Tracks

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/v1/tracks` | List all tracks |
| GET | `/v1/tracks/cot` | Tracks as CoT XML |
| GET | `/v1/tracks/{id}/history` | Track position history |

#### Tasks

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/v1/tasks` | List tasks (filter by `?state=`) |
| PATCH | `/v1/tasks/{id}/state` | Update task state |
| POST | `/v1/tasks/{id}/ack` | Acknowledge task receipt |

#### Assets

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/v1/assets` | List available assets |
| POST | `/v1/assets/telemetry` | Update asset telemetry |

#### Missions

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/v1/missions` | List mission configurations |
| POST | `/v1/missions` | Create new mission |

### WebSocket Streams

#### `/ws/tracks`

Real-time track and task updates as JSON.

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/tracks');
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    // data.type: 'track' | 'task' | 'task_update' | 'asset_telemetry'
};
```

#### `/ws/cot`

Cursor-on-Target XML stream for ATAK/WinTAK integration.

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/cot');
ws.onmessage = (event) => {
    // event.data is CoT XML string
    const xml = event.data;
};
```

## Cursor-on-Target (CoT) Format

Ghost Sentry generates MIL-STD-2525 compliant CoT events:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<event version="2.0" 
       uid="550e8400-e29b-41d4-a716-446655440000" 
       type="a-f-A" 
       time="2024-01-15T10:30:00Z" 
       start="2024-01-15T10:30:00Z" 
       stale="2024-01-15T10:35:00Z" 
       how="m-g">
  <point lat="33.9425" lon="-118.4081" hae="0" ce="10" le="10"/>
  <detail>
    <contact callsign="GS-AIR"/>
    <remarks>Detected airplane (conf: 0.92)</remarks>
  </detail>
</event>
```

### CoT Type Codes

| Detection | CoT Type | Description |
|-----------|----------|-------------|
| airplane | `a-f-A` | Assumed friendly air |
| truck | `a-u-G-E-V` | Unknown ground vehicle |
| car | `a-u-G-E-V` | Unknown ground vehicle |
| boat | `a-u-S` | Unknown surface |
| default | `a-u-G` | Unknown ground |

## Task State Machine

Tasks follow this lifecycle:

```
                    ┌─────────────┐
                    │   PENDING   │
                    └──────┬──────┘
                           │ assign
                    ┌──────▼──────┐
           ┌────────│  ASSIGNED   │────────┐
           │        └──────┬──────┘        │
           │ cancel        │ start         │ timeout
           │        ┌──────▼──────┐        │
           │        │ IN_PROGRESS │        │
           │        └──────┬──────┘        │
           │               │ complete      │
           │        ┌──────▼──────┐        │
           └───────▶│  COMPLETED  │◀───────┘
                    └─────────────┘
                           │
                    ┌──────▼──────┐
                    │  CANCELLED  │
                    └─────────────┘
```

### State Transition API

```bash
# Assign task to operator
curl -X PATCH "http://localhost:8000/v1/tasks/{id}/state?state=assigned"

# Start work
curl -X PATCH "http://localhost:8000/v1/tasks/{id}/state?state=in_progress"

# Complete task
curl -X PATCH "http://localhost:8000/v1/tasks/{id}/state?state=completed"

# Acknowledge receipt (separate from state)
curl -X POST "http://localhost:8000/v1/tasks/{id}/ack"
```

## Entity Lifecycle Management

Tracks transition through lifecycle states based on observation freshness:

| State | Criteria | TTL |
|-------|----------|-----|
| TENTATIVE | New detection, single observation | 30s |
| FIRM | 2+ correlated observations | 5min |
| STALE | No update within TTL | 10min |
| DROPPED | Stale for extended period | Archive |

## Multi-INT Fusion

When multiple sensors observe the same entity:

1. **Spatial Correlation**: Within 100m radius
2. **Temporal Correlation**: Within 60s window
3. **Type Matching**: Same or compatible types

**Fusion Priority:**
1. AIS/ADS-B (authoritative for maritime/air)
2. SAR (all-weather, high precision)
3. Optical (highest resolution, weather-dependent)

## Error Handling

### Connection Failures

```python
try:
    connector.publish_track(track)
except LatticeConnectionError as e:
    # Queue for retry
    db.add_event("retry_queue", track.model_dump())
    logging.error(f"Lattice publish failed: {e}")
```

### Validation Errors

All entities are validated against Pydantic schemas before publish:

```python
from pydantic import ValidationError

try:
    track = LatticeTrack(**data)
except ValidationError as e:
    logging.error(f"Invalid track data: {e}")
```

## Testing Integration

```bash
# Run integration tests
pytest tests/ -v

# Test with mock Lattice
LATTICE_MODE=dev pytest tests/test_lattice_integration.py

# Test CoT output
curl http://localhost:8000/v1/tracks/cot
```
