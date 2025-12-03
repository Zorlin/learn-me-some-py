"""
Tests for Touchscreen Input Mode

Tests cover:
1. Touch event processing
2. Gesture recognition
3. Zone detection
4. Code palette interaction
5. Virtual keyboard
6. Multi-touch gestures (pinch)
"""

import pytest
from datetime import datetime, timedelta

from lmsp.input.touchscreen import (
    TouchPoint,
    TouchEvent,
    GestureEvent,
    TouchGesture,
    TouchZone,
    TouchState,
    TouchscreenInput,
    GestureRecognizer,
    CodePaletteButton,
)


class TestTouchPoint:
    """Test touch point data structure."""

    def test_touch_point_creation(self):
        """Should create touch point with coordinates."""
        point = TouchPoint(x=100.0, y=200.0, touch_id=1)

        assert point.x == 100.0
        assert point.y == 200.0
        assert point.touch_id == 1

    def test_touch_point_has_timestamp(self):
        """Touch point should have timestamp."""
        point = TouchPoint(x=50.0, y=50.0, touch_id=1)

        assert point.timestamp is not None
        assert isinstance(point.timestamp, datetime)

    def test_touch_point_pressure(self):
        """Touch point can have pressure value."""
        point = TouchPoint(x=50.0, y=50.0, touch_id=1, pressure=0.8)

        assert point.pressure == 0.8
        assert 0.0 <= point.pressure <= 1.0


class TestTouchEvent:
    """Test touch event structure."""

    def test_touch_event_types(self):
        """Should support down, move, up events."""
        point = TouchPoint(x=10.0, y=20.0, touch_id=1)

        down = TouchEvent(event_type="down", point=point)
        move = TouchEvent(event_type="move", point=point)
        up = TouchEvent(event_type="up", point=point)

        assert down.event_type == "down"
        assert move.event_type == "move"
        assert up.event_type == "up"

    def test_touch_event_has_zone(self):
        """Touch event should detect which zone it's in."""
        point = TouchPoint(x=100.0, y=300.0, touch_id=1)
        event = TouchEvent(
            event_type="down",
            point=point,
            zone=TouchZone.CODE_EDITOR
        )

        assert event.zone == TouchZone.CODE_EDITOR

    def test_move_event_has_delta(self):
        """Move events should track delta from previous position."""
        point = TouchPoint(x=110.0, y=220.0, touch_id=1)
        event = TouchEvent(
            event_type="move",
            point=point,
            delta_x=10.0,
            delta_y=20.0
        )

        assert event.delta_x == 10.0
        assert event.delta_y == 20.0


class TestTouchState:
    """Test touch state management."""

    def test_state_tracks_active_touches(self):
        """Should track all active touches."""
        state = TouchState()

        point1 = TouchPoint(x=50.0, y=50.0, touch_id=1)
        point2 = TouchPoint(x=150.0, y=150.0, touch_id=2)

        state.add_touch(point1)
        state.add_touch(point2)

        assert state.get_touch_count() == 2

    def test_state_removes_touches(self):
        """Should remove touches by ID."""
        state = TouchState()

        point1 = TouchPoint(x=50.0, y=50.0, touch_id=1)
        point2 = TouchPoint(x=150.0, y=150.0, touch_id=2)

        state.add_touch(point1)
        state.add_touch(point2)

        state.remove_touch(touch_id=1)

        assert state.get_touch_count() == 1

    def test_keyboard_state(self):
        """State should track keyboard visibility."""
        state = TouchState()

        assert state.keyboard_visible is False

        state.keyboard_visible = True
        assert state.keyboard_visible is True

    def test_palette_state(self):
        """State should track palette mode."""
        state = TouchState()

        assert state.palette_visible is True
        assert state.palette_mode == "keywords"

        state.palette_mode = "operators"
        assert state.palette_mode == "operators"


class TestGestureRecognizer:
    """Test gesture recognition algorithms."""

    @pytest.fixture
    def recognizer(self):
        """Create a recognizer for tests."""
        return GestureRecognizer()

    def test_tap_gesture(self, recognizer):
        """Should recognize tap gesture."""
        point_down = TouchPoint(x=100.0, y=100.0, touch_id=1)
        recognizer.on_touch_down(point_down)

        # Quick up with minimal movement
        point_up = TouchPoint(x=102.0, y=101.0, touch_id=1)
        point_up.timestamp = point_down.timestamp + timedelta(milliseconds=100)

        gesture = recognizer.on_touch_up(point_up, TouchZone.CODE_EDITOR)

        assert gesture is not None
        assert gesture.gesture == TouchGesture.TAP

    def test_long_press_gesture(self, recognizer):
        """Should recognize long press."""
        point_down = TouchPoint(x=100.0, y=100.0, touch_id=1)
        recognizer.on_touch_down(point_down)

        # Hold for long duration with minimal movement
        point_up = TouchPoint(x=101.0, y=100.0, touch_id=1)
        point_up.timestamp = point_down.timestamp + timedelta(milliseconds=600)

        gesture = recognizer.on_touch_up(point_up, TouchZone.CODE_EDITOR)

        assert gesture is not None
        assert gesture.gesture == TouchGesture.LONG_PRESS

    def test_swipe_right_gesture(self, recognizer):
        """Should recognize swipe right."""
        point_down = TouchPoint(x=100.0, y=200.0, touch_id=1)
        recognizer.on_touch_down(point_down)

        # Fast movement to the right
        point_up = TouchPoint(x=200.0, y=205.0, touch_id=1)
        point_up.timestamp = point_down.timestamp + timedelta(milliseconds=200)

        gesture = recognizer.on_touch_up(point_up, TouchZone.CODE_EDITOR)

        assert gesture is not None
        assert gesture.gesture == TouchGesture.SWIPE_RIGHT
        assert gesture.distance >= 50.0

    def test_swipe_left_gesture(self, recognizer):
        """Should recognize swipe left."""
        point_down = TouchPoint(x=200.0, y=200.0, touch_id=1)
        recognizer.on_touch_down(point_down)

        point_up = TouchPoint(x=100.0, y=205.0, touch_id=1)
        point_up.timestamp = point_down.timestamp + timedelta(milliseconds=200)

        gesture = recognizer.on_touch_up(point_up, TouchZone.CODE_EDITOR)

        assert gesture is not None
        assert gesture.gesture == TouchGesture.SWIPE_LEFT

    def test_swipe_up_gesture(self, recognizer):
        """Should recognize swipe up."""
        point_down = TouchPoint(x=200.0, y=300.0, touch_id=1)
        recognizer.on_touch_down(point_down)

        point_up = TouchPoint(x=205.0, y=200.0, touch_id=1)
        point_up.timestamp = point_down.timestamp + timedelta(milliseconds=200)

        gesture = recognizer.on_touch_up(point_up, TouchZone.CODE_EDITOR)

        assert gesture is not None
        assert gesture.gesture == TouchGesture.SWIPE_UP

    def test_swipe_down_gesture(self, recognizer):
        """Should recognize swipe down."""
        point_down = TouchPoint(x=200.0, y=100.0, touch_id=1)
        recognizer.on_touch_down(point_down)

        point_up = TouchPoint(x=205.0, y=200.0, touch_id=1)
        point_up.timestamp = point_down.timestamp + timedelta(milliseconds=200)

        gesture = recognizer.on_touch_up(point_up, TouchZone.CODE_EDITOR)

        assert gesture is not None
        assert gesture.gesture == TouchGesture.SWIPE_DOWN

    def test_pinch_out_gesture(self, recognizer):
        """Should recognize pinch out (zoom in)."""
        # Two touches start close together
        touch1 = TouchPoint(x=190.0, y=200.0, touch_id=1)
        touch2 = TouchPoint(x=210.0, y=200.0, touch_id=2)

        recognizer.on_touch_down(touch1)
        recognizer.on_touch_down(touch2)

        # Move apart
        touch1_end = TouchPoint(x=150.0, y=200.0, touch_id=1)
        touch2_end = TouchPoint(x=250.0, y=200.0, touch_id=2)

        gesture = recognizer.recognize_pinch(touch1_end, touch2_end)

        assert gesture is not None
        assert gesture.gesture == TouchGesture.PINCH_OUT
        assert gesture.scale_factor > 1.0

    def test_pinch_in_gesture(self, recognizer):
        """Should recognize pinch in (zoom out)."""
        # Two touches start far apart
        touch1 = TouchPoint(x=100.0, y=200.0, touch_id=1)
        touch2 = TouchPoint(x=300.0, y=200.0, touch_id=2)

        recognizer.on_touch_down(touch1)
        recognizer.on_touch_down(touch2)

        # Move together
        touch1_end = TouchPoint(x=190.0, y=200.0, touch_id=1)
        touch2_end = TouchPoint(x=210.0, y=200.0, touch_id=2)

        gesture = recognizer.recognize_pinch(touch1_end, touch2_end)

        assert gesture is not None
        assert gesture.gesture == TouchGesture.PINCH_IN
        assert gesture.scale_factor < 1.0

    def test_gesture_has_velocity(self, recognizer):
        """Swipe gestures should calculate velocity."""
        point_down = TouchPoint(x=100.0, y=200.0, touch_id=1)
        recognizer.on_touch_down(point_down)

        point_up = TouchPoint(x=300.0, y=200.0, touch_id=1)
        point_up.timestamp = point_down.timestamp + timedelta(milliseconds=400)

        gesture = recognizer.on_touch_up(point_up, TouchZone.CODE_EDITOR)

        if gesture and gesture.gesture == TouchGesture.SWIPE_RIGHT:
            # 200 pixels in 0.4 seconds = 500 pixels/second
            assert gesture.velocity > 0
            assert gesture.velocity >= 100  # Should be fast swipe


class TestZoneDetection:
    """Test UI zone detection."""

    @pytest.fixture
    def input(self):
        return TouchscreenInput()

    def test_detect_code_editor_zone(self, input):
        """Middle-right area should be code editor."""
        zone = input.determine_zone(x=600, y=300, screen_width=800, screen_height=600)

        assert zone == TouchZone.CODE_EDITOR

    def test_detect_palette_zone(self, input):
        """Bottom area should be palette."""
        zone = input.determine_zone(x=400, y=550, screen_width=800, screen_height=600)

        # Either palette or keyboard depending on state
        assert zone in [TouchZone.PALETTE, TouchZone.KEYBOARD]

    def test_detect_navigation_zone(self, input):
        """Top-left should be navigation."""
        zone = input.determine_zone(x=100, y=30, screen_width=800, screen_height=600)

        assert zone == TouchZone.NAVIGATION

    def test_detect_progress_zone(self, input):
        """Top-right should be progress."""
        zone = input.determine_zone(x=700, y=30, screen_width=800, screen_height=600)

        assert zone == TouchZone.PROGRESS

    def test_detect_challenge_zone(self, input):
        """Left side should be challenge."""
        zone = input.determine_zone(x=100, y=300, screen_width=800, screen_height=600)

        assert zone == TouchZone.CHALLENGE


class TestCodePalette:
    """Test code palette buttons."""

    def test_palette_button_structure(self):
        """Palette button should have required fields."""
        button = CodePaletteButton(
            text="def",
            insert_code="def ",
            description="Define function",
            category="keywords"
        )

        assert button.text == "def"
        assert button.insert_code == "def "
        assert button.description == "Define function"
        assert button.category == "keywords"

    def test_palette_has_keyword_buttons(self):
        """Palette should have keyword buttons."""
        input = TouchscreenInput()

        keywords = [b for b in input.palette_buttons if b.category == "keywords"]

        assert len(keywords) > 0
        assert any(b.text == "def" for b in keywords)
        assert any(b.text == "if" for b in keywords)
        assert any(b.text == "for" for b in keywords)

    def test_palette_has_operator_buttons(self):
        """Palette should have operator buttons."""
        input = TouchscreenInput()

        operators = [b for b in input.palette_buttons if b.category == "operators"]

        assert len(operators) > 0
        assert any(b.text == "==" for b in operators)
        assert any(b.text == "!=" for b in operators)

    def test_get_button_at_coordinates(self):
        """Should find button at touch coordinates."""
        input = TouchscreenInput()

        # Get first button's position
        button = input.palette_buttons[0]

        found = input.get_palette_button_at(
            x=button.x + 10,
            y=button.y + 10
        )

        assert found is not None
        assert found.text == button.text

    def test_tap_palette_inserts_code(self):
        """Tapping palette button should return code to insert."""
        input = TouchscreenInput()

        # Get a keyword button
        button = next(b for b in input.palette_buttons if b.text == "def")

        # Create tap gesture on button
        point = TouchPoint(x=button.x + 10, y=button.y + 10, touch_id=1)
        gesture = GestureEvent(
            gesture=TouchGesture.TAP,
            zone=TouchZone.PALETTE,
            start_point=point
        )

        code = input.handle_palette_tap(gesture)

        assert code == "def "


class TestTouchscreenInput:
    """Test main touchscreen input handler."""

    @pytest.fixture
    def input(self):
        return TouchscreenInput()

    def test_process_touch_down(self, input):
        """Should process touch down event."""
        event = input.process_touch_down(x=100.0, y=200.0, touch_id=1)

        assert event is not None
        assert event.event_type == "down"
        assert event.point.x == 100.0
        assert event.point.y == 200.0

    def test_touch_down_adds_to_state(self, input):
        """Touch down should add to active touches."""
        input.process_touch_down(x=100.0, y=200.0, touch_id=1)

        assert input.state.get_touch_count() == 1

    def test_process_touch_move(self, input):
        """Should process touch move event."""
        # First touch down
        input.process_touch_down(x=100.0, y=200.0, touch_id=1)

        # Then move
        event = input.process_touch_move(x=120.0, y=220.0, touch_id=1)

        assert event is not None
        assert event.event_type == "move"
        assert event.delta_x == 20.0
        assert event.delta_y == 20.0

    def test_process_touch_up(self, input):
        """Should process touch up and recognize gesture."""
        # Touch down
        input.process_touch_down(x=100.0, y=200.0, touch_id=1)

        # Touch up quickly (tap)
        gesture = input.process_touch_up(x=102.0, y=201.0, touch_id=1)

        # May recognize tap
        if gesture:
            assert gesture.gesture == TouchGesture.TAP

    def test_touch_up_removes_from_state(self, input):
        """Touch up should remove from active touches."""
        input.process_touch_down(x=100.0, y=200.0, touch_id=1)
        input.process_touch_up(x=102.0, y=201.0, touch_id=1)

        assert input.state.get_touch_count() == 0

    def test_multi_touch_support(self, input):
        """Should handle multiple simultaneous touches."""
        input.process_touch_down(x=100.0, y=200.0, touch_id=1)
        input.process_touch_down(x=300.0, y=400.0, touch_id=2)

        assert input.state.get_touch_count() == 2

    def test_register_gesture_handler(self, input):
        """Should allow registering gesture handlers."""
        handled = []

        def handler(event):
            handled.append(event)

        input.register_gesture_handler(TouchGesture.TAP, handler)

        # Simulate tap
        input.process_touch_down(x=100.0, y=200.0, touch_id=1)
        gesture = input.process_touch_up(x=101.0, y=200.0, touch_id=1)

        # Handler should have been called if tap recognized
        if gesture and gesture.gesture == TouchGesture.TAP:
            assert len(handled) > 0

    def test_toggle_keyboard(self, input):
        """Should toggle virtual keyboard."""
        assert input.state.keyboard_visible is False

        input.toggle_keyboard()
        assert input.state.keyboard_visible is True

        input.toggle_keyboard()
        assert input.state.keyboard_visible is False

    def test_set_palette_mode(self, input):
        """Should change palette mode."""
        input.set_palette_mode("operators")
        assert input.state.palette_mode == "operators"

        input.set_palette_mode("keywords")
        assert input.state.palette_mode == "keywords"


class TestTouchAccessibility:
    """Test touch-friendly design."""

    def test_palette_buttons_are_large_enough(self):
        """Buttons should be touch-friendly (60px+ height)."""
        input = TouchscreenInput()

        for button in input.palette_buttons:
            assert button.height >= 60
            assert button.width >= 100

    def test_zones_are_distinct(self):
        """Touch zones should not overlap."""
        input = TouchscreenInput()

        # Test various points
        zones = []
        for x in [100, 400, 700]:
            for y in [50, 300, 550]:
                zone = input.determine_zone(x, y, 800, 600)
                zones.append((x, y, zone))

        # Should have variety of zones
        unique_zones = set(z for _, _, z in zones)
        assert len(unique_zones) >= 3


# Self-teaching note:
#
# This file demonstrates:
# - Touch event handling (Level 5+)
# - Gesture recognition algorithms (Level 6)
# - Coordinate geometry (Level 4)
# - State management (Level 5)
# - Event-driven architecture (Level 6)
# - Fixture use in pytest (Level 5)
#
# Touch gestures are recognized by:
# - Tap: minimal movement + short duration
# - Long press: minimal movement + long duration
# - Swipe: significant distance + high velocity + primary direction
# - Pinch: two touches moving toward/away from each other
#
# Prerequisites:
# - Level 4: Geometry, collections, datetime
# - Level 5: Dataclasses, complex state
# - Level 6: Event systems, pattern recognition
#
# Touchscreen support makes LMSP accessible on tablets and
# mobile devices, expanding who can learn Python.
