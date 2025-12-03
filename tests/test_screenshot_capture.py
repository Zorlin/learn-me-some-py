"""
Screenshot Capture Utilities for Visual Regression Testing
===========================================================

Provides helper functions for capturing and managing screenshots during
visual regression testing. Can be used with Playwright MCP tools.

Features:
- Smart screenshot naming and organization
- Metadata storage alongside screenshots
- Viewport state tracking
- Theme/state context capture
"""

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


@dataclass
class ScreenshotMetadata:
    """Metadata for a captured screenshot."""

    name: str
    state: str  # welcome, challenge, code_editor, results, etc.
    viewport_width: int
    viewport_height: int
    theme: str  # oled_dark, light, etc.
    timestamp: str
    url: Optional[str] = None
    additional_context: Optional[Dict] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "state": self.state,
            "viewport": {"width": self.viewport_width, "height": self.viewport_height},
            "theme": self.theme,
            "timestamp": self.timestamp,
            "url": self.url,
            "context": self.additional_context or {},
        }


class ScreenshotManager:
    """Manages screenshot capture, storage, and metadata."""

    def __init__(self, base_dir: Path = None):
        """
        Initialize the screenshot manager.

        Args:
            base_dir: Base directory for storing screenshots
        """
        if base_dir is None:
            base_dir = Path(__file__).parent / "visual_baselines"
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.screenshots: Dict[str, ScreenshotMetadata] = {}

    def capture(
        self,
        screenshot_bytes: bytes,
        name: str,
        state: str,
        viewport_width: int,
        viewport_height: int,
        theme: str = "oled_dark",
        url: Optional[str] = None,
        context: Optional[Dict] = None,
    ) -> Path:
        """
        Capture and store a screenshot with metadata.

        Args:
            screenshot_bytes: PNG bytes from page.screenshot()
            name: Screenshot identifier (e.g., 'welcome_screen')
            state: UI state (welcome, challenge, code_editor, results)
            viewport_width: Viewport width in pixels
            viewport_height: Viewport height in pixels
            theme: Theme being used
            url: Current page URL
            context: Additional context dictionary

        Returns:
            Path to saved screenshot
        """
        # Create directory for this state
        state_dir = self.base_dir / state
        state_dir.mkdir(parents=True, exist_ok=True)

        # Save screenshot
        screenshot_path = state_dir / f"{name}.png"
        with open(screenshot_path, "wb") as f:
            f.write(screenshot_bytes)

        # Create and store metadata
        metadata = ScreenshotMetadata(
            name=name,
            state=state,
            viewport_width=viewport_width,
            viewport_height=viewport_height,
            theme=theme,
            timestamp=datetime.now().isoformat(),
            url=url,
            additional_context=context,
        )
        self.screenshots[f"{state}/{name}"] = metadata

        # Save metadata
        metadata_path = state_dir / f"{name}_metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(metadata.to_dict(), f, indent=2)

        return screenshot_path

    def save_manifest(self) -> Path:
        """Save a manifest of all captured screenshots."""
        manifest = {
            "captured_at": datetime.now().isoformat(),
            "total_screenshots": len(self.screenshots),
            "screenshots": {
                key: metadata.to_dict()
                for key, metadata in self.screenshots.items()
            },
        }

        manifest_path = self.base_dir / "manifest.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

        return manifest_path


class ViewportConfig:
    """Standard viewport configurations for testing."""

    # Desktop viewports
    DESKTOP_1280x720 = {"width": 1280, "height": 720}
    DESKTOP_1920x1080 = {"width": 1920, "height": 1080}
    DESKTOP_1366x768 = {"width": 1366, "height": 768}

    # Tablet viewports
    TABLET_768x1024 = {"width": 768, "height": 1024}
    TABLET_834x1112 = {"width": 834, "height": 1112}

    # Mobile viewports
    MOBILE_375x667 = {"width": 375, "height": 667}
    MOBILE_414x896 = {"width": 414, "height": 896}

    @classmethod
    def get_all(cls) -> list:
        """Get all standard viewport configurations."""
        return [
            ("desktop_1280x720", cls.DESKTOP_1280x720),
            ("desktop_1920x1080", cls.DESKTOP_1920x1080),
            ("desktop_1366x768", cls.DESKTOP_1366x768),
            ("tablet_768x1024", cls.TABLET_768x1024),
            ("tablet_834x1112", cls.TABLET_834x1112),
            ("mobile_375x667", cls.MOBILE_375x667),
            ("mobile_414x896", cls.MOBILE_414x896),
        ]


class ScreenshotCapturePlan:
    """Plan for what screenshots to capture during a test run."""

    def __init__(self):
        """Initialize the capture plan."""
        self.captures = []

    def add_welcome_screen(self) -> "ScreenshotCapturePlan":
        """Add capture of welcome screen at standard viewports."""
        for viewport_name, viewport in ViewportConfig.get_all():
            self.captures.append({
                "name": f"welcome_{viewport_name}",
                "state": "welcome",
                "viewport": viewport,
                "description": f"Welcome screen at {viewport_name}",
            })
        return self

    def add_challenge_view(self) -> "ScreenshotCapturePlan":
        """Add capture of challenge view."""
        self.captures.append({
            "name": "challenge_view",
            "state": "challenge",
            "viewport": ViewportConfig.DESKTOP_1280x720,
            "description": "Challenge view with description and editor",
        })
        return self

    def add_code_editor_states(self) -> "ScreenshotCapturePlan":
        """Add captures of code editor in different states."""
        states = [
            ("empty", "Empty code editor"),
            ("with_code", "Editor with sample code"),
            ("with_errors", "Editor highlighting errors"),
            ("cursor_position", "Cursor at different positions"),
        ]
        for state_name, desc in states:
            self.captures.append({
                "name": f"editor_{state_name}",
                "state": "code_editor",
                "viewport": ViewportConfig.DESKTOP_1280x720,
                "description": desc,
            })
        return self

    def add_results_panel_states(self) -> "ScreenshotCapturePlan":
        """Add captures of results panel in different states."""
        states = [
            ("all_pass", "All tests passing"),
            ("partial_pass", "Mixed pass/fail results"),
            ("all_fail", "All tests failing"),
            ("execution_time", "With execution time display"),
        ]
        for state_name, desc in states:
            self.captures.append({
                "name": f"results_{state_name}",
                "state": "results",
                "viewport": ViewportConfig.DESKTOP_1280x720,
                "description": desc,
            })
        return self

    def add_emotional_feedback_states(self) -> "ScreenshotCapturePlan":
        """Add captures of emotional feedback in different states."""
        states = [
            ("neutral", "Neutral state (no triggers)"),
            ("positive", "Positive feedback (RT triggered)"),
            ("negative", "Negative feedback (LT triggered)"),
            ("mixed", "Mixed emotional response"),
        ]
        for state_name, desc in states:
            self.captures.append({
                "name": f"emotional_{state_name}",
                "state": "emotional_feedback",
                "viewport": ViewportConfig.DESKTOP_1280x720,
                "description": desc,
            })
        return self

    def add_achievement_celebration(self) -> "ScreenshotCapturePlan":
        """Add capture of achievement celebration."""
        self.captures.append({
            "name": "achievement_celebration",
            "state": "achievements",
            "viewport": ViewportConfig.DESKTOP_1280x720,
            "description": "Achievement celebration animation",
        })
        return self

    def get_captures(self) -> list:
        """Get all planned captures."""
        return self.captures


def create_standard_capture_plan() -> ScreenshotCapturePlan:
    """Create a standard plan that captures all key UI states."""
    return (
        ScreenshotCapturePlan()
        .add_welcome_screen()
        .add_challenge_view()
        .add_code_editor_states()
        .add_results_panel_states()
        .add_emotional_feedback_states()
        .add_achievement_celebration()
    )


# Tests for the screenshot capture utilities
def test_screenshot_metadata():
    """Test ScreenshotMetadata creation and serialization."""
    metadata = ScreenshotMetadata(
        name="welcome_screen",
        state="welcome",
        viewport_width=1280,
        viewport_height=720,
        theme="oled_dark",
        timestamp="2025-12-03T10:30:00Z",
        url="http://localhost:8000/",
    )

    assert metadata.name == "welcome_screen"
    assert metadata.state == "welcome"

    # Test serialization
    data = metadata.to_dict()
    assert data["state"] == "welcome"
    assert data["viewport"]["width"] == 1280


def test_screenshot_manager_init():
    """Test ScreenshotManager initialization."""
    base_dir = Path(__file__).parent / "test_screenshots"
    manager = ScreenshotManager(base_dir)

    assert manager.base_dir == base_dir
    assert manager.base_dir.exists()


def test_viewport_config():
    """Test ViewportConfig standard sizes."""
    assert ViewportConfig.DESKTOP_1280x720["width"] == 1280
    assert ViewportConfig.MOBILE_375x667["width"] == 375

    # Should have all viewports
    viewports = ViewportConfig.get_all()
    assert len(viewports) > 0
    assert all(isinstance(name, str) for name, _ in viewports)


def test_screenshot_capture_plan():
    """Test building a capture plan."""
    plan = (
        ScreenshotCapturePlan()
        .add_welcome_screen()
        .add_challenge_view()
    )

    captures = plan.get_captures()
    assert len(captures) > 0
    assert any(c["state"] == "welcome" for c in captures)
    assert any(c["state"] == "challenge" for c in captures)


def test_standard_capture_plan():
    """Test the standard capture plan."""
    plan = create_standard_capture_plan()
    captures = plan.get_captures()

    # Should have captures for all key states
    states = {c["state"] for c in captures}
    assert "welcome" in states
    assert "challenge" in states
    assert "code_editor" in states
    assert "results" in states
    assert "emotional_feedback" in states
    assert "achievements" in states


# Self-teaching note:
#
# This file demonstrates:
# - Data structures for managing test artifacts (Level 4+: dataclasses)
# - File organization and metadata management (Level 4+)
# - Builder pattern for test configuration (Level 5+: design patterns)
# - JSON serialization (Level 4+)
# - Testing utilities (Level 5+: professional patterns)
#
# Prerequisites:
# - Level 4: Functions, dictionaries, file I/O
# - Level 5: Classes, dataclasses, design patterns
#
# The pattern shown here (ScreenshotCapturePlan using builder pattern)
# is used in professional testing frameworks like Selenium, Playwright,
# and Cypress for flexible test configuration.
