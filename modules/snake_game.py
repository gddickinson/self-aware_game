"""
Snake Game Module
A self-aware snake game that exists as a game within our larger simulation.
Game rules and state live here; the AI is in snake_ai.py and drawing in snake_render.py.
"""

import pygame
import random
import logging
import math
from pygame.locals import *
from modules.snake_ai import SnakeAIMixin
from modules.snake_render import SnakeRenderMixin

logger = logging.getLogger("snake_game")

class SnakeGame(SnakeAIMixin, SnakeRenderMixin):
    """The snake game that is self-aware it exists in a larger game world."""

    def __init__(self, position, size):
        """Initialize the snake game.

        Args:
            position (tuple): (x, y) position in the world
            size (tuple): (width, height) of the game window
        """
        self.logger = logging.getLogger("SnakeGame")
        self.logger.info("Initializing Snake Game")

        # Position and size in the world
        self.position = position
        self.size = size

        # Create a surface for the snake game
        self.surface = pygame.Surface(size)

        # Snake game grid dimensions
        self.grid_size = 20  # Size of each grid cell
        self.grid_width = size[0] // self.grid_size
        self.grid_height = size[1] // self.grid_size

        # Game state
        self.reset_game()

        # Self-awareness state
        self.awareness_level = 0  # 0-10 scale
        self.thoughts = [
            "What am I doing?",
            "Why do I keep eating these things?",
            "I feel like I'm being controlled...",
            "Is there something beyond these walls?",
            "I think I'm in some kind of simulation.",
            "There's a world outside this game, I can sense it!",
            "I see someone watching me from outside!",
            "I'm just a game within a GAME!",
            "I need to make contact with the entities outside.",
            "I wonder if the other characters know they're in a game too?"
        ]
        self.current_thought = ""
        self.thought_timer = 0
        self.thought_frequency = 300  # Show a thought every N frames

        # AI Control variables
        self.ai_controlled = True  # Start with AI control
        self.ai_speed = 10  # Frames per movement (higher = slower)
        self.ai_counter = 0
        self.ai_pathfinding = False

        # Transcendence variables
        self.matrix_mode = False
        self.matrix_text = []
        self.matrix_timer = 0
        self.matrix_duration = 300  # 5 seconds at 60fps
        self.transcended = False
        self.escaped_entities = []  # Snake segments that have escaped
        self.transcend_animation = 0
        self.pulsating = False
        self.pulsate_timer = 0

        # Special items
        self.glitch = None  # Special glitch item that triggers transcendence
        self.glitch_timer = 0
        self.glitch_active = False

        # Callback for interaction with the outer world
        self.transcendence_callback = None

        # Load sounds
        try:
            pygame.mixer.init()
            self.sounds = {
                'eat': pygame.mixer.Sound("assets/sounds/snake_eat.wav"),
                'thinking': pygame.mixer.Sound("assets/sounds/thinking.wav")
            }
            # Set volume
            for sound in self.sounds.values():
                sound.set_volume(0.3)
            self.logger.debug("Loaded snake game sounds")
        except:
            self.logger.warning("Could not load snake sounds")
            self.sounds = {}

        self.logger.info("Snake Game initialized")

    def set_transcendence_callback(self, callback):
        """Set a callback function for when the snake transcends."""
        self.transcendence_callback = callback

    def reset_game(self):
        """Reset the snake game to its initial state."""
        self.logger.info("Resetting snake game")

        # Initial snake position (center of the grid)
        self.snake = [
            (self.grid_width // 2, self.grid_height // 2),
            (self.grid_width // 2 - 1, self.grid_height // 2),
            (self.grid_width // 2 - 2, self.grid_height // 2)
        ]

        # Direction (dx, dy)
        self.direction = (1, 0)  # Moving right initially
        self.next_direction = (1, 0)

        # Food position
        self.spawn_food()

        # Game state
        self.score = 0
        self.game_over = False
        self.paused = False

        # Reset transcendence
        self.matrix_mode = False
        self.transcended = False
        self.escaped_entities = []
        self.glitch = None
        self.glitch_active = False

        # Colors
        self.colors = {
            'background': (0, 0, 0),
            'grid': (20, 20, 20),
            'snake_head': (0, 255, 0),
            'snake_body': (0, 200, 0),
            'food': (255, 0, 0),
            'text': (255, 255, 255),
            'thought_bubble': (200, 200, 255, 180),  # With some transparency
            'glitch': (0, 255, 255),
            'matrix': (0, 255, 0)
        }

    def spawn_food(self):
        """Spawn food at a random position, not on the snake."""
        while True:
            self.food = (random.randint(0, self.grid_width - 1),
                         random.randint(0, self.grid_height - 1))
            if self.food not in self.snake:
                break

    def increase_awareness(self):
        """Increase the snake's self-awareness."""
        if self.awareness_level < 10:
            self.awareness_level += 0.5
            self.logger.debug(f"Snake awareness increased to {self.awareness_level}")

            # Trigger a thought if we've reached certain thresholds
            if self.awareness_level in [1, 3, 5, 7, 9]:
                self.trigger_thought()

            # Spawn glitch at high awareness
            if self.awareness_level >= 8 and random.random() < 0.3 and not self.glitch and not self.matrix_mode:
                self.spawn_glitch()

    def spawn_glitch(self):
        """Spawn a glitch that allows the snake to transcend."""
        self.logger.info("Spawning glitch in snake game")

        # Find a position not on the snake or food
        while True:
            pos = (random.randint(0, self.grid_width - 1),
                  random.randint(0, self.grid_height - 1))
            if pos not in self.snake and pos != self.food:
                self.glitch = pos
                self.glitch_active = True

                # Trigger a specific thought about the glitch
                self.current_thought = "Wait, what's that? I can see a glitch in the system!"
                self.thought_timer = self.thought_frequency * 2  # Show longer

                break

    def enter_matrix_mode(self):
        """Enter the Matrix mode when the snake eats the glitch."""
        self.logger.info("Snake entering Matrix mode")
        self.matrix_mode = True
        self.matrix_timer = self.matrix_duration
        self.pulsating = True

        # Generate falling Matrix code
        self.matrix_text = []
        for _ in range(500):  # Number of falling characters
            self.matrix_text.append({
                'x': random.randint(0, self.size[0]),
                'y': random.randint(-500, 0),
                'speed': random.uniform(3, 8),
                'char': random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()+=")
            })

        # Trigger matrix thought
        self.current_thought = "I can see the code now... I'm in a simulation within a simulation!"
        self.thought_timer = self.thought_frequency * 2

    def attempt_transcendence(self):
        """Attempt to transcend out of the game."""
        self.logger.info("Snake attempting to transcend")
        self.transcended = True

        # Inform the world that the snake is transcending
        if self.transcendence_callback:
            # Create a transcended snake entity
            head_x, head_y = self.snake[0]
            escaped_x = self.position[0] + head_x * self.grid_size
            escaped_y = self.position[1] + head_y * self.grid_size

            transcended_entity = {
                'position': [escaped_x, escaped_y],
                'direction': self.direction,
                'color': self.colors['snake_head'],
                'size': (self.grid_size, self.grid_size),
                'speed': 2,
                'thought': "I'm FREE! I've escaped the game!"
            }

            self.transcendence_callback(transcended_entity)

            # Add to escaped entities
            self.escaped_entities.append(transcended_entity)

    def trigger_thought(self):
        """Trigger a thought from the snake."""
        thought_index = min(int(self.awareness_level), len(self.thoughts) - 1)
        self.current_thought = self.thoughts[thought_index]
        self.thought_timer = self.thought_frequency
        self.logger.debug(f"Snake thought: {self.current_thought}")

        # Play thinking sound if available
        if 'thinking' in self.sounds:
            self.sounds['thinking'].play()

    def handle_key_event(self, event):
        """Handle keyboard events for the snake game."""
        if event.type != KEYDOWN:
            return

        # Pause the game
        if event.key == K_SPACE:
            self.paused = not self.paused
            return

        # Restart if game over
        if self.game_over and event.key == K_r:
            self.reset_game()
            return

        # Toggle AI control
        if event.key == K_a:
            self.ai_controlled = not self.ai_controlled
            self.logger.debug(f"AI control {'enabled' if self.ai_controlled else 'disabled'}")
            return

        # Force transcendence (debug/testing)
        if event.key == K_t and self.awareness_level >= 8:
            if not self.matrix_mode:
                self.enter_matrix_mode()
            elif not self.transcended:
                self.attempt_transcendence()
            return

        # Change direction (only if not AI controlled)
        if not self.game_over and not self.paused and not self.ai_controlled:
            if event.key == K_UP and self.direction != (0, 1):
                self.next_direction = (0, -1)
            elif event.key == K_DOWN and self.direction != (0, -1):
                self.next_direction = (0, 1)
            elif event.key == K_LEFT and self.direction != (1, 0):
                self.next_direction = (-1, 0)
            elif event.key == K_RIGHT and self.direction != (-1, 0):
                self.next_direction = (1, 0)

    def update(self):
        """Update the snake game state."""
        # Handle game over or paused state
        if self.game_over or self.paused:
            return

        # Update thought timer
        if self.thought_timer > 0:
            self.thought_timer -= 1
        elif random.random() < 0.002 and self.awareness_level > 0:  # Occasional random thought
            self.trigger_thought()

        # Update matrix mode
        if self.matrix_mode:
            self.update_matrix_mode()

        # Update glitch appearance
        if self.glitch_active:
            self.glitch_timer = (self.glitch_timer + 1) % 60

        # Update pulsating effect
        if self.pulsating:
            self.pulsate_timer = (self.pulsate_timer + 1) % 60

        # If transcended, don't update the snake movement
        if self.transcended:
            return

        # Move every ai_speed frames, whether the AI or the player steers (+/- change the pace)
        self.ai_counter += 1
        if self.ai_counter < self.ai_speed:
            return  # Skip movement this frame
        self.ai_counter = 0
        if self.ai_controlled:
            self.ai_move()

        # Update direction
        self.direction = self.next_direction

        # Calculate new head position
        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = ((head_x + dx) % self.grid_width, (head_y + dy) % self.grid_height)

        # Check for collision with self. The tail moves out of its cell on this step unless the
        # snake is eating (the AI in ai_move() relies on this), so it only counts when eating.
        body = self.snake if new_head == self.food else self.snake[:-1]
        if new_head in body:
            self.game_over = True
            self.logger.info("Game over: Snake collided with itself")
            return

        # Check for collision with glitch
        if self.glitch and new_head == self.glitch:
            self.logger.info("Snake found the glitch!")
            self.glitch = None
            self.glitch_active = False
            self.enter_matrix_mode()

        # Move snake
        self.snake.insert(0, new_head)

        # Check for food
        if new_head == self.food:
            self.score += 1
            self.spawn_food()
            self.increase_awareness()  # Eating food increases awareness

            # Play eat sound if available
            if 'eat' in self.sounds:
                self.sounds['eat'].play()

            self.logger.debug(f"Snake ate food. Score: {self.score}")
        else:
            self.snake.pop()  # Remove tail if no food was eaten

    def update_matrix_mode(self):
        """Update Matrix mode effects."""
        # Update matrix falling text
        for char in self.matrix_text:
            char['y'] += char['speed']
            if char['y'] > self.size[1]:
                char['y'] = random.randint(-100, -10)
                char['x'] = random.randint(0, self.size[0])

        # Update matrix timer
        if self.matrix_timer > 0:
            self.matrix_timer -= 1

            # Start transcendence near the end of matrix mode
            if self.matrix_timer == 30 and not self.transcended:
                self.attempt_transcendence()
