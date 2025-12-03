"""
Tests for Gamepad Input System (Easy Mode)
==========================================

Tests for pygame-based gamepad detection, button mappings,
trigger-based indentation, and haptic feedback.

TDD: These tests were written BEFORE the implementation.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

# Skip all tests in this module if pygame not available
pygame = pytest.importorskip("pygame", minversion=None)

from lmsp.input.gamepad import (
    Gamepad,
    GamepadManager,
    GamepadButton,
    GamepadState,
    HapticPattern,
    DPadDirection,
)


class TestGamepadButton:
    """Test button enumeration."""

    def test_button_values(self):
        """Button enums should match pygame indices."""
        assert GamepadButton.A.value == 0
        assert GamepadButton.B.value == 1
        assert GamepadButton.X.value == 2
        assert GamepadButton.Y.value == 3
        assert GamepadButton.LB.value == 4
        assert GamepadButton.RB.value == 5

    def test_all_buttons_defined(self):
        """All standard gamepad buttons should be defined."""
        buttons = list(GamepadButton)
        assert len(buttons) >= 10  # At least 10 standard buttons


class TestHapticPattern:
    """Test haptic feedback patterns."""

    def test_pattern_structure(self):
        """Each pattern should have type and duration."""
        pattern = HapticPattern.LIGHT_TAP
        assert isinstance(pattern.value, tuple)
        assert len(pattern.value) == 2

        type_str, duration_ms = pattern.value
        assert isinstance(type_str, str)
        assert isinstance(duration_ms, int)
        assert duration_ms > 0

    def test_all_patterns_defined(self):
        """Required haptic patterns should exist."""
        required = ["LIGHT_TAP", "MEDIUM_PULSE", "HEAVY_THUMP",
                    "SUCCESS", "ERROR", "COMPLETION"]
        for pattern_name in required:
            assert hasattr(HapticPattern, pattern_name)


class TestGamepadState:
    """Test gamepad state tracking."""

    def test_default_state(self):
        """New state should have all buttons unpressed."""
        state = GamepadState()

        for button in GamepadButton:
            assert state.is_pressed(button) is False

        assert state.left_trigger == 0.0
        assert state.right_trigger == 0.0
        assert state.left_stick_x == 0.0
        assert state.left_stick_y == 0.0
        assert state.right_stick_x == 0.0
        assert state.right_stick_y == 0.0
        assert state.dpad == (0, 0)

    def test_button_press(self):
        """State should track button presses."""
        state = GamepadState()
        state.buttons[GamepadButton.A] = True

        assert state.is_pressed(GamepadButton.A) is True
        assert state.is_pressed(GamepadButton.B) is False

    def test_trigger_values(self):
        """Triggers should be 0.0 to 1.0."""
        state = GamepadState()
        state.left_trigger = 0.5
        state.right_trigger = 1.0

        assert state.left_trigger == 0.5
        assert state.right_trigger == 1.0

    def test_stick_values(self):
        """Sticks should be -1.0 to 1.0."""
        state = GamepadState()
        state.left_stick_x = -0.7
        state.left_stick_y = 0.8
        state.right_stick_x = 1.0
        state.right_stick_y = -1.0

        assert state.left_stick_x == -0.7
        assert state.left_stick_y == 0.8
        assert state.right_stick_x == 1.0
        assert state.right_stick_y == -1.0

    def test_indentation_delta_right_trigger(self):
        """Right trigger should increase indentation."""
        state = GamepadState()
        state.right_trigger = 0.8

        assert state.get_indentation_delta() == 1

    def test_indentation_delta_left_trigger(self):
        """Left trigger should decrease indentation."""
        state = GamepadState()
        state.left_trigger = 0.8

        assert state.get_indentation_delta() == -1

    def test_indentation_delta_both_triggers(self):
        """Both triggers should cancel out."""
        state = GamepadState()
        state.left_trigger = 0.8
        state.right_trigger = 0.8

        assert state.get_indentation_delta() == 0

    def test_indentation_delta_threshold(self):
        """Triggers below threshold should not change indentation."""
        state = GamepadState()
        state.right_trigger = 0.2  # Below default threshold of 0.3

        assert state.get_indentation_delta() == 0


class TestGamepad:
    """Test the Gamepad class."""

    @pytest.fixture
    def mock_joystick(self):
        """Create a mock pygame joystick."""
        joystick = MagicMock()
        joystick.get_init.return_value = True
        joystick.get_button.return_value = False
        joystick.get_axis.return_value = 0.0
        joystick.get_hat.return_value = (0, 0)
        joystick.get_name.return_value = "Mock Controller"
        joystick.rumble = MagicMock()
        joystick.quit = MagicMock()
        return joystick

    @patch('pygame.joystick.get_count', return_value=1)
    @patch('pygame.joystick.Joystick')
    @patch('pygame.init')
    @patch('pygame.joystick.init')
    @patch('pygame.get_init', return_value=False)
    def test_initialization_no_controllers(self, mock_get_init, mock_joy_init,
                                            mock_pygame_init, mock_joystick_cls,
                                            mock_count):
        """Initialization should fail gracefully without controller."""
        mock_count.return_value = 0
        gamepad = Gamepad()
        result = gamepad.initialize()

        assert result is False
        assert gamepad.joystick is None

    @patch('pygame.joystick.get_count', return_value=1)
    @patch('pygame.joystick.Joystick')
    @patch('pygame.init')
    @patch('pygame.joystick.init')
    @patch('pygame.get_init', return_value=False)
    def test_initialization_with_controller(self, mock_get_init, mock_joy_init,
                                             mock_pygame_init, mock_joystick_cls,
                                             mock_count, mock_joystick):
        """Initialization should succeed with controller."""
        mock_joystick_cls.return_value = mock_joystick
        gamepad = Gamepad()
        result = gamepad.initialize()

        assert result is True
        assert gamepad.joystick is not None

    def test_easy_mode_action_a_button(self, mock_joystick):
        """A button should return 'def '."""
        gamepad = Gamepad()
        gamepad.joystick = mock_joystick
        gamepad.state.buttons[GamepadButton.A] = True

        action = gamepad.get_easy_mode_action()
        assert action == "def "

    def test_easy_mode_action_b_button(self, mock_joystick):
        """B button should return 'return '."""
        gamepad = Gamepad()
        gamepad.joystick = mock_joystick
        gamepad.state.buttons[GamepadButton.B] = True

        action = gamepad.get_easy_mode_action()
        assert action == "return "

    def test_easy_mode_action_x_button(self, mock_joystick):
        """X button should return 'if '."""
        gamepad = Gamepad()
        gamepad.joystick = mock_joystick
        gamepad.state.buttons[GamepadButton.X] = True

        action = gamepad.get_easy_mode_action()
        assert action == "if "

    def test_easy_mode_action_y_button(self, mock_joystick):
        """Y button should return 'for '."""
        gamepad = Gamepad()
        gamepad.joystick = mock_joystick
        gamepad.state.buttons[GamepadButton.Y] = True

        action = gamepad.get_easy_mode_action()
        assert action == "for "

    def test_easy_mode_no_action(self, mock_joystick):
        """No buttons pressed should return None."""
        gamepad = Gamepad()
        gamepad.joystick = mock_joystick

        action = gamepad.get_easy_mode_action()
        assert action is None

    def test_indentation_change_right_trigger(self, mock_joystick):
        """Right trigger should return +1."""
        gamepad = Gamepad()
        gamepad.joystick = mock_joystick
        gamepad.state.right_trigger = 0.8

        delta = gamepad.get_indentation_change()
        assert delta == 1

    def test_indentation_change_left_trigger(self, mock_joystick):
        """Left trigger should return -1."""
        gamepad = Gamepad()
        gamepad.joystick = mock_joystick
        gamepad.state.left_trigger = 0.8

        delta = gamepad.get_indentation_change()
        assert delta == -1

    def test_deadzone_application(self):
        """Small stick movements should be ignored."""
        gamepad = Gamepad()
        gamepad._deadzone = 0.3

        # Below deadzone
        assert gamepad._apply_deadzone(0.2) == 0.0
        assert gamepad._apply_deadzone(-0.2) == 0.0

        # Above deadzone
        assert gamepad._apply_deadzone(0.5) == 0.5
        assert gamepad._apply_deadzone(-0.5) == -0.5

    def test_rumble_calls_joystick(self, mock_joystick):
        """Rumble should call joystick rumble if available."""
        mock_joystick.rumble = Mock()
        gamepad = Gamepad()
        gamepad.joystick = mock_joystick

        gamepad.rumble(HapticPattern.LIGHT_TAP)

        # Should have attempted to rumble
        mock_joystick.rumble.assert_called_once()

    def test_rumble_graceful_without_support(self, mock_joystick):
        """Rumble should not crash if controller doesn't support it."""
        gamepad = Gamepad()
        gamepad.joystick = mock_joystick

        # Should not raise
        gamepad.rumble(HapticPattern.LIGHT_TAP)

    def test_disconnect(self, mock_joystick):
        """Disconnect should clean up joystick."""
        gamepad = Gamepad()
        gamepad.joystick = mock_joystick

        gamepad.disconnect()

        assert gamepad.joystick is None
        mock_joystick.quit.assert_called_once()

    def test_is_connected(self, mock_joystick):
        """is_connected should reflect joystick state."""
        gamepad = Gamepad()

        assert gamepad.is_connected is False

        gamepad.joystick = mock_joystick
        assert gamepad.is_connected is True

    def test_controller_name(self, mock_joystick):
        """Should return controller name."""
        gamepad = Gamepad()
        gamepad.joystick = mock_joystick

        name = gamepad.name
        assert name == "Mock Controller"


class TestGamepadManager:
    """Test gamepad hot-swap management."""

    @patch('pygame.joystick.get_count', return_value=0)
    @patch('pygame.init')
    @patch('pygame.joystick.init')
    @patch('pygame.get_init', return_value=False)
    def test_detect_no_gamepads(self, mock_get_init, mock_joy_init,
                                 mock_pygame_init, mock_count):
        """Detect should return empty list with no controllers."""
        manager = GamepadManager()
        gamepads = manager.detect_gamepads()

        assert len(gamepads) == 0
        assert manager.active_gamepad is None

    @patch('pygame.joystick.get_count', return_value=2)
    @patch('pygame.joystick.Joystick')
    @patch('pygame.init')
    @patch('pygame.joystick.init')
    @patch('pygame.get_init', return_value=False)
    def test_detect_multiple_gamepads(self, mock_get_init, mock_joy_init,
                                       mock_pygame_init, mock_joystick_cls,
                                       mock_count):
        """Detect should find all connected controllers."""
        mock_joystick_cls.return_value = MagicMock()
        mock_joystick_cls.return_value.get_init.return_value = True

        manager = GamepadManager()
        gamepads = manager.detect_gamepads()

        assert len(gamepads) == 2
        assert manager.active_gamepad == gamepads[0]

    @patch('pygame.event.get')
    @patch('pygame.event.pump')
    def test_check_for_changes_no_events(self, mock_pump, mock_get):
        """No events should return False."""
        mock_get.return_value = []

        manager = GamepadManager()
        changed = manager.check_for_changes()

        assert changed is False

    @patch('pygame.event.get')
    @patch('pygame.event.pump')
    def test_check_for_changes_device_added(self, mock_pump, mock_get):
        """Device added event should trigger detection."""
        event = Mock()
        event.type = pygame.JOYDEVICEADDED
        event.device = 0
        mock_get.return_value = [event]

        manager = GamepadManager()
        with patch.object(manager, 'detect_gamepads') as mock_detect:
            changed = manager.check_for_changes()

            assert changed is True
            mock_detect.assert_called_once()

    @patch('pygame.event.get')
    @patch('pygame.event.pump')
    def test_check_for_changes_device_removed(self, mock_pump, mock_get):
        """Device removed event should trigger detection."""
        event = Mock()
        event.type = pygame.JOYDEVICEREMOVED
        event.instance_id = 0
        mock_get.return_value = [event]

        manager = GamepadManager()
        with patch.object(manager, 'detect_gamepads') as mock_detect:
            changed = manager.check_for_changes()

            assert changed is True
            mock_detect.assert_called_once()

    def test_cleanup(self):
        """Cleanup should disconnect all gamepads."""
        manager = GamepadManager()

        mock_gamepad1 = Mock(spec=Gamepad)
        mock_gamepad2 = Mock(spec=Gamepad)
        manager.gamepads = [mock_gamepad1, mock_gamepad2]
        manager.active_gamepad = mock_gamepad1

        manager.cleanup()

        mock_gamepad1.disconnect.assert_called_once()
        mock_gamepad2.disconnect.assert_called_once()
        assert len(manager.gamepads) == 0
        assert manager.active_gamepad is None


class TestDPadDirection:
    """Test D-pad direction enum."""

    def test_cardinal_directions(self):
        """Cardinal directions should have correct values."""
        assert DPadDirection.UP.value == (0, 1)
        assert DPadDirection.DOWN.value == (0, -1)
        assert DPadDirection.LEFT.value == (-1, 0)
        assert DPadDirection.RIGHT.value == (1, 0)

    def test_diagonal_directions(self):
        """Diagonal directions should combine axes."""
        assert DPadDirection.UP_LEFT.value == (-1, 1)
        assert DPadDirection.UP_RIGHT.value == (1, 1)
        assert DPadDirection.DOWN_LEFT.value == (-1, -1)
        assert DPadDirection.DOWN_RIGHT.value == (1, -1)

    def test_center(self):
        """Center should be (0, 0)."""
        assert DPadDirection.CENTER.value == (0, 0)


class TestGamepadIntegration:
    """Test gamepad integration with game loop."""

    def test_gamepad_produces_python_keywords(self):
        """Gamepad actions should produce valid Python."""
        keywords = ["def ", "return ", "if ", "for "]

        gamepad = Gamepad()
        gamepad.joystick = Mock()

        for button in [GamepadButton.A, GamepadButton.B,
                       GamepadButton.X, GamepadButton.Y]:
            gamepad.state.buttons[button] = True
            action = gamepad.get_easy_mode_action()
            gamepad.state.buttons[button] = False

            assert action in keywords

    def test_indentation_delta_values(self):
        """Indentation delta should be -1, 0, or 1."""
        gamepad = Gamepad()

        # Test all combinations
        for lt in [0.0, 0.5, 1.0]:
            for rt in [0.0, 0.5, 1.0]:
                gamepad.state.left_trigger = lt
                gamepad.state.right_trigger = rt

                delta = gamepad.get_indentation_change()
                assert delta in (-1, 0, 1)


# Self-teaching note:
#
# This file demonstrates:
# - unittest.mock for testing hardware integration (Level 6)
# - pytest fixtures for test setup (Level 5)
# - Testing external libraries (pygame) (Level 5+)
# - Mocking strategies for hardware (Level 6)
# - Testing enums and dataclasses (Level 5)
#
# The learner will encounter this AFTER mastering:
# - Level 3: Functions and classes
# - Level 4: Testing basics with pytest
# - Level 5: Dataclasses and external libraries
# - Level 6: Mocking and advanced testing
#
# This is professional Python for hardware testing - the same patterns
# used to test robots, game controllers, and IoT devices!
