"""
Input handling for LMSP

Supports:
- Gamepad (primary, optional)
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

# Gamepad is optional - only import if pygame available
_gamepad_available = False
try:
    from lmsp.input.gamepad import (
        Gamepad,
        GamepadManager,
        GamepadButton,
        GamepadState,
        HapticPattern,
        DPadDirection,
    )
    _gamepad_available = True
except ImportError:
    # Pygame not installed - gamepad disabled
    Gamepad = None
    GamepadManager = None
    GamepadButton = None
    GamepadState = None
    HapticPattern = None
    DPadDirection = None

__all__ = [
    "EmotionalDimension",
    "EmotionalSample",
    "EmotionalState",
    "EmotionalPrompt",
    "Gamepad",
    "GamepadManager",
    "GamepadButton",
    "GamepadState",
    "HapticPattern",
    "DPadDirection",
    "_gamepad_available",
]
