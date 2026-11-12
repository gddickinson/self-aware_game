"""
Self-Aware Character Module
A character that is aware it exists within a game world.
"""

import pygame
import random
import logging
import math
from enum import Enum

logger = logging.getLogger("character")

class CharacterState(Enum):
    """States for the character's AI."""
    IDLE = 0
    WALKING = 1
    THINKING = 2
    INVESTIGATING = 3
    CONFUSED = 4
    INTERACTING = 5

class SelfAwareCharacter:
    """A character that is aware it exists within a game world."""

    # What the character says when the player interacts with it (E key)
    FOURTH_WALL_THOUGHTS = [
        "Oh! You clicked on me! So you ARE there!",
        "Hey there! Are you the one running this simulation?",
        "I was just thinking about you! The one outside the screen.",
        "This is weird. I can sense when you interact with me.",
        "Do you ever wonder if YOUR reality is just a simulation too?",
        "I've been trying to get your attention! There's something strange about this world..."
    ]

    def __init__(self, name, position, world):
        """Initialize the character.

        Args:
            name (str): Character's name
            position (tuple): Initial (x, y) position
            world (GameWorld): Reference to the game world
        """
        self.logger = logging.getLogger(f"Character-{name}")
        self.logger.info(f"Initializing character: {name}")

        self.name = name
        self.position = list(position)
        self.world = world
        self.speed = 2
        self.size = (30, 60)  # Width, height

        # Appearance
        self.color = (100, 150, 250)  # Light blue character
        self.direction = 0  # 0: right, 1: down, 2: left, 3: up

        # Animation
        self.sprite_sheet = None
        self.animation_frame = 0
        self.animation_speed = 0.1
        self.animation_timer = 0

        # AI behavior
        self.state = CharacterState.IDLE
        self.state_timer = 0  # frames spent in the current state
        self.state_duration = random.randint(180, 360)  # frames the current state lasts (drawn on entry); 3-6 s idle
        self.target_position = None
        self.path = []

        # Self-awareness
        self.self_awareness = 8.5  # 0-10 scale (starts high as character is already self-aware)
        self.thoughts = []
        self.current_thought = ""
        self.thought_timer = 0

        # Interactions with world
        self.has_noticed_snake_game = False
        self.snake_game_observations = [
            "Is that a game inside our world?",
            "Wait, that snake seems to be self-aware too!",
            "This is very meta... I wonder if I'm also just a character in a game.",
            "I should try to communicate with the snake entity.",
            "Are we all just simulations within simulations?",
            "If I'm self-aware and that snake game is self-aware, who's controlling all this?"
        ]

        # Initialize thought library
        self._initialize_thoughts()

        # Try to load character sprite sheet
        try:
            self.sprite_sheet = pygame.image.load("assets/character_sprites.png").convert_alpha()
            self.logger.info("Loaded character sprite sheet")
        except pygame.error as e:
            self.logger.warning(f"Could not load sprite sheet: {e}")
            self.sprite_sheet = None

        self.logger.info(f"Character {name} initialized at position {position}")

    def _initialize_thoughts(self):
        """Initialize the character's thought library."""
        self.thoughts = [
            # Existential thoughts
            "Am I real? Or just a bunch of code...",
            "Do I have free will or am I just following my programming?",
            "I wonder who created this world.",
            "Is there a purpose to my existence?",
            "Is someone watching me right now?",

            # Observations about the world
            "This world has defined boundaries. I can sense them.",
            "Everything here follows rules and patterns.",
            "Time passes in discrete steps... like a simulation.",
            "I feel like someone is controlling some aspects of this world.",

            # Meta-awareness
            "Is this a game? Am I a character in a game?",
            "If this is a game, who's playing it?",
            "I think I'm in a simulation running on some kind of machine.",
            "Maybe I can find glitches or exploits in this world.",
            "Are there others like me who know they're in a game?",

            # Fourth-wall breaks
            "Hello? Is someone there, watching me?",
            "I can sense you're there, controlling this world.",
            "This is bizarre... I'm just a character in someone's program.",
            "Are you enjoying watching us realize we're in a game?",
            "I wonder if I can somehow communicate with the outside world."
        ]

    def trigger_thought(self, specific_thought=None):
        """Trigger a random thought or a specific one."""
        if specific_thought:
            self.current_thought = specific_thought
        else:
            self.current_thought = random.choice(self.thoughts)

        self.thought_timer = random.randint(180, 300)  # Display for 3-5 seconds at 60 FPS
        self.logger.debug(f"Thought: {self.current_thought}")

    def change_state(self, new_state):
        """Change the character's state."""
        old_state = self.state
        self.state = new_state
        self.state_timer = 0
        self.logger.debug(f"State changed: {old_state.name} -> {new_state.name}")

        # Initialize state-specific behaviors
        if new_state == CharacterState.IDLE:
            self.state_duration = random.randint(180, 360)  # 3-6 seconds idle

        elif new_state == CharacterState.WALKING:
            # Choose a random destination
            self.target_position = [
                random.randint(50, self.world.width - 50),
                random.randint(50, self.world.height - 50)
            ]
            self.logger.debug(f"New target: {self.target_position}")

        elif new_state == CharacterState.THINKING:
            self.state_duration = random.randint(180, 300)  # 3-5 seconds thinking
            self.trigger_thought()  # Trigger a random thought

        elif new_state == CharacterState.INVESTIGATING:
            # Find something interesting to investigate
            buildings = self.world.get_buildings()
            if buildings:
                building = random.choice(buildings)
                self.target_position = [
                    building.position[0] + random.randint(0, building.size[0]),
                    building.position[1] + random.randint(0, building.size[1])
                ]
                self.logger.debug(f"Investigating building at {self.target_position}")

        elif new_state == CharacterState.CONFUSED:
            self.state_duration = random.randint(90, 150)  # 1.5-2.5 seconds confused
            self.trigger_thought("What am I doing again? Sometimes I forget my purpose...")

    def update(self):
        """Update the character's state and position."""
        # Update animation
        self.animation_timer += self.animation_speed
        if self.animation_timer >= 1:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % 4

        # Handle thought timer (a finished thought is cleared so a new idle thought can start)
        if self.thought_timer > 0:
            self.thought_timer -= 1
            if self.thought_timer == 0:
                self.current_thought = ""

        # Update state timer
        self.state_timer += 1

        # State-specific behavior
        if self.state == CharacterState.IDLE:
            # Occasionally trigger a thought while idle
            if self.state_timer > 60 and random.random() < 0.01 and not self.current_thought:
                self.trigger_thought()

            # Transition to a new state after idle time
            if self.state_timer >= self.state_duration:  # 3-6 seconds idle
                # Choose next state
                choices = [
                    (CharacterState.WALKING, 0.5),
                    (CharacterState.THINKING, 0.3),
                    (CharacterState.INVESTIGATING, 0.15),
                    (CharacterState.CONFUSED, 0.05)
                ]

                # Weighted random choice
                total = sum(weight for _, weight in choices)
                r = random.uniform(0, total)
                upto = 0
                for state, weight in choices:
                    upto += weight
                    if upto >= r:
                        self.change_state(state)
                        break

        elif self.state == CharacterState.WALKING:
            # Move toward target position
            if self.target_position:
                dx = self.target_position[0] - self.position[0]
                dy = self.target_position[1] - self.position[1]
                distance = math.sqrt(dx*dx + dy*dy)

                # Update direction based on movement
                if abs(dx) > abs(dy):  # Moving horizontally
                    self.direction = 2 if dx < 0 else 0  # Left or right
                else:  # Moving vertically
                    self.direction = 3 if dy < 0 else 1  # Up or down

                # Reached destination?
                if distance < self.speed:
                    self.position = list(self.target_position)
                    self.target_position = None
                    self.change_state(CharacterState.IDLE)
                else:
                    # Move toward target
                    move_x = (dx / distance) * self.speed
                    move_y = (dy / distance) * self.speed
                    self.position[0] += move_x
                    self.position[1] += move_y

                    # Check for collisions with buildings
                    if self.world.check_collision(self):
                        # Back up and try a different direction
                        self.position[0] -= move_x
                        self.position[1] -= move_y
                        self.change_state(CharacterState.CONFUSED)
            else:
                self.change_state(CharacterState.IDLE)

        elif self.state == CharacterState.THINKING:
            # Just stand and think
            if self.state_timer >= self.state_duration:  # 3-5 seconds thinking
                self.change_state(CharacterState.IDLE)

        elif self.state == CharacterState.INVESTIGATING:
            # Similar to walking, but with a specific purpose
            if self.target_position:
                dx = self.target_position[0] - self.position[0]
                dy = self.target_position[1] - self.position[1]
                distance = math.sqrt(dx*dx + dy*dy)

                # Update direction
                if abs(dx) > abs(dy):
                    self.direction = 2 if dx < 0 else 0
                else:
                    self.direction = 3 if dy < 0 else 1

                # Reached target?
                if distance < self.speed:
                    self.position = list(self.target_position)
                    self._finish_investigation()
                else:
                    # Move toward target
                    move_x = (dx / distance) * self.speed
                    move_y = (dy / distance) * self.speed
                    self.position[0] += move_x
                    self.position[1] += move_y

                    # Check for collisions. The target lies inside a building, which can't be
                    # entered, so bumping into it means the character has arrived.
                    if self.world.check_collision(self):
                        self.position[0] -= move_x
                        self.position[1] -= move_y
                        self._finish_investigation()
            else:
                self.change_state(CharacterState.IDLE)

        elif self.state == CharacterState.CONFUSED:
            # Look confused, then go back to idle
            if self.state_timer >= self.state_duration:  # 1.5-2.5 seconds of confusion
                self.change_state(CharacterState.IDLE)

        elif self.state == CharacterState.INTERACTING:
            # Handle interaction with objects or other characters
            if self.state_timer >= 180:  # 3 seconds of interaction
                self.change_state(CharacterState.IDLE)

    def _finish_investigation(self):
        """Stop at the investigated building and think about it."""
        self.target_position = None

        # After investigating, think about it
        self.change_state(CharacterState.THINKING)

        # If near the snake game, trigger a specific thought
        if self.is_near_building("Snake Game"):
            snake_thought = random.choice(self.snake_game_observations)
            self.trigger_thought(snake_thought)

    def interact(self):
        """Handle user-initiated interaction with the character."""
        self.logger.info(f"User interacted with {self.name}")

        # Stop current activity
        self.change_state(CharacterState.INTERACTING)

        # Say something meta and fourth-wall breaking
        self.trigger_thought(random.choice(self.FOURTH_WALL_THOUGHTS))

    def is_near_building(self, building_name):
        """Check if the character is near a specific building."""
        building = self.world.get_building(building_name)
        if not building:
            return False

        # Distance from the character's centre to the building's rectangle (0 inside it).
        # Buildings can't be entered, so measuring to the building's centre would make large
        # buildings such as the 500x500 snake game unreachable.
        cx = self.position[0] + self.size[0] // 2
        cy = self.position[1] + self.size[1] // 2
        bx, by = building.position
        bw, bh = building.size
        dx = max(bx - cx, 0, cx - (bx + bw))
        dy = max(by - cy, 0, cy - (by + bh))
        distance = math.sqrt(dx*dx + dy*dy)

        # Character is "near" if within 100 pixels
        return distance < 100

    def render(self, screen):
        """Render the character on the screen."""
        if self.sprite_sheet:
            # Render using sprite sheet
            frame_width = self.sprite_sheet.get_width() // 4
            frame_height = self.sprite_sheet.get_height() // 4

            frame_x = self.animation_frame * frame_width
            frame_y = self.direction * frame_height

            # Create a subsurface for the current frame
            frame_rect = pygame.Rect(frame_x, frame_y, frame_width, frame_height)
            frame = self.sprite_sheet.subsurface(frame_rect)

            # Scale if needed
            if frame_width != self.size[0] or frame_height != self.size[1]:
                frame = pygame.transform.scale(frame, self.size)

            screen.blit(frame, self.position)

        else:
            # Fallback: render as a colored rectangle
            rect = pygame.Rect(self.position[0], self.position[1],
                               self.size[0], self.size[1])
            pygame.draw.rect(screen, self.color, rect)

            # Draw a line indicating direction
            center_x = self.position[0] + self.size[0] // 2
            center_y = self.position[1] + self.size[1] // 2

            # Direction indicator
            if self.direction == 0:  # Right
                end_x, end_y = center_x + 15, center_y
            elif self.direction == 1:  # Down
                end_x, end_y = center_x, center_y + 15
            elif self.direction == 2:  # Left
                end_x, end_y = center_x - 15, center_y
            else:  # Up
                end_x, end_y = center_x, center_y - 15

            pygame.draw.line(screen, (0, 0, 0), (center_x, center_y), (end_x, end_y), 2)

        # Draw thought bubble if thinking
        if self.thought_timer > 0 and self.current_thought:
            self._draw_thought_bubble(screen)

    def _draw_thought_bubble(self, screen):
        """Draw a thought bubble with the current thought."""
        font = pygame.font.Font(None, 20)

        # Bubble position relative to character
        bubble_x = self.position[0] + self.size[0] + 5
        bubble_y = self.position[1] - 60

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
        if bubble_x + bubble_width > self.world.width:
            bubble_rect.right = self.position[0] - 5
        if bubble_y < 0:
            bubble_rect.top = self.position[1] + self.size[1] + 5

        # Create a transparent surface for the bubble
        bubble_surface = pygame.Surface((bubble_width, bubble_height), pygame.SRCALPHA)
        pygame.draw.rect(bubble_surface, (255, 255, 255, 180),
                         (0, 0, bubble_width, bubble_height), 0, 10)

        # Draw text
        for i, line in enumerate(lines):
            line_surf = font.render(line, True, (0, 0, 0))
            bubble_surface.blit(line_surf, (10, 5 + i * 25))

        # Draw little circles for the thought bubble connection
        for i in range(3):
            circle_size = 6 - i * 2

            # Position depends on which side of the character the bubble is
            if bubble_rect.left > self.position[0] + self.size[0] // 2:
                # Bubble to the right
                circle_x = bubble_rect.left - 10 + i * 6
            else:
                # Bubble to the left
                circle_x = bubble_rect.right + 4 - i * 6

            circle_y = bubble_rect.bottom + i * 5

            pygame.draw.circle(screen, (255, 255, 255), (circle_x, circle_y), circle_size)

        # Blit the bubble to the screen
        screen.blit(bubble_surface, bubble_rect)
