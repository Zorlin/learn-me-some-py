"""
Tests for the visual theme system.
"""

import pytest
from lmsp.ui.themes import (
    ThemeType,
    ColorScheme,
    ThemeManager,
    theme_manager,
    THEMES,
)


def test_all_themes_exist():
    """Verify all defined theme types have color schemes."""
    for theme_type in ThemeType:
        assert theme_type in THEMES, f"Missing color scheme for {theme_type}"


def test_color_scheme_structure():
    """Verify all color schemes have required fields."""
    required_fields = [
        "primary_text",
        "secondary_text",
        "dim_text",
        "highlight_text",
        "background",
        "panel",
        "selected",
        "hover",
        "success",
        "warning",
        "error",
        "info",
        "accent_1",
        "accent_2",
        "accent_3",
        "accent_4",
        "keyword",
        "string",
        "number",
        "comment",
        "function",
        "class_name",
        "variable",
        "operator",
        "xp_bar",
        "hp_bar",
        "streak_glow",
        "achievement",
    ]

    for theme_type, scheme in THEMES.items():
        for field in required_fields:
            assert hasattr(scheme, field), f"{theme_type} missing field: {field}"
            value = getattr(scheme, field)
            assert isinstance(value, str), f"{theme_type}.{field} should be string"
            assert value.startswith("#"), f"{theme_type}.{field} should be hex color"


def test_theme_manager_default():
    """Test theme manager starts with default theme."""
    manager = ThemeManager()
    assert manager.current_theme == ThemeType.CYBERPUNK
    colors = manager.get_colors()
    assert isinstance(colors, ColorScheme)


def test_theme_manager_set_theme():
    """Test changing themes."""
    manager = ThemeManager()

    manager.set_theme(ThemeType.FOREST)
    assert manager.current_theme == ThemeType.FOREST

    colors = manager.get_colors()
    assert colors == THEMES[ThemeType.FOREST]


def test_theme_manager_cycle():
    """Test cycling through themes."""
    manager = ThemeManager()
    manager.set_theme(ThemeType.CYBERPUNK)

    themes_visited = []
    for _ in range(len(ThemeType) + 2):  # Cycle through all + wrap around
        themes_visited.append(manager.cycle_theme())

    # Should visit all themes
    assert set(themes_visited) == set(ThemeType)


def test_theme_manager_listeners():
    """Test theme change notification."""
    manager = ThemeManager()
    notifications = []

    def listener(colors):
        notifications.append(colors)

    manager.add_listener(listener)

    manager.set_theme(ThemeType.OCEAN)
    assert len(notifications) == 1
    assert notifications[0] == THEMES[ThemeType.OCEAN]

    manager.set_theme(ThemeType.SUNSET)
    assert len(notifications) == 2
    assert notifications[1] == THEMES[ThemeType.SUNSET]


def test_global_theme_manager():
    """Test the global theme_manager instance."""
    assert isinstance(theme_manager, ThemeManager)
    assert theme_manager.current_theme in ThemeType


def test_theme_colors_are_valid_hex():
    """Verify all color values are valid hex colors."""
    import re

    hex_pattern = re.compile(r"^#[0-9a-fA-F]{6}$")

    for theme_type, scheme in THEMES.items():
        for field, value in scheme.__dict__.items():
            if isinstance(value, str):
                assert hex_pattern.match(value), (
                    f"{theme_type}.{field} = '{value}' is not valid hex color"
                )


def test_high_contrast_theme():
    """Verify high contrast theme has sufficient contrast."""
    hc_scheme = THEMES[ThemeType.HIGH_CONTRAST]

    # High contrast should use bright, distinct colors
    assert hc_scheme.primary_text == "#ffffff"
    assert hc_scheme.background == "#000000"

    # Should use fully saturated colors
    assert hc_scheme.success == "#00ff00"
    assert hc_scheme.error == "#ff0000"
    assert hc_scheme.warning == "#ffff00"


def test_theme_manager_get_all_themes():
    """Test retrieving all themes."""
    manager = ThemeManager()
    all_themes = manager.get_all_themes()

    assert isinstance(all_themes, dict)
    assert len(all_themes) == len(ThemeType)

    for theme_type in ThemeType:
        assert theme_type in all_themes
        assert isinstance(all_themes[theme_type], ColorScheme)


def test_multiple_listeners():
    """Test multiple theme change listeners."""
    manager = ThemeManager()

    notifications_1 = []
    notifications_2 = []

    manager.add_listener(lambda c: notifications_1.append(c))
    manager.add_listener(lambda c: notifications_2.append(c))

    manager.set_theme(ThemeType.DRACULA)

    assert len(notifications_1) == 1
    assert len(notifications_2) == 1
    assert notifications_1[0] == notifications_2[0]


# Self-teaching note:
#
# This file demonstrates:
# - pytest test structure (prerequisite: Level 2)
# - Assertions and test functions (prerequisite: Level 3)
# - Enums and dataclasses (prerequisite: Level 5)
# - Testing callbacks and observers (Level 6)
# - Regular expressions for validation (Level 5)
#
# The learner will write tests like these to validate the
# theme system they've built, ensuring all colors are valid
# and the theme manager works correctly.
