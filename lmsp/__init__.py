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

# Import only modules that exist
from lmsp.adaptive.engine import AdaptiveEngine, LearnerProfile
from lmsp.input.emotional import EmotionalState, EmotionalDimension

__all__ = ["AdaptiveEngine", "LearnerProfile", "EmotionalState", "EmotionalDimension"]
