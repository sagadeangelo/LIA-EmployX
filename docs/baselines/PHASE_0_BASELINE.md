# Phase 0 Baseline — Runtime Unification

## Purpose

This record freezes the observed project state before Phase 1A. It is a
reference artifact only; it does not define the target architecture or alter
runtime behavior.

## Source-control baseline

- Branch: `codex/stabilization/runtime-unification`
- Base commit: `5e6d76585a9d65a75a0314fd2d7159b248d0ac75`
- Base subject: `docs: update README in English`
- Working tree on capture: dirty, with 88 reported paths.
- Tracked diff at capture: 25 files changed, 2,300 insertions and 1,374
  deletions. Untracked paths were preserved and are intentionally not included
  in this Phase 0 artifact.

## Static validation baseline

- Python files parsed with the AST parser: 300
- Python syntax errors: 0
- Test discovery: unavailable. Both the system interpreter and `.venv` lack
  the `pytest` module; no test run was attempted.
- Flutter analysis: not run in Phase 0, to avoid creating generated artifacts
  in an already dirty worktree.

## Live API observations

The already-running local server at `http://127.0.0.1:8000` was queried with
read-only `GET` requests. Capture time is intentionally omitted because
mission data is mutable.

| Endpoint | Observed result |
| --- | --- |
| `GET /` | `200`; reports `running` / `runtime: active` |
| `GET /api/v1/ping` | `200`; `{ "ok": true }` |
| `GET /api/v1/health` | `200`; health, runtime, storage and database report true |
| `GET /api/v1/runtime` | `200`; reports zero active missions and no registered event types |
| `GET /api/v1/missions` | `200`; returns persisted missions, including historical failures and a mission in `RUNNING` state |
| `GET /openapi.json` | `200`; records the public paths listed below |

### Runtime evidence requiring Phase 1A investigation

The read-only mission response included persisted `MissionEvent` validation
failures from agents: required `source`, `type`, `title`, and `description`
were absent from the event payload. It also included a `RUNNING` mission while
the Runtime Inspector reported zero active missions. These are baseline
observations, not changes made by Phase 0.

## Public API inventory

### Root and diagnostics

- `GET /`
- `GET /api/v1/ping`
- `GET /api/v1/health`

### Upload and CV

- `POST /api/v1/upload`
- `POST /api/v1/cv/upload`

### Missions

- `POST /api/v1/missions` → `MissionSnapshot`
- `GET /api/v1/missions` → `list[Mission]`
- `GET /api/v1/missions/{mission_id}/snapshot` → `MissionSnapshot`
- `POST /api/v1/missions/{mission_id}/run`
- `POST /api/v1/missions/{mission_id}/resume`
- `POST /api/v1/missions/{mission_id}/restart`
- `DELETE /api/v1/missions/{mission_id}`

### Runtime inspector

- `GET /api/v1/runtime`
- `GET /api/v1/runtime/missions`
- `GET /api/v1/runtime/{mission_id}`
- `GET /api/v1/runtime/{mission_id}/memory`
- `GET /api/v1/runtime/{mission_id}/timeline`
- `GET /api/v1/runtime/{mission_id}/events`
- `POST /api/v1/runtime/{mission_id}/cancel`
- `POST /api/v1/runtime/{mission_id}/pause`

### Command Center

- `GET /api/v1/command-center/{mission_id}` → `CommandCenterData`
- `POST /api/v1/command-center/{mission_id}/execute`

## Contract baseline

The backend OpenAPI schema exposes `Mission`, `MissionEvent`,
`MissionSnapshot`, `RuntimeStatus`, and `SystemHealth` as the mission-facing
contracts. The Flutter application also has `MissionModel`,
`MissionEventModel`, and `MissionSnapshotModel`.

Known mismatches to resolve in Phase 1B, not Phase 0:

- Flutter calls `GET /missions/{id}` and `PUT /missions/{id}`; those paths are
  absent from the captured OpenAPI schema.
- Flutter parses `POST /missions` as `MissionModel`, while OpenAPI declares
  `MissionSnapshot`.
- The CV client bypasses the shared Flutter API client and owns a separate
  base URL.

## Runtime topology baseline

- Current Runtime path: `RuntimeRegistry` → `MissionRuntime` → modern
  `AgentRegistry` → `RuntimeEventBus`.
- Current controller path: API/CV flow → `MissionController` → background
  task execution.
- Legacy path still present: `backend/orchestrator` has a separate
  `AgentRegistry` and Event Bus.

Phase 1A owns consolidation of these paths. Phase 0 intentionally leaves all
three untouched.

## Rollback

Return to base commit `5e6d76585a9d65a75a0314fd2d7159b248d0ac75` or abandon
this dedicated branch. Existing user changes were present before Phase 0 and
must be preserved independently of any rollback decision.
