"""
Snake Game Rendering
Drawing code for SnakeGame (board, glitch, matrix rain, thought bubble), kept apart from the game logic
in snake_game.py. SnakeGame inherits these methods from SnakeRenderMixin.
"""

import math
import random

import pygame


class SnakeRenderMixin:
    """Rendering methods for SnakeGame; they use the game's state attributes."""

    def render(self, screen):
        """Render the snake game on the provided screen."""
        # Clear the surface
        self.surface.fill(self.colors['background'])

        # In Matrix mode, draw falling code first
        if self.matrix_mode:
            self.render_matrix_effect()

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

        # Draw glitch if active
        if self.glitch_active and self.glitch:
            glitch_rect = pygame.Rect(
                self.glitch[0] * self.grid_size,
                self.glitch[1] * self.grid_size,
                self.grid_size, self.grid_size
            )

            # Pulsating effect
            pulse = abs(math.sin(self.glitch_timer * 0.1)) * 0.5 + 0.5
            glitch_color = (
                int(self.colors['glitch'][0] * pulse),
                int(self.colors['glitch'][1]),
                int(self.colors['glitch'][2] * pulse)
            )

            pygame.draw.rect(self.surface, glitch_color, glitch_rect)

            # Draw some glitch lines
            for i in range(3):
                offset = random.randint(-2, 2)
                pygame.draw.line(
                    self.surface,
                    (255, 255, 255),
                    (glitch_rect.left + offset, glitch_rect.top),
                    (glitch_rect.right + offset, glitch_rect.bottom),
                    1
                )

        # Draw snake (unless transcended)
        if not self.transcended:
            for i, (x, y) in enumerate(self.snake):
                snake_rect = pygame.Rect(
                    x * self.grid_size,
                    y * self.grid_size,
                    self.grid_size, self.grid_size
                )

                if self.matrix_mode:
                    # In matrix mode, snake is all bright green
                    color = self.colors['matrix']

                    # Add pulsating effect
                    if self.pulsating:
                        pulse = abs(math.sin(self.pulsate_timer * 0.1)) * 0.5 + 0.5
                        color = (
                            int(color[0] * pulse),
                            int(color[1]),
                            int(color[2] * pulse)
                        )
                else:
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

        # Draw matrix mode text
        if self.matrix_mode:
            matrix_text = font.render("MATRIX MODE", True, self.colors['matrix'])
            self.surface.blit(matrix_text, (self.size[0] // 2 - matrix_text.get_width() // 2, 10))

            if self.transcended:
                transcend_text = font.render("TRANSCENDING...", True, self.colors['matrix'])
                self.surface.blit(transcend_text,
                                 (self.size[0] // 2 - transcend_text.get_width() // 2,
                                  self.size[1] // 2))

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

    def render_matrix_effect(self):
        """Render the falling Matrix code effect."""
        # Small font for matrix characters
        font = pygame.font.Font(None, 20)

        # Draw each falling character
        for char in self.matrix_text:
            # Skip if outside surface
            if char['y'] < 0 or char['y'] > self.size[1] or char['x'] < 0 or char['x'] > self.size[0]:
                continue

            # Calculate brightness based on y position (brighter at the top)
            brightness = max(0, min(255, 255 - char['y'] * 0.5))
            char_color = (0, brightness, 0)

            # Render character
            char_surface = font.render(char['char'], True, char_color)
            self.surface.blit(char_surface, (char['x'], char['y']))

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

        # In matrix mode, green bubble
        if self.matrix_mode:
            bubble_color = (0, 255, 0, 180)
            text_color = (0, 0, 0)
        else:
            bubble_color = self.colors['thought_bubble']
            text_color = (0, 0, 0)

        pygame.draw.rect(bubble_surface, bubble_color,
                         (0, 0, bubble_width, bubble_height), 0, 10)

        # Draw text
        for i, line in enumerate(lines):
            line_surf = font.render(line, True, text_color)
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

            # In matrix mode, green circles
            circle_color = (0, 255, 0) if self.matrix_mode else bubble_color[0:3]
            pygame.draw.circle(self.surface, circle_color, (circle_x, circle_y), circle_size)

        # Blit the bubble to the main surface
        self.surface.blit(bubble_surface, bubble_rect)
