"""
One-Command Launcher: Starts both FastAPI Backend & React Frontend concurrently from backend directory.
"""

from pathlib import Path
import sys

# Forward to root start_all.py
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import start_all

if __name__ == "__main__":
    start_all.main()
