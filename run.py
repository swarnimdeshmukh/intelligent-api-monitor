import os
import sys
import time
import signal
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ENV = os.environ.copy()
ENV["PYTHONPATH"] = str(ROOT)

processes = []

def shutdown(signum=None, frame=None):
    print("\n\nStopping all services...")

    for process in processes:
        if process.poll() is None:
            process.terminate()

    time.sleep(1)

    for process in processes:
        if process.poll() is None:
            process.kill()

    print("All services stopped.")
    sys.exit(0)

signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGTERM, shutdown)

print("=" * 60)
print("  INTELLIGENT API MONITORING SYSTEM")
print("=" * 60)

print("\n[1/3] Starting API...")
api = subprocess.Popen(
    [
        sys.executable, "-m", "uvicorn",
        "app.test_service:app",
        "--host", "127.0.0.1",
        "--port", "8000"
    ],
    cwd=ROOT,
    env=ENV
)
processes.append(api)

time.sleep(2)

print("[2/3] Starting monitoring engine...")
monitor = subprocess.Popen(
    [sys.executable, "-m", "app.monitoring.service"],
    cwd=ROOT,
    env=ENV
)
processes.append(monitor)

time.sleep(2)

print("[3/3] Starting dashboard...")
dashboard = subprocess.Popen(
    [
        sys.executable, "-m", "streamlit",
        "run",
        "dashboard/dashboard.py",
        "--server.headless", "true"
    ],
    cwd=ROOT,
    env=ENV
)
processes.append(dashboard)

print("\n" + "=" * 60)
print("  SYSTEM RUNNING")
print("=" * 60)
print("  API:       http://127.0.0.1:8000")
print("  Dashboard: http://localhost:8501")
print("=" * 60)
print("\nPress Ctrl+C ONCE to stop everything.\n")

try:
    while True:
        if api.poll() is not None:
            print("API stopped unexpectedly.")
            shutdown()

        if monitor.poll() is not None:
            print("Monitoring stopped unexpectedly.")
            shutdown()

        if dashboard.poll() is not None:
            print("Dashboard stopped unexpectedly.")
            shutdown()

        time.sleep(1)

except KeyboardInterrupt:
    shutdown()
