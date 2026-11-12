"""Regression tests for bugs fixed in the desktop game (each fails on the code before its fix).

Run: python -m pytest -q tests/test_regressions.py
"""
import random

import pygame
import pytest

import main
from modules.character import CharacterState


@pytest.fixture
def game():
    random.seed(0)
    return main.SelfAwareGame()


def test_snake_game_updates_once_per_frame(game):
    """The snake game is a building of the world: one frame must advance it by exactly one tick."""
    before = game.snake_game.ai_counter
    game.update()
    assert game.snake_game.ai_counter == before + 1


def test_snake_game_renders_once_per_frame(game, monkeypatch):
    calls = []
    monkeypatch.setattr(game.snake_game, "render", lambda screen: calls.append(1))
    game.render()
    assert len(calls) == 1


def _snake(manual=True):
    from modules.snake_game import SnakeGame
    random.seed(1)
    s = SnakeGame((0, 0), (500, 500))
    s.ai_controlled = not manual
    return s


def test_snake_may_move_into_the_cell_its_tail_leaves():
    """A 2x2 loop: the head moves into the tail's cell, which the tail vacates on the same step."""
    s = _snake()
    s.snake = [(5, 5), (5, 6), (6, 6), (6, 5)]
    s.direction = s.next_direction = (1, 0)  # head (5,5) -> (6,5), the tail
    s.food = (0, 0)
    s.update()
    assert not s.game_over
    assert s.snake[0] == (6, 5) and len(s.snake) == 4


def test_snake_still_dies_on_its_tail_when_eating():
    """When the move eats food the tail does not move, so entering its cell is a collision."""
    s = _snake()
    s.snake = [(5, 5), (5, 6), (6, 6), (6, 5)]
    s.direction = s.next_direction = (1, 0)
    s.food = (6, 5)
    s.update()
    assert s.game_over
