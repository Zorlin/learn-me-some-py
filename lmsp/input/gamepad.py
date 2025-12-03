"""
Gamepad Input System - Easy Mode
=================================

Makes coding feel like a game with controller-native input.

Easy Mode button mapping:
- A button: Insert "def"
- B button: Insert "return"
- X button: Insert "if"
- Y button: Insert "for"
- RT (analog): Increase indentation
- LT (analog): Decrease indentation
- RB: Smart autocomplete
- LB: Undo

This module provides pygame-based gamepad detection, event handling,
and haptic feedback support.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import pygame


class GamepadButton(Enum):
    """Standard gamepad buttons (Xbox layout)."""
    A = 0  # Cross on PlayStation
    B = 1  # Circle on PlayStation
    X = 2  # Square on PlayStation
    Y = 3  # Triangle on PlayStation
    LB = 4  # Left bumper
    RB = 5  # Right bumper
    BACK = 6
    START = 7
    L_STICK = 8  # Left stick click
    R_STICK = 9  # Right stick click


class DPadDirection(Enum):
    """D-pad directions."""
    UP = (0, 1)
    DOWN = (0, -1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    UP_LEFT = (-1, 1)
    UP_RIGHT = (1, 1)
    DOWN_LEFT = (-1, -1)
    DOWN_RIGHT = (1, -1)
    CENTER = (0, 0)


class HapticPattern(Enum):
    """Predefined haptic feedback patterns."""
    LIGHT_TAP = ("light", 100)  # duration_ms
    MEDIUM_PULSE = ("medium", 200)
    HEAVY_THUMP = ("heavy", 300)
    SUCCESS = ("success", 150)  # Short satisfying pulse
    ERROR = ("error", 250)  # Longer warning pulse
    COMPLETION = ("completion", 500)  # Level complete celebration


@dataclass
class GamepadState:
    """Current state of all gamepad inputs."""

    # Buttons (pressed = True)
    buttons: dict[GamepadButton, bool] = field(default_factory=dict)

    # Analog triggers (0.0 to 1.0)
    left_trigger: float = 0.0
    right_trigger: float = 0.0

    # Analog sticks (-1.0 to 1.0 for each axis)
    left_stick_x: float = 0.0
    left_stick_y: float = 0.0
    right_stick_x: float = 0.0
    right_stick_y: float = 0.0

    # D-pad
    dpad: tuple[int, int] = (0, 0)

    def __post_init__(self):
        """Initialize button states."""
        if not self.buttons:
            self.buttons = {button: False for button in GamepadButton}

    def is_pressed(self, button: GamepadButton) -> bool:
        """Check if a button is currently pressed."""
        return self.buttons.get(button, False)

    def get_indentation_delta(self, threshold: float = 0.3) -> int:
        """
        Get indentation change from triggers.

        Returns:
            +1 for RT pressed (indent)
            -1 for LT pressed (dedent)
            0 for neither or both
        """
        rt_active = self.right_trigger > threshold
        lt_active = self.left_trigger > threshold

        if rt_active and not lt_active:
            return 1
        elif lt_active and not rt_active:
            return -1
        else:
            return 0


class Gamepad:
    """
    Pygame-based gamepad interface with Easy Mode mappings.

    Features:
    - Automatic detection and hot-swap support
    - Easy Mode button-to-code mappings
    - Analog trigger indentation control
    - Haptic feedback for actions

    Usage:
        gamepad = Gamepad()
        if gamepad.initialize():
            while True:
                action = gamepad.poll()
                if action:
                    handle_action(action)
    """

    def __init__(self):
        self.joystick: Optional[pygame.joystick.Joystick] = None
        self.state = GamepadState()
        self._deadzone = 0.15  # Ignore small stick movements
        self._trigger_threshold = 0.3  # Trigger activation threshold

    def initialize(self) -> bool:
        """
        Initialize pygame and detect gamepad.

        Returns:
            True if gamepad found and initialized
        """
        if not pygame.get_init():
            pygame.init()

        pygame.joystick.init()

        if pygame.joystick.get_count() == 0:
            return False

        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()

        return True

    def poll(self) -> Optional[str]:
        """
        Poll for gamepad input and return action.

        Returns:
            Action string or None if no action this frame
        """
        if not self.joystick:
            return None

        # Process pygame events
        pygame.event.pump()

        # Update button states
        for button in GamepadButton:
            try:
                self.state.buttons[button] = self.joystick.get_button(button.value)
            except pygame.error:
                self.state.buttons[button] = False

        # Update triggers (axes 2 and 5 on most controllers)
        try:
            # Triggers usually range from -1.0 to 1.0, normalize to 0.0 to 1.0
            raw_lt = self.joystick.get_axis(2)
            raw_rt = self.joystick.get_axis(5)
            self.state.left_trigger = (raw_lt + 1.0) / 2.0
            self.state.right_trigger = (raw_rt + 1.0) / 2.0
        except pygame.error:
            self.state.left_trigger = 0.0
            self.state.right_trigger = 0.0

        # Update analog sticks
        try:
            self.state.left_stick_x = self._apply_deadzone(self.joystick.get_axis(0))
            self.state.left_stick_y = self._apply_deadzone(self.joystick.get_axis(1))
            self.state.right_stick_x = self._apply_deadzone(self.joystick.get_axis(3))
            self.state.right_stick_y = self._apply_deadzone(self.joystick.get_axis(4))
        except pygame.error:
            pass

        # Update D-pad
        try:
            hat = self.joystick.get_hat(0)
            self.state.dpad = hat if hat else (0, 0)
        except pygame.error:
            self.state.dpad = (0, 0)

        return None  # Actions handled by get_easy_mode_action

    def get_easy_mode_action(self) -> Optional[str]:
        """
        Get Easy Mode action from current gamepad state.

        Returns:
            Python keyword string or None
        """
        # Check face buttons (just pressed this frame)
        if self._just_pressed(GamepadButton.A):
            return "def "
        elif self._just_pressed(GamepadButton.B):
            return "return "
        elif self._just_pressed(GamepadButton.X):
            return "if "
        elif self._just_pressed(GamepadButton.Y):
            return "for "

        return None

    def get_indentation_change(self) -> int:
        """
        Get indentation change from analog triggers.

        Returns:
            +1, -1, or 0 for indent/dedent/no change
        """
        return self.state.get_indentation_delta(self._trigger_threshold)

    def _apply_deadzone(self, value: float) -> float:
        """Apply deadzone to stick input."""
        if abs(value) < self._deadzone:
            return 0.0
        return value

    def _just_pressed(self, button: GamepadButton) -> bool:
        """
        Check if button was just pressed this frame.

        Note: Requires frame-by-frame state tracking in full implementation.
        For now, returns current state (to be improved with event history).
        """
        return self.state.is_pressed(button)

    def rumble(self, pattern: HapticPattern, intensity: float = 1.0):
        """
        Trigger haptic feedback.

        Args:
            pattern: Predefined haptic pattern
            intensity: 0.0 to 1.0 (if supported)
        """
        if not self.joystick:
            return

        # Try to rumble (not all controllers support this)
        try:
            # pygame 2.0+ has rumble support
            if hasattr(self.joystick, 'rumble'):
                duration_ms = pattern.value[1]
                self.joystick.rumble(intensity, intensity, duration_ms)
        except (pygame.error, AttributeError):
            # Rumble not supported on this controller
            pass

    def disconnect(self):
        """Clean up gamepad resources."""
        if self.joystick:
            self.joystick.quit()
            self.joystick = None

    @property
    def is_connected(self) -> bool:
        """Check if gamepad is still connected."""
        return self.joystick is not None and self.joystick.get_init()

    @property
    def name(self) -> str:
        """Get controller name."""
        if self.joystick:
            return self.joystick.get_name()
        return "No controller"


class GamepadManager:
    """
    Manages gamepad hot-swapping and multi-controller support.

    Features:
    - Automatic detection on startup
    - Hot-swap detection (connect/disconnect during play)
    - Support for multiple controllers
    """

    def __init__(self):
        self.gamepads: list[Gamepad] = []
        self.active_gamepad: Optional[Gamepad] = None

    def detect_gamepads(self) -> list[Gamepad]:
        """
        Detect all connected gamepads.

        Returns:
            List of Gamepad objects
        """
        if not pygame.get_init():
            pygame.init()

        pygame.joystick.init()

        self.gamepads = []
        for i in range(pygame.joystick.get_count()):
            gamepad = Gamepad()
            if gamepad.initialize():
                self.gamepads.append(gamepad)

        # Set first gamepad as active
        if self.gamepads and not self.active_gamepad:
            self.active_gamepad = self.gamepads[0]

        return self.gamepads

    def check_for_changes(self) -> bool:
        """
        Check if gamepad connection status changed.

        Returns:
            True if gamepads were added or removed
        """
        pygame.event.pump()

        # Check for device added/removed events
        for event in pygame.event.get([pygame.JOYDEVICEADDED, pygame.JOYDEVICEREMOVED]):
            if event.type == pygame.JOYDEVICEADDED:
                print(f"Gamepad connected: {event.device}")
                self.detect_gamepads()
                return True
            elif event.type == pygame.JOYDEVICEREMOVED:
                print(f"Gamepad disconnected: {event.instance_id}")
                self.detect_gamepads()
                return True

        return False

    def cleanup(self):
        """Disconnect all gamepads."""
        for gamepad in self.gamepads:
            gamepad.disconnect()
        self.gamepads = []
        self.active_gamepad = None


# Self-teaching note:
#
# This file demonstrates:
# - Enum for type-safe constants (GamepadButton, HapticPattern)
# - Dataclass for structured data (GamepadState)
# - External library integration (pygame)
# - Hardware abstraction (gamepad -> Python actions)
# - Resource management (initialize/cleanup pattern)
# - Hot-swapping detection (event-driven)
#
# The learner will encounter this after mastering:
# - Level 3: Classes and objects
# - Level 4: Enums and dataclasses
# - Level 5: External libraries and resource management
#
# This is professional Python for hardware integration!
