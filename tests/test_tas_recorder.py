"""
Tests for TAS Recorder for Playtest Replay

Tests the enhanced TAS recording system specifically designed for
player-zero integration and playtest analysis.
"""

import pytest
import json
from datetime import datetime
from pathlib import Path

from lmsp.multiplayer.player_zero.tas.recorder import (
    PlaytestRecorder,
    PlaytestEvent,
    PlaytestSession,
    EventType,
    StruggleIndicator,
)


def test_recorder_initializes():
    """Test that recorder initializes with session metadata."""
    recorder = PlaytestRecorder(
        session_name="test_session",
        player_name="test_player",
        challenge_id="hello_world"
    )

    assert recorder.session_name == "test_session"
    assert recorder.player_name == "test_player"
    assert recorder.challenge_id == "hello_world"
    assert len(recorder.events) == 0
    assert not recorder.is_recording


def test_recorder_starts_and_stops():
    """Test recording start/stop lifecycle."""
    recorder = PlaytestRecorder("test", "player1", "challenge1")

    recorder.start_recording()
    assert recorder.is_recording

    recorder.stop_recording()
    assert not recorder.is_recording


def test_recorder_captures_events():
    """Test that recorder captures events with timestamps."""
    recorder = PlaytestRecorder("test", "player1", "challenge1")
    recorder.start_recording()

    # Record some events
    recorder.record_event(
        event_type=EventType.CODE_CHANGE,
        code="print('hello')",
        cursor_position=(0, 13)
    )

    recorder.record_event(
        event_type=EventType.TEST_RUN,
        data={"result": "pass"}
    )

    assert len(recorder.events) == 2
    assert recorder.events[0].event_type == EventType.CODE_CHANGE
    assert recorder.events[0].code == "print('hello')"
    assert recorder.events[1].event_type == EventType.TEST_RUN


def test_recorder_detects_struggles():
    """Test that recorder detects struggle indicators."""
    recorder = PlaytestRecorder("test", "player1", "challenge1")
    recorder.start_recording()

    # Simulate struggle: multiple quick changes in the same line
    for i in range(5):
        recorder.record_event(
            event_type=EventType.CODE_CHANGE,
            code=f"print('attempt_{i}')",
            cursor_position=(0, 15)
        )

    # Simulate struggle: hint usage
    recorder.record_event(
        event_type=EventType.HINT_USED,
        data={"hint_id": "hint_1"}
    )

    # Analyze struggles
    struggles = recorder.analyze_struggles()

    assert len(struggles) > 0
    assert any(s.indicator_type == StruggleIndicator.RAPID_CHANGES for s in struggles)


def test_recorder_saves_to_json():
    """Test that recorder saves session to JSON file."""
    recorder = PlaytestRecorder("test", "player1", "challenge1")
    recorder.start_recording()

    recorder.record_event(
        event_type=EventType.CODE_CHANGE,
        code="x = 1"
    )

    recorder.stop_recording()

    # Save to temporary file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        output_path = Path(f.name)

    try:
        recorder.save_to_json(output_path)

        # Verify file exists and is valid JSON
        assert output_path.exists()

        with open(output_path, 'r') as f:
            data = json.load(f)

        assert data['session_name'] == "test"
        assert data['player_name'] == "player1"
        assert data['challenge_id'] == "challenge1"
        assert len(data['events']) == 1
        assert data['events'][0]['event_type'] == EventType.CODE_CHANGE.value

    finally:
        # Clean up
        if output_path.exists():
            output_path.unlink()


def test_recorder_loads_from_json():
    """Test that recorder can load and replay from JSON file."""
    # Create and save a session
    recorder1 = PlaytestRecorder("test", "player1", "challenge1")
    recorder1.start_recording()
    recorder1.record_event(EventType.CODE_CHANGE, code="x = 1")
    recorder1.record_event(EventType.TEST_RUN, data={"result": "pass"})
    recorder1.stop_recording()

    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        output_path = Path(f.name)

    try:
        recorder1.save_to_json(output_path)

        # Load in a new recorder
        recorder2 = PlaytestRecorder.load_from_json(output_path)

        assert recorder2.session_name == "test"
        assert recorder2.player_name == "player1"
        assert len(recorder2.events) == 2
        assert recorder2.events[0].code == "x = 1"

    finally:
        if output_path.exists():
            output_path.unlink()


def test_recorder_tracks_timing():
    """Test that recorder tracks timing between events."""
    recorder = PlaytestRecorder("test", "player1", "challenge1")
    recorder.start_recording()

    import time

    recorder.record_event(EventType.CODE_CHANGE, code="x = 1")
    time.sleep(0.1)  # 100ms delay
    recorder.record_event(EventType.CODE_CHANGE, code="x = 2")

    # Second event should have duration_ms > 0
    assert recorder.events[1].duration_ms >= 100


def test_recorder_generates_playback_report():
    """Test that recorder generates human-readable playback report."""
    recorder = PlaytestRecorder("test", "player1", "challenge1")
    recorder.start_recording()

    recorder.record_event(EventType.CODE_CHANGE, code="print('hello')")
    recorder.record_event(EventType.TEST_RUN, data={"result": "fail"})
    recorder.record_event(EventType.CODE_CHANGE, code="print('hello world')")
    recorder.record_event(EventType.TEST_RUN, data={"result": "pass"})

    recorder.stop_recording()

    report = recorder.generate_report()

    assert "test" in report
    assert "player1" in report
    assert "challenge1" in report
    assert "4" in report  # Event count


def test_recorder_identifies_ux_issues():
    """Test that recorder identifies potential UX issues."""
    recorder = PlaytestRecorder("test", "player1", "challenge1")
    recorder.start_recording()

    # Simulate confusion: back and forth between different approaches
    recorder.record_event(EventType.CODE_CHANGE, code="def foo():\n    pass")
    recorder.record_event(EventType.CODE_CHANGE, code="def bar():\n    pass")
    recorder.record_event(EventType.CODE_CHANGE, code="def foo():\n    return 1")
    recorder.record_event(EventType.CODE_CHANGE, code="def bar():\n    return 2")

    # Simulate multiple test failures
    for i in range(5):
        recorder.record_event(EventType.TEST_FAIL, data={"error": f"Error {i}"})

    recorder.stop_recording()

    ux_issues = recorder.identify_ux_issues()

    assert len(ux_issues) > 0
    # Should detect high test failure rate or confusion patterns


def test_playtest_event_serialization():
    """Test PlaytestEvent to_dict and from_dict."""
    event = PlaytestEvent(
        event_type=EventType.CODE_CHANGE,
        timestamp=datetime.now(),
        frame_number=42,
        code="x = 1",
        cursor_position=(5, 10),
        data={"extra": "info"},
        duration_ms=150.0
    )

    # Serialize
    event_dict = event.to_dict()
    assert event_dict['event_type'] == EventType.CODE_CHANGE.value
    assert event_dict['frame_number'] == 42
    assert event_dict['code'] == "x = 1"

    # Deserialize
    event2 = PlaytestEvent.from_dict(event_dict)
    assert event2.event_type == EventType.CODE_CHANGE
    assert event2.frame_number == 42
    assert event2.code == "x = 1"


# Self-teaching note:
#
# This test file demonstrates:
# - Test-driven development (Level 6: TDD methodology)
# - Testing file I/O and JSON serialization (Level 4-5)
# - Testing complex state machines (Level 5-6)
# - Mock data generation for testing (Level 5)
# - Assertions and test organization (Level 3+)
#
# These tests define the expected behavior of the TAS recorder BEFORE
# the implementation exists. This is TDD (Test-Driven Development).
#
# Prerequisites:
# - Level 4: File I/O, JSON, collections
# - Level 5: Dataclasses, testing patterns
# - Level 6: Complex state management, analysis algorithms
