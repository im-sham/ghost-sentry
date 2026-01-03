# Detailed Execution Plan: Ghost Sentry (Phase 2 & 3)

**Role**: Executor (Gemini Flash)
**Context**: This plan covers the "Advancement" arc (SAR + Web GUI + Deployment).
**Prerequisites**: Phase 0-5 (Core Implementation) must be complete.

---

## Phase 2: SAR Integration (Sentinel-1)
**Goal**: Integrate Synthetic Aperture Radar (SAR) data processing for all-weather detection.

### Step 2.1: Dependencies
Update `pyproject.toml` to include:
```toml
dependencies = [
    # ... existing ...
    "numpy",
    "scipy",
]
```
Run `pip install -e .`

### Step 2.2: Mock SAR Data (`data/samples/mock_sar.json`)
Create a mock strategy for SAR detections (simulating a "Cloudy Day" scenario where optical fails but SAR succeeds).
```json
[
  {"label": "tank", "confidence": 0.82, "bbox": [0,0,0,0], "geo_location": [33.95, -118.42], "sensor": "SAR"}
]
```

### Step 2.3: Multi-Modal Detector (`core/fusion.py`)
Create a `FusionEngine` that accepts both Optical (YOLO) and SAR inputs.
- Note: For MVP, assume SAR input is pre-processed detections (not raw interferometry).
- Logic: If Optical confidence < 0.5 (cloudy), prioritize SAR detections.

**Verification**:
```bash
python -m ghost_sentry.scripts.test_fusion --cloudy
```

---

## Phase 3: Lattice-Style Web GUI
**Goal**: Build a visual dashboard mimicking the Anduril Lattice interface (Dark mode, Map-centric).

### Step 3.1: Frontend Scaffold
Initialize a React app inside `ghost-sentry/web`:
```bash
cd ghost-sentry
npm create vite@latest web -- --template react-ts
cd web
npm install leaflet react-leaflet tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

### Step 3.2: Lattice Design System (`web/tailwind.config.js`)
Configure custom colors to match Anduril's aesthetic:
- **Background**: `#0a0a0a` (Deep Space)
- **Panel**: `#1a1a1a` (Dark Gray)
- **Primary**: `#00ff9d` (Lattice Cyan/Green)
- **Alert**: `#ff3333` (Tactical Red)

### Step 3.3: Map Component (`web/src/components/Map.tsx`)
- Use `react-leaflet` with a dark CartoDB tile layer.
- Render tracks as custom SVG icons (Cyan circles for friendly, Red diamonds for hostile/unknown).
- Fetch tracks from `http://localhost:8000/tracks` every 2 seconds.

### Step 3.4: Sidebar (`web/src/components/Sidebar.tsx`)
- List active Tracks and Tasks.
- Use a "Data Table" density (monospaced fonts, tight padding).

**Verification**:
```bash
cd web && npm run dev
# Verify at http://localhost:5173
```

---

## Phase 4: Containerization & Deployment
**Goal**: proper "Edge" packaging.

### Step 4.1: Dockerfile
Create `Dockerfile` in root:
```dockerfile
# Use Python 3.11 for Lattice SDK compatibility
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install -e .

CMD ["uvicorn", "ghost_sentry.api:app", "--host", "0.0.0.0"]
```

### Step 4.2: Compose Stack
Create `docker-compose.yml`:
- Service 1: `api` (Backend)
- Service 2: `web` (Frontend - build stage required)

**Verification**:
```bash
docker build -t ghost-sentry:latest .
docker run -p 8000:8000 ghost-sentry:latest
```
