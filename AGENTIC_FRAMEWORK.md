# The Agentic Project Framework

**Version:** 1.1
**Status:** Living Document
**Audited By:** Claude (2025-12-30)

## 1. Core Philosophy

This framework establishes a rigorous, "optimization-first" methodology for AI-assisted software development. It moves beyond simple "chat-and-code" to a structured, audit-driven engineering process designed to maximize the specific strengths of different AI models.

### Key Principles
1.  **Context Persistency**: The project history must live in the **filesystem**, not just the chat context. Decisions, plans, and statuses are artifacts.
2.  **Model Specialization**: Different models have different cognitive profiles. We assign roles (Architect, Designer, Executor) to the best-fit model.
3.  **Traceable Reasoning**: Every major architectural decision must be logged with its "Why", alternatives considered, and consequences.
4.  **Verification Artifacts**: Proof of work is not "I did it", but a `walkthrough.md` with logs, screenshots, and test results.

---

## 2. The Repository Structure ("The Brain")

A standardized `.agent` directory serves as the project's "hippocampus"—storing long-term memory and procedural knowledge.

```text
.agent/
├── workflows/              # Standard Operating Procedures (SOPs)
│   ├── feature-development.md
│   └── bug-fixing.md
├── traces/                 # Architectural decision logs (JSONL)
│   └── decision_log.jsonl
├── memory/                 # Long-term context
│   ├── active_context.md   # Current state for handoffs
│   └── roadmap.md          # High-level goals
├── rules/                  # Model-specific overrides & user rules
│   └── multi-model-protocol.md
├── artifacts/              # (Optional) plan storage
│   ├── implementation_plans/
│   └── walkthroughs/
└── AGENTS.md               # The user manual for the AI agents
```

> [!NOTE]
> **Traces Directory Clarification**: If your project has a root-level `/traces/` directory, that is for *runtime* agent traces (RAG retrieval, LLM calls). The `.agent/traces/` directory is specifically for *architectural decision logs* made during development.

---

## 3. The "Multi-Model Optimization Protocol"

We do not use one model for everything. We intentionally route tasks to the best-fit model and require cross-audits.

### The Roles

| Role | Recommended Model | Responsibilities |
|------|-------------------|------------------|
| **Architect** | Gemini Pro | System design, cross-module dependencies, high-level planning, breaking down ambiguity. |
| **Designer** | Claude Opus/Sonnet | Solution design, detailed API specs, reviewing architectural feasibility, complex refactoring. |
| **Executor** | Claude Sonnet / GPT-4o | Writing code, running tests, pattern-following implementation. |
| **Debugger** | Context-Dependent | Systemic issues → Gemini (log analysis); Localized logic bugs → Claude. |

> [!TIP]
> The Designer/Executor distinction is about **task complexity**, not strictly model tier. Use higher-capability models for *novel solution design*; use faster models for *pattern-following implementation*.

### The Handoff & Audit Loop

1.  **Assessment**: Agent 1 assesses the request and tags it (e.g., `SYSTEM_ARCHITECTURE`, `SOLUTION_DESIGN`, `EXECUTION`).
2.  **Self-Match Check**: If the agent is not optimal for the task, it states: *"This task is tagged as [ROLE]. Consider switching to [MODEL]."*
3.  **Drafting**: The assigned agent drafts `implementation_plan.md`.
4.  **The Cross-Check**: Before execution, the plan MUST be audited by the Counter-Model.
5.  **Execution**: Once audited, the Executor implements the plan.
6.  **Handoff Protocol**: When switching, the outgoing agent writes `.agent/memory/active_context.md` summarizing:
    *   Current state and open files
    *   Specific questions for the incoming agent
    *   Next logical step

---

## 4. The Development Lifecycle

Every significant unit of work follows this lifecycle.

### Phase 1: Research (The "Search")
*   **Goal**: Understand before acting.
*   **Action**: Agent explores codebase, reads docs.
*   **Output**: Mental model or notes in `.agent/research/`. No code changes yet.

### Phase 2: Decision (The "Plan")
*   **Goal**: Agree on the 'What' and 'Why'.
*   **Action**: Create `implementation_plan.md`.
*   **Content**:
    *   Problem Description
    *   Proposed Changes (File by File)
    *   **User Review Required** (Breaking changes?)
    *   Verification Plan (How will we prove it works?)
*   **Constraint**: User MUST approve this plan before code is written.

### Phase 3: Audit (The "Check")
*   **Goal**: Catch design flaws early.
*   **Action**: Switch models (if applicable) to review the `implementation_plan.md`.
*   **Output**: "Approved" or "Request Changes" with specific feedback.

### Phase 4: Execution (The "Code")
*   **Goal**: Implement the approved plan.
*   **Action**: Write code, create files.
*   **Constraints**:
    *   **Scope Lock Rule**: If a change touches more files than planned, STOP and return to Phase 2.
    *   **Defensive Imports**: Always verify imports/dependencies exist before writing code that depends on them.

### Phase 4.5: Incremental Testing
*   **Goal**: Catch regressions early.
*   **Action**: Run relevant tests *as you implement*, not just at the end.
*   **Output**: Passing tests for each logical unit of work.

### Phase 5: Verification (The "Proof")
*   **Goal**: Demonstrate correctness.
*   **Action**: Run full test suite, generate logs, take screenshots.
*   **Output**: `walkthrough.md` showing *evidence* that the feature works.
*   **Rollback Criteria**: Document what constitutes a failed verification. If critical tests fail or unexpected side effects occur, rollback rather than patch.

---

## 5. Decision Tracing & Observability

We do not rely on implicit chat history for "why" a decision was made.

### The Decision Log
We maintain a structured log (e.g., `.agent/traces/decision_log.jsonl`) for architectural pivots.

**Schema:**
| Field | Description |
|-------|-------------|
| `context` | What was the situation? |
| `decision` | What did we choose? |
| `alternatives` | What did we reject? |
| `consequences` | What is the trade-off? |
| `model` | Which AI made this call? |
| `timestamp` | When was this decision made? |

### RAG Metadata
If RAG is used to fetch context:
*   Log `retrieval_records` (documents accessed, relevance scores).
*   Enables debugging *why* an agent hallucinated or missed context.

---

## 6. How to Start a New Project

1.  **Initialize**: `mkdir -p .agent/workflows .agent/memory .agent/rules .agent/traces`
2.  **Define Rules**: Create `AGENTS.md` with project context and coding standards.
3.  **Seed Workflows**: Add `feature-development.md` to `.agent/workflows`.
4.  **First Memory**: Create `.agent/memory/roadmap.md` with the initial user vision.
5.  **User Rules**: Add any model-specific rules to `.agent/rules/`.
6.  **Bootstrap**: Ask the first AI Agent to "Read AGENTS.md and help me plan the MVP."

---

## 7. Anti-Patterns to Avoid

These patterns undermine the framework's effectiveness:

| Anti-Pattern | Why It's Harmful | Corrective Action |
|--------------|------------------|-------------------|
| **Implementing Without a Plan** | Leads to scope creep, missed edge cases, and inconsistent architecture. | Always create `implementation_plan.md` first. |
| **Scope Creep Mid-Execution** | Touching unplanned files introduces risk and breaks auditability. | Return to Phase 2 if scope expands. |
| **Skipping the Audit** | The primary model's blind spots go unchecked. | Always get Counter-Model review on non-trivial changes. |
| **Chat-Only Context** | Decisions are lost when the conversation ends. | Persist decisions to `.agent/` artifacts. |
| **Verification Without Evidence** | "It works" is not proof; screenshots and logs are. | Always produce `walkthrough.md` with artifacts. |
| **Ignoring the Handoff File** | Context is lost between models or sessions. | Read `active_context.md` at session start. |

---

## 8. Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-12-30 | Initial draft | Gemini |
| 1.1 | 2025-12-30 | Added Phase 4.5, Anti-Patterns, Scope Lock Rule, Rollback Criteria, Rules directory, Traces clarification | Claude |
