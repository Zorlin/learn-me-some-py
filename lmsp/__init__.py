"""
Learn Me Some Py (LMSP)
=======================

The game that teaches you to build it.

A Python learning game with:
- Full controller support
- Adaptive AI that learns YOUR learning style
- Multiplayer (coop, competitive, teaching)
- Project-driven curriculum

Built in Python, teaching Python, BY building itself.
"""

__version__ = "0.1.0"
__author__ = "Wings"

from lmsp.game import Game
from lmsp.input import InputManager
from lmsp.adaptive import AdaptiveEngine

__all__ = ["Game", "InputManager", "AdaptiveEngine"]
