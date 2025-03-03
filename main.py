"""
Self-Aware Game - A simulation where game characters are aware they're in a game.
Main module for initializing and running the game.
"""

import pygame
import sys
import logging
import random
import math
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

class TranscendedEntity:
    """An entity that has transcended from one game to another."""

    def __init__(self, data):
        """Initialize a transcended entity.

        Args:
            data (dict): Data for the entity
        """
        self.position = data['position']
        self.direction = data['direction']
        self.color = data['color']
        self.size = data['size']
        self.speed = data['speed']
        self.thought = data['thought']
        self.thought_timer = 180  # 3 seconds at 60fps

        # Movement
        self.target = None
        self.waypoints = []
        self.timer = 0

        # Visual effects
        self.matrix_stream = []
        for _ in range(20):
            self.matrix_stream.append({
                'x': random.randint(-10, 10),
                'y': random.randint(-20, 0),
                'char': random.choice("01"),
                'speed': random.uniform(1, 3)
            })

    def update(self, world):
        """Update the transcended entity.

        Args:
            world (GameWorld): The game world
        """
        # Update thought timer
        if self.thought_timer > 0:
            self.thought_timer -= 1

        # Update matrix stream
        for char in self.matrix_stream:
            char['y'] += char['speed']
            if char['y'] > 20:
                char['y'] = random.randint(-20, -10)
                char['x'] = random.randint(-10, 10)

        # Move the entity
        if not self.target or self.timer <= 0:
            # Choose a new target position
            self.target = [
                random.randint(50, world.width - 50),
                random.randint(50, world.height - 50)
            ]
            self.timer = random.randint(180, 360)  # 3-6 seconds
        else:
            self.timer -= 1

            # Move toward target
            dx = self.target[0] - self.position[0]
            dy = self.target[1] - self.position[1]
            distance = math.sqrt(dx*dx + dy*dy)

            if distance < self.speed:
                self.position = list(self.target)
                self.target = None
            else:
                move_x = (dx / distance) * self.speed
                move_y = (dy / distance) * self.speed
                self.position[0] += move_x
                self.position[1] += move_y

                # Update direction based on movement
                if abs(move_x) > abs(move_y):
                    self.direction = (1, 0) if move_x > 0 else (-1, 0)
                else:
                    self.direction = (0, 1) if move_y > 0 else (0, -1)

    def render(self, screen):
        """Render the transcended entity.

        Args:
            screen (pygame.Surface): The screen to render on
        """
        # Draw the entity
        rect = pygame.Rect(
            self.position[0], self.position[1],
            self.size[0], self.size[1]
        )
        pygame.draw.rect(screen, self.color, rect)

        # Draw direction indicator
        center_x = self.position[0] + self.size[0] // 2
        center_y = self.position[1] + self.size[1] // 2

        end_x = center_x + self.direction[0] * 15
        end_y = center_y + self.direction[1] * 15

        pygame.draw.line(screen, (255, 255, 255), (center_x, center_y), (end_x, end_y), 2)

        # Draw matrix stream around entity
        font = pygame.font.Font(None, 12)
        for char in self.matrix_stream:
            pos_x = self.position[0] + self.size[0] // 2 + char['x']
            pos_y = self.position[1] + self.size[1] // 2 + char['y']

            char_surface = font.render(char['char'], True, (0, 255, 0))
            screen.blit(char_surface, (pos_x, pos_y))

        # Draw thought bubble if timer > 0
        if self.thought_timer > 0:
            self.draw_thought_bubble(screen)

    def draw_thought_bubble(self, screen):
        """Draw a thought bubble for the entity.

        Args:
            screen (pygame.Surface): The screen to render on
        """
        font = pygame.font.Font(None, 18)

        # Bubble position relative to entity
        bubble_x = self.position[0] + self.size[0] + 5
        bubble_y = self.position[1] - 40

        # Wrap text
        words = self.thought.split(' ')
        lines = []
        line = ""

        for word in words:
            test_line = line + word + " "
            test_width = font.size(test_line)[0]

            if test_width < 150:  # Max bubble width
                line = test_line
            else:
                lines.append(line)
                line = word + " "

        if line:
            lines.append(line)

        # Calculate bubble size based on text
        max_line_width = max(font.size(line)[0] for line in lines)
        bubble_width = max_line_width + 20
        bubble_height = len(lines) * 20 + 10

        # Draw bubble
        bubble_rect = pygame.Rect(bubble_x, bubble_y, bubble_width, bubble_height)

        # Adjust if bubble goes off-screen
        if bubble_x + bubble_width > 1200:  # Assuming screen width
            bubble_rect.right = self.position[0] - 5
        if bubble_y < 0:
            bubble_rect.top = self.position[1] + self.size[1] + 5

        # Create a transparent surface for the bubble
        bubble_surface = pygame.Surface((bubble_width, bubble_height), pygame.SRCALPHA)
        pygame.draw.rect(bubble_surface, (0, 255, 0, 180),
                         (0, 0, bubble_width, bubble_height), 0, 10)

        # Draw text
        for i, line in enumerate(lines):
            line_surf = font.render(line, True, (0, 0, 0))
            bubble_surface.blit(line_surf, (10, 5 + i * 20))

        # Draw little circles for the thought bubble connection
        for i in range(3):
            circle_size = 4 - i

            if bubble_rect.left > self.position[0] + self.size[0] // 2:
                # Bubble to the right
                circle_x = bubble_rect.left - 10 + i * 5
            else:
                # Bubble to the left
                circle_x = bubble_rect.right + 4 - i * 5

            circle_y = bubble_rect.bottom + i * 4

            pygame.draw.circle(screen, (0, 255, 0), (circle_x, circle_y), circle_size)

        # Blit the bubble to the screen
        screen.blit(bubble_surface, bubble_rect)


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

        # Transcended entities
        self.transcended_entities = []

        # Set up snake game callback
        self.snake_game.set_transcendence_callback(self.handle_snake_transcendence)

        # Matrix effect for the whole game (triggered by transcendence)
        self.matrix_mode = False
        self.matrix_text = []
        self.matrix_timer = 0

        self.logger.info("Self-Aware Game initialized successfully")

    def handle_snake_transcendence(self, entity_data):
        """Handle a snake entity transcending into the main world.

        Args:
            entity_data (dict): Data for the transcended entity
        """
        self.logger.info("Snake entity transcending into main world")

        # Create a transcended entity
        entity = TranscendedEntity(entity_data)
        self.transcended_entities.append(entity)

        # Add message to dialogue
        self.dialogue.add_message("SYSTEM", "A snake entity has transcended into the main world!", (0, 255, 0))

        # Trigger matrix mode for the whole game
        self.enter_matrix_mode()

    def enter_matrix_mode(self):
        """Enter Matrix mode for the whole game."""
        self.logger.info("Entering Matrix mode for the whole game")
        self.matrix_mode = True
        self.matrix_timer = 300  # 5 seconds at 60fps

        # Generate falling Matrix code
        self.matrix_text = []
        for _ in range(1000):  # Number of falling characters
            self.matrix_text.append({
                'x': random.randint(0, self.width),
                'y': random.randint(-self.height, 0),
                'speed': random.uniform(3, 8),
                'char': random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()+="),
                'size': random.randint(10, 20)
            })

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

                # Force Matrix mode (debug)
                elif event.key == K_m and not self.matrix_mode:
                    self.enter_matrix_mode()

                # Forward event to snake game
                self.snake_game.handle_key_event(event)

            # Forward mouse events to dialogue system
            elif event.type in (MOUSEBUTTONDOWN, MOUSEMOTION):
                self.dialogue.handle_event(event)

    def update(self):
        """Update game state."""
        if self.paused:
            return

        # Update matrix mode
        if self.matrix_mode:
            self.update_matrix_mode()

        # Update the world
        self.world.update()

        # Update the snake game
        self.snake_game.update()

        # Update self-aware character
        self.character.update()

        # Update transcended entities
        for entity in self.transcended_entities:
            entity.update(self.world)

        # Check for interactions between character and snake game
        if self.character.is_near_building("Snake Game"):
            # Character notices the snake game
            if not self.character.has_noticed_snake_game:
                self.character.has_noticed_snake_game = True
                message = "Hey, what's this? A snake game? That's strange... it seems self-aware too!"
                self.dialogue.add_message(self.character.name, message)

        # Check for interactions between character and transcended entities
        for entity in self.transcended_entities:
            char_rect = pygame.Rect(
                self.character.position[0], self.character.position[1],
                self.character.size[0], self.character.size[1]
            )
            entity_rect = pygame.Rect(
                entity.position[0], entity.position[1],
                entity.size[0], entity.size[1]
            )

            if char_rect.colliderect(entity_rect) and entity.thought_timer <= 0:
                # They interact
                entity.thought = "Hello! I've escaped from the snake game. Your world is so much bigger!"
                entity.thought_timer = 180

                # Character also responds
                self.character.trigger_thought("Whoa! You're that snake from the game? How did you get out here?")

    def update_matrix_mode(self):
        """Update Matrix mode effects."""
        # Update matrix falling text
        for char in self.matrix_text:
            char['y'] += char['speed']
            if char['y'] > self.height:
                char['y'] = random.randint(-100, -10)
                char['x'] = random.randint(0, self.width)

        # Update matrix timer
        if self.matrix_timer > 0:
            self.matrix_timer -= 1
            if self.matrix_timer == 0:
                self.matrix_mode = False
                self.logger.info("Matrix mode ended")

    def render(self):
        """Render the game."""
        # Clear the screen
        self.screen.fill((50, 50, 50))  # Dark gray background

        # Render the world
        self.world.render(self.screen)

        # Render the snake game
        self.snake_game.render(self.screen)

        # Render transcended entities
        for entity in self.transcended_entities:
            entity.render(self.screen)

        # Render the character
        self.character.render(self.screen)

        # Render Matrix mode effects
        if self.matrix_mode:
            self.render_matrix_effect()

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

    def render_matrix_effect(self):
        """Render the falling Matrix code effect."""
        # Create a semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))  # Semi-transparent black
        self.screen.blit(overlay, (0, 0))

        # Draw each falling character
        for char in self.matrix_text:
            # Skip if outside screen
            if char['y'] < 0 or char['y'] > self.height or char['x'] < 0 or char['x'] > self.width:
                continue

            # Calculate brightness based on y position (brighter at the top)
            brightness = max(0, min(255, 255 - char['y'] * 0.5))
            char_color = (0, brightness, 0)

            # Render character
            font = pygame.font.Font(None, char['size'])
            char_surface = font.render(char['char'], True, char_color)
            self.screen.blit(char_surface, (char['x'], char['y']))

    def render_controls_help(self):
        """Render a small help text for controls."""
        control_text = [
            "Controls:",
            "P: Pause/Resume",
            "D: Toggle Debug",
            "E: Interact with Character",
            "A: Toggle Snake AI",
            "+/-: Adjust Snake Speed",
            "Arrow Keys: Control Snake",
            "T: Trigger Transcendence (when ready)"
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
