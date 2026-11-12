"""FastAPI web app for the Self-Aware Game: serves the front end in static/ and the JSON API under /api.

Run with `python run_web.py` (http://127.0.0.1:8142, local only). `scripts/build_static.py` exports every path in
STATIC_ENDPOINTS to JSON for the GitHub Pages site, so keep that list in step with the GET routes below. The game itself
runs in the browser (static/sim_*.js); the API supplies the Python game's text libraries and recorded Python runs.
"""
from pathlib import Path
from typing import Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from web.sim_record import KEYS, run, texts

STATIC = Path(__file__).resolve().parent / "static"
REFERENCE = {"seed": 0, "frames": 5000, "every": 50}  # the Verify page's recorded Python run (snake transcends ~3600)

app = FastAPI(title="Self-Aware Game")
app.mount("/static", StaticFiles(directory=STATIC), name="static")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/api/info")
def info():
    """Project summary and counts for the home page, read from the game's own code."""
    t = texts()
    return {"title": "Self-Aware Game", "world": [1200, 800], "snake_grid": [25, 25],
            "character_thoughts": len(t["character"]), "snake_thoughts": len(t["snake"]),
            "observations": len(t["observations"]), "fourth_wall": len(t["fourthWall"]),
            "states": ["IDLE", "WALKING", "THINKING", "INVESTIGATING", "CONFUSED", "INTERACTING"],
            "keys": sorted(KEYS), "controls": t["controls"]}


@app.get("/api/texts")
def text_libraries():
    """Every thought and line the characters can say (from modules/character.py and modules/snake_game.py)."""
    return texts()


@app.get("/api/reference")
def reference():
    """A seeded run of the Python game (state every 50 frames) for the browser to replay and compare."""
    return run(**REFERENCE)


class RunRequest(BaseModel):
    seed: int = Field(1, ge=0, le=2**31 - 1)
    frames: int = Field(2000, ge=1, le=20000)
    every: int = Field(50, ge=1, le=1000)
    keys: Dict[int, List[str]] = {}


@app.post("/api/run")
def run_python(req: RunRequest):
    """Play any seeded run (with key presses) through the Python game: local app only."""
    bad = {k for v in req.keys.values() for k in v} - set(KEYS)
    if bad:
        raise HTTPException(422, f"unknown keys: {sorted(bad)}")
    return run(seed=req.seed, frames=req.frames, keys=req.keys, every=req.every)


# GET paths (without the /api prefix) written to the static site as api/<path>.json.
STATIC_ENDPOINTS = ["/info", "/texts", "/reference"]
