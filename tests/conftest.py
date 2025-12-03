"""
Pytest Configuration for LMSP Web UI Testing
==============================================

Configures pytest for multi-browser Playwright testing across:
- Chromium (Chrome/Edge)
- Firefox
- WebKit (Safari)

Features:
- Server lifecycle management
- Multi-browser fixtures
- Screenshot capture on failure
- Customizable viewport sizes
- Test markers for browser-specific tests

Usage:
    # Run all tests
    pytest tests/ -v

    # Run only Chromium tests
    pytest tests/test_web_playwright.py -m chromium -v

    # Run only visual regression tests
    pytest tests/test_visual_regression.py -v

    # Run with screenshots on failure
    pytest tests/ -v --screenshot-on-failure
"""

import pytest
import subprocess
import time
import signal
import os
import sys
from pathlib import Path
from typing import Generator
import tempfile


# ========== Browser Configuration ==========

BROWSER_CONFIGS = {
    "chromium": {
        "name": "Chromium",
        "launch_args": {
            "args": ["--disable-blink-features=AutomationControlled"],
            "headless": True,
        },
    },
    "firefox": {
        "name": "Firefox",
        "launch_args": {
            "args": [],
            "headless": True,
        },
    },
    "webkit": {
        "name": "WebKit",
        "launch_args": {
            "args": [],
            "headless": True,
        },
    },
}

# Viewport configurations for responsive testing
VIEWPORTS = {
    "desktop": {"width": 1280, "height": 720},
    "laptop": {"width": 1920, "height": 1080},
    "tablet": {"width": 768, "height": 1024},
    "mobile": {"width": 375, "height": 667},
}


# ========== Web Server Management ==========

class WebServerManager:
    """Manages FastAPI web server lifecycle."""

    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.process = None
        self.url = f"http://{host}:{port}"

    def start(self) -> str:
        """Start the FastAPI server."""
        try:
            # Try to find uvicorn
            self.process = subprocess.Popen(
                [
                    "uvicorn",
                    "lmsp.web.app:app",
                    "--host", self.host,
                    "--port", str(self.port),
                    "--log-level", "warning",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid if sys.platform != "win32" else None,
                cwd=Path(__file__).parent.parent,
            )
            # Wait for server to start
            time.sleep(2)
            return self.url
        except Exception as e:
            raise RuntimeError(f"Failed to start web server: {e}")

    def stop(self):
        """Stop the FastAPI server."""
        if self.process:
            try:
                if sys.platform != "win32":
                    os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                else:
                    self.process.terminate()
                self.process.wait(timeout=5)
            except Exception as e:
                print(f"Warning: Failed to stop server cleanly: {e}")
            finally:
                self.process = None

    def is_alive(self) -> bool:
        """Check if server is still running."""
        return self.process is not None and self.process.poll() is None


# ========== Pytest Fixtures ==========


@pytest.fixture(scope="session")
def web_server() -> Generator[str, None, None]:
    """Session-scoped fixture: Start web server for all tests."""
    manager = WebServerManager()
    url = manager.start()
    print(f"\nWeb server started at {url}")
    yield url
    manager.stop()
    print(f"Web server stopped")


@pytest.fixture
def browser_url(web_server) -> str:
    """Fixture: Get the base URL for the test web server."""
    return web_server


@pytest.fixture(params=["chromium", "firefox", "webkit"])
def browser_type(request) -> str:
    """Parametrized fixture: Test across all three browsers."""
    return request.param


@pytest.fixture(params=list(VIEWPORTS.keys()))
def viewport(request) -> dict:
    """Parametrized fixture: Test across multiple viewport sizes."""
    return VIEWPORTS[request.param]


@pytest.fixture
def viewport_desktop() -> dict:
    """Fixture: Desktop viewport (1280x720)."""
    return VIEWPORTS["desktop"]


@pytest.fixture
def viewport_mobile() -> dict:
    """Fixture: Mobile viewport (375x667)."""
    return VIEWPORTS["mobile"]


@pytest.fixture
def viewport_tablet() -> dict:
    """Fixture: Tablet viewport (768x1024)."""
    return VIEWPORTS["tablet"]


@pytest.fixture
def temp_screenshots_dir() -> Generator[Path, None, None]:
    """Fixture: Temporary directory for test screenshots."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


# ========== Pytest Configuration ==========


def pytest_addoption(parser):
    """Add custom command-line options."""
    parser.addoption(
        "--screenshot-on-failure",
        action="store_true",
        default=False,
        help="Capture screenshots when tests fail",
    )
    parser.addoption(
        "--browsers",
        action="store",
        default="chromium,firefox,webkit",
        help="Comma-separated list of browsers to test (chromium,firefox,webkit)",
    )
    parser.addoption(
        "--viewport",
        action="store",
        default="desktop",
        help="Viewport size for tests (desktop,mobile,tablet,laptop)",
    )
    parser.addoption(
        "--create-baselines",
        action="store_true",
        default=False,
        help="Create baseline images for visual regression tests",
    )


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "chromium: mark test to run only on Chromium"
    )
    config.addinivalue_line(
        "markers", "firefox: mark test to run only on Firefox"
    )
    config.addinivalue_line(
        "markers", "webkit: mark test to run only on WebKit"
    )
    config.addinivalue_line(
        "markers", "desktop: mark test to run only on desktop viewport"
    )
    config.addinivalue_line(
        "markers", "mobile: mark test to run only on mobile viewport"
    )
    config.addinivalue_line(
        "markers", "responsive: mark test as responsive design test"
    )
    config.addinivalue_line(
        "markers", "visual: mark test as visual regression test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "playtest: mark test as AI playtest integration test"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection based on markers and options."""
    # Skip browser-specific tests based on --browsers option
    browsers = config.getoption("--browsers", "chromium,firefox,webkit")
    browser_list = set(b.strip() for b in browsers.split(","))

    for item in items:
        # Skip if marker doesn't match selected browsers
        if item.get_closest_marker("chromium") and "chromium" not in browser_list:
            item.add_marker(pytest.mark.skip(reason="chromium not selected"))
        if item.get_closest_marker("firefox") and "firefox" not in browser_list:
            item.add_marker(pytest.mark.skip(reason="firefox not selected"))
        if item.get_closest_marker("webkit") and "webkit" not in browser_list:
            item.add_marker(pytest.mark.skip(reason="webkit not selected"))


# ========== Test Helpers ==========


def get_browser_config(browser_name: str) -> dict:
    """Get launch configuration for a browser."""
    return BROWSER_CONFIGS.get(browser_name, {})


def get_viewport_config(viewport_name: str) -> dict:
    """Get viewport configuration by name."""
    return VIEWPORTS.get(viewport_name, VIEWPORTS["desktop"])


class BrowserEnvironment:
    """Helper class for browser testing environment."""

    def __init__(self, browser_type: str, viewport: dict):
        """Initialize browser environment."""
        self.browser_type = browser_type
        self.viewport = viewport
        self.config = get_browser_config(browser_type)

    def get_launch_args(self) -> dict:
        """Get launch arguments for this browser."""
        return self.config.get("launch_args", {})

    def get_viewport_str(self) -> str:
        """Get viewport as formatted string."""
        return f"{self.viewport['width']}x{self.viewport['height']}"

    def get_display_name(self) -> str:
        """Get display name for this environment."""
        browser_name = self.config.get("name", self.browser_type)
        viewport_str = self.get_viewport_str()
        return f"{browser_name} {viewport_str}"


# ========== Session Fixtures ==========


@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """Get the path to test data directory."""
    return Path(__file__).parent / "test_data"


@pytest.fixture(scope="session")
def screenshots_baseline_dir() -> Path:
    """Get the path to baseline screenshots directory."""
    return Path(__file__).parent / "visual_baselines"


@pytest.fixture(scope="session")
def screenshots_results_dir() -> Path:
    """Get the path to results screenshots directory."""
    return Path(__file__).parent / "visual_baselines" / "results"


# ========== Request Fixtures ==========


@pytest.fixture
def web_server_url(web_server) -> str:
    """Get web server URL for this test."""
    return web_server
