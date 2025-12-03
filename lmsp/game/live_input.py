"""
Non-blocking keyboard input handler for event-driven Rich game loop.

Replaces blocking input() prompts with event-driven keyboard handling
for gorgeous, responsive terminal UX.
"""

import sys
import tty
import termios
import select
from enum import Enum, auto
from typing import Optional
from dataclasses import dataclass


class KeyType(Enum):
    """Types of keys detected."""
    REGULAR = auto()
    ARROW = auto()
    SPECIAL = auto()
    QUIT = auto()


@dataclass
class KeyEvent:
    """Represents a keyboard event."""
    key: str
    key_type: KeyType
    raw_bytes: bytes = b''


class LiveInputHandler:
    """
    Non-blocking keyboard input handler.

    Captures keyboard events without blocking the game loop,
    enabling real-time, responsive terminal UI.

    Usage:
        handler = LiveInputHandler()

        while running:
            key = handler.get_key_non_blocking()
            if key:
                handle_key(key)

            # Update display
            render_frame()
    """

    # ANSI escape sequences for special keys
    ARROW_UP = b'\x1b[A'
    ARROW_DOWN = b'\x1b[B'
    ARROW_RIGHT = b'\x1b[C'
    ARROW_LEFT = b'\x1b[D'

    ESCAPE = b'\x1b'
    CTRL_C = b'\x03'
    CTRL_D = b'\x04'

    def __init__(self):
        self._old_settings = None
        self._raw_mode_active = False

    def enable_raw_mode(self):
        """Enable raw terminal mode for character-by-character input."""
        if sys.stdin.isatty() and not self._raw_mode_active:
            self._old_settings = termios.tcgetattr(sys.stdin)
            tty.setraw(sys.stdin.fileno())
            self._raw_mode_active = True

    def disable_raw_mode(self):
        """Restore normal terminal mode."""
        if self._old_settings and self._raw_mode_active:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self._old_settings)
            self._raw_mode_active = False

    def __enter__(self):
        """Context manager entry - enable raw mode."""
        self.enable_raw_mode()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - disable raw mode."""
        self.disable_raw_mode()

    def get_key_non_blocking(self, timeout: float = 0.0) -> Optional[KeyEvent]:
        """
        Get a key press without blocking.

        Args:
            timeout: How long to wait for input (0.0 = immediate return)

        Returns:
            KeyEvent if key pressed, None if no input
        """
        if not sys.stdin.isatty():
            # Not a terminal - can't do non-blocking input
            return None

        # Check if data is available
        ready, _, _ = select.select([sys.stdin], [], [], timeout)

        if not ready:
            return None

        # Read available bytes
        ch = sys.stdin.read(1).encode()

        # Check for multi-byte sequences (arrows, etc.)
        if ch == b'\x1b':
            # Escape sequence - try to read more
            ready, _, _ = select.select([sys.stdin], [], [], 0.001)
            if ready:
                extra = sys.stdin.read(2).encode()
                ch += extra

        # Parse the key
        return self._parse_key(ch)

    def _parse_key(self, raw_bytes: bytes) -> KeyEvent:
        """Parse raw bytes into a KeyEvent."""
        # Check for quit keys
        if raw_bytes in (self.CTRL_C, self.CTRL_D, b'q', b'Q'):
            return KeyEvent(key='quit', key_type=KeyType.QUIT, raw_bytes=raw_bytes)

        if raw_bytes == self.ESCAPE:
            return KeyEvent(key='escape', key_type=KeyType.SPECIAL, raw_bytes=raw_bytes)

        # Check for arrow keys
        if raw_bytes == self.ARROW_UP:
            return KeyEvent(key='up', key_type=KeyType.ARROW, raw_bytes=raw_bytes)
        elif raw_bytes == self.ARROW_DOWN:
            return KeyEvent(key='down', key_type=KeyType.ARROW, raw_bytes=raw_bytes)
        elif raw_bytes == self.ARROW_LEFT:
            return KeyEvent(key='left', key_type=KeyType.ARROW, raw_bytes=raw_bytes)
        elif raw_bytes == self.ARROW_RIGHT:
            return KeyEvent(key='right', key_type=KeyType.ARROW, raw_bytes=raw_bytes)

        # Regular keys
        if raw_bytes == b'\r' or raw_bytes == b'\n':
            return KeyEvent(key='enter', key_type=KeyType.SPECIAL, raw_bytes=raw_bytes)

        if raw_bytes == b'\x7f' or raw_bytes == b'\x08':
            return KeyEvent(key='backspace', key_type=KeyType.SPECIAL, raw_bytes=raw_bytes)

        # Regular character
        try:
            char = raw_bytes.decode('utf-8')
            return KeyEvent(key=char, key_type=KeyType.REGULAR, raw_bytes=raw_bytes)
        except UnicodeDecodeError:
            return KeyEvent(key='<unknown>', key_type=KeyType.REGULAR, raw_bytes=raw_bytes)

    def is_quit_key(self, key: str) -> bool:
        """Check if a key is a quit signal."""
        return key in ('q', 'Q', '\x03', '\x04', 'escape', 'quit')

    def is_navigation_key(self, key: str) -> bool:
        """Check if a key is a navigation key."""
        return key in ('up', 'down', 'left', 'right', 'enter')


# Self-teaching note:
#
# This file demonstrates:
# - Non-blocking I/O with select() (Level 6: Advanced I/O)
# - Terminal control with termios and tty (Level 6: System programming)
# - Context managers (__enter__/__exit__) (Level 5: Special methods)
# - ANSI escape sequences (Professional: Terminal control)
# - Event-driven architecture (Level 6: Design patterns)
# - Dataclasses for structured events (Level 5)
#
# Prerequisites:
# - Level 3: Functions and error handling
# - Level 4: Enums and basic classes
# - Level 5: Dataclasses and context managers
# - Level 6: System programming and I/O
#
# This is professional-grade terminal input handling used in tools like:
# - htop
# - vim
# - emacs
# - tmux
# - Modern CLI TUIs
#
# The key insight: Don't WAIT for input - CHECK for input and keep running!
