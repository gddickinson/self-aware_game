"""
Transcended entity module.

Contains the TranscendedEntity class, which represents a game entity
that has transcended from one game context into the main world.
"""

import pygame
import random
import math


class TranscendedEntity:
    """An entity that has transcended from one game to another."""

    def __init__(self, data):
        """Initialize a transcended entity.

        Args:
            data (dict): Data for the entity, must contain keys:
                position, direction, color, size, speed, thought
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
            distance = math.sqrt(dx * dx + dy * dy)

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

        pygame.draw.line(screen, (255, 255, 255),
                         (center_x, center_y), (end_x, end_y), 2)

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
        bubble_surface = pygame.Surface(
            (bubble_width, bubble_height), pygame.SRCALPHA
        )
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

            pygame.draw.circle(screen, (0, 255, 0),
                               (circle_x, circle_y), circle_size)

        # Blit the bubble to the screen
        screen.blit(bubble_surface, bubble_rect)
