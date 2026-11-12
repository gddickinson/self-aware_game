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
    s.ai_counter = s.ai_speed - 1  # move on the next update
    s.update()
    assert not s.game_over
    assert s.snake[0] == (6, 5) and len(s.snake) == 4


def test_snake_still_dies_on_its_tail_when_eating():
    """When the move eats food the tail does not move, so entering its cell is a collision."""
    s = _snake()
    s.snake = [(5, 5), (5, 6), (6, 6), (6, 5)]
    s.direction = s.next_direction = (1, 0)
    s.food = (6, 5)
    s.ai_counter = s.ai_speed - 1
    s.update()
    assert s.game_over


def test_character_next_to_snake_game_is_near_it(game):
    """The 500x500 snake building can't be entered, so 'near' must be measured from its edge."""
    c = game.character
    c.position = [610.0, 300.0]  # building spans x 100..600
    assert c.is_near_building("Snake Game")
    c.position = [1000.0, 700.0]
    assert not c.is_near_building("Snake Game")


def test_character_notices_snake_game_when_next_to_it(game):
    c = game.character
    c.position = [610.0, 300.0]
    c.state = CharacterState.THINKING
    game.update()
    assert c.has_noticed_snake_game
    assert any("snake game" in m.message for m in game.dialogue.messages)


def test_investigating_the_snake_game_ends_in_a_thought_about_it(game):
    c = game.character
    c.position = [700.0, 300.0]
    random.seed(3)
    c.change_state(CharacterState.INVESTIGATING)
    for _ in range(400):
        c.update()
        if c.state != CharacterState.INVESTIGATING:
            break
    assert c.state == CharacterState.THINKING
    assert c.current_thought in c.snake_game_observations


def test_finished_thought_is_cleared_so_idle_thoughts_can_recur(game):
    """The idle state only starts a new thought when no thought is current."""
    c = game.character
    c.state, c.state_timer = CharacterState.INTERACTING, -10_000  # a state that starts no thoughts
    c.trigger_thought("first")
    for _ in range(c.thought_timer):
        c.update()
    assert c.thought_timer == 0
    assert c.current_thought == ""


def test_debug_console_shows_the_game_clock_fps(game, monkeypatch):
    """The FPS line used a brand-new Clock, which always reports 0.0."""
    class FakeClock:
        def get_fps(self):
            return 59.5
    shown = []
    real = game.debug_console.font

    class SpyFont:
        def render(self, text, *a):
            shown.append(text)
            return real.render(text, *a)

        def __getattr__(self, name):
            return getattr(real, name)
    monkeypatch.setattr(game.debug_console, "font", SpyFont())
    game.clock = FakeClock()
    game.debug_mode = True
    game.render()
    assert "FPS: 59.5" in shown


def test_manual_snake_moves_at_the_same_pace_as_the_ai():
    """Under arrow-key control the snake moved one cell every frame (60 cells/s): unplayable."""
    s = _snake(manual=True)
    head = s.snake[0]
    for _ in range(s.ai_speed - 1):
        s.update()
    assert s.snake[0] == head
    s.update()
    assert s.snake[0] == (head[0] + 1, head[1])


def _frames_in_state(game, state, seed):
    """Enter `state` and count updates until the character leaves it."""
    random.seed(seed)
    c = game.character
    c.position = [900.0, 500.0]
    c.change_state(state)
    for n in range(1, 2000):
        c.update()
        if c.state != state:
            return n
    return None


@pytest.mark.parametrize("state, lo, hi", [
    (CharacterState.IDLE, 180, 360),       # "3-6 seconds idle"
    (CharacterState.THINKING, 180, 300),   # "3-5 seconds thinking"
    (CharacterState.CONFUSED, 90, 150),    # "1.5-2.5 seconds confused"
])
def test_state_durations_match_the_comments(game, state, lo, hi):
    """The exit threshold was re-rolled every frame and compared with a timer that started part-way (or at 0 for a
    fixed 120), so idle lasted ~1 s, thinking ~0.3 s and confusion ~0.1 s instead of the commented durations."""
    frames = [_frames_in_state(game, state, seed) for seed in range(40)]
    assert all(lo <= f <= hi for f in frames), (min(frames), max(frames))
    assert max(frames) - min(frames) > (hi - lo) / 3  # still random within the range
