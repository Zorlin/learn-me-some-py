"""
Tests for the Introspection System - Phase 5

Tests screenshot capture, wireframe generation, video recording,
mosaic generation, TAS features, and discovery primitives.

Following TDD: Write tests first, then implement.
"""

import pytest
import ast
import json
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
from dataclasses import dataclass

# Note: These imports will fail until we implement the modules
# That's expected in TDD - tests first!


class TestWireframe:
    """Tests for Wireframe - the mental context behind a screenshot."""

    def test_wireframe_from_code_simple(self):
        """Wireframe captures basic code state."""
        from lmsp.introspection.wireframe import Wireframe

        code = "x = 5\nprint(x)"
        wireframe = Wireframe.from_code(code)

        assert wireframe.code == code
        assert wireframe.ast_tree is not None
        assert wireframe.line_count == 2

    def test_wireframe_from_code_with_syntax_error(self):
        """Wireframe handles code with syntax errors gracefully."""
        from lmsp.introspection.wireframe import Wireframe

        code = "def foo(\n  broken"
        wireframe = Wireframe.from_code(code)

        assert wireframe.code == code
        assert wireframe.ast_tree is None
        assert wireframe.parse_error is not None

    def test_wireframe_with_game_state(self):
        """Wireframe includes game state metadata."""
        from lmsp.introspection.wireframe import Wireframe
        from lmsp.game.state import GameState

        state = GameState(
            current_challenge="test_challenge",
            current_code="x = 1",
            tests_passing=3,
            tests_total=5,
            hints_used=1
        )

        wireframe = Wireframe.from_game_state(state)

        assert wireframe.code == "x = 1"
        assert wireframe.challenge_id == "test_challenge"
        assert wireframe.tests_passing == 3
        assert wireframe.tests_total == 5
        assert wireframe.hints_used == 1

    def test_wireframe_to_dict(self):
        """Wireframe serializes to dictionary."""
        from lmsp.introspection.wireframe import Wireframe

        wireframe = Wireframe.from_code("y = 10")
        data = wireframe.to_dict()

        assert data["code"] == "y = 10"
        assert data["line_count"] == 1
        assert "ast_summary" in data

    def test_wireframe_ast_summary(self):
        """Wireframe generates AST summary."""
        from lmsp.introspection.wireframe import Wireframe

        code = """
def greet(name):
    return f"Hello, {name}!"

class Person:
    def __init__(self, name):
        self.name = name
"""
        wireframe = Wireframe.from_code(code)
        summary = wireframe.get_ast_summary()

        assert "functions" in summary
        assert "greet" in summary["functions"]
        assert "classes" in summary
        assert "Person" in summary["classes"]


class TestScreenshot:
    """Tests for Screenshot - visual capture with metadata."""

    def test_screenshot_bundle_creation(self):
        """Screenshot bundle includes image placeholder and wireframe."""
        from lmsp.introspection.screenshot import ScreenshotBundle
        from lmsp.introspection.wireframe import Wireframe
        from lmsp.game.state import GameState

        state = GameState(current_code="test = True")
        bundle = ScreenshotBundle.capture(state)

        assert bundle.wireframe is not None
        assert bundle.wireframe.code == "test = True"
        assert bundle.timestamp is not None

    def test_screenshot_with_player_info(self):
        """Screenshot includes player information."""
        from lmsp.introspection.screenshot import ScreenshotBundle
        from lmsp.game.state import GameState

        state = GameState(current_code="x = 1")
        bundle = ScreenshotBundle.capture(
            state,
            player_id="alice",
            mastery_levels={"lists": 3, "loops": 2}
        )

        assert bundle.player_id == "alice"
        assert bundle.mastery_levels["lists"] == 3

    def test_screenshot_with_emotion(self):
        """Screenshot captures emotional state."""
        from lmsp.introspection.screenshot import ScreenshotBundle
        from lmsp.game.state import GameState
        from lmsp.input.emotional import EmotionalDimension

        state = GameState(current_code="x = 1")
        bundle = ScreenshotBundle.capture(
            state,
            current_emotion={
                "dimension": EmotionalDimension.ENJOYMENT,
                "value": 0.8
            }
        )

        assert bundle.current_emotion["value"] == 0.8

    def test_screenshot_to_json(self):
        """Screenshot serializes to JSON."""
        from lmsp.introspection.screenshot import ScreenshotBundle
        from lmsp.game.state import GameState

        state = GameState(current_code="test = True")
        bundle = ScreenshotBundle.capture(state)
        json_str = bundle.to_json()

        data = json.loads(json_str)
        assert "wireframe" in data
        assert "timestamp" in data


class TestMosaic:
    """Tests for Mosaic - grid of frames for Claude vision."""

    def test_mosaic_from_frames(self):
        """Mosaic composes frames into grid."""
        from lmsp.introspection.mosaic import Mosaic, Frame

        # Create simple mock frames
        frames = [
            Frame(width=100, height=100, data=b"frame1"),
            Frame(width=100, height=100, data=b"frame2"),
            Frame(width=100, height=100, data=b"frame3"),
            Frame(width=100, height=100, data=b"frame4"),
        ]

        mosaic = Mosaic.from_frames(frames, grid=(2, 2))

        assert mosaic.grid == (2, 2)
        assert mosaic.frame_count == 4
        assert mosaic.width == 200  # 2 * 100
        assert mosaic.height == 200  # 2 * 100

    def test_mosaic_select_frames(self):
        """Mosaic selects evenly distributed frames."""
        from lmsp.introspection.mosaic import Mosaic, Frame

        # 16 frames, but we only want 4
        frames = [Frame(width=50, height=50, data=f"frame{i}".encode()) for i in range(16)]

        mosaic = Mosaic.from_frames(frames, grid=(2, 2), select_count=4)

        assert mosaic.frame_count == 4
        # Should select frames 0, 5, 10, 15 (evenly distributed)
        assert mosaic.selected_indices == [0, 5, 10, 15]

    def test_mosaic_metadata(self):
        """Mosaic includes recording metadata."""
        from lmsp.introspection.mosaic import Mosaic, Frame

        frames = [Frame(width=100, height=100, data=b"f") for _ in range(4)]

        mosaic = Mosaic.from_frames(
            frames,
            grid=(2, 2),
            duration=10.0,
            fps=10
        )

        assert mosaic.duration == 10.0
        assert mosaic.fps == 10


class TestVideoRecorder:
    """Tests for Video Recording - strategic capture."""

    def test_recorder_start_stop(self):
        """Recorder starts and stops recording."""
        from lmsp.introspection.video import VideoRecorder

        recorder = VideoRecorder()
        recorder.start()

        assert recorder.is_recording
        assert recorder.start_time is not None

        recorder.stop()
        assert not recorder.is_recording

    def test_recorder_capture_frame(self):
        """Recorder captures frames."""
        from lmsp.introspection.video import VideoRecorder
        from lmsp.game.state import GameState

        recorder = VideoRecorder()
        recorder.start()

        state = GameState(current_code="x = 1")
        recorder.capture_frame(state)
        recorder.capture_frame(GameState(current_code="x = 2"))

        assert len(recorder.frames) == 2

    def test_recorder_to_mosaic(self):
        """Recorder exports to mosaic."""
        from lmsp.introspection.video import VideoRecorder
        from lmsp.game.state import GameState

        recorder = VideoRecorder()
        recorder.start()

        for i in range(16):
            recorder.capture_frame(GameState(current_code=f"x = {i}"))

        mosaic = recorder.to_mosaic(grid=(4, 4))

        assert mosaic.grid == (4, 4)
        assert mosaic.frame_count == 16


class TestTASRecorder:
    """Tests for TAS Recording - Tool-Assisted Learning."""

    def test_tas_record_event(self):
        """TAS records game events."""
        from lmsp.introspection.tas import TASRecorder, TASEvent

        recorder = TASRecorder()
        recorder.start()

        recorder.record(TASEvent(
            event_type="keystroke",
            data={"key": "a"},
            game_state={"code": "a"}
        ))

        assert len(recorder.events) == 1
        assert recorder.events[0].event_type == "keystroke"

    def test_tas_checkpoint(self):
        """TAS saves checkpoints."""
        from lmsp.introspection.tas import TASRecorder, TASEvent
        from lmsp.game.state import GameState

        recorder = TASRecorder()
        recorder.start()

        state = GameState(current_code="x = 1")
        recorder.checkpoint("before_change", state)
        recorder.record(TASEvent(event_type="code_change", data={"code": "x = 2"}, game_state={"code": "x = 2"}))

        assert "before_change" in recorder.checkpoints
        assert recorder.checkpoints["before_change"].current_code == "x = 1"

    def test_tas_rewind_to_checkpoint(self):
        """TAS rewinds to checkpoint."""
        from lmsp.introspection.tas import TASRecorder, TASEvent
        from lmsp.game.state import GameState

        recorder = TASRecorder()
        recorder.start()

        state1 = GameState(current_code="x = 1")
        recorder.checkpoint("start", state1)

        # Simulate events
        for i in range(5):
            recorder.record(TASEvent(event_type="change", data={}, game_state={"code": f"x = {i+2}"}))

        restored = recorder.rewind_to("start")

        assert restored.current_code == "x = 1"

    def test_tas_step_forward(self):
        """TAS steps forward through recording."""
        from lmsp.introspection.tas import TASRecorder, TASEvent

        recorder = TASRecorder()
        recorder.start()

        for i in range(5):
            recorder.record(TASEvent(event_type="change", data={"val": i}, game_state={}))

        recorder.stop()

        # Reset to beginning
        recorder.reset_playback()

        event1 = recorder.step_forward()
        assert event1.data["val"] == 0

        event2 = recorder.step_forward()
        assert event2.data["val"] == 1

    def test_tas_step_backward(self):
        """TAS steps backward through recording."""
        from lmsp.introspection.tas import TASRecorder, TASEvent
        from lmsp.game.state import GameState

        recorder = TASRecorder()
        recorder.start()

        for i in range(5):
            state = GameState(current_code=f"x = {i}")
            recorder.record(TASEvent(event_type="change", data={"val": i}, game_state=state))

        recorder.stop()

        # Go to end
        recorder.playback_index = len(recorder.events)

        prev_state = recorder.step_backward()
        assert prev_state is not None

    def test_tas_diff_checkpoints(self):
        """TAS diffs two checkpoints."""
        from lmsp.introspection.tas import TASRecorder, TASEvent
        from lmsp.game.state import GameState

        recorder = TASRecorder()
        recorder.start()

        state1 = GameState(current_code="x = 1", tests_passing=0)
        recorder.checkpoint("v1", state1)

        state2 = GameState(current_code="x = 1\nprint(x)", tests_passing=2)
        recorder.checkpoint("v2", state2)

        diff = recorder.diff_checkpoints("v1", "v2")

        assert diff["code_changed"] is True
        assert diff["tests_passing_diff"] == 2

    def test_tas_export_recording(self):
        """TAS exports recording to JSON."""
        from lmsp.introspection.tas import TASRecorder, TASEvent

        recorder = TASRecorder()
        recorder.start()

        recorder.record(TASEvent(event_type="test", data={"x": 1}, game_state={}))
        recorder.stop()

        json_str = recorder.export()
        data = json.loads(json_str)

        assert "events" in data
        assert "duration" in data


class TestDiscoveryPrimitives:
    """Tests for Progressive Discovery Primitives."""

    def test_get_primitives_level_0(self):
        """Level 0 players have basic primitives."""
        from lmsp.introspection.primitives import get_available_primitives

        primitives = get_available_primitives(primitive_level=0)

        assert "/help" in primitives
        assert "/screenshot" in primitives
        assert "/checkpoint" not in primitives  # Level 1+

    def test_get_primitives_level_1(self):
        """Level 1 players unlock checkpoint/restore."""
        from lmsp.introspection.primitives import get_available_primitives

        primitives = get_available_primitives(primitive_level=1)

        assert "/help" in primitives
        assert "/checkpoint" in primitives
        assert "/restore" in primitives
        assert "/rewind" not in primitives  # Level 2+

    def test_get_primitives_level_2(self):
        """Level 2 players unlock rewind/step/diff."""
        from lmsp.introspection.primitives import get_available_primitives

        primitives = get_available_primitives(primitive_level=2)

        assert "/rewind" in primitives
        assert "/step" in primitives
        assert "/diff" in primitives
        assert "/video" not in primitives  # Level 3+

    def test_get_primitives_level_3(self):
        """Level 3 players unlock video/mosaic/wireframe."""
        from lmsp.introspection.primitives import get_available_primitives

        primitives = get_available_primitives(primitive_level=3)

        assert "/video" in primitives
        assert "/mosaic" in primitives
        assert "/wireframe" in primitives

    def test_get_primitives_all(self):
        """High level players have all primitives."""
        from lmsp.introspection.primitives import get_available_primitives

        primitives = get_available_primitives(primitive_level=5)

        assert "/help" in primitives
        assert "/checkpoint" in primitives
        assert "/video" in primitives
        assert "/discover" in primitives
        assert "/teach" in primitives

    def test_primitive_info(self):
        """Each primitive has description and usage."""
        from lmsp.introspection.primitives import get_primitive_info

        info = get_primitive_info("/checkpoint")

        assert "description" in info
        assert "usage" in info
        assert "level" in info
        assert info["level"] == 1

    def test_discover_new_primitives(self):
        """Shows newly unlocked primitives."""
        from lmsp.introspection.primitives import get_newly_unlocked

        # Player went from level 0 to level 1
        new_primitives = get_newly_unlocked(old_level=0, new_level=1)

        assert "/checkpoint" in new_primitives
        assert "/restore" in new_primitives
        assert "/help" not in new_primitives  # Already had it


class TestPrimitiveExecution:
    """Tests for executing discovery primitives."""

    def test_execute_help(self):
        """Execute /help shows available commands."""
        from lmsp.introspection.primitives import execute_primitive

        result = execute_primitive("/help", primitive_level=0)

        assert result.success
        assert "/help" in result.output
        assert "/screenshot" in result.output

    def test_execute_screenshot(self):
        """Execute /screenshot captures state."""
        from lmsp.introspection.primitives import execute_primitive
        from lmsp.game.state import GameState

        state = GameState(current_code="x = 1")
        result = execute_primitive("/screenshot", primitive_level=0, game_state=state)

        assert result.success
        assert result.data is not None
        assert "wireframe" in result.data

    def test_execute_checkpoint_save(self):
        """Execute /checkpoint saves state."""
        from lmsp.introspection.primitives import execute_primitive, PrimitiveContext
        from lmsp.game.state import GameState
        from lmsp.introspection.tas import TASRecorder

        recorder = TASRecorder()
        recorder.start()
        state = GameState(current_code="y = 2")

        ctx = PrimitiveContext(
            game_state=state,
            tas_recorder=recorder
        )

        result = execute_primitive("/checkpoint my_save", primitive_level=1, context=ctx)

        assert result.success
        assert "my_save" in recorder.checkpoints

    def test_execute_restore(self):
        """Execute /restore restores checkpoint."""
        from lmsp.introspection.primitives import execute_primitive, PrimitiveContext
        from lmsp.game.state import GameState
        from lmsp.introspection.tas import TASRecorder

        recorder = TASRecorder()
        recorder.start()
        state1 = GameState(current_code="original")
        recorder.checkpoint("backup", state1)

        ctx = PrimitiveContext(
            game_state=GameState(current_code="modified"),
            tas_recorder=recorder
        )

        result = execute_primitive("/restore backup", primitive_level=1, context=ctx)

        assert result.success
        assert result.restored_state.current_code == "original"

    def test_execute_unknown_primitive(self):
        """Execute unknown primitive returns error."""
        from lmsp.introspection.primitives import execute_primitive

        result = execute_primitive("/unknown_command", primitive_level=5)

        assert not result.success
        assert "unknown" in result.error.lower()

    def test_execute_insufficient_level(self):
        """Execute primitive above level returns error."""
        from lmsp.introspection.primitives import execute_primitive

        # /video requires level 3
        result = execute_primitive("/video 10", primitive_level=0)

        assert not result.success
        assert "unlock" in result.error.lower() or "level" in result.error.lower()


class TestIntrospectionModule:
    """Integration tests for the introspection module."""

    def test_module_exports(self):
        """Module exports all main classes."""
        from lmsp.introspection import (
            Wireframe,
            ScreenshotBundle,
            Mosaic,
            VideoRecorder,
            TASRecorder,
            get_available_primitives,
            execute_primitive,
        )

        # Just verify imports work
        assert Wireframe is not None
        assert ScreenshotBundle is not None
        assert Mosaic is not None
        assert VideoRecorder is not None
        assert TASRecorder is not None

    def test_full_workflow(self):
        """Complete introspection workflow."""
        from lmsp.introspection import (
            Wireframe,
            ScreenshotBundle,
            TASRecorder,
            execute_primitive,
            PrimitiveContext,
        )
        from lmsp.game.state import GameState

        # 1. Start a TAS recording session
        recorder = TASRecorder()
        recorder.start()

        # 2. Create initial state and checkpoint
        state = GameState(current_code="# Start")
        recorder.checkpoint("start", state)

        # 3. Take a screenshot
        screenshot = ScreenshotBundle.capture(state, player_id="test")
        assert screenshot.wireframe is not None

        # 4. Simulate some events
        from lmsp.introspection.tas import TASEvent
        recorder.record(TASEvent(event_type="edit", data={"key": "x"}, game_state=state))

        # 5. Create another checkpoint
        state2 = GameState(current_code="x = 1")
        recorder.checkpoint("after_edit", state2)

        # 6. Get diff
        diff = recorder.diff_checkpoints("start", "after_edit")
        assert diff["code_changed"] is True

        # 7. Export recording
        export = recorder.export()
        assert "events" in json.loads(export)


# Self-teaching note:
#
# This file demonstrates:
# - pytest fixtures and test organization (Level 6: testing patterns)
# - Test-Driven Development (TDD) - tests before implementation
# - Mocking with unittest.mock (Level 6: advanced testing)
# - JSON serialization testing (Level 4: data formats)
# - Class-based test organization with pytest
#
# The tests define the expected behavior of the introspection system.
# Implementation will follow to make these tests pass.
