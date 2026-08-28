#!/usr/bin/env python3
"""
MINEGUARD — Start All Local Services
SIH26025 | Team: RED HACK

Starts:
  1. FastAPI Backend       → http://localhost:8000
  2. Vite React Frontend   → http://localhost:5173
  3. 20-Node LoRa Simulator (publishes to Mosquitto)
  4. MINEGATE Gateway Agent (subscribes + edge buffer)

Prerequisites (already running as Windows Services):
  - Mosquitto MQTT Broker (port 1883)
  - PostgreSQL 18 (port 5432)  ← if using PostgreSQL
    OR SQLite auto-created at backend/mine_monitoring.db

Usage:
  python start_all.py
"""

import subprocess
import sys
import os
import time
import signal

ROOT = os.path.dirname(os.path.abspath(__file__))
BACKEND = os.path.join(ROOT, "backend")
FRONTEND = os.path.join(ROOT, "frontend")
PYTHON = sys.executable

procs = []

def start(name, cmd, cwd, env=None):
    e = os.environ.copy()
    if env:
        e.update(env)
    p = subprocess.Popen(
        cmd,
        cwd=cwd,
        env=e,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
    )
    procs.append((name, p))
    print(f"  [STARTED] {name} (PID {p.pid})")
    return p

def stop_all():
    print("\nShutting down all MINEGUARD services...")
    for name, p in procs:
        try:
            p.terminate()
            print(f"  [STOPPED] {name}")
        except Exception:
            pass

if __name__ == "__main__":
    print("=" * 60)
    print("  MINEGUARD — Starting Local Stack (SIH26025)")
    print("=" * 60)

    # 1. FastAPI Backend
    start(
        "FastAPI Backend (port 8000)",
        [PYTHON, "-m", "uvicorn", "main:app",
         "--app-dir", BACKEND, "--host", "127.0.0.1", "--port", "8000"],
        ROOT
    )
    time.sleep(3)

    # 2. 20-Node LoRa Simulator
    start(
        "20-Node LoRa Simulator",
        [PYTHON, "-m", "simulator.node_simulator"],
        ROOT
    )
    time.sleep(1)

    # 3. MINEGATE Gateway Agent
    start(
        "MINEGATE Gateway Agent",
        [PYTHON, "-m", "gateway.gateway_agent"],
        ROOT
    )
    time.sleep(1)

    # 4. React/Vite Frontend
    npm = "npm.cmd" if os.name == "nt" else "npm"
    start(
        "React Frontend (port 5173)",
        [npm, "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"],
        FRONTEND
    )

    print()
    print("=" * 60)
    print("  All services started!")
    print()
    print("  MINEGUARD Dashboard:  http://localhost:5173")
    print("  FastAPI Swagger Docs: http://localhost:8000/docs")
    print("  FastAPI Redoc:        http://localhost:8000/redoc")
    print()
    print("  Press Ctrl+C to stop all services.")
    print("=" * 60)

    try:
        while True:
            time.sleep(2)
            # Check if any critical process died
            for name, p in procs:
                if p.poll() is not None:
                    print(f"\n[WARNING] {name} exited unexpectedly (code {p.returncode})")
    except KeyboardInterrupt:
        stop_all()
