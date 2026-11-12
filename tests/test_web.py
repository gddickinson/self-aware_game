"""Web interface tests: every exported endpoint answers, the static build is complete, and the JS engine tests pass.

Run: python -m pytest -q tests/test_web.py
"""
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from web.app import STATIC, STATIC_ENDPOINTS, app  # noqa: E402

client = TestClient(app)


def test_index_served():
    r = client.get("/")
    assert r.status_code == 200 and "static/main.js" in r.text


@pytest.mark.parametrize("path", STATIC_ENDPOINTS)
def test_endpoint(path):
    r = client.get("/api" + path)
    assert r.status_code == 200, r.text
    assert r.json() is not None


def test_static_build(tmp_path):
    sys.path.insert(0, str(ROOT / "scripts"))
    import build_static
    build_static.build(tmp_path / "site")
    assert (tmp_path / "site" / "index.html").read_text().count("APP_STATIC") == 1
    for path in STATIC_ENDPOINTS:
        assert (tmp_path / "site" / "api" / (path.strip("/") + ".json")).exists()


def test_static_assets_referenced_exist():
    html = (STATIC / "index.html").read_text()
    for name in ("style.css", "main.js"):
        assert f"static/{name}" in html and (STATIC / name).exists()


@pytest.mark.skipif(not shutil.which("node"), reason="node not installed")
def test_js_engine():
    tests = sorted(STATIC.glob("*.test.mjs"))
    for t in tests:
        r = subprocess.run(["node", str(t)], capture_output=True, text=True)
        assert r.returncode == 0, r.stdout + r.stderr


# --- project-specific -------------------------------------------------------------------------------------------
import json  # noqa: E402
import math  # noqa: E402

FIXTURE = ROOT / "tests" / "fixtures" / "sim_fixtures.json"


def _close(a, b, path=""):
    """Recursive equality with a relative tolerance on floats (libm may differ in the last digit across platforms)."""
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool):
        assert math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-9), f"{path}: {a} != {b}"
    elif isinstance(a, dict):
        assert isinstance(b, dict) and a.keys() == b.keys(), f"{path}: keys differ"
        for k in a:
            _close(a[k], b[k], f"{path}.{k}")
    elif isinstance(a, list):
        assert isinstance(b, list) and len(a) == len(b), f"{path}: lengths differ"
        for i, (x, y) in enumerate(zip(a, b)):
            _close(x, y, f"{path}[{i}]")
    else:
        assert a == b, f"{path}: {a!r} != {b!r}"


def test_fixture_is_current():
    """tests/fixtures/sim_fixtures.json matches what the Python game produces now (regenerate with
    python scripts/make_sim_fixtures.py after changing the game)."""
    sys.path.insert(0, str(ROOT / "scripts"))
    import make_sim_fixtures
    _close(json.loads(FIXTURE.read_text()), json.loads(json.dumps(make_sim_fixtures.build())))


def test_info_counts_come_from_the_game():
    from modules.character import SelfAwareCharacter
    info = client.get("/api/info").json()
    assert info["fourth_wall"] == len(SelfAwareCharacter.FOURTH_WALL_THOUGHTS) == 6
    assert info["character_thoughts"] == 19 and info["snake_thoughts"] == 10
    assert info["controls"][0] == "Controls:"


def test_reference_run_reaches_transcendence():
    ref = client.get("/api/reference").json()
    assert any(s["snake"]["transcended"] for s in ref["snaps"]) and ref["snaps"][-1]["entities"]


def test_run_endpoint_is_deterministic_and_takes_keys():
    body = {"seed": 3, "frames": 300, "every": 100, "keys": {"10": ["e"], "20": ["a"]}}
    a, b = client.post("/api/run", json=body).json(), client.post("/api/run", json=body).json()
    assert a == b and len(a["snaps"]) == 4
    assert a["snaps"][1]["snake"]["ai"] is False
    assert client.post("/api/run", json={**body, "keys": {"5": ["x"]}}).status_code == 422
    assert client.post("/api/run", json={**body, "frames": 10**6}).status_code == 422


def test_static_site_never_calls_the_python_run():
    js = (STATIC / "static_api.js").read_text()
    assert "clean === 'run'" in js
