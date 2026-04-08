# Self-Aware Game -- Interface Map

## Entry Point
- **`main.py`** -- `SelfAwareGame` class
  - Game loop, event handling, rendering, matrix effects
  - Imports all modules below; single entry point via `python main.py`

## Modules (`modules/`)
- **`modules/__init__.py`** -- Package init (logging setup)
- **`modules/snake_game.py`** -- `SnakeGame` class
  - Self-aware snake game-within-a-game; AI-controlled snake with transcendence
- **`modules/character.py`** -- `SelfAwareCharacter` class
  - Roaming NPC with thought system, building interaction, awareness levels
- **`modules/world.py`** -- `GameWorld` class
  - World map, buildings, spatial queries
- **`modules/dialogue.py`** -- `DialogueSystem` class
  - On-screen message display, thought bubble rendering
- **`modules/debug.py`** -- `DebugConsole` class
  - FPS, character state, snake stats overlay
- **`modules/entities.py`** -- `TranscendedEntity` class
  - Entity that escaped from the snake game into the main world

## Tools
- **`tools/placeholder_creation.py`** -- Dev script to generate placeholder sprites

## Tests
- **`test_game.py`** -- Smoke tests for all core modules (pytest, dummy display)

## Assets
- **`assets/character_sprites.png`** -- Character sprite sheet
- **`assets/sounds/`** -- Sound files
- **`assets/fonts/`** -- Font files
- **`assets/ui/`** -- UI element images

## Dependencies
- pygame (see `requirements.txt`)
