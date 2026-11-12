# Session log

## 2026-11-11 -- web interface, static GitHub Pages site, bug fixes (branch `web-interface`)

**Bugs fixed in the Python (each in its own commit, regression tests in `tests/test_regressions.py`):**
- The snake game was updated and drawn twice per frame (`main.py` called it directly and through the world, where it
  is a building): the snake moved every 5 frames instead of `ai_speed` = 10 and its timers ran at double speed.
- The snake died moving into the cell its tail was leaving: the AI treats that cell as safe, the rules did not.
  172 of 200 seeded headless games ended this way, usually at score 1. Now the tail only blocks when eating.
- Alex could never be "near" the snake game (centre-to-centre < 100 px for a 500 px building it can't enter), so it
  never noticed it, and every investigation ended in a collision and CONFUSED. "Near" is now measured from the
  building's edge, and bumping into the investigated building counts as arriving.
- Alex's idle thoughts stopped after the first thought (`current_thought` was never cleared).
- Debug console FPS always read 0.0 (it used a new `pygame.time.Clock()`); it now gets the game's clock.
- Under arrow-key control the snake moved every frame (60 cells/s); it now uses the same `ai_speed` pacing.
- `.gitignore` was listed as done in ROADMAP.md but missing; `debug.log` and `.DS_Store` were tracked. Added/untracked.
- `snake_game.py` (760 lines) split into `snake_game.py`, `snake_ai.py`, `snake_render.py` (500-line rule).
- README: clone URL, project structure, full key list (A, R, T, M, +/-, E works anywhere, mouse only highlights).

**Web interface:** `web/` (FastAPI + ES modules, web kit theme, green/violet/cyan accents), pages Home / World /
Thoughts / Verify / About. `main.SelfAwareGame` gained `seed=` (and `main.py --seed N`); the interaction lines moved to
`SelfAwareCharacter.FOURTH_WALL_THOUGHTS` (no behaviour change). The game is ported to JS (`web/static/sim_*.js` +
`py_random.js`, the CPython Mersenne Twister from the go repo's kit plus random/uniform/randint). Every random draw is
in the same order, including the snake's render-time glitch-line draws, so runs are frame-identical:
`sim_engine.test.mjs` replays 5 Python runs (34,400 frames, every key, natural and forced transcendence, game over and
restart, manual control) and checks 905 snapshots + the RNG afterwards. Local app adds "Check with Python"
(POST /api/run) for the run you are watching; verified identical in the browser (seed 5, 2174 frames, 6 keys).
No LLM/API anywhere in the project.

**Open:** dialogue fading uses wall-clock time in the desktop and game frames on the web.

## 2026-11-11 (later) -- George's decisions on the two open questions

- Fixed: after transcending, the snake game stayed in Matrix mode with no snake for the rest of the run. Matrix mode
  now ends after `matrix_duration` (5 s, as the code says) and the game starts over with a new snake at awareness 0
  (`SnakeGame.start_new_snake`), which can escape again; runs now produce several transcended entities.
- Fixed: idle/thinking/confused spells lasted ~1.25 s / 0.27 s / 0.07 s (median) instead of the commented 3-6 s,
  3-5 s, 1.5-2.5 s: the exit threshold was re-rolled every frame against a timer started part-way. The duration is
  now drawn once on entry (`state_duration`), timer from 0.
- JS engine ported for both, fixture regenerated (905 snapshots identical, up to 3 transcendences per run); seed 0 now
  transcends at frame 5200 (Verify run 6000 frames, home hero frame 5170). Browser "Check with Python" on seed 0,
  6170 frames with keys: identical. Screenshots refreshed.
