# Ghost Sentry Roadmap

## Vision

Ghost Sentry aims to be a reference implementation for autonomous ISR integration with Lattice, demonstrating best practices for:
- Multi-sensor fusion
- Autonomous cueing and tasking
- Edge deployment
- Tactical interoperability (CoT/ATAK)

---

## Release History

### v0.1.0 - MVP (Current)
- [x] YOLOv8-based tactical detection
- [x] Lattice SDK adapter pattern (dev mode)
- [x] SQLite persistence layer
- [x] Autonomous cueing with debounce
- [x] Loitering detection analytics
- [x] CoT XML output for ATAK/WinTAK
- [x] Textual TUI console
- [x] Docker deployment
- [x] REST API with WebSocket streaming

### v0.2.0 - Production Hardening (Planned)
- [x] Entity correlation and deduplication
- [x] Track lifecycle states (TENTATIVE → FIRM → STALE → DROPPED)
- [x] Threat classification
- [x] Formation detection
- [x] Task acknowledgment workflow
- [x] API versioning (/v1/)
- [x] CoT WebSocket streaming
- [x] GitHub Actions CI/CD
- [ ] Prometheus metrics endpoint
- [ ] Structured logging (JSON)

---

## Future Phases

### Phase 3: Multi-Sensor Fusion
- [ ] SAR imagery integration (Sentinel-1)
- [ ] AIS feed ingestion for maritime
- [ ] ADS-B feed for air traffic
- [ ] Fusion confidence propagation
- [ ] Sensor disagreement resolution

### Phase 4: Advanced Analytics
- [ ] Convoy detection (coordinated ground movement)
- [ ] Pattern-of-life analysis
- [ ] Geo-fence alerting (enter/exit zones)
- [ ] Predictive track projection
- [ ] Anomaly scoring model

### Phase 5: Lattice Production Integration
- [ ] gRPC Lattice SDK integration
- [ ] mTLS authentication
- [ ] Entity subscription (receive tracks from mesh)
- [ ] Distributed track correlation
- [ ] Lattice UI plugin

### Phase 6: Edge Optimization
- [ ] ONNX model export for edge inference
- [ ] ARM64 Docker builds
- [ ] Offline operation mode
- [ ] Bandwidth-constrained sync
- [ ] Resilient message queuing

---

## Technical Debt

| Item | Priority | Notes |
|------|----------|-------|
| Add mypy strict mode | Medium | Currently optional |
| Increase test coverage to 90% | Medium | Focus on edge cases |
| Add OpenAPI schema validation | Low | FastAPI auto-generates |
| Database migrations | Low | Schema is stable |

---

## Contributing

This project follows the contribution guidelines in [AGENTS.md](../.agent/AGENTS.md).

Key principles:
1. **Lattice First**: All data models must comply with SDK schemas
2. **Edge Ready**: Code must run in constrained environments
3. **No Fluff**: Focus on tactical utility over aesthetics
