# Dashboard UI

This dashboard is a local viewer for Codex-only manual runs.

## Start

From the project root:

```bash
python .agents/magent.py ui
```

Then open:

- `http://localhost:8080/dashboard.html`
- `http://localhost:8080/dashboard-live.html`

## Data sources

The dashboard reads only local files under `.agents/reports/runs/`:

- `dispatch-plan.json`
- `execution-summary.json`
- `stream.jsonl`
- `*.output.md`

## Endpoints

The server exposes simple local JSON endpoints for the browser UI:

- `GET /api/runs/latest/summary`
- `GET /api/runs/latest/stream`
- `GET /api/runs/<run-id>/output/<agent-id>`
- `GET /api/events`

These are local dashboard endpoints, not external service APIs.

## Workflow

1. Run `magent run --task "..." --scope "..."`
2. Fill agent outputs from the current Codex session
3. Run `magent step latest`
4. Watch status update in the dashboard

## Notes

- `total_tokens` is kept for schema compatibility and remains `0` in manual mode.
- The live view uses `stream.jsonl` plus SSE from the local server.
