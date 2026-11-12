"""Write tests/fixtures/sim_fixtures.json: seeded runs of the real desktop game (main.SelfAwareGame, headless) that
web/static/sim_engine.test.mjs requires the JavaScript engine to reproduce.

Each scenario is (name, seed, frames, snapshot every N frames, {frame: [keys]}). Together they cover the natural arc
(the snake grows aware, finds the glitch, enters Matrix mode and transcends into the world), every key the desktop
game handles, manual snake control, game over and restart, plus raw random.Random outputs.
Run: python scripts/make_sim_fixtures.py   (tests/test_web.py checks the file is current)
"""
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from web.sim_record import run, texts  # noqa: E402

OUT = ROOT / "tests" / "fixtures" / "sim_fixtures.json"


def _every(start, stop, step, keys):
    return {f: list(keys) for f in range(start, stop, step)}


SCENARIOS = [
    ("natural arc: awareness, glitch, Matrix, transcendence", 0, 8000, 40, {}),
    ("every desktop key", 5, 3000, 20, {
        10: ["d"], 50: ["e"], 120: ["plus", "plus", "plus"], 300: ["minus"], 400: ["m"], 900: ["space"],
        1000: ["space"], 1200: ["p"], 1260: ["p", "e"], 1500: ["a"], 1510: ["up"], 1560: ["left"], 1620: ["down"],
        1700: ["right"], 1800: ["a"], 2000: ["t"], 2500: ["e"], 2600: ["e"]}),
    ("manual snake: arrows, speed, AI toggle", 7, 2400, 10, {
        5: ["a"], **_every(40, 2300, 60, ["up"]), **_every(70, 2300, 60, ["right"]),
        **_every(55, 2300, 240, ["left"]), 600: ["minus", "minus"], 1200: ["plus"] * 6, 2310: ["a"]}),
    ("game over, restart and forced transcendence", 3, 9000, 50, {
        **_every(4450, 9000, 400, ["r"]), **_every(100, 9000, 700, ["t"]), 6000: ["m"]}),
    ("long run", 4, 12000, 200, {**_every(1000, 12000, 1500, ["e"])}),
]
PRNG_SEEDS = [0, 1, 42, 2**32 + 5, 123456789012345]


def build() -> dict:
    cases = [{"name": n, **run(seed=s, frames=f, keys=k, every=e)} for n, s, f, e, k in SCENARIOS]
    prng = []
    for seed in PRNG_SEEDS:
        r = random.Random(seed)
        prng.append({"seed": seed, "random": [r.random() for _ in range(5)],
                     "randint": [r.randint(-100, 1200) for _ in range(5)], "uniform": [r.uniform(3, 8) for _ in range(3)]})
    return {"texts": texts(), "cases": cases, "prng": prng}


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(build(), separators=(",", ":")))
    print(f"wrote {OUT} ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
