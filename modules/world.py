"""
Game World Module
Manages the world environment, buildings, and objects.
"""

import pygame
import logging

logger = logging.getLogger("world")

class Building:
    """A building in the game world that can contain a sub-game or functionality."""
    
    def __init__(self, name, position, size, game_instance=None):
        """Initialize a building.
        
        Args:
            name (str): Name of the building
            position (tuple): (x, y) position in the world
            size (tuple): (width, height) of the building
            game_instance (object, optional): Game that runs inside this building
        """
        self.name = name
        self.position = position
        self.size = size
        self.game_instance = game_instance
        self.color = (150, 150, 150)  # Default gray
        self.border_color = (100, 100, 100)
        self.highlighted = False
    
    def contains_point(self, x, y):
        """Check if a point is inside the building."""
        return (self.position[0] <= x <= self.position[0] + self.size[0] and
                self.position[1] <= y <= self.position[1] + self.size[1])
    
    def update(self):
        """Update the building and any contained game."""
        if self.game_instance:
            self.game_instance.update()
    
    def render(self, screen):
        """Render the building on the screen."""
        # Don't draw the building background if it has a game instance
        # Let the game draw itself
        if not self.game_instance:
            rect = pygame.Rect(self.position[0], self.position[1], 
                              self.size[0], self.size[1])
            pygame.draw.rect(screen, self.color, rect)
            pygame.draw.rect(screen, self.border_color, rect, 2)
            
            # Draw name
            font = pygame.font.Font(None, 24)
            text = font.render(self.name, True, (0, 0, 0))
            text_pos = (self.position[0] + (self.size[0] - text.get_width()) // 2,
                       self.position[1] + 10)
            screen.blit(text, text_pos)
        
        # If building has a game instance, let it render itself
        if self.game_instance:
            self.game_instance.render(screen)
            
            # Draw border around the game instance
            rect = pygame.Rect(self.position[0], self.position[1], 
                              self.size[0], self.size[1])
            border_color = (255, 255, 0) if self.highlighted else (50, 50, 50)
            pygame.draw.rect(screen, border_color, rect, 3)
            
            # Draw a small badge with the name
            badge_font = pygame.font.Font(None, 20)
            badge_text = badge_font.render(self.name, True, (255, 255, 255))
            badge_width = badge_text.get_width() + 10
            badge_height = badge_text.get_height() + 6
            
            badge_rect = pygame.Rect(
                self.position[0], 
                self.position[1] - badge_height,
                badge_width, 
                badge_height
            )
            pygame.draw.rect(screen, (0, 0, 0), badge_rect)
            pygame.draw.rect(screen, border_color, badge_rect, 1)
            
            screen.blit(badge_text, (
                self.position[0] + 5,
                self.position[1] - badge_height + 3
            ))


class GameWorld:
    """Manages the game world environment and all objects within it."""
    
    def __init__(self, width, height):
        """Initialize the game world.
        
        Args:
            width (int): Width of the world
            height (int): Height of the world
        """
        self.logger = logging.getLogger("GameWorld")
        self.logger.info(f"Initializing game world: {width}x{height}")
        
        self.width = width
        self.height = height
        self.buildings = {}
        self.characters = []
        self.objects = []
        
        # World properties
        self.background_color = (100, 150, 100)  # Grass-like
        self.grid_size = 50
        self.show_grid = True
        
        # Add some basic buildings
        self._create_default_buildings()
        
        self.logger.info("Game world initialized")
    
    def _create_default_buildings(self):
        """Create some default buildings in the world."""
        # We'll add buildings later when running the game
        pass
    
    def add_building(self, name, position, size, game_instance=None):
        """Add a building to the world."""
        self.logger.info(f"Adding building: {name} at {position}")
        building = Building(name, position, size, game_instance)
        self.buildings[name] = building
        return building
    
    def get_building(self, name):
        """Get a building by name."""
        return self.buildings.get(name)
    
    def get_buildings(self):
        """Return a list of all buildings."""
        return list(self.buildings.values())
    
    def add_character(self, character):
        """Add a character to the world."""
        self.logger.info(f"Adding character: {character.name}")
        self.characters.append(character)
    
    def check_collision(self, entity):
        """Check if an entity collides with any building."""
        entity_rect = pygame.Rect(entity.position[0], entity.position[1],
                                 entity.size[0], entity.size[1])
        
        for building in self.buildings.values():
            building_rect = pygame.Rect(building.position[0], building.position[1],
                                       building.size[0], building.size[1])
            
            if entity_rect.colliderect(building_rect):
                return True
        
        # Check world boundaries
        if (entity.position[0] < 0 or 
            entity.position[0] + entity.size[0] > self.width or
            entity.position[1] < 0 or
            entity.position[1] + entity.size[1] > self.height):
            return True
        
        return False
    
    def update(self):
        """Update all world elements."""
        # Update buildings
        for building in self.buildings.values():
            building.update()
    
    def render(self, screen):
        """Render the world."""
        # Fill background
        screen.fill(self.background_color)
        
        # Draw grid if enabled
        if self.show_grid:
            for x in range(0, self.width, self.grid_size):
                pygame.draw.line(screen, (120, 170, 120), (x, 0), (x, self.height))
            for y in range(0, self.height, self.grid_size):
                pygame.draw.line(screen, (120, 170, 120), (0, y), (self.width, y))
        
        # Draw buildings
        for building in self.buildings.values():
            building.render(screen)
