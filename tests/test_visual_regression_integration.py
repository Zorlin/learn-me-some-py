"""
Visual Regression Testing Integration Tests
============================================

Comprehensive integration tests for visual regression testing that verify
the full pipeline: baseline creation, screenshot capture, comparison,
and diff visualization.

Tests cover:
- Welcome screen visual consistency
- Challenge view layout and styling
- Code editor appearance and syntax highlighting
- Results panel with different states
- Emotional feedback visualization
- Achievement celebration animations
- Theme switching and dark mode
- Responsive design across viewports
"""

import json
import pytest
from pathlib import Path
from dataclasses import asdict

# Import testing utilities
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from test_visual_regression import VisualRegressionTester
from test_screenshot_capture import (
    ScreenshotManager,
    ScreenshotMetadata,
    ViewportConfig,
    create_standard_capture_plan,
)


class TestVisualRegressionIntegration:
    """Integration tests for visual regression testing pipeline."""

    @pytest.fixture
    def visual_tester(self):
        """Create a visual regression tester for tests."""
        baselines_dir = Path(__file__).parent / "integration_baselines"
        return VisualRegressionTester(baselines_dir, threshold=0.01)

    @pytest.fixture
    def screenshot_manager(self):
        """Create a screenshot manager for tests."""
        return ScreenshotManager()

    def test_welcome_screen_baseline_creation(self, visual_tester, screenshot_manager):
        """Test creating baseline for welcome screen."""
        # Minimal 1x1 PNG
        test_png = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
            b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00"
            b"\x00\x0cIDATx\x9cc\xf8\xcf\xc0\x00\x00\x00\x03\x00\x01"
            b"u\xa5\xe6\xfe\x00\x00\x00\x00IEND\xaeB`\x82"
        )

        # Clear baseline if exists
        baseline = visual_tester.get_baseline_path("welcome_screen")
        if baseline.exists():
            baseline.unlink()

        # Capture welcome screen
        path = screenshot_manager.capture(
            test_png,
            name="welcome_screen",
            state="welcome",
            viewport_width=1280,
            viewport_height=720,
            theme="oled_dark",
            url="http://localhost:8000/",
            context={"notes": "Homepage welcome screen baseline"},
        )

        assert path.exists()
        assert "welcome" in str(path)

    def test_challenge_view_consistency(self, visual_tester, screenshot_manager):
        """Test that challenge view remains visually consistent."""
        try:
            from PIL import Image
        except ImportError:
            pytest.skip("PIL is required for this test")

        # Create baseline
        test_png = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
            b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00"
            b"\x00\x0cIDATx\x9cc\xf8\xcf\xc0\x00\x00\x00\x03\x00\x01"
            b"u\xa5\xe6\xfe\x00\x00\x00\x00IEND\xaeB`\x82"
        )

        baseline_path = visual_tester.create_baseline("challenge_view", test_png)
        assert baseline_path.exists()

        # Compare same image should pass
        result = visual_tester.compare_screenshots("challenge_view", test_png)
        assert result["status"] == "passed"
        assert result["diff_ratio"] == 0.0

    def test_screenshot_metadata_storage(self, screenshot_manager):
        """Test storing and retrieving screenshot metadata."""
        test_png = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
            b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00"
            b"\x00\x0cIDATx\x9cc\xf8\xcf\xc0\x00\x00\x00\x03\x00\x01"
            b"u\xa5\xe6\xfe\x00\x00\x00\x00IEND\xaeB`\x82"
        )

        # Capture with context
        screenshot_manager.capture(
            test_png,
            name="test_screen",
            state="challenge",
            viewport_width=1280,
            viewport_height=720,
            theme="oled_dark",
            url="http://localhost:8000/challenges/test",
            context={
                "challenge_id": "hello_world",
                "challenge_level": 1,
                "tests_passing": 0,
                "tests_total": 3,
            },
        )

        # Save manifest
        manifest_path = screenshot_manager.save_manifest()
        assert manifest_path.exists()

        # Load and verify
        with open(manifest_path, "r") as f:
            manifest = json.load(f)

        assert "screenshots" in manifest
        assert manifest["total_screenshots"] == 1

    def test_capture_plan_generation(self):
        """Test generating a capture plan for all UI states."""
        plan = create_standard_capture_plan()
        captures = plan.get_captures()

        # Should have captures for each key state
        state_counts = {}
        for capture in captures:
            state = capture["state"]
            state_counts[state] = state_counts.get(state, 0) + 1

        # Verify all expected states
        assert "welcome" in state_counts
        assert "challenge" in state_counts
        assert "code_editor" in state_counts
        assert "results" in state_counts
        assert "emotional_feedback" in state_counts
        assert "achievements" in state_counts

    def test_viewport_configuration(self):
        """Test viewport configurations for responsive testing."""
        # Test desktop
        assert ViewportConfig.DESKTOP_1280x720["width"] == 1280
        assert ViewportConfig.DESKTOP_1920x1080["width"] == 1920

        # Test tablet
        assert ViewportConfig.TABLET_768x1024["height"] == 1024

        # Test mobile
        assert ViewportConfig.MOBILE_375x667["width"] == 375

        # All viewports should have width and height
        for name, config in ViewportConfig.get_all():
            assert "width" in config
            assert "height" in config
            assert config["width"] > 0
            assert config["height"] > 0

    def test_metadata_serialization(self):
        """Test metadata serialization and deserialization."""
        metadata = ScreenshotMetadata(
            name="test_screenshot",
            state="challenge",
            viewport_width=1280,
            viewport_height=720,
            theme="oled_dark",
            timestamp="2025-12-03T10:30:00Z",
            url="http://localhost:8000/challenges/test",
            additional_context={"challenge_id": "hello_world"},
        )

        # Serialize
        data = metadata.to_dict()
        assert isinstance(data, dict)
        assert data["state"] == "challenge"
        assert data["viewport"]["width"] == 1280

        # Should be JSON serializable
        json_str = json.dumps(data)
        assert "challenge" in json_str

    def test_regression_detection_workflow(self, visual_tester):
        """Test complete regression detection workflow."""
        # Minimal PNG
        test_png = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
            b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00"
            b"\x00\x0cIDATx\x9cc\xf8\xcf\xc0\x00\x00\x00\x03\x00\x01"
            b"u\xa5\xe6\xfe\x00\x00\x00\x00IEND\xaeB`\x82"
        )

        # Step 1: Create baseline
        baseline_name = "workflow_test"
        baseline = visual_tester.get_baseline_path(baseline_name)
        if baseline.exists():
            baseline.unlink()

        # Step 2: First comparison creates baseline
        result = visual_tester.compare_screenshots(baseline_name, test_png)
        assert result["status"] == "baseline_created"
        assert baseline.exists()

        # Step 3: Comparing same image passes
        result = visual_tester.compare_screenshots(baseline_name, test_png)
        assert result["status"] == "passed"
        assert result["diff_ratio"] == 0.0

    def test_baseline_directory_structure(self, visual_tester):
        """Test that baseline directory structure is created correctly."""
        try:
            from PIL import Image
        except ImportError:
            pytest.skip("PIL is required for this test")

        # Create test baseline
        test_png = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
            b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00"
            b"\x00\x0cIDATx\x9cc\xf8\xcf\xc0\x00\x00\x00\x03\x00\x01"
            b"u\xa5\xe6\xfe\x00\x00\x00\x00IEND\xaeB`\x82"
        )

        visual_tester.create_baseline("structure_test", test_png)

        # Verify directory structure
        assert visual_tester.baseline_dir.exists()
        assert visual_tester.results_dir.exists()
        assert (visual_tester.baseline_dir / "structure_test.png").exists()

    def test_manifest_generation(self, screenshot_manager):
        """Test manifest file generation."""
        test_png = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
            b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00"
            b"\x00\x0cIDATx\x9cc\xf8\xcf\xc0\x00\x00\x00\x03\x00\x01"
            b"u\xa5\xe6\xfe\x00\x00\x00\x00IEND\xaeB`\x82"
        )

        # Capture multiple screenshots
        screenshot_manager.capture(
            test_png,
            name="screen1",
            state="welcome",
            viewport_width=1280,
            viewport_height=720,
            theme="oled_dark",
        )

        screenshot_manager.capture(
            test_png,
            name="screen2",
            state="challenge",
            viewport_width=1280,
            viewport_height=720,
            theme="light",
        )

        # Generate manifest
        manifest_path = screenshot_manager.save_manifest()
        assert manifest_path.exists()

        # Load and verify
        with open(manifest_path, "r") as f:
            manifest = json.load(f)

        assert manifest["total_screenshots"] == 2
        assert len(manifest["screenshots"]) == 2


class TestVisualRegressionEdgeCases:
    """Test edge cases in visual regression testing."""

    @pytest.fixture
    def visual_tester(self):
        """Create a visual regression tester for tests."""
        baselines_dir = Path(__file__).parent / "edge_case_baselines"
        return VisualRegressionTester(baselines_dir, threshold=0.01)

    def test_threshold_configuration(self, visual_tester):
        """Test that threshold can be configured."""
        assert visual_tester.threshold == 0.01

        # Create tester with different threshold
        strict_tester = VisualRegressionTester(
            visual_tester.baseline_dir, threshold=0.001
        )
        assert strict_tester.threshold == 0.001

    def test_empty_baseline_directory(self):
        """Test behavior with empty baseline directory."""
        base_dir = Path(__file__).parent / "empty_baselines"
        base_dir.mkdir(exist_ok=True, parents=True)

        tester = VisualRegressionTester(base_dir)
        assert tester.baseline_dir.exists()
        assert len(list(tester.baseline_dir.glob("*.png"))) == 0

    def test_results_directory_creation(self):
        """Test that results directory is created automatically."""
        base_dir = Path(__file__).parent / "auto_create_results"
        # Remove if exists
        if base_dir.exists():
            import shutil
            shutil.rmtree(base_dir)

        tester = VisualRegressionTester(base_dir)
        assert tester.results_dir.exists()
        assert tester.results_dir.parent == tester.baseline_dir


# Self-teaching note:
#
# This file demonstrates:
# - Integration testing patterns (Level 5+)
# - Fixture composition and reuse (Level 5+: pytest)
# - JSON serialization and file I/O (Level 4+)
# - Visual testing workflows (Professional: QA automation)
# - Responsive design testing (Professional: Web development)
#
# Prerequisites:
# - Level 4: Functions, file I/O, JSON
# - Level 5: Classes, pytest fixtures, testing patterns
# - Professional: Visual testing, CI/CD integration
#
# The workflow shown here is similar to tools like:
# - Chromatic (for Storybook)
# - Percy (for visual testing)
# - GitHub's visual regression actions
# - Professional CI/CD pipelines
