# Self-Aware Game -- Interface Map

## Entry Point
- **`main.py`** -- `SelfAwareGame(seed=None)` class; `python main.py [--seed N]`
  - Game loop (`run`: `handle_events` -> `update` -> `render`), key handling, transcendence callback
    (`handle_snake_transcendence`), world-wide Matrix effect (`enter_matrix_mode`, `update_matrix_mode`)
  - The snake game is a building of the world: `world.update()`/`world.render()` update and draw it (once per frame)

## Modules (`modules/`)
- **`modules/__init__.py`** -- Package init (logging setup)
- **`modules/snake_game.py`** -- `SnakeGame(SnakeAIMixin, SnakeRenderMixin)`: rules and state of the self-aware
  snake (awareness, thoughts, glitch, Matrix mode, transcendence, key handling)
- **`modules/snake_ai.py`** -- `SnakeAIMixin`: `ai_move` (toward food/glitch, smarter from awareness 5),
  `ai_matrix_move` (toward the edges)
- **`modules/snake_render.py`** -- `SnakeRenderMixin`: `render`, matrix rain, thought bubble (the glitch lines use
  `random`, the only random draw in any render code)
- **`modules/character.py`** -- `CharacterState` enum, `SelfAwareCharacter` (states, thoughts,
  `FOURTH_WALL_THOUGHTS`, `is_near_building` measured from the building's edge, `interact`)
- **`modules/world.py`** -- `Building`, `GameWorld` (buildings, collision with pygame.Rect, rendering)
- **`modules/dialogue.py`** -- `DialogueMessage`, `DialogueSystem` (last 5 messages, fading)
- **`modules/debug.py`** -- `DebugConsole` (FPS from the game clock, character/snake stats), `DebugCommand`
- **`modules/entities.py`** -- `TranscendedEntity`: the snake after escaping into the main world

## Web interface (`web/`)
- **`web/app.py`** -- FastAPI app: `/api/info`, `/api/texts`, `/api/reference` (exported to the static site via
  `STATIC_ENDPOINTS`), `POST /api/run` (local only: any seeded run with key presses through the Python game)
- **`web/sim_record.py`** -- `run(seed, frames, keys, every)` drives the real `SelfAwareGame` headless and records
  `snapshot()`s; `texts()` returns the dialogue libraries; `KEYS` maps key names to pygame keys
- **`web/static/`** -- ES-module front end (no build step)
  - `core.js`, `style.css` (shared web kit), `style_app.css`, `index.html`, `main.js` (router), `static_api.js`, `bg.js`
  - Pages: `home.js`, `world.js` (simulation UI) + `inspector.js`, `thoughts.js`, `verify.js`, `about.js`
  - Engine (JS port of the Python, same RNG draws): `py_random.js` (CPython's random.Random), `sim_world.js`
    (`Game`: main.py + world + dialogue), `sim_character.js` (`SelfAwareCharacter`, `TranscendedEntity`),
    `sim_snake.js` (`SnakeGame` + AI), `sim_texts.js` (all lines), `sim_snapshot.js` (`snapshot`, `diff`, `replay`)
  - `sim_render.js` -- canvas drawing following the desktop render code; `character_sprites.png` copy of the asset
  - `sim_engine.test.mjs` -- node test: replays `tests/fixtures/sim_fixtures.json`

## Scripts
- **`run_web.py`** -- starts the web app on 127.0.0.1:8142
- **`scripts/build_static.py`** -- exports the static GitHub Pages site to `site/`
- **`scripts/make_sim_fixtures.py`** -- writes `tests/fixtures/sim_fixtures.json` from Python runs
- **`scripts/screenshots.py`** -- browser smoke test and README screenshots (`docs/img/`)
- **`tools/placeholder_creation.py`** -- Dev script to generate placeholder sprites
- **`.github/workflows/pages.yml`** -- web tests + static build + Pages deploy on push to main

## Tests
- **`test_game.py`** -- Smoke tests for all core modules (pytest, dummy display)
- **`tests/conftest.py`** -- headless pygame, quiet logging (no debug.log)
- **`tests/test_regressions.py`** -- regression tests for the bugs fixed on 2026-11-11
- **`tests/test_web.py`** -- API, static build, fixture-is-current, node engine test

## Assets
- **`assets/character_sprites.png`** -- Character sprite sheet (4x4: rows = direction, columns = animation frame)
- **`assets/sounds/`** -- Sound files
- **`assets/ui/`** -- UI element images (not used by the code)

## Dependencies
- pygame (see `requirements.txt`); web: `requirements-web.txt` (fastapi, uvicorn, httpx, pytest, pygame, pinned)
