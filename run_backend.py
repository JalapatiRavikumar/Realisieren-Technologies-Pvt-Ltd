"""
FastAPI Backend Launcher.
"""
from pathlib import Path
import sys
import uvicorn

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.main import app

if __name__ == "__main__":
    print("Starting FastAPI Backend on http://localhost:8000 ...")
    uvicorn.run(app, host="127.0.0.1", port=8000)
