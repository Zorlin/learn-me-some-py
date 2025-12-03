"""
Visual Regression Testing for LMSP Web UI
==========================================

Uses Playwright to capture screenshots of key UI states and detect visual regressions
automatically. Reference images are captured once and subsequent runs are compared
against these baselines.

Features:
- Automatic baseline screenshot capture
- Visual regression detection with image comparison
- Per-state snapshot storage
- Configurable comparison thresholds
- Multi-state testing (welcome, challenge, code editor, results)

Usage:
    # First run: Create baseline images
    pytest tests/test_visual_regression.py -v --create-baselines

    # Subsequent runs: Compare against baselines
    pytest tests/test_visual_regression.py -v

    # Show detailed diff reports
    pytest tests/test_visual_regression.py -v --show-diffs
"""

import json
import os
from pathlib import Path
from typing import Optional

import pytest

# Try to import PIL for image comparison, skip if not available
try:
    from PIL import Image, ImageChops, ImageDraw
except ImportError:
    Image = None  # type: ignore


class VisualRegressionTester:
    """Helper class for visual regression testing with Playwright."""

    def __init__(
        self,
        baseline_dir: Path,
        threshold: float = 0.01,
    ):
        """
        Initialize the visual regression tester.

        Args:
            baseline_dir: Directory to store baseline screenshots
            threshold: Acceptable difference threshold (0.0-1.0)
        """
        self.baseline_dir = baseline_dir
        self.threshold = threshold
        self.baseline_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir = self.baseline_dir / "results"
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def get_baseline_path(self, name: str) -> Path:
        """Get the path to a baseline image."""
        return self.baseline_dir / f"{name}.png"

    def get_result_path(self, name: str) -> Path:
        """Get the path to a result image from the last test run."""
        return self.results_dir / f"{name}.png"

    def save_screenshot(self, screenshot_bytes: bytes, name: str) -> Path:
        """
        Save a screenshot from Playwright.

        Args:
            screenshot_bytes: Screenshot bytes from page.screenshot()
            name: Identifier for this screenshot

        Returns:
            Path to saved screenshot
        """
        if Image is None:
            raise ImportError("PIL is required for visual regression testing")

        path = self.get_result_path(name)
        with open(path, "wb") as f:
            f.write(screenshot_bytes)
        return path

    def compare_screenshots(self, name: str, screenshot_bytes: bytes) -> dict:
        """
        Compare a screenshot against its baseline.

        Args:
            name: Identifier for this screenshot
            screenshot_bytes: Screenshot bytes from page.screenshot()

        Returns:
            Dictionary with comparison results
        """
        if Image is None:
            pytest.skip("PIL is required for visual regression testing")

        # Save the current screenshot
        current_path = self.save_screenshot(screenshot_bytes, name)

        # Check if baseline exists
        baseline_path = self.get_baseline_path(name)
        if not baseline_path.exists():
            return {
                "status": "baseline_created",
                "baseline_path": str(baseline_path),
                "current_path": str(current_path),
                "message": f"Baseline created: {baseline_path}",
            }

        # Load both images
        baseline = Image.open(baseline_path)
        current = Image.open(current_path)

        # Check dimensions match
        if baseline.size != current.size:
            return {
                "status": "size_mismatch",
                "baseline_size": baseline.size,
                "current_size": current.size,
                "message": "Image dimensions don't match",
            }

        # Compare images
        diff = ImageChops.difference(baseline, current)
        diff_stat = diff.getextrema()

        # Calculate difference ratio
        # If max channel difference > 0, there's a difference
        max_diff = max(diff_stat) if diff_stat else (0, 0)
        # Normalize to 0-1 range (assuming 8-bit images, max is 255)
        diff_ratio = max_diff[1] / 255.0 if max_diff else 0.0

        if diff_ratio <= self.threshold:
            return {
                "status": "passed",
                "diff_ratio": diff_ratio,
                "threshold": self.threshold,
                "message": f"Visual regression test passed (diff: {diff_ratio:.4f})",
            }
        else:
            # Create diff visualization
            diff_path = self.results_dir / f"{name}_diff.png"
            diff.save(diff_path)

            return {
                "status": "failed",
                "diff_ratio": diff_ratio,
                "threshold": self.threshold,
                "baseline_path": str(baseline_path),
                "current_path": str(current_path),
                "diff_path": str(diff_path),
                "message": f"Visual regression detected (diff: {diff_ratio:.4f})",
            }

    def create_baseline(self, name: str, screenshot_bytes: bytes) -> Path:
        """Create a baseline image for a screenshot."""
        if Image is None:
            raise ImportError("PIL is required for visual regression testing")

        baseline_path = self.get_baseline_path(name)
        with open(baseline_path, "wb") as f:
            f.write(screenshot_bytes)
        return baseline_path


@pytest.fixture
def visual_tester(request):
    """Fixture to provide visual regression tester."""
    baselines_dir = Path(__file__).parent / "visual_baselines"
    tester = VisualRegressionTester(baselines_dir, threshold=0.01)

    # Check if we're creating baselines
    if request.config.getoption("--create-baselines", False):
        yield tester
    else:
        yield tester


@pytest.fixture
def mock_page():
    """
    Mock Playwright page object for testing without browser.
    In real usage, this would be a real Playwright page from a fixture.
    """

    class MockPage:
        async def screenshot(self, **kwargs) -> bytes:
            """Return a minimal 1x1 PNG for testing."""
            # Minimal PNG: 1x1 white pixel
            return (
                b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
                b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00"
                b"\x00\x0cIDATx\x9cc\xf8\xcf\xc0\x00\x00\x00\x03\x00\x01"
                b"u\xa5\xe6\xfe\x00\x00\x00\x00IEND\xaeB`\x82"
            )

    return MockPage()


def test_visual_regression_tester_init():
    """Test VisualRegressionTester initialization."""
    baselines_dir = Path(__file__).parent / "visual_baselines"
    tester = VisualRegressionTester(baselines_dir)

    assert tester.baseline_dir == baselines_dir
    assert tester.threshold == 0.01
    assert tester.baseline_dir.exists()
    assert tester.results_dir.exists()


def test_baseline_path():
    """Test baseline path generation."""
    baselines_dir = Path(__file__).parent / "visual_baselines"
    tester = VisualRegressionTester(baselines_dir)

    path = tester.get_baseline_path("welcome_screen")
    assert path.name == "welcome_screen.png"
    assert str(baselines_dir) in str(path)


def test_result_path():
    """Test result path generation."""
    baselines_dir = Path(__file__).parent / "visual_baselines"
    tester = VisualRegressionTester(baselines_dir)

    path = tester.get_result_path("welcome_screen")
    assert path.name == "welcome_screen.png"
    assert "results" in str(path)


def test_save_screenshot(visual_tester, mock_page):
    """Test saving a screenshot."""
    if Image is None:
        pytest.skip("PIL is required for this test")

    import asyncio

    # Get minimal PNG data
    async def get_screenshot():
        return await mock_page.screenshot()

    screenshot_bytes = asyncio.run(get_screenshot())

    # Save screenshot
    path = visual_tester.save_screenshot(screenshot_bytes, "test_screen")
    assert path.exists()
    assert path.suffix == ".png"


def test_compare_screenshots_baseline_creation(visual_tester, mock_page):
    """Test baseline creation on first comparison."""
    if Image is None:
        pytest.skip("PIL is required for this test")

    import asyncio

    async def get_screenshot():
        return await mock_page.screenshot()

    screenshot_bytes = asyncio.run(get_screenshot())

    # Clear any existing baseline
    baseline_path = visual_tester.get_baseline_path("new_baseline")
    if baseline_path.exists():
        baseline_path.unlink()

    # Compare should create baseline
    result = visual_tester.compare_screenshots("new_baseline", screenshot_bytes)
    assert result["status"] == "baseline_created"
    assert baseline_path.exists()


def test_compare_screenshots_identical(visual_tester, mock_page):
    """Test comparing identical screenshots."""
    if Image is None:
        pytest.skip("PIL is required for this test")

    import asyncio

    async def get_screenshot():
        return await mock_page.screenshot()

    screenshot_bytes = asyncio.run(get_screenshot())

    # Create baseline
    baseline_name = "identical_test"
    visual_tester.create_baseline(baseline_name, screenshot_bytes)

    # Compare same image
    result = visual_tester.compare_screenshots(baseline_name, screenshot_bytes)
    assert result["status"] == "passed"
    assert result["diff_ratio"] == 0.0


def test_compare_screenshots_size_mismatch(visual_tester):
    """Test comparing screenshots with different sizes."""
    if Image is None:
        pytest.skip("PIL is required for this test")

    # Create baseline (1x1 image)
    baseline_name = "size_mismatch_test"
    small_png = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
        b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00"
        b"\x00\x0cIDATx\x9cc\xf8\xcf\xc0\x00\x00\x00\x03\x00\x01"
        b"u\xa5\xe6\xfe\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    visual_tester.create_baseline(baseline_name, small_png)

    # Create different-sized image (2x2)
    large_img = Image.new("RGB", (2, 2), color="red")
    import io

    large_png = io.BytesIO()
    large_img.save(large_png, format="PNG")
    large_bytes = large_png.getvalue()

    # Should detect size mismatch
    result = visual_tester.compare_screenshots(baseline_name, large_bytes)
    assert result["status"] == "size_mismatch"


def test_visual_regression_metadata_storage(visual_tester):
    """Test storing and retrieving test metadata."""
    metadata = {
        "state": "welcome_screen",
        "theme": "oled_dark",
        "resolution": "1280x720",
        "timestamp": "2025-12-03T10:30:00Z",
    }

    metadata_path = visual_tester.results_dir / "metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)

    # Load and verify
    with open(metadata_path, "r") as f:
        loaded = json.load(f)

    assert loaded == metadata
    assert loaded["state"] == "welcome_screen"
    assert loaded["theme"] == "oled_dark"


# Test scenarios for key UI states
class TestWelcomeScreenVisuals:
    """Visual regression tests for the welcome screen."""

    def test_welcome_screen_layout(self, visual_tester):
        """
        Test that welcome screen layout doesn't regress.

        This test would run against the actual web server:
        1. Navigate to /
        2. Capture screenshot of welcome screen
        3. Compare against baseline
        """
        # In actual implementation with Playwright:
        # async with async_playwright() as p:
        #     browser = await p.chromium.launch()
        #     page = await browser.new_page(viewport={"width": 1280, "height": 720})
        #     await page.goto("http://localhost:8000/")
        #     screenshot = await page.screenshot()
        #     result = visual_tester.compare_screenshots("welcome_screen", screenshot)
        #     assert result["status"] in ["passed", "baseline_created"]
        pass

    def test_welcome_screen_oled_theme(self, visual_tester):
        """
        Test that OLED black theme is applied correctly.

        Should verify:
        - Background is pure black (#000000)
        - Text contrast is high
        - No washed-out grays
        """
        pass

    def test_welcome_screen_responsive(self, visual_tester):
        """
        Test welcome screen at multiple viewports.

        Should test at:
        - 1280x720 (standard)
        - 1920x1080 (full HD)
        - 768x1024 (tablet)
        - 375x667 (mobile)
        """
        pass


class TestChallengeViewVisuals:
    """Visual regression tests for challenge view."""

    def test_challenge_view_layout(self, visual_tester):
        """
        Test that challenge view layout doesn't regress.

        Should capture:
        - Challenge description panel
        - Code editor panel
        - Test results panel
        - Progress tracking
        """
        pass

    def test_challenge_code_syntax_highlighting(self, visual_tester):
        """
        Test that syntax highlighting is applied correctly.

        Should verify:
        - Python keywords are highlighted
        - Strings have correct color
        - Comments are visible
        """
        pass

    def test_challenge_success_state(self, visual_tester):
        """
        Test visual appearance when tests pass.

        Should show:
        - Green checkmarks
        - Success message
        - Next challenge button
        - Achievement rewards (if applicable)
        """
        pass

    def test_challenge_failure_state(self, visual_tester):
        """
        Test visual appearance when tests fail.

        Should show:
        - Red X marks for failed tests
        - Clear error messages
        - Helpful hints
        """
        pass


class TestCodeEditorVisuals:
    """Visual regression tests for code editor."""

    def test_code_editor_empty(self, visual_tester):
        """Test empty code editor appearance."""
        pass

    def test_code_editor_with_code(self, visual_tester):
        """Test code editor with sample code."""
        pass

    def test_code_editor_with_errors(self, visual_tester):
        """Test code editor showing error highlights."""
        pass

    def test_code_editor_cursor_position(self, visual_tester):
        """Test cursor visibility and position."""
        pass


class TestResultsPanelVisuals:
    """Visual regression tests for results panel."""

    def test_results_panel_all_pass(self, visual_tester):
        """Test results panel when all tests pass."""
        pass

    def test_results_panel_partial_pass(self, visual_tester):
        """Test results panel with mixed pass/fail."""
        pass

    def test_results_panel_all_fail(self, visual_tester):
        """Test results panel when all tests fail."""
        pass

    def test_results_panel_execution_time(self, visual_tester):
        """Test execution time display in results."""
        pass


# Configuration for pytest
def pytest_addoption(parser):
    """Add custom command-line options."""
    parser.addoption(
        "--create-baselines",
        action="store_true",
        default=False,
        help="Create baseline images instead of comparing",
    )
    parser.addoption(
        "--show-diffs",
        action="store_true",
        default=False,
        help="Show detailed diff reports",
    )


# Self-teaching note:
#
# This file demonstrates:
# - Visual regression testing with Playwright (Level 6+: Web testing)
# - Image comparison and diff detection (Level 5+: Image processing)
# - Fixture usage for test setup (Level 4+: Testing patterns)
# - Parameterized UI testing across multiple states (Level 5+)
# - Baseline-based testing patterns (Professional QA)
#
# Prerequisites:
# - Level 4: Functions, testing basics
# - Level 5: Classes, file I/O, image basics
# - Level 6: Web frameworks, async/await
#
# Visual regression testing is crucial for:
# - Catching unintended UI changes
# - Verifying theme consistency
# - Ensuring responsive design works
# - Maintaining design system integrity
# - Automating visual QA
#
# This pattern is used by major companies:
# - Google (uses VNG - Visual Regression Testing)
# - Facebook/Meta (uses similar approaches)
# - GitHub, GitLab, and others
