"""
Game Core Module
================

Core game functionality including:
- Game state management
- Session tracking
- Event recording
- Game loop execution
- Main game engine
"""

from lmsp.game.state import GameState, GameSession, GameEvent
from lmsp.game.engine import (
    GameEngine,
    GamePhase,
    GameConfig,
    InputHandler,
    KeyboardInputHandler,
)

__all__ = [
    # State management
    "GameState",
    "GameSession",
    "GameEvent",
    # Game engine
    "GameEngine",
    "GamePhase",
    "GameConfig",
    "InputHandler",
    "KeyboardInputHandler",
]
