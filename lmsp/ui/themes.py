"""
Visual theme system with multiple color schemes.

Provides beautiful, accessible themes for the LMSP UI.
"""

from dataclasses import dataclass
from typing import Dict
from enum import Enum


class ThemeType(Enum):
    """Available visual themes."""
    CYBERPUNK = "cyberpunk"
    FOREST = "forest"
    OCEAN = "ocean"
    SUNSET = "sunset"
    MONOCHROME = "monochrome"
    HIGH_CONTRAST = "high_contrast"
    DRACULA = "dracula"
    SOLARIZED = "solarized"


@dataclass
class ColorScheme:
    """Color scheme for a theme."""
    # Text colors
    primary_text: str
    secondary_text: str
    dim_text: str
    highlight_text: str

    # Background colors
    background: str
    panel: str
    selected: str
    hover: str

    # Status colors
    success: str
    warning: str
    error: str
    info: str

    # Accent colors
    accent_1: str
    accent_2: str
    accent_3: str
    accent_4: str

    # Code syntax colors
    keyword: str
    string: str
    number: str
    comment: str
    function: str
    class_name: str
    variable: str
    operator: str

    # Game-specific colors
    xp_bar: str
    hp_bar: str
    streak_glow: str
    achievement: str


# Theme definitions
THEMES: Dict[ThemeType, ColorScheme] = {
    ThemeType.CYBERPUNK: ColorScheme(
        # Text
        primary_text="#00ff41",  # Matrix green
        secondary_text="#00cc33",
        dim_text="#008822",
        highlight_text="#00ffff",  # Cyan

        # Background
        background="#0d0208",  # Deep black
        panel="#1a0f1e",  # Dark purple
        selected="#2a1f2e",
        hover="#1f1528",

        # Status
        success="#00ff41",
        warning="#ffaa00",
        error="#ff0055",
        info="#00ffff",

        # Accents
        accent_1="#ff00ff",  # Magenta
        accent_2="#00ffff",  # Cyan
        accent_3="#ffff00",  # Yellow
        accent_4="#ff6600",  # Orange

        # Syntax
        keyword="#ff00ff",
        string="#00ffff",
        number="#ffaa00",
        comment="#008822",
        function="#00ff41",
        class_name="#ff00ff",
        variable="#00cc33",
        operator="#ffffff",

        # Game
        xp_bar="#00ff41",
        hp_bar="#ff0055",
        streak_glow="#ffaa00",
        achievement="#ffd700",
    ),

    ThemeType.FOREST: ColorScheme(
        # Text
        primary_text="#c9d1d9",  # Light gray
        secondary_text="#8b949e",
        dim_text="#6e7681",
        highlight_text="#7ee787",  # Bright green

        # Background
        background="#0d1117",  # Very dark gray
        panel="#161b22",
        selected="#21262d",
        hover="#30363d",

        # Status
        success="#7ee787",  # Green
        warning="#d29922",  # Amber
        error="#f85149",  # Red
        info="#58a6ff",  # Blue

        # Accents
        accent_1="#7ee787",  # Green
        accent_2="#56d364",  # Lighter green
        accent_3="#3fb950",  # Forest green
        accent_4="#2ea043",  # Deep green

        # Syntax
        keyword="#ff7b72",  # Pink
        string="#a5d6ff",  # Light blue
        number="#79c0ff",  # Blue
        comment="#8b949e",  # Gray
        function="#d2a8ff",  # Purple
        class_name="#ffa657",  # Orange
        variable="#c9d1d9",  # White
        operator="#ff7b72",

        # Game
        xp_bar="#7ee787",
        hp_bar="#f85149",
        streak_glow="#d29922",
        achievement="#ffd700",
    ),

    ThemeType.OCEAN: ColorScheme(
        # Text
        primary_text="#e6f1ff",  # Very light blue
        secondary_text="#c5dff8",
        dim_text="#82aaff",
        highlight_text="#82aaff",  # Bright blue

        # Background
        background="#011627",  # Deep navy
        panel="#0b2942",
        selected="#0d3a58",
        hover="#0e4366",

        # Status
        success="#7fdbca",  # Teal
        warning="#ffcc00",  # Gold
        error="#ef5350",  # Red
        info="#82aaff",  # Blue

        # Accents
        accent_1="#82aaff",  # Blue
        accent_2="#7fdbca",  # Teal
        accent_3="#c792ea",  # Purple
        accent_4="#ffcc00",  # Gold

        # Syntax
        keyword="#c792ea",  # Purple
        string="#ecc48d",  # Peach
        number="#f78c6c",  # Orange
        comment="#637777",  # Gray-green
        function="#82aaff",  # Blue
        class_name="#ffcb8b",  # Yellow
        variable="#e6f1ff",  # White
        operator="#89ddff",  # Cyan

        # Game
        xp_bar="#7fdbca",
        hp_bar="#ef5350",
        streak_glow="#ffcc00",
        achievement="#ffd700",
    ),

    ThemeType.SUNSET: ColorScheme(
        # Text
        primary_text="#fef9c7",  # Cream
        secondary_text="#fdd8a8",
        dim_text="#f9a547",
        highlight_text="#ff8f00",  # Bright orange

        # Background
        background="#1a0a0a",  # Very dark brown
        panel="#2d1810",
        selected="#3d2418",
        hover="#4d2e20",

        # Status
        success="#a7c957",  # Lime green
        warning="#ff8f00",  # Orange
        error="#e63946",  # Red
        info="#457b9d",  # Blue

        # Accents
        accent_1="#ff8f00",  # Orange
        accent_2="#f77f00",  # Dark orange
        accent_3="#d62828",  # Red
        accent_4="#fcbf49",  # Yellow

        # Syntax
        keyword="#f77f00",  # Orange
        string="#fcbf49",  # Yellow
        number="#ff8f00",  # Bright orange
        comment="#a3825f",  # Brown
        function="#e63946",  # Red
        class_name="#f77f00",  # Orange
        variable="#fef9c7",  # Cream
        operator="#ff6d00",

        # Game
        xp_bar="#fcbf49",
        hp_bar="#e63946",
        streak_glow="#ff8f00",
        achievement="#ffd700",
    ),

    ThemeType.MONOCHROME: ColorScheme(
        # Text
        primary_text="#ffffff",
        secondary_text="#cccccc",
        dim_text="#888888",
        highlight_text="#ffffff",

        # Background
        background="#000000",
        panel="#1a1a1a",
        selected="#2a2a2a",
        hover="#333333",

        # Status
        success="#ffffff",
        warning="#aaaaaa",
        error="#666666",
        info="#cccccc",

        # Accents
        accent_1="#ffffff",
        accent_2="#dddddd",
        accent_3="#bbbbbb",
        accent_4="#999999",

        # Syntax
        keyword="#ffffff",
        string="#dddddd",
        number="#cccccc",
        comment="#888888",
        function="#ffffff",
        class_name="#eeeeee",
        variable="#cccccc",
        operator="#ffffff",

        # Game
        xp_bar="#ffffff",
        hp_bar="#999999",
        streak_glow="#cccccc",
        achievement="#ffffff",
    ),

    ThemeType.HIGH_CONTRAST: ColorScheme(
        # Text
        primary_text="#ffffff",
        secondary_text="#ffff00",  # Bright yellow
        dim_text="#00ffff",  # Bright cyan
        highlight_text="#ff00ff",  # Bright magenta

        # Background
        background="#000000",
        panel="#000000",
        selected="#333333",
        hover="#222222",

        # Status
        success="#00ff00",  # Bright green
        warning="#ffff00",  # Bright yellow
        error="#ff0000",  # Bright red
        info="#00ffff",  # Bright cyan

        # Accents
        accent_1="#ff00ff",  # Magenta
        accent_2="#00ffff",  # Cyan
        accent_3="#ffff00",  # Yellow
        accent_4="#ff0000",  # Red

        # Syntax
        keyword="#ff00ff",
        string="#00ffff",
        number="#ffff00",
        comment="#00ff00",
        function="#ffffff",
        class_name="#ff00ff",
        variable="#ffffff",
        operator="#ffffff",

        # Game
        xp_bar="#00ff00",
        hp_bar="#ff0000",
        streak_glow="#ffff00",
        achievement="#ffff00",
    ),

    ThemeType.DRACULA: ColorScheme(
        # Text
        primary_text="#f8f8f2",  # Foreground
        secondary_text="#6272a4",  # Comment
        dim_text="#44475a",  # Current line
        highlight_text="#8be9fd",  # Cyan

        # Background
        background="#282a36",  # Background
        panel="#343746",
        selected="#44475a",
        hover="#4d4f5c",

        # Status
        success="#50fa7b",  # Green
        warning="#f1fa8c",  # Yellow
        error="#ff5555",  # Red
        info="#8be9fd",  # Cyan

        # Accents
        accent_1="#bd93f9",  # Purple
        accent_2="#ff79c6",  # Pink
        accent_3="#ffb86c",  # Orange
        accent_4="#50fa7b",  # Green

        # Syntax
        keyword="#ff79c6",  # Pink
        string="#f1fa8c",  # Yellow
        number="#bd93f9",  # Purple
        comment="#6272a4",  # Comment
        function="#50fa7b",  # Green
        class_name="#8be9fd",  # Cyan
        variable="#f8f8f2",  # Foreground
        operator="#ff79c6",

        # Game
        xp_bar="#50fa7b",
        hp_bar="#ff5555",
        streak_glow="#f1fa8c",
        achievement="#ffd700",
    ),

    ThemeType.SOLARIZED: ColorScheme(
        # Text
        primary_text="#839496",  # Base0
        secondary_text="#657b83",  # Base00
        dim_text="#586e75",  # Base01
        highlight_text="#93a1a1",  # Base1

        # Background
        background="#002b36",  # Base03
        panel="#073642",  # Base02
        selected="#094554",
        hover="#0a4d5e",

        # Status
        success="#859900",  # Green
        warning="#b58900",  # Yellow
        error="#dc322f",  # Red
        info="#268bd2",  # Blue

        # Accents
        accent_1="#268bd2",  # Blue
        accent_2="#2aa198",  # Cyan
        accent_3="#6c71c4",  # Violet
        accent_4="#cb4b16",  # Orange

        # Syntax
        keyword="#859900",  # Green
        string="#2aa198",  # Cyan
        number="#d33682",  # Magenta
        comment="#586e75",  # Base01
        function="#268bd2",  # Blue
        class_name="#b58900",  # Yellow
        variable="#839496",  # Base0
        operator="#859900",

        # Game
        xp_bar="#859900",
        hp_bar="#dc322f",
        streak_glow="#b58900",
        achievement="#ffd700",
    ),
}


class ThemeManager:
    """Manages theme selection and application."""

    def __init__(self):
        self.current_theme = ThemeType.CYBERPUNK
        self._listeners = []

    def set_theme(self, theme: ThemeType) -> None:
        """Change the current theme."""
        self.current_theme = theme
        self._notify_listeners()

    def get_colors(self) -> ColorScheme:
        """Get the current color scheme."""
        return THEMES[self.current_theme]

    def add_listener(self, callback) -> None:
        """Add a callback to be notified of theme changes."""
        self._listeners.append(callback)

    def _notify_listeners(self) -> None:
        """Notify all listeners of theme change."""
        colors = self.get_colors()
        for listener in self._listeners:
            listener(colors)

    def cycle_theme(self) -> ThemeType:
        """Cycle to the next theme."""
        themes = list(ThemeType)
        current_index = themes.index(self.current_theme)
        next_index = (current_index + 1) % len(themes)
        self.set_theme(themes[next_index])
        return self.current_theme

    def get_all_themes(self) -> Dict[ThemeType, ColorScheme]:
        """Get all available themes."""
        return THEMES.copy()


# Global theme manager instance
theme_manager = ThemeManager()


# Self-teaching note:
#
# This file demonstrates:
# - Enums for type-safe constants (prerequisite: Level 3)
# - Dataclasses for data containers (prerequisite: Level 5)
# - Type hints with Dict, str (prerequisite: Level 4)
# - Observer pattern (listeners) for event handling (Level 6)
# - Global singletons (theme_manager)
#
# The learner will encounter this AFTER mastering:
# - Basic Python types and collections
# - Functions and classes
# - Decorators (@dataclass)
# - Design patterns
#
# This is professional Python for theming systems - the same pattern
# used in VS Code, JetBrains IDEs, and other professional tools.
