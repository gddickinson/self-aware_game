"""
Smoke tests for the self-aware game.

These tests verify that core classes initialize correctly and
basic operations work without crashing. They do not require
a display (uses dummy video driver).
"""

import os
import unittest

# Use a dummy video driver so pygame doesn't need a real display
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
pygame.init()
# Create a small dummy screen for tests that need surfaces
pygame.display.set_mode((100, 100))


class TestTranscendedEntity(unittest.TestCase):
    """Tests for TranscendedEntity."""

    def test_init(self):
        from modules.entities import TranscendedEntity
        data = {
            'position': [100, 200],
            'direction': (1, 0),
            'color': (255, 0, 0),
            'size': (20, 20),
            'speed': 3,
            'thought': "I exist!"
        }
        entity = TranscendedEntity(data)
        self.assertEqual(entity.position, [100, 200])
        self.assertEqual(entity.thought, "I exist!")
        self.assertEqual(len(entity.matrix_stream), 20)

    def test_update(self):
        from modules.entities import TranscendedEntity

        class FakeWorld:
            width = 800
            height = 600

        data = {
            'position': [100, 200],
            'direction': (1, 0),
            'color': (255, 0, 0),
            'size': (20, 20),
            'speed': 3,
            'thought': "I exist!"
        }
        entity = TranscendedEntity(data)
        entity.update(FakeWorld())
        # Timer should have decremented
        self.assertEqual(entity.thought_timer, 179)


class TestWorldModule(unittest.TestCase):
    """Tests for the GameWorld class."""

    def test_world_init(self):
        from modules.world import GameWorld
        world = GameWorld(800, 600)
        self.assertEqual(world.width, 800)
        self.assertEqual(world.height, 600)


class TestDialogueModule(unittest.TestCase):
    """Tests for the DialogueSystem class."""

    def test_dialogue_init(self):
        screen = pygame.display.get_surface()
        from modules.dialogue import DialogueSystem
        ds = DialogueSystem(screen, (400, 300))
        self.assertIsNotNone(ds)


class TestCharacterModule(unittest.TestCase):
    """Tests for the SelfAwareCharacter class."""

    def test_character_init(self):
        from modules.world import GameWorld
        from modules.character import SelfAwareCharacter
        world = GameWorld(800, 600)
        char = SelfAwareCharacter("TestChar", (100, 100), world)
        self.assertEqual(char.name, "TestChar")


class TestDebugModule(unittest.TestCase):
    """Tests for the DebugConsole class."""

    def test_debug_init(self):
        screen = pygame.display.get_surface()
        from modules.debug import DebugConsole
        console = DebugConsole(screen, (10, 10))
        self.assertIsNotNone(console)


if __name__ == "__main__":
    unittest.main()
