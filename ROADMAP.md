# Self-Aware Game -- Roadmap

## Current State
A Pygame-based simulation with a self-aware snake game and a roaming character
that wanders and expresses existential thoughts. Modular structure with
`modules/` containing `snake_game.py`, `character.py`, `world.py`, `dialogue.py`,
and `debug.py`. `main.py` is the single entry point and also defines
`TranscendedEntity` inline. A `placeholder_creation.py` script exists for
generating placeholder sprite assets. No tests, no CI, no type hints. The debug
log (`debug.log`) is committed to the repo.

## Short-term Improvements
- [x] Move `TranscendedEntity` out of `main.py` into `modules/entities.py`
- [x] Add `.gitignore` to exclude `debug.log`, `__pycache__`, and `*.pyc`
- [ ] Add type hints to all public methods in `modules/`
- [ ] Add error handling for missing assets (`assets/character_sprites.png`,
      `assets/sounds/`) -- fall back to colored rectangles gracefully
- [ ] Replace `logging.basicConfig()` in `main.py` with a dedicated logging
      config module to avoid handler duplication
- [ ] Add a `--windowed` / `--fullscreen` CLI flag via argparse
- [x] Write basic smoke tests: game initializes, snake moves, character updates

## Feature Enhancements
- [ ] Implement multiple self-aware characters with distinct personalities
      (per the existing roadmap in README.md)
- [ ] Add a day/night cycle in `world.py` that affects character behavior and
      dialogue selection in `dialogue.py`
- [ ] Create a save/load system using JSON serialization of game state
- [ ] Add more mini-games beyond snake (e.g., Pong, Conway's Life) that
      characters can discover and "escape" from
- [ ] Implement a character interaction system -- when two characters meet,
      trigger a dialogue exchange based on their awareness levels
- [ ] Add particle effects for transcendence events (replace the manual
      `matrix_stream` list in `TranscendedEntity` with a proper particle system)
- [ ] Sound effects and ambient audio tied to awareness level

## Web version (2026-11-11)
- [x] Browser version of the whole game (JS port, frame-identical to `python main.py --seed N`), GitHub Pages site
- [ ] If the game logic changes, regenerate `tests/fixtures/sim_fixtures.json` and update `web/static/sim_*.js`

## Long-term Vision
- [ ] Story progression system: define narrative beats that trigger based on
      collective awareness levels across all characters
- [ ] Procedural world generation: expand beyond the fixed building layout in
      `world.py` to generate unique worlds each playthrough
- [ ] Modding support: let users define custom characters and dialogues via
      YAML/JSON config files
- [ ] Steam/itch.io release with PyInstaller packaging
- [ ] Multiplayer: two players each control a character, discovering the meta
      nature of their shared world

## Technical Debt
- [x] `main.py` is likely over 500 lines -- split game loop, event handling,
      and rendering into separate modules (TranscendedEntity extracted to modules/entities.py; main.py now ~340 lines)
- [x] `placeholder_creation.py` should be a dev-only script, not in the main
      project root -- move to a `tools/` directory
- [x] `debug.log` should not be version-controlled
- [x] No `requirements.txt` version pinning -- pin `pygame>=2.0.0`
- [x] The README references `expanded_main.py` but the file is `main.py` (no longer the case)
- [ ] Dialogue strings are hardcoded in `dialogue.py` -- externalize to a
      JSON/YAML data file for easier editing
