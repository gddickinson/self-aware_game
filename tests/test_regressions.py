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
