# Phase 3: Code Polish - Execution Plan

**Executor**: Gemini Flash
**Date**: 2025-12-30
**Objective**: Address all audit recommendations to polish the Ghost Sentry codebase.

---

## Prerequisites
- Workspace: `/Users/shamimrehman/Projects/anor/ghost-sentry`
- Virtual env: `.venv` (already configured)
- Running services (for verification): API at `8000`, Web at `5173`

---

## Task 1: FusionEngine - Implement or Remove `optical_threshold`

**File**: `src/ghost_sentry/core/fusion.py`

**Current Issue**: The `optical_threshold` parameter is defined in `__init__` but never used in `fuse()`.

**Option A (Recommended)**: Implement threshold logic.
```python
def fuse(self, optical_detections: List[Detection], sar_detections: List[Detection]) -> List[Detection]:
    fused = []
    
    # Only include high-confidence optical detections
    for d in optical_detections:
        if d.confidence >= self.optical_threshold:
            d.label = f"{d.label} (Optical)"
            fused.append(d)
    
    # Add SAR detections (always include, they're all-weather)
    for d in sar_detections:
        d.label = f"{d.label} (SAR)"
        fused.append(d)
        
    return fused
```

**Option B**: Remove unused parameter if simplicity is preferred.

**Verification**: Run `python -m ghost_sentry.scripts.test_fusion` and confirm output.

---

## Task 2: FusionEngine - Add Unit Tests

**File**: `tests/test_core.py` (append new test class)

**New Tests**:
```python
class TestFusionEngine:
    def test_fuse_combines_sources(self):
        from ghost_sentry.core.fusion import FusionEngine
        engine = FusionEngine()
        optical = [Detection(label="tank", confidence=0.9, bbox=(0,0,0,0), geo_location=(33.94, -118.4))]
        sar = [Detection(label="truck", confidence=0.85, bbox=(0,0,0,0), geo_location=(33.95, -118.41))]
        fused = engine.fuse(optical, sar)
        assert len(fused) == 2
        assert "(Optical)" in fused[0].label
        assert "(SAR)" in fused[1].label

    def test_fuse_filters_low_confidence_optical(self):
        from ghost_sentry.core.fusion import FusionEngine
        engine = FusionEngine(optical_threshold=0.7)
        optical = [Detection(label="car", confidence=0.5, bbox=(0,0,0,0), geo_location=(33.94, -118.4))]
        sar = []
        fused = engine.fuse(optical, sar)
        # If threshold logic is implemented, this should be 0
        # If not implemented, it's 1
        # Adjust assertion based on Task 1 choice
```

**Verification**: Run `pytest tests/ -v` and confirm new tests pass.

---

## Task 3: API - Use Dynamic Confidence in CoT Endpoint

**File**: `src/ghost_sentry/api.py`

**Current Code (Line ~49)**:
```python
confidence=0.9,  # Hardcoded
```

**Updated Code**:
```python
confidence=track.get('confidence', 0.9),  # Use actual track confidence
```

**Verification**: 
1. Run CLI mock: `.venv/bin/python -m ghost_sentry.cli data/samples/mock_detections.json --mock`
2. Curl the endpoint: `curl http://localhost:8000/tracks/cot`
3. Confirm confidence values in CoT XML match the track data.

---

## Task 4: Web GUI - Remove Unused State Variable

**File**: `web/src/App.tsx`

**Current Code (Line ~27)**:
```typescript
const [tasks, setTasks] = useState<any[]>([]);
```

**Action**: Remove this line entirely as `tasks` is never used.

**Verification**: Run `npm run dev` in `web/` and confirm no console errors.

---

## Verification Checklist

| Task | Command | Expected Result |
| :--- | :--- | :--- |
| 1 | `python -m ghost_sentry.scripts.test_fusion` | Output shows fused detections |
| 2 | `pytest tests/ -v` | All tests (old + new) pass |
| 3 | `curl http://localhost:8000/tracks/cot` | Confidence in XML matches track |
| 4 | `npm run dev` (in `web/`) | No console errors, app loads |

---

## Handoff to Gemini Flash

**Action**: Execute the 4 tasks above in order.
**Report**: After completion, run the full verification checklist and update `task.md` to mark Phase 3 items as complete.
