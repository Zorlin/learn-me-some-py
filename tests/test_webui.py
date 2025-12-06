"""
Tests for WebUI (FastAPI + HTMX)

Tests the web interface for LMSP, including:
- Server startup and routes
- HTMX interactions
- Gamepad API integration
- Theme switching
- Challenge rendering
"""

import pytest
from fastapi.testclient import TestClient


def test_webui_imports():
    """Test that webui module can be imported."""
    try:
        from lmsp.web import app
        assert app is not None
    except ImportError as e:
        pytest.skip(f"WebUI dependencies not installed: {e}")


def test_index_page():
    """Test the index page loads and contains expected elements."""
    from lmsp.web import app

    client = TestClient(app.app)
    response = client.get("/")

    assert response.status_code == 200
    assert b"LMSP" in response.content
    assert b"Learn Me Some Py" in response.content


def test_theme_dark_default():
    """Test that dark theme is loaded by default."""
    from lmsp.web import app

    client = TestClient(app.app)
    response = client.get("/")

    # Should contain OLED black background
    assert b"#000000" in response.content or b"background: black" in response.content


def test_gamepad_api_script():
    """Test that gamepad API script is included."""
    from lmsp.web import app

    client = TestClient(app.app)
    response = client.get("/")

    # Check for gamepad detection
    assert b"navigator.getGamepads" in response.content or b"gamepad" in response.content.lower()


def test_htmx_library_included():
    """Test that HTMX library is loaded."""
    from lmsp.web import app

    client = TestClient(app.app)
    response = client.get("/")

    # Check for HTMX
    assert b"htmx" in response.content.lower()


def test_challenge_list_endpoint():
    """Test the challenge list API endpoint."""
    from lmsp.web import app

    client = TestClient(app.app)
    response = client.get("/api/challenges")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_challenge_detail_endpoint():
    """Test the challenge detail endpoint."""
    from lmsp.web import app

    client = TestClient(app.app)

    # First get available challenges
    list_response = client.get("/api/challenges")
    challenges = list_response.json()

    if len(challenges) > 0:
        challenge_id = challenges[0]["id"]
        response = client.get(f"/api/challenge/{challenge_id}")
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "name" in data


def test_code_submit_endpoint():
    """Test code submission endpoint."""
    from lmsp.web import app

    client = TestClient(app.app)
    response = client.post(
        "/api/submit",
        json={
            "challenge_id": "test_challenge",
            "code": "print('hello')"
        }
    )

    # Should return validation results or error
    assert response.status_code in [200, 400, 404]


def test_theme_switch_endpoint():
    """Test theme switching endpoint."""
    from lmsp.web import app

    client = TestClient(app.app)
    response = client.post(
        "/api/theme",
        json={"theme": "light"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["theme"] in ["light", "dark"]


def test_static_assets():
    """Test that static assets are served."""
    from lmsp.web import app

    client = TestClient(app.app)

    # Test CSS
    response = client.get("/static/style.css")
    assert response.status_code == 200

    # Test JS
    response = client.get("/static/gamepad.js")
    assert response.status_code == 200


def test_responsive_design_meta():
    """Test that responsive design meta tags are present."""
    from lmsp.web import app

    client = TestClient(app.app)
    response = client.get("/")

    assert b"viewport" in response.content
    assert b"width=device-width" in response.content


def test_accessibility_features():
    """Test accessibility features are present."""
    from lmsp.web import app

    client = TestClient(app.app)
    response = client.get("/")

    # Check for semantic HTML and ARIA labels
    assert b"role=" in response.content or b"aria-" in response.content
    assert b"alt=" in response.content or b"<main" in response.content


def test_error_handling():
    """Test that error pages are handled gracefully."""
    from lmsp.web import app

    client = TestClient(app.app)

    # 404 page
    response = client.get("/nonexistent-page")
    assert response.status_code == 404

    # Invalid challenge ID
    response = client.get("/api/challenge/invalid_id_that_does_not_exist")
    assert response.status_code in [404, 400]


def test_websocket_endpoint():
    """Test WebSocket endpoint for real-time updates."""
    from lmsp.web import app

    client = TestClient(app.app)

    # Test websocket connection
    with client.websocket_connect("/ws") as websocket:
        # Should be able to connect
        data = websocket.receive_json()
        assert "type" in data

        # Send a message
        websocket.send_json({"type": "ping"})
        response = websocket.receive_json()
        assert response["type"] in ["pong", "message"]


@pytest.mark.parametrize("route", [
    "/",
    "/challenges",
    "/progress",
    "/settings",
])
def test_all_pages_load(route):
    """Test that all main pages load successfully."""
    from lmsp.web import app

    client = TestClient(app.app)
    response = client.get(route)

    assert response.status_code == 200
    assert len(response.content) > 0


class TestStdoutCapture:
    """Tests for capturing player's print() output."""

    def test_capture_player_stdout_function(self):
        """Test the capture_player_stdout helper function."""
        from lmsp.web.app import capture_player_stdout

        # Simple print
        stdout = capture_player_stdout('print("Hello, World!")')
        assert stdout.strip() == "Hello, World!"

    def test_capture_multiple_prints(self):
        """Test capturing multiple print statements."""
        from lmsp.web.app import capture_player_stdout

        code = '''
print("Line 1")
print("Line 2")
print("Line 3")
'''
        stdout = capture_player_stdout(code)
        lines = stdout.strip().split('\n')
        assert len(lines) == 3
        assert lines[0] == "Line 1"
        assert lines[1] == "Line 2"
        assert lines[2] == "Line 3"

    def test_capture_empty_output(self):
        """Test code with no print statements."""
        from lmsp.web.app import capture_player_stdout

        stdout = capture_player_stdout('x = 1 + 1')
        assert stdout == ""

    def test_capture_handles_errors(self):
        """Test that errors don't crash the capture."""
        from lmsp.web.app import capture_player_stdout

        # Code with an error - should not raise exception
        stdout = capture_player_stdout('raise ValueError("oops")')
        # Should return something (either empty or error message)
        assert isinstance(stdout, str)

    def test_code_submit_returns_stdout(self):
        """Test that code submission endpoint returns stdout field."""
        from lmsp.web.app import app

        client = TestClient(app)

        # Submit code with print to a known challenge
        list_response = client.get("/api/challenges")
        challenges = list_response.json()

        if len(challenges) > 0:
            challenge_id = challenges[0]["id"]
            response = client.post(
                "/api/code/submit",
                json={
                    "challenge_id": challenge_id,
                    "code": 'print("test output")\ndef solution():\n    return 42',
                    "player_id": "test_player"
                }
            )

            if response.status_code == 200:
                data = response.json()
                assert "stdout" in data
                # stdout should contain our print output
                assert "test output" in data.get("stdout", "")


# Self-teaching note:
#
# This file demonstrates:
# - Testing web applications with TestClient (Level 5+)
# - Parametrized tests with pytest (Level 4+)
# - HTTP endpoint testing (Level 5+)
# - WebSocket testing (Level 6+)
# - Accessibility and responsive design testing (Professional)
#
# Prerequisites:
# - Level 4: Functions, testing basics
# - Level 5: Classes, HTTP concepts
# - Level 6: Web frameworks, real-time communication
#
# These tests ensure the WebUI works correctly and feels good to use.
