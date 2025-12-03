"""
Input handling for LMSP

Supports:
- Gamepad (primary)
- Radial typing (thumbstick text input)
- Touchscreen (mobile/tablet)
- Keyboard (fallback)
"""

from lmsp.input.emotional import (
    EmotionalDimension,
    EmotionalSample,
    EmotionalState,
    EmotionalPrompt,
)

__all__ = [
    "EmotionalDimension",
    "EmotionalSample",
    "EmotionalState",
    "EmotionalPrompt",
]
