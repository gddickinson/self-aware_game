"""Run the real desktop game (main.SelfAwareGame) headlessly and record its state, for the web interface.

The recorder drives the same per-frame loop as SelfAwareGame.run(): key events -> handle_events() -> update() ->
render(). render() only touches the simulation through one random draw site (the snake game's glitch lines,
three random.randint(-2, 2) per frame while a glitch is on the board), so it is called on those frames only;
on every other frame it changes nothing and is skipped for speed. The JS engine (web/static/sim_*.js) replays
the same seeded runs and must match these records (web/static/sim_engine.test.mjs).
"""
import logging
import os
import random
import threading

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
if not logging.getLogger().handlers:  # keep main.py's basicConfig from writing debug.log
    logging.basicConfig(level=logging.WARNING, handlers=[logging.NullHandler()])

import pygame  # noqa: E402
from pygame.locals import (K_DOWN, K_EQUALS, K_LEFT, K_MINUS, K_RIGHT, K_SPACE, K_UP, KEYDOWN,  # noqa: E402
                           K_a, K_d, K_e, K_m, K_p, K_r, K_t)

import main  # noqa: E402
from modules.character import SelfAwareCharacter  # noqa: E402

KEYS = {"p": K_p, "d": K_d, "e": K_e, "m": K_m, "a": K_a, "t": K_t, "r": K_r, "space": K_SPACE,
        "plus": K_EQUALS, "minus": K_MINUS, "up": K_UP, "down": K_DOWN, "left": K_LEFT, "right": K_RIGHT}
_lock = threading.Lock()  # pygame state is global: one recorded run at a time


def _r(v):
    return round(v, 9) if isinstance(v, float) else v


def _xy(p):
    return [_r(p[0]), _r(p[1])] if p is not None else None


def snapshot(game, frame):
    c, s = game.character, game.snake_game
    return {
        "frame": frame,
        "paused": game.paused, "matrix": game.matrix_mode, "matrixTimer": game.matrix_timer,
        "rain": [_xy((m["x"], m["y"])) for m in game.matrix_text[:3]],
        "char": {"pos": _xy(c.position), "state": c.state.name, "stateTimer": c.state_timer, "dir": c.direction,
                 "target": _xy(c.target_position), "thought": c.current_thought, "thoughtTimer": c.thought_timer,
                 "noticed": c.has_noticed_snake_game, "anim": c.animation_frame},
        "snake": {"body": [list(p) for p in s.snake], "dir": list(s.direction), "next": list(s.next_direction),
                  "food": list(s.food), "score": s.score, "awareness": s.awareness_level, "over": s.game_over,
                  "paused": s.paused, "ai": s.ai_controlled, "speed": s.ai_speed, "counter": s.ai_counter,
                  "thought": s.current_thought, "thoughtTimer": s.thought_timer,
                  "glitch": list(s.glitch) if s.glitch else None, "matrix": s.matrix_mode,
                  "matrixTimer": s.matrix_timer, "transcended": s.transcended,
                  "rain": [_xy((m["x"], m["y"])) for m in s.matrix_text[:3]]},
        "entities": [{"pos": _xy(e.position), "dir": list(e.direction), "thought": e.thought,
                      "thoughtTimer": e.thought_timer, "target": _xy(e.target), "timer": e.timer,
                      "stream": _xy((e.matrix_stream[0]["x"], e.matrix_stream[0]["y"]))}
                     for e in game.transcended_entities],
        "dialogue": [[m.sender, m.message] for m in game.dialogue.messages],
    }


def run(seed=1, frames=600, keys=None, every=10):
    """Play `frames` frames of a seeded game. keys: {frame: [key names]} pressed before that frame's update.

    Returns {"seed", "frames", "every", "keys", "snaps": [state every `every` frames and after the last],
    "rng": the next four random.random() values (checks the generators are still in step)}.
    """
    keys = {int(k): v for k, v in (keys or {}).items()}
    with _lock:
        game = main.SelfAwareGame(seed=seed)
        snaps = [snapshot(game, 0)]
        for f in range(1, frames + 1):
            pygame.event.clear()
            for name in keys.get(f, []):
                pygame.event.post(pygame.event.Event(KEYDOWN, key=KEYS[name], mod=0, unicode="", scancode=0))
            game.handle_events()
            game.update()
            if game.snake_game.glitch_active and game.snake_game.glitch:
                game.render()
            if f % every == 0 or f == frames:
                snaps.append(snapshot(game, f))
        rng = [random.random() for _ in range(4)]
    return {"seed": seed, "frames": frames, "every": every, "keys": {str(k): v for k, v in keys.items()},
            "snaps": snaps, "rng": rng}


def texts():
    """The game's own dialogue libraries (shown on the Thoughts page and checked against the JS copy)."""
    with _lock:
        game = main.SelfAwareGame(seed=0)
    c, s = game.character, game.snake_game
    return {"character": list(c.thoughts), "observations": list(c.snake_game_observations),
            "fourthWall": list(SelfAwareCharacter.FOURTH_WALL_THOUGHTS), "snake": list(s.thoughts),
            "controls": [line for line in _controls_help()]}


def _controls_help():
    """The in-game controls panel text, read from main.render_controls_help's source list."""
    import inspect
    src = inspect.getsource(main.SelfAwareGame.render_controls_help)
    body = src.split("control_text = [", 1)[1].split("]", 1)[0]
    return [ln.strip().strip(",").strip('"') for ln in body.splitlines() if ln.strip()]
