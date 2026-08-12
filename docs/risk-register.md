# LIA-EmployX Risk Register

This register tracks live technical risks discovered during stabilization.
Risks remain open until a completed phase validates their resolution.

| ID | Risk | Status | Detected | Resolution |
| --- | --- | --- | --- | --- |
| R-001 | Runtime state and persisted mission state can diverge; an observed `RUNNING` mission had no active Runtime instance. | Open | Phase 0 | — |
| R-002 | Agent-produced event payloads can fail `MissionEvent` validation because required event fields are absent. | Open | Phase 0 | — |
| R-003 | `pytest` is unavailable in both the system interpreter and the configured virtual environment, preventing test discovery and execution. | Open | Phase 0 | — |
| R-004 | The worktree contained pre-existing local changes, so the baseline cannot be reproduced from the base commit alone. | Open | Phase 0 | — |
| R-005 | Runtime execution is split between `MissionController` and `MissionRuntime`/`RuntimeRegistry`; a legacy orchestrator remains present. | Open | Audit / Phase 0 | — |
| R-006 | Flutter mission calls and FastAPI routes/responses do not share a single public contract. | Open | Audit / Phase 0 | — |

## Maintenance policy

- Add a risk when evidence identifies a potential impact on stability, data
  integrity, architecture, security, or delivery.
- Link mitigation and resolution to the phase that owns the risk.
- Mark a risk resolved only after its phase exit criteria and relevant
  validation have passed.
