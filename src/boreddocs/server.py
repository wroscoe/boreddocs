"""`boreddocs serve` — local preview HTTP server with auto-rebuild."""

from __future__ import annotations

import http.server
import socketserver
import threading
import time
from pathlib import Path

from boreddocs.builder import Builder
from boreddocs.config import Config


def _make_handler(directory: Path):
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **kw):
            super().__init__(*a, directory=str(directory), **kw)

        def log_message(self, format, *args):
            print(f"[boreddocs serve] {format % args}")

    return Handler


def _start_http(directory: Path, host: str, port: int):
    handler = _make_handler(directory)
    httpd = socketserver.ThreadingTCPServer((host, port), handler)
    httpd.daemon_threads = True
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    return httpd


def _watch_and_rebuild(config: Config, builder: Builder, watch_paths: list[Path]) -> None:
    try:
        from watchdog.events import FileSystemEventHandler
        from watchdog.observers import Observer
    except ImportError:
        print("[boreddocs serve] watchdog not installed; auto-rebuild disabled.")
        print("                  install with: pip install boreddocs[serve]")
        while True:
            time.sleep(3600)
        return

    class Rebuilder(FileSystemEventHandler):
        last = 0.0
        debounce_s = 0.4

        def on_any_event(self, event):
            now = time.monotonic()
            if now - self.last < self.debounce_s:
                return
            self.last = now
            try:
                counts = builder.build()
                print(f"[boreddocs serve] rebuilt: {counts}")
            except Exception as e:
                print(f"[boreddocs serve] build failed: {e}")

    observer = Observer()
    handler = Rebuilder()
    for p in watch_paths:
        if p.exists():
            observer.schedule(handler, str(p), recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


def serve(config: Config, host: str = "127.0.0.1", port: int = 8000) -> None:
    builder = Builder(config)
    counts = builder.build()
    print(f"[boreddocs serve] initial build: {counts}")

    httpd = _start_http(config.output_path, host, port)
    print(f"[boreddocs serve] http://{host}:{port}/")

    watch_paths = [
        config.meetings_dir,
        config.policies_dir,
        config.data_dir,
        config.overrides_dir,
        config.project_dir / "boreddocs.yml",
    ]
    try:
        _watch_and_rebuild(config, builder, watch_paths)
    finally:
        httpd.shutdown()
