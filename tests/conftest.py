"""Shared pytest setup: headless pygame (dummy video/audio) and quiet logging.

Configuring the root logger first makes main.py's logging.basicConfig a no-op, so tests do not write debug.log.
"""
import logging
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
logging.basicConfig(level=logging.WARNING, handlers=[logging.NullHandler()])

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.chdir(ROOT)  # the game loads assets/ by relative path
