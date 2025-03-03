"""
Snake Game Module
A self-aware snake game that exists as a game within our larger simulation.
"""

import pygame
import random
import logging
import math
from pygame.locals import *

logger = logging.getLogger("snake_game")

class SnakeGame:
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

        # Colors
        self.colors = {
            'background': (0, 0, 0),
            'grid': (20, 20, 20),
            'snake_head': (0, 255, 0),
            'snake_body': (0, 200, 0),
            'food': (255, 0, 0),
            'text': (255, 255, 255),
            'thought_bubble': (200, 200, 255, 180)  # With some transparency
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

        # AI control
        if self.ai_controlled:
            self.ai_counter += 1
            if self.ai_counter >= self.ai_speed:
                self.ai_counter = 0
                self.ai_move()
            else:
                return  # Skip movement this frame for slower AI speed

        # Update direction
        self.direction = self.next_direction

        # Calculate new head position
        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = ((head_x + dx) % self.grid_width, (head_y + dy) % self.grid_height)

        # Check for collision with self
        if new_head in self.snake:
            self.game_over = True
            self.logger.info("Game over: Snake collided with itself")
            return

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

    def ai_move(self):
        """Determine the next move using AI."""
        head_x, head_y = self.snake[0]
        food_x, food_y = self.food

        # Available directions (can't go directly backwards)
        available_directions = []

        # Check which directions are valid moves (not immediately resulting in collision)
        opposite_direction = (-self.direction[0], -self.direction[1])

        for direction in [(0, -1), (1, 0), (0, 1), (-1, 0)]:  # Up, Right, Down, Left
            # Skip opposite direction (can't go backwards)
            if direction == opposite_direction:
                continue

            # Calculate potential new head position
            new_x = (head_x + direction[0]) % self.grid_width
            new_y = (head_y + direction[1]) % self.grid_height
            new_head = (new_x, new_y)

            # Check if this would hit the snake's body
            # (Skip the last tail segment which will move out of the way)
            if new_head not in self.snake[:-1]:
                available_directions.append(direction)

        # If no valid moves, continue in current direction (will likely result in game over)
        if not available_directions:
            return

        # If awareness is higher, use smarter pathfinding
        if self.awareness_level >= 5 and random.random() < 0.8:
            # Calculate distances for each direction
            direction_scores = []

            for direction in available_directions:
                new_x = (head_x + direction[0]) % self.grid_width
                new_y = (head_y + direction[1]) % self.grid_height

                # Manhattan distance to food
                distance = abs(new_x - food_x) + abs(new_y - food_y)

                # Check if moving in this direction leaves escape routes
                # (Higher awareness means more look-ahead)
                escape_routes = 0
                for test_dir in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
                    test_x = (new_x + test_dir[0]) % self.grid_width
                    test_y = (new_y + test_dir[1]) % self.grid_height
                    if (test_x, test_y) not in self.snake[:-1]:
                        escape_routes += 1

                # Score is better (lower) with:
                # - Closer to food
                # - More escape routes
                score = distance - (escape_routes * 0.5)
                direction_scores.append((direction, score))

            # Sort by score (lower is better)
            direction_scores.sort(key=lambda x: x[1])

            # Choose the best direction
            self.next_direction = direction_scores[0][0]

        else:
            # Simpler AI for lower awareness - try to move toward food when possible
            best_direction = None
            best_distance = float('inf')

            for direction in available_directions:
                new_x = (head_x + direction[0]) % self.grid_width
                new_y = (head_y + direction[1]) % self.grid_height

                # Manhattan distance to food
                distance = abs(new_x - food_x) + abs(new_y - food_y)

                # Sometimes make random moves when awareness is low
                if self.awareness_level < 3 and random.random() < 0.3:
                    distance = random.randint(0, 100)  # Random decision

                if distance < best_distance:
                    best_distance = distance
                    best_direction = direction

            if best_direction:
                self.next_direction = best_direction
            else:
                # Fallback - choose random direction
                self.next_direction = random.choice(available_directions)

    def render(self, screen):
        """Render the snake game on the provided screen."""
        # Clear the surface
        self.surface.fill(self.colors['background'])

        # Draw grid
        for x in range(0, self.size[0], self.grid_size):
            pygame.draw.line(self.surface, self.colors['grid'], (x, 0), (x, self.size[1]))
        for y in range(0, self.size[1], self.grid_size):
            pygame.draw.line(self.surface, self.colors['grid'], (0, y), (self.size[0], y))

        # Draw food
        food_rect = pygame.Rect(
            self.food[0] * self.grid_size,
            self.food[1] * self.grid_size,
            self.grid_size, self.grid_size
        )
        pygame.draw.rect(self.surface, self.colors['food'], food_rect)

        # Draw snake
        for i, (x, y) in enumerate(self.snake):
            snake_rect = pygame.Rect(
                x * self.grid_size,
                y * self.grid_size,
                self.grid_size, self.grid_size
            )
            color = self.colors['snake_head'] if i == 0 else self.colors['snake_body']
            pygame.draw.rect(self.surface, color, snake_rect)

        # Draw score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score}", True, self.colors['text'])
        self.surface.blit(score_text, (10, 10))

        # Draw awareness level if > 0
        if self.awareness_level > 0:
            awareness_text = font.render(f"Awareness: {int(self.awareness_level)}", True, self.colors['text'])
            self.surface.blit(awareness_text, (10, 50))

        # Draw AI mode indicator
        if self.ai_controlled:
            ai_text = font.render("AI Mode", True, (100, 200, 255))
            self.surface.blit(ai_text, (self.size[0] - 100, 10))

        # Draw thought bubble if active
        if self.thought_timer > 0:
            self.draw_thought_bubble()

        # Draw game over message
        if self.game_over:
            game_over_font = pygame.font.Font(None, 72)
            game_over_text = game_over_font.render("Game Over", True, (255, 0, 0))
            restart_text = font.render("Press R to restart", True, self.colors['text'])

            # Center the text
            self.surface.blit(
                game_over_text,
                (self.size[0] // 2 - game_over_text.get_width() // 2,
                 self.size[1] // 2 - game_over_text.get_height() // 2)
            )
            self.surface.blit(
                restart_text,
                (self.size[0] // 2 - restart_text.get_width() // 2,
                 self.size[1] // 2 + game_over_text.get_height())
            )

        # Draw paused indicator
        if self.paused:
            paused_font = pygame.font.Font(None, 72)
            paused_text = paused_font.render("PAUSED", True, (255, 255, 255))
            self.surface.blit(
                paused_text,
                (self.size[0] // 2 - paused_text.get_width() // 2,
                 self.size[1] // 2 - paused_text.get_height() // 2)
            )

        # Draw the surface on the screen at the correct position
        screen.blit(self.surface, self.position)

    def draw_thought_bubble(self):
        """Draw a thought bubble with the current thought."""
        font = pygame.font.Font(None, 24)

        # Get head position
        head_x, head_y = self.snake[0]
        bubble_x = head_x * self.grid_size + self.grid_size
        bubble_y = head_y * self.grid_size - 60

        # Wrap text
        words = self.current_thought.split(' ')
        lines = []
        line = ""

        for word in words:
            test_line = line + word + " "
            test_width = font.size(test_line)[0]

            if test_width < 200:  # Max bubble width
                line = test_line
            else:
                lines.append(line)
                line = word + " "

        if line:
            lines.append(line)

        # Calculate bubble size based on text
        max_line_width = max(font.size(line)[0] for line in lines)
        bubble_width = max_line_width + 20
        bubble_height = len(lines) * 25 + 10

        # Draw bubble
        bubble_rect = pygame.Rect(bubble_x, bubble_y, bubble_width, bubble_height)

        # Adjust if bubble goes off-screen
        if bubble_x + bubble_width > self.size[0]:
            bubble_rect.right = head_x * self.grid_size - 5
        if bubble_y < 0:
            bubble_rect.top = head_y * self.grid_size + self.grid_size + 5

        # Create a transparent surface for the bubble
        bubble_surface = pygame.Surface((bubble_width, bubble_height), pygame.SRCALPHA)
        pygame.draw.rect(bubble_surface, self.colors['thought_bubble'],
                         (0, 0, bubble_width, bubble_height), 0, 10)

        # Draw text
        for i, line in enumerate(lines):
            line_surf = font.render(line, True, (0, 0, 0))
            bubble_surface.blit(line_surf, (10, 5 + i * 25))

        # Draw little circles for the thought bubble connection
        for i in range(3):
            circle_size = 6 - i * 2

            # Position depends on which side of the head the bubble is
            if bubble_rect.left > head_x * self.grid_size:
                # Bubble to the right
                circle_x = bubble_rect.left - 10 + i * 6
            else:
                # Bubble to the left
                circle_x = bubble_rect.right + 4 - i * 6

            circle_y = bubble_rect.bottom + i * 5

            pygame.draw.circle(self.surface, self.colors['thought_bubble'][0:3],
                               (circle_x, circle_y), circle_size)

        # Blit the bubble to the main surface
        self.surface.blit(bubble_surface, bubble_rect)

        # Create a transparent surface for the bubble
        bubble_surface = pygame.Surface((bubble_width, bubble_height), pygame.SRCALPHA)
        pygame.draw.rect(bubble_surface, self.colors['thought_bubble'],
                         (0, 0, bubble_width, bubble_height), 0, 10)

        # Draw text
        for i, line in enumerate(lines):
            line_surf = font.render(line, True, (0, 0, 0))
            bubble_surface.blit(line_surf, (10, 5 + i * 25))

        # Draw little circles for the thought bubble connection
        for i in range(3):
            circle_size = 6 - i * 2

            # Position depends on which side of the head the bubble is
            if bubble_rect.left > head_x * self.grid_size:
                # Bubble to the right
                circle_x = bubble_rect.left - 10 + i * 6
            else:
                # Bubble to the left
                circle_x = bubble_rect.right + 4 - i * 6

            circle_y = bubble_rect.bottom + i * 5

            pygame.draw.circle(self.surface, self.colors['thought_bubble'][0:3],
                               (circle_x, circle_y), circle_size)

        # Blit the bubble to the main surface
        self.surface.blit(bubble_surface, bubble_rect)
