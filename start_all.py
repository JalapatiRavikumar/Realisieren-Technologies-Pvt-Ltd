"""
One-Command Launcher: Starts both FastAPI Backend & React Frontend concurrently.

Usage:
    python start_all.py
"""

import os
from pathlib import Path
import subprocess
import sys
import time

ROOT_DIR = Path(__file__).resolve().parent
# If running from backend folder, go up one level to root
if ROOT_DIR.name == "backend":
    ROOT_DIR = ROOT_DIR.parent

FRONTEND_DIR = ROOT_DIR / "frontend"


def main():
    print("=" * 60)
    print("🚀 Starting Full-Stack Web Scraping Dashboard...")
    print("=" * 60)

    # 1. Start FastAPI Backend subprocess
    print(" [1/2] Starting FastAPI Backend on http://localhost:8000 ...")
    backend_cmd = [sys.executable, "-m", "uvicorn", "backend.main:app", "--reload", "--port", "8000"]
    backend_proc = subprocess.Popen(
        backend_cmd,
        cwd=str(ROOT_DIR),
        shell=True,
    )

    time.sleep(1.5)

    # 2. Start React Frontend subprocess
    print(" [2/2] Starting React Frontend on http://localhost:5173 ...")
    npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
    frontend_proc = subprocess.Popen(
        [npm_cmd, "run", "dev"],
        cwd=str(FRONTEND_DIR),
        shell=True,
    )

    print("=" * 60)
    print("✨ Both Services are RUNNING:")
    print("   👉 Frontend Dashboard: http://localhost:5173")
    print("   👉 Backend API Docs:   http://localhost:8000/docs")
    print("   Press CTRL+C anytime to stop all services.")
    print("=" * 60)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping all services...")
        backend_proc.terminate()
        frontend_proc.terminate()
        print("Goodbye!")


if __name__ == "__main__":
    main()
