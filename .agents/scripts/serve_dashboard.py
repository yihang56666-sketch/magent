#!/usr/bin/env python3
"""Simple HTTP server for the Codex-only multi-agent dashboard."""

from __future__ import annotations

import json
import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse


if getattr(sys, "frozen", False):
    ROOT = Path(sys._MEIPASS)
    UI_DIR = ROOT / "ui"
else:
    ROOT = Path(__file__).resolve().parents[1]
    UI_DIR = ROOT / "ui"

REPORTS_DIR = ROOT / "reports" / "runs"


class DashboardHandler(SimpleHTTPRequestHandler):
    """Serve static dashboard files plus run-summary endpoints."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(UI_DIR), **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/events":
            self.handle_sse()
            return
        if parsed.path.startswith("/api/"):
            self.handle_api(parsed.path)
            return
        super().do_GET()

    def handle_sse(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        import time

        last_positions: dict[str, int] = {}
        while True:
            try:
                run_id = self.get_latest_run()
                if run_id:
                    stream_file = REPORTS_DIR / run_id / "stream.jsonl"
                    if stream_file.exists():
                        last_pos = last_positions.get(run_id, 0)
                        with open(stream_file, "r", encoding="utf-8") as handle:
                            handle.seek(last_pos)
                            for line in handle:
                                if line.strip():
                                    self.wfile.write(f"data: {line}\n\n".encode("utf-8"))
                                    self.wfile.flush()
                            last_positions[run_id] = handle.tell()
                time.sleep(0.5)
            except Exception:
                break

    def handle_api(self, path: str):
        parts = path.split("/")
        if len(parts) < 5 or parts[2] != "runs":
            self.send_json_response({"error": "Invalid API path"}, 400)
            return

        run_id = parts[3]
        endpoint = parts[4]
        if run_id == "latest":
            run_id = self.get_latest_run()
        if not run_id:
            self.send_json_response({"error": "No runs found"}, 404)
            return

        run_dir = REPORTS_DIR / run_id
        if endpoint == "summary":
            self.serve_summary(run_dir)
        elif endpoint == "stream":
            self.serve_stream(run_dir)
        elif endpoint == "output" and len(parts) >= 6:
            self.serve_agent_output(run_dir, parts[5])
        else:
            self.send_json_response({"error": "Unknown endpoint"}, 404)

    def serve_summary(self, run_dir: Path):
        summary_file = run_dir / "execution-summary.json"
        if summary_file.exists():
            self.send_json_response(json.loads(summary_file.read_text(encoding="utf-8")))
            return

        plan_file = run_dir / "dispatch-plan.json"
        if not plan_file.exists():
            self.send_json_response({"error": "No data found"}, 404)
            return

        plan = json.loads(plan_file.read_text(encoding="utf-8"))
        agents = plan.get("dispatch_plan", [])
        summary = {
            "total": len(agents),
            "completed": 0,
            "pending": len(agents),
            "failed": 0,
            "total_tokens": 0,
            "results": [
                {
                    "agent_id": agent["id"],
                    "identity_id": agent.get("identity_id", agent["id"]),
                    "agent_type": agent.get("agent_type", "explorer"),
                    "execution_role": agent.get("execution_role", agent.get("agent_type", "explorer")),
                    "status": "pending",
                    "tokens": 0,
                }
                for agent in agents
            ],
        }
        self.send_json_response(summary)

    def serve_stream(self, run_dir: Path):
        stream_file = run_dir / "stream.jsonl"
        if not stream_file.exists():
            self.send_json_response([])
            return

        events = []
        with open(stream_file, "r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    events.append(json.loads(line))
        self.send_json_response(events)

    def serve_agent_output(self, run_dir: Path, agent_id: str):
        output_file = run_dir / f"{agent_id}.output.md"
        if not output_file.exists():
            self.send_response(404)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write("Output not available yet".encode("utf-8"))
            return

        content = output_file.read_text(encoding="utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(content.encode("utf-8"))

    def send_json_response(self, data, status: int = 200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def get_latest_run(self) -> str | None:
        if not REPORTS_DIR.exists():
            return None
        runs = sorted(REPORTS_DIR.iterdir(), key=lambda path: path.stat().st_mtime, reverse=True)
        return runs[0].name if runs else None

    def log_message(self, format, *args):
        print(f"[{self.address_string()}] {format % args}")


def main():
    port = int(os.environ.get("PORT", 8080))
    print(
        f"\n"
        f"Codex-only Multi-Agent Dashboard Server\n"
        f"Dashboard: http://localhost:{port}/dashboard.html\n"
        f"Live view:  http://localhost:{port}/dashboard-live.html\n"
        f"Summary:    http://localhost:{port}/api/runs/latest/summary\n"
        f"Press Ctrl+C to stop.\n"
    )

    server = HTTPServer(("0.0.0.0", port), DashboardHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")


if __name__ == "__main__":
    main()
