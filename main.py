"""
Self-Aware Game - A simulation where game characters are aware they're in a game.
Main module for initializing and running the game.
"""

import pygame
import sys
import logging
from pygame.locals import *
from modules.snake_game import SnakeGame
from modules.character import SelfAwareCharacter
from modules.world import GameWorld
from modules.dialogue import DialogueSystem
from modules.debug import DebugConsole

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("main")

class SelfAwareGame:
    """Main game class that manages all game components."""

    def __init__(self):
        """Initialize the game and all its components."""
        self.logger = logging.getLogger("SelfAwareGame")
        self.logger.info("Initializing Self-Aware Game")

        # Initialize Pygame
        pygame.init()
        pygame.display.set_caption("Self-Aware Game")

        # Screen dimensions
        self.width = 1200
        self.height = 800

        # Create the main game window
        self.screen = pygame.display.set_mode((self.width, self.height))

        # Create game clock
        self.clock = pygame.time.Clock()
        self.running = True
        self.paused = False

        # Create game world
        self.world = GameWorld(self.width, self.height)

        # Create the snake game (as a "game within the game")
        snake_pos = (100, 100)  # Position in the world
        snake_size = (500, 500)  # Size of the snake game window
        self.snake_game = SnakeGame(snake_pos, snake_size)

        # Add the snake game as a building to the world
        self.world.add_building("Snake Game", snake_pos, snake_size, self.snake_game)

        # Create self-aware character
        start_pos = (700, 400)
        self.character = SelfAwareCharacter("Alex", start_pos, self.world)

        # Create dialogue system
        self.dialogue = DialogueSystem(self.screen, (self.width // 2, self.height - 100))

        # Create debug console
        self.debug_console = DebugConsole(self.screen, (10, 10))
        self.debug_mode = False

        self.logger.info("Self-Aware Game initialized successfully")

    def handle_events(self):
        """Process game events and user input."""
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False

            elif event.type == KEYDOWN:
                # Toggle pause
                if event.key == K_p:
                    self.paused = not self.paused
                    status = "paused" if self.paused else "resumed"
                    self.logger.info(f"Game {status}")

                # Toggle debug mode
                elif event.key == K_d:
                    self.debug_mode = not self.debug_mode
                    self.logger.info(f"Debug mode {'enabled' if self.debug_mode else 'disabled'}")

                # Interact with character
                elif event.key == K_e:
                    self.character.interact()

                # Control snake game speed
                elif event.key == K_PLUS or event.key == K_EQUALS:
                    if self.snake_game.ai_speed > 1:
                        self.snake_game.ai_speed -= 1
                        self.logger.debug(f"Snake AI speed increased: {self.snake_game.ai_speed}")

                elif event.key == K_MINUS:
                    if self.snake_game.ai_speed < 20:
                        self.snake_game.ai_speed += 1
                        self.logger.debug(f"Snake AI speed decreased: {self.snake_game.ai_speed}")

                # Forward event to snake game
                self.snake_game.handle_key_event(event)

            # Forward mouse events to dialogue system
            elif event.type in (MOUSEBUTTONDOWN, MOUSEMOTION):
                self.dialogue.handle_event(event)

    def update(self):
        """Update game state."""
        if self.paused:
            return

        # Update the world
        self.world.update()

        # Update the snake game
        self.snake_game.update()

        # Update self-aware character
        self.character.update()

        # Check for interactions between character and snake game
        if self.character.is_near_building("Snake Game"):
            # Character notices the snake game
            if not self.character.has_noticed_snake_game:
                self.character.has_noticed_snake_game = True
                message = "Hey, what's this? A snake game? That's strange... it seems self-aware too!"
                self.dialogue.add_message(self.character.name, message)

    def render(self):
        """Render the game."""
        # Clear the screen
        self.screen.fill((50, 50, 50))  # Dark gray background

        # Render the world
        self.world.render(self.screen)

        # Render the snake game
        self.snake_game.render(self.screen)

        # Render the character
        self.character.render(self.screen)

        # Render dialogue
        self.dialogue.render()

        # Render debug information if enabled
        if self.debug_mode:
            self.debug_console.render(self.character, self.world, self.snake_game)

        # Render "PAUSED" if game is paused
        if self.paused:
            font = pygame.font.Font(None, 74)
            text = font.render("PAUSED", True, (255, 255, 255))
            self.screen.blit(text, (self.width // 2 - text.get_width() // 2,
                                     self.height // 2 - text.get_height() // 2))

        # Render game controls help
        self.render_controls_help()

        # Update the display
        pygame.display.flip()

    def render_controls_help(self):
        """Render a small help text for controls."""
        control_text = [
            "Controls:",
            "P: Pause/Resume",
            "D: Toggle Debug",
            "E: Interact with Character",
            "A: Toggle Snake AI",
            "+/-: Adjust Snake Speed",
            "Arrow Keys: Control Snake"
        ]

        font = pygame.font.Font(None, 20)
        y_offset = 10

        for text in control_text:
            surface = font.render(text, True, (200, 200, 200))
            self.screen.blit(surface, (self.width - surface.get_width() - 10, y_offset))
            y_offset += 20

    def run(self):
        """Main game loop."""
        self.logger.info("Starting game loop")

        try:
            while self.running:
                self.handle_events()
                self.update()
                self.render()
                self.clock.tick(60)  # 60 FPS

        except Exception as e:
            self.logger.error(f"Error in game loop: {e}", exc_info=True)

        finally:
            self.logger.info("Shutting down")
            pygame.quit()
            sys.exit()

if __name__ == "__main__":
    # Create and run the game
    game = SelfAwareGame()
    game.run()
