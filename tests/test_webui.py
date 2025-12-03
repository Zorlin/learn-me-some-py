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
