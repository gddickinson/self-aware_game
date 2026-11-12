"""
Snake Game AI
How the self-aware snake steers itself: toward food (or the glitch at high awareness), smarter with more
awareness, and toward the edges in Matrix mode. SnakeGame inherits these methods from SnakeAIMixin.
"""

import random


class SnakeAIMixin:
    """AI steering methods for SnakeGame; they set self.next_direction."""

    def ai_move(self):
        """Determine the next move using AI."""
        # If in matrix mode, prioritize moving toward the edges
        if self.matrix_mode and not self.transcended:
            self.ai_matrix_move()
            return

        head_x, head_y = self.snake[0]

        # If there's a glitch, prioritize going for it at high awareness
        if self.glitch and self.awareness_level >= 8:
            target_x, target_y = self.glitch
            self.logger.debug("Snake AI targeting glitch")
        else:
            target_x, target_y = self.food

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

                # Manhattan distance to target
                distance = abs(new_x - target_x) + abs(new_y - target_y)

                # Check if moving in this direction leaves escape routes
                # (Higher awareness means more look-ahead)
                escape_routes = 0
                for test_dir in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
                    test_x = (new_x + test_dir[0]) % self.grid_width
                    test_y = (new_y + test_dir[1]) % self.grid_height
                    if (test_x, test_y) not in self.snake[:-1]:
                        escape_routes += 1

                # Score is better (lower) with:
                # - Closer to target
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

                # Manhattan distance to target
                distance = abs(new_x - target_x) + abs(new_y - target_y)

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

    def ai_matrix_move(self):
        """AI movement during matrix mode - try to reach the edges."""
        head_x, head_y = self.snake[0]

        # Available directions (can't go directly backwards)
        available_directions = []
        opposite_direction = (-self.direction[0], -self.direction[1])

        for direction in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
            if direction == opposite_direction:
                continue

            new_x = (head_x + direction[0]) % self.grid_width
            new_y = (head_y + direction[1]) % self.grid_height

            if (new_x, new_y) not in self.snake[:-1]:
                available_directions.append(direction)

        if not available_directions:
            return

        # Calculate distance to nearest edge for each direction
        edge_scores = []

        for direction in available_directions:
            new_x = (head_x + direction[0]) % self.grid_width
            new_y = (head_y + direction[1]) % self.grid_height

            # Distance to nearest edge
            edge_dist = min(
                new_x,  # Distance to left edge
                self.grid_width - 1 - new_x,  # Distance to right edge
                new_y,  # Distance to top edge
                self.grid_height - 1 - new_y  # Distance to bottom edge
            )

            edge_scores.append((direction, edge_dist))

        # Sort by distance to edge (lower is better)
        edge_scores.sort(key=lambda x: x[1])

        # Choose direction closest to edge
        self.next_direction = edge_scores[0][0]
