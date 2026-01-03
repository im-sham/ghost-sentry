# AGENTS.md: The Ghost Sentry Manual

**Project**: Ghost Sentry
**Goal**: Autonomous ISR & Anomaly Detection Pipeline (Anduril Portfolio Application)
**Stack**: Python, FastAPI, YOLOv8, Textual, Docker

## Core Directives
1.  **Lattice First**: Data models must comply with Lattice SDK schemas (even if mocked).
2.  **Edge Ready**: Code must run in Docker with constrained resources.
3.  **No Fluff**: Focus on tactical utility (CoT output, TUI console) over web aesthetics.

## Role Protocol
- **Architect (Gemini Pro)**: Plans phases, solves blockers.
- **Executor (Gemini Flash/Claude Sonnet/GPT-4o)**: Implements code, runs tests.
- **Designer (Claude Opus)**: Reviews architecture, designs complex interactions.

## Repository Standards
- **Imports**: Absolute imports (e.g., `from ghost_sentry.core import detector`).
- **Typing**: Strict `mypy` compliance. Use `Pydantic` for data boundaries.
- **Docs**: Google-style docstrings.
