"""
Touchscreen Input Mode

Provides touch-optimized input for tablets and mobile devices.

Features:
- Large, tap-friendly UI elements
- Gesture support (swipe, pinch, drag)
- Virtual keyboard for code input
- Quick-insert code palette
- Touch-friendly code navigation
- Haptic feedback (where available)

Self-teaching note:
This file demonstrates:
- Touch event handling (Level 5+: event systems)
- Gesture recognition algorithms (Level 6: pattern recognition)
- UI state management (Level 5: complex state)
- Coordinate math for gestures (Level 4: geometry)
"""

from dataclasses import dataclass, field
from typing import Optional, List, Tuple, Callable
from enum import Enum
from datetime import datetime, timedelta


class TouchGesture(Enum):
    """Recognized touch gestures."""
    TAP = "tap"
    DOUBLE_TAP = "double_tap"
    LONG_PRESS = "long_press"
    SWIPE_LEFT = "swipe_left"
    SWIPE_RIGHT = "swipe_right"
    SWIPE_UP = "swipe_up"
    SWIPE_DOWN = "swipe_down"
    PINCH_IN = "pinch_in"  # Zoom out
    PINCH_OUT = "pinch_out"  # Zoom in
    DRAG = "drag"


class TouchZone(Enum):
    """Touch zones for different UI areas."""
    CODE_EDITOR = "code_editor"
    PALETTE = "palette"  # Quick-insert buttons
    NAVIGATION = "navigation"  # Back/forward/menu
    KEYBOARD = "keyboard"  # Virtual keyboard
    PROGRESS = "progress"  # XP/achievements area
    CHALLENGE = "challenge"  # Challenge description


@dataclass
class TouchPoint:
    """A single touch point."""

    # Position
    x: float
    y: float

    # Touch tracking
    touch_id: int  # Unique ID for multi-touch
    timestamp: datetime = field(default_factory=datetime.now)

    # Pressure (0.0 to 1.0, if available)
    pressure: float = 1.0


@dataclass
class TouchEvent:
    """A touch event (down, move, up)."""

    event_type: str  # "down", "move", "up"
    point: TouchPoint

    # Zone detection
    zone: Optional[TouchZone] = None

    # Delta for move events
    delta_x: float = 0.0
    delta_y: float = 0.0


@dataclass
class GestureEvent:
    """A recognized gesture."""

    gesture: TouchGesture
    zone: TouchZone

    # Gesture details
    start_point: TouchPoint
    end_point: Optional[TouchPoint] = None

    # Swipe details
    velocity: float = 0.0  # pixels per second
    distance: float = 0.0  # pixels

    # Pinch details
    scale_factor: float = 1.0  # For pinch gestures


@dataclass
class TouchState:
    """Current state of all touches."""

    active_touches: List[TouchPoint] = field(default_factory=list)
    recent_gestures: List[GestureEvent] = field(default_factory=list)

    # Virtual keyboard state
    keyboard_visible: bool = False
    keyboard_layout: str = "code"  # "code", "symbols", "numbers"

    # Quick palette state
    palette_visible: bool = True
    palette_mode: str = "keywords"  # "keywords", "operators", "snippets"

    def add_touch(self, point: TouchPoint):
        """Add a new touch point."""
        self.active_touches.append(point)

    def remove_touch(self, touch_id: int):
        """Remove a touch point by ID."""
        self.active_touches = [t for t in self.active_touches if t.touch_id != touch_id]

    def get_touch_count(self) -> int:
        """Get number of active touches."""
        return len(self.active_touches)


@dataclass
class CodePaletteButton:
    """A button in the quick-insert code palette."""

    text: str  # What to display
    insert_code: str  # What to insert
    description: str  # Tooltip/help text
    category: str  # "keywords", "operators", "snippets"

    # Visual properties
    x: int = 0
    y: int = 0
    width: int = 100
    height: int = 60


class GestureRecognizer:
    """
    Recognizes touch gestures from touch events.

    Algorithms:
    - Tap: Touch down + up with minimal movement
    - Swipe: Fast movement in one direction
    - Long press: Touch held for duration threshold
    - Pinch: Two touches moving toward/apart from each other
    """

    # Thresholds
    TAP_MAX_DURATION_MS = 300
    TAP_MAX_MOVEMENT = 20  # pixels
    LONG_PRESS_DURATION_MS = 500
    SWIPE_MIN_VELOCITY = 100  # pixels per second
    SWIPE_MIN_DISTANCE = 50  # pixels
    PINCH_MIN_SCALE_CHANGE = 0.1

    def __init__(self):
        self.touch_start_times: dict[int, datetime] = {}
        self.touch_start_positions: dict[int, Tuple[float, float]] = {}
        self.touch_current_positions: dict[int, Tuple[float, float]] = {}

    def on_touch_down(self, point: TouchPoint) -> Optional[GestureEvent]:
        """
        Handle touch down event.

        Args:
            point: Touch point that went down

        Returns:
            Gesture event if recognized, None otherwise
        """
        self.touch_start_times[point.touch_id] = point.timestamp
        self.touch_start_positions[point.touch_id] = (point.x, point.y)
        self.touch_current_positions[point.touch_id] = (point.x, point.y)
        return None

    def on_touch_move(self, point: TouchPoint) -> Optional[GestureEvent]:
        """
        Handle touch move event.

        Args:
            point: Touch point that moved

        Returns:
            Gesture event if recognized (e.g., drag)
        """
        if point.touch_id in self.touch_current_positions:
            self.touch_current_positions[point.touch_id] = (point.x, point.y)

        # TODO: Detect continuous gestures like drag
        return None

    def on_touch_up(self, point: TouchPoint, zone: TouchZone) -> Optional[GestureEvent]:
        """
        Handle touch up event and recognize gesture.

        Args:
            point: Touch point that went up
            zone: Which UI zone the touch was in

        Returns:
            Recognized gesture event
        """
        if point.touch_id not in self.touch_start_times:
            return None

        start_time = self.touch_start_times[point.touch_id]
        start_pos = self.touch_start_positions[point.touch_id]

        duration_ms = (point.timestamp - start_time).total_seconds() * 1000
        dx = point.x - start_pos[0]
        dy = point.y - start_pos[1]
        distance = (dx**2 + dy**2)**0.5

        # Determine gesture
        gesture = None

        if distance < self.TAP_MAX_MOVEMENT and duration_ms < self.TAP_MAX_DURATION_MS:
            # Tap
            gesture = TouchGesture.TAP

        elif distance < self.TAP_MAX_MOVEMENT and duration_ms >= self.LONG_PRESS_DURATION_MS:
            # Long press
            gesture = TouchGesture.LONG_PRESS

        elif distance >= self.SWIPE_MIN_DISTANCE:
            # Swipe - determine direction
            velocity = distance / (duration_ms / 1000.0) if duration_ms > 0 else 0

            if velocity >= self.SWIPE_MIN_VELOCITY:
                # Determine primary direction
                if abs(dx) > abs(dy):
                    gesture = TouchGesture.SWIPE_RIGHT if dx > 0 else TouchGesture.SWIPE_LEFT
                else:
                    gesture = TouchGesture.SWIPE_DOWN if dy > 0 else TouchGesture.SWIPE_UP

        # Clean up tracking
        del self.touch_start_times[point.touch_id]
        del self.touch_start_positions[point.touch_id]
        if point.touch_id in self.touch_current_positions:
            del self.touch_current_positions[point.touch_id]

        if gesture:
            start_point = TouchPoint(
                x=start_pos[0],
                y=start_pos[1],
                touch_id=point.touch_id,
                timestamp=start_time
            )

            return GestureEvent(
                gesture=gesture,
                zone=zone,
                start_point=start_point,
                end_point=point,
                velocity=distance / (duration_ms / 1000.0) if duration_ms > 0 else 0,
                distance=distance
            )

        return None

    def recognize_pinch(self, touch1: TouchPoint, touch2: TouchPoint) -> Optional[GestureEvent]:
        """
        Recognize pinch gesture from two touch points.

        Args:
            touch1: First touch point
            touch2: Second touch point

        Returns:
            Pinch gesture event if recognized
        """
        # Need start positions for both touches
        if touch1.touch_id not in self.touch_start_positions:
            return None
        if touch2.touch_id not in self.touch_start_positions:
            return None

        # Calculate initial distance
        start1 = self.touch_start_positions[touch1.touch_id]
        start2 = self.touch_start_positions[touch2.touch_id]
        start_distance = ((start1[0] - start2[0])**2 + (start1[1] - start2[1])**2)**0.5

        # Calculate current distance
        current_distance = ((touch1.x - touch2.x)**2 + (touch1.y - touch2.y)**2)**0.5

        if start_distance == 0:
            return None

        scale_factor = current_distance / start_distance

        # Check if scale change is significant
        if abs(scale_factor - 1.0) < self.PINCH_MIN_SCALE_CHANGE:
            return None

        gesture = TouchGesture.PINCH_OUT if scale_factor > 1.0 else TouchGesture.PINCH_IN

        return GestureEvent(
            gesture=gesture,
            zone=TouchZone.CODE_EDITOR,  # Assume pinch is for editor zoom
            start_point=touch1,
            end_point=touch2,
            scale_factor=scale_factor
        )


class TouchscreenInput:
    """
    Main touchscreen input handler.

    Manages:
    - Touch event processing
    - Gesture recognition
    - Virtual keyboard
    - Quick-insert code palette
    - Touch-to-code translation

    Usage:
        touch_input = TouchscreenInput()

        # Process touch events
        event = touch_input.process_touch_down(x, y, touch_id)

        # Handle gesture
        if event and event.gesture == TouchGesture.TAP:
            if event.zone == TouchZone.PALETTE:
                touch_input.handle_palette_tap(event)
    """

    def __init__(self):
        self.state = TouchState()
        self.recognizer = GestureRecognizer()
        self.palette_buttons: List[CodePaletteButton] = []
        self.gesture_handlers: dict[TouchGesture, Callable] = {}

        self._init_palette()

    def _init_palette(self):
        """Initialize the code palette with common buttons."""
        # Keywords
        keywords = [
            ("def", "def ", "Define function"),
            ("if", "if :", "If statement"),
            ("for", "for  in :", "For loop"),
            ("while", "while :", "While loop"),
            ("return", "return ", "Return value"),
            ("class", "class :", "Define class"),
            ("import", "import ", "Import module"),
            ("from", "from  import ", "Import from"),
        ]

        for i, (text, code, desc) in enumerate(keywords):
            self.palette_buttons.append(CodePaletteButton(
                text=text,
                insert_code=code,
                description=desc,
                category="keywords",
                x=(i % 4) * 100,
                y=(i // 4) * 60
            ))

        # Operators
        operators = [
            ("==", " == ", "Equal to"),
            ("!=", " != ", "Not equal"),
            ("and", " and ", "Logical AND"),
            ("or", " or ", "Logical OR"),
            ("not", "not ", "Logical NOT"),
            ("+=", " += ", "Add assign"),
            ("-=", " -= ", "Subtract assign"),
            ("*=", " *= ", "Multiply assign"),
        ]

        for i, (text, code, desc) in enumerate(operators):
            self.palette_buttons.append(CodePaletteButton(
                text=text,
                insert_code=code,
                description=desc,
                category="operators",
                x=(i % 4) * 100,
                y=(i // 4) * 60 + 200
            ))

    def determine_zone(self, x: float, y: float, screen_width: int, screen_height: int) -> TouchZone:
        """
        Determine which UI zone a touch is in.

        Args:
            x: Touch X coordinate
            y: Touch Y coordinate
            screen_width: Screen width
            screen_height: Screen height

        Returns:
            TouchZone for the touch
        """
        # Simple zone detection (would be more sophisticated in real app)

        # Bottom third: palette and keyboard
        if y > screen_height * 0.67:
            if self.state.keyboard_visible:
                return TouchZone.KEYBOARD
            else:
                return TouchZone.PALETTE

        # Top bar: navigation and progress
        if y < screen_height * 0.1:
            if x < screen_width * 0.3:
                return TouchZone.NAVIGATION
            else:
                return TouchZone.PROGRESS

        # Middle left: challenge description
        if x < screen_width * 0.3:
            return TouchZone.CHALLENGE

        # Middle right: code editor
        return TouchZone.CODE_EDITOR

    def process_touch_down(self, x: float, y: float, touch_id: int, screen_width: int = 800, screen_height: int = 600) -> Optional[TouchEvent]:
        """
        Process a touch down event.

        Args:
            x: Touch X coordinate
            y: Touch Y coordinate
            touch_id: Unique touch identifier
            screen_width: Screen width for zone detection
            screen_height: Screen height for zone detection

        Returns:
            TouchEvent
        """
        point = TouchPoint(x=x, y=y, touch_id=touch_id)
        zone = self.determine_zone(x, y, screen_width, screen_height)

        self.state.add_touch(point)
        self.recognizer.on_touch_down(point)

        return TouchEvent(
            event_type="down",
            point=point,
            zone=zone
        )

    def process_touch_move(self, x: float, y: float, touch_id: int, screen_width: int = 800, screen_height: int = 600) -> Optional[TouchEvent]:
        """
        Process a touch move event.

        Args:
            x: Touch X coordinate
            y: Touch Y coordinate
            touch_id: Unique touch identifier
            screen_width: Screen width for zone detection
            screen_height: Screen height for zone detection

        Returns:
            TouchEvent
        """
        point = TouchPoint(x=x, y=y, touch_id=touch_id)
        zone = self.determine_zone(x, y, screen_width, screen_height)

        # Calculate delta from previous position
        for touch in self.state.active_touches:
            if touch.touch_id == touch_id:
                delta_x = x - touch.x
                delta_y = y - touch.y
                break
        else:
            delta_x = 0.0
            delta_y = 0.0

        # Update touch in state
        for i, touch in enumerate(self.state.active_touches):
            if touch.touch_id == touch_id:
                self.state.active_touches[i] = point
                break

        self.recognizer.on_touch_move(point)

        return TouchEvent(
            event_type="move",
            point=point,
            zone=zone,
            delta_x=delta_x,
            delta_y=delta_y
        )

    def process_touch_up(self, x: float, y: float, touch_id: int, screen_width: int = 800, screen_height: int = 600) -> Optional[GestureEvent]:
        """
        Process a touch up event and recognize gesture.

        Args:
            x: Touch X coordinate
            y: Touch Y coordinate
            touch_id: Unique touch identifier
            screen_width: Screen width for zone detection
            screen_height: Screen height for zone detection

        Returns:
            GestureEvent if gesture recognized
        """
        point = TouchPoint(x=x, y=y, touch_id=touch_id)
        zone = self.determine_zone(x, y, screen_width, screen_height)

        self.state.remove_touch(touch_id)

        # Recognize gesture
        gesture_event = self.recognizer.on_touch_up(point, zone)

        if gesture_event:
            self.state.recent_gestures.append(gesture_event)

            # Call registered handlers
            if gesture_event.gesture in self.gesture_handlers:
                self.gesture_handlers[gesture_event.gesture](gesture_event)

        return gesture_event

    def register_gesture_handler(self, gesture: TouchGesture, handler: Callable):
        """
        Register a handler for a gesture.

        Args:
            gesture: Gesture type to handle
            handler: Callable that takes GestureEvent
        """
        self.gesture_handlers[gesture] = handler

    def get_palette_button_at(self, x: float, y: float) -> Optional[CodePaletteButton]:
        """
        Get palette button at coordinates.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            CodePaletteButton if found
        """
        for button in self.palette_buttons:
            if (button.x <= x < button.x + button.width and
                button.y <= y < button.y + button.height):
                return button
        return None

    def handle_palette_tap(self, event: GestureEvent) -> Optional[str]:
        """
        Handle tap on code palette.

        Args:
            event: Gesture event

        Returns:
            Code to insert, if button was tapped
        """
        if event.gesture != TouchGesture.TAP:
            return None

        button = self.get_palette_button_at(event.start_point.x, event.start_point.y)
        if button:
            return button.insert_code

        return None

    def toggle_keyboard(self):
        """Toggle virtual keyboard visibility."""
        self.state.keyboard_visible = not self.state.keyboard_visible

    def set_palette_mode(self, mode: str):
        """
        Set palette mode.

        Args:
            mode: "keywords", "operators", or "snippets"
        """
        self.state.palette_mode = mode


# Self-teaching note:
#
# This file demonstrates:
# - Touch event handling and gesture recognition (Level 6)
# - Coordinate geometry for gesture detection (Level 4+)
# - State management for complex UI (Level 5)
# - Callback/handler pattern (Level 5)
# - Dataclasses for event structures (Level 5)
# - Enum for type-safe constants (Level 4)
#
# Touch gesture algorithms:
# 1. Tap = minimal movement + short duration
# 2. Long press = minimal movement + long duration
# 3. Swipe = significant distance + velocity in one direction
# 4. Pinch = two touches moving toward/apart
# 5. Drag = continuous movement tracking
#
# Key concepts:
# - Touch IDs for multi-touch tracking
# - Velocity calculation for swipe detection
# - Zone-based UI organization
# - Virtual keyboard and palette for code input
# - Touch-friendly button sizing (60px+ height)
#
# Prerequisites:
# - Level 4: Collections, geometry, datetime
# - Level 5: Dataclasses, enums, callbacks
# - Level 6: Event systems, state management
#
# This enables LMSP to work on tablets and touch devices,
# making Python learning accessible on mobile platforms.
