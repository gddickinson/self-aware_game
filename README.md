# Self-Aware Game

A Python simulation featuring self-aware game characters who realize they're in a game. The project includes a meta "game within a game" structure, where a self-aware snake game exists inside a larger world with a roaming self-aware character.

## Features

- **Self-aware Snake Game**: A snake game where the snake gradually becomes aware it exists in a simulation
- **Roaming Character**: A character that wanders around the world, thinks about its existence, and interacts with the snake game
- **Dialogue System**: Characters express their thoughts about being in a game
- **Expandable World**: Framework for adding more buildings, games, and characters
- **Debugging Tools**: Comprehensive error tracking and performance monitoring

## Project Structure

```
self-aware-game/
│
├── main.py                   # Main entry point for the game
├── modules/
│   ├── __init__.py           # Package initialization
│   ├── snake_game.py         # The self-aware snake game
│   ├── character.py          # Self-aware character implementation
│   ├── world.py              # Game world and buildings
│   ├── dialogue.py           # Dialogue and thought system
│   └── debug.py              # Debugging tools
│
├── assets/
│   ├── character_sprites.png # Character sprite sheet
│   └── sounds/               # Game sounds
│
├── debug.log                 # Log file (created when running)
├── requirements.txt          # Required Python packages
└── README.md                 # This file
```

## Requirements

- Python 3.8 or higher
- Pygame 2.0.0 or higher

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/self-aware-game.git
   cd self-aware-game
   ```

2. Create and activate a virtual environment (recommended):
   ```
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Running the Game

Run the main script to start the game:

```
python main.py
```

## Controls

- **Arrow Keys**: Control the snake (when not in AI mode)
- **Space**: Pause/resume the snake game
- **P**: Pause/resume the entire simulation
- **D**: Toggle debug information
- **E**: Interact with the character when nearby
- **Mouse**: Click on dialogue to interact

## Building a Custom World

The game is designed to be easily expandable. To add new elements:

1. **New Buildings**: Use the `GameWorld.add_building()` method
2. **New Characters**: Create instances of `SelfAwareCharacter` or subclass it
3. **New Games**: Create a new game class that follows the same interface as `SnakeGame`

Example:
```python
# Add a new building
world.add_building("New Building", (500, 300), (200, 150))

# Add a new character
new_character = SelfAwareCharacter("Bob", (400, 400), world)
world.add_character(new_character)
```

## Development Roadmap

- [ ] Multiple self-aware characters with unique personalities
- [ ] Character interaction system
- [ ] More mini-games that characters can discover
- [ ] Day/night cycle with different character behaviors
- [ ] Save/load game state
- [ ] Story progression based on character awareness levels

## Debugging

The game includes a debug console that can be toggled with the 'D' key. This displays:

- Current FPS
- Character position and state
- Snake game stats
- Any errors that occur during runtime

All debug information is also written to `debug.log`.

## License

This project is licensed under the MIT License - see the LICENSE file for details.


---
*Built with AI assistance from [Claude (Anthropic)](https://claude.com/).*
