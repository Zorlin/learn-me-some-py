"""
Tests for Stream-JSON Protocol

Tests the multi-agent awareness protocol for broadcasting events between players.
This enables multiplayer modes like coop, race, teach, and swarm.

Events include:
- Keystrokes
- Test results
- Emotional feedback
- Player thoughts/suggestions
- Completion status

"""

import pytest
import json
from unittest.mock import Mock, MagicMock, patch
from io import StringIO

from lmsp.multiplayer.stream.json import (
    StreamJSON,
    EventType,
    StreamEvent,
    EventBroadcaster,
)


class TestEventType:
    """Test EventType enumeration."""

    def test_event_types_defined(self):
        """Should have all required event types."""
        assert EventType.CURSOR_MOVE is not None
        assert EventType.KEYSTROKE is not None
        assert EventType.THOUGHT is not None
        assert EventType.SUGGESTION is not None
        assert EventType.EMOTION is not None
        assert EventType.TEST_RESULT is not None
        assert EventType.PLAYER_COMPLETE is not None
        assert EventType.CODE_UPDATE is not None

    def test_event_type_values(self):
        """Should have string values matching ULTRASPEC."""
        assert EventType.CURSOR_MOVE.value == "cursor_move"
        assert EventType.KEYSTROKE.value == "keystroke"
        assert EventType.THOUGHT.value == "thought"
        assert EventType.SUGGESTION.value == "suggestion"
        assert EventType.EMOTION.value == "emotion"
        assert EventType.TEST_RESULT.value == "test_result"
        assert EventType.PLAYER_COMPLETE.value == "player_complete"


class TestStreamEvent:
    """Test StreamEvent dataclass."""

    def test_create_keystroke_event(self):
        """Should create a keystroke event."""
        event = StreamEvent(
            type=EventType.KEYSTROKE,
            player="Wings",
            data={"char": "d"}
        )

        assert event.type == EventType.KEYSTROKE
        assert event.player == "Wings"
        assert event.data["char"] == "d"
        assert event.timestamp > 0

    def test_create_emotion_event(self):
        """Should create an emotion event."""
        event = StreamEvent(
            type=EventType.EMOTION,
            player="Wings",
            data={"dimension": "enjoyment", "value": 0.8}
        )

        assert event.type == EventType.EMOTION
        assert event.data["dimension"] == "enjoyment"
        assert event.data["value"] == 0.8

    def test_create_test_result_event(self):
        """Should create a test result event."""
        event = StreamEvent(
            type=EventType.TEST_RESULT,
            player="Wings",
            data={"passed": 3, "total": 5}
        )

        assert event.type == EventType.TEST_RESULT
        assert event.data["passed"] == 3
        assert event.data["total"] == 5

    def test_create_completion_event(self):
        """Should create a player completion event."""
        event = StreamEvent(
            type=EventType.PLAYER_COMPLETE,
            player="Lief",
            data={"time_seconds": 145}
        )

        assert event.type == EventType.PLAYER_COMPLETE
        assert event.data["time_seconds"] == 145

    def test_to_json(self):
        """Should serialize event to JSON string."""
        event = StreamEvent(
            type=EventType.KEYSTROKE,
            player="Wings",
            data={"char": "x"}
        )

        json_str = event.to_json()
        parsed = json.loads(json_str)

        assert parsed["type"] == "keystroke"
        assert parsed["player"] == "Wings"
        assert parsed["char"] == "x"

    def test_from_json(self):
        """Should deserialize event from JSON string."""
        json_str = '{"type": "thought", "player": "Lief", "content": "Defining a function!"}'

        event = StreamEvent.from_json(json_str)

        assert event.type == EventType.THOUGHT
        assert event.player == "Lief"
        assert event.data["content"] == "Defining a function!"

    def test_from_json_preserves_extra_fields(self):
        """Should preserve extra fields from JSON."""
        json_str = '{"type": "emotion", "player": "Wings", "dimension": "enjoyment", "value": 0.8, "context": "lists"}'

        event = StreamEvent.from_json(json_str)

        assert event.data["dimension"] == "enjoyment"
        assert event.data["value"] == 0.8
        assert event.data["context"] == "lists"


class TestStreamJSON:
    """Test the StreamJSON protocol handler."""

    def test_create_stream(self):
        """Should create a StreamJSON instance."""
        stream = StreamJSON(player_id="Wings")

        assert stream.player_id == "Wings"
        assert stream is not None

    def test_emit_event(self):
        """Should emit events to registered listeners."""
        stream = StreamJSON(player_id="Wings")
        received = []

        stream.subscribe(lambda e: received.append(e))

        stream.emit(EventType.KEYSTROKE, {"char": "d"})

        assert len(received) == 1
        assert received[0].type == EventType.KEYSTROKE
        assert received[0].player == "Wings"

    def test_multiple_subscribers(self):
        """Should broadcast to multiple subscribers."""
        stream = StreamJSON(player_id="Wings")
        received_1 = []
        received_2 = []

        stream.subscribe(lambda e: received_1.append(e))
        stream.subscribe(lambda e: received_2.append(e))

        stream.emit(EventType.TEST_RESULT, {"passed": 1, "total": 3})

        assert len(received_1) == 1
        assert len(received_2) == 1

    def test_unsubscribe(self):
        """Should allow unsubscribing from events."""
        stream = StreamJSON(player_id="Wings")
        received = []

        handler = lambda e: received.append(e)
        stream.subscribe(handler)
        stream.emit(EventType.KEYSTROKE, {"char": "a"})

        stream.unsubscribe(handler)
        stream.emit(EventType.KEYSTROKE, {"char": "b"})

        assert len(received) == 1

    def test_receive_event_from_json(self):
        """Should receive and process JSON events from other players."""
        stream = StreamJSON(player_id="Wings")
        received = []

        stream.subscribe(lambda e: received.append(e))

        # Simulate receiving event from another player
        json_line = '{"type": "keystroke", "player": "Lief", "char": "f"}'
        stream.receive(json_line)

        assert len(received) == 1
        assert received[0].player == "Lief"

    def test_emit_cursor_move(self):
        """Should emit cursor move events."""
        stream = StreamJSON(player_id="Wings")
        received = []

        stream.subscribe(lambda e: received.append(e))
        stream.emit_cursor_move(line=5, col=12)

        assert len(received) == 1
        assert received[0].type == EventType.CURSOR_MOVE
        assert received[0].data["line"] == 5
        assert received[0].data["col"] == 12

    def test_emit_keystroke(self):
        """Should emit keystroke events."""
        stream = StreamJSON(player_id="Wings")
        received = []

        stream.subscribe(lambda e: received.append(e))
        stream.emit_keystroke(char="d")

        assert len(received) == 1
        assert received[0].type == EventType.KEYSTROKE
        assert received[0].data["char"] == "d"

    def test_emit_thought(self):
        """Should emit thought events."""
        stream = StreamJSON(player_id="Lief")
        received = []

        stream.subscribe(lambda e: received.append(e))
        stream.emit_thought("Defining a function!")

        assert len(received) == 1
        assert received[0].type == EventType.THOUGHT
        assert received[0].data["content"] == "Defining a function!"

    def test_emit_suggestion(self):
        """Should emit suggestion events."""
        stream = StreamJSON(player_id="Lief")
        received = []

        stream.subscribe(lambda e: received.append(e))
        stream.emit_suggestion("Don't forget the colon")

        assert len(received) == 1
        assert received[0].type == EventType.SUGGESTION
        assert received[0].data["content"] == "Don't forget the colon"

    def test_emit_emotion(self):
        """Should emit emotion events."""
        stream = StreamJSON(player_id="Wings")
        received = []

        stream.subscribe(lambda e: received.append(e))
        stream.emit_emotion("enjoyment", 0.8)

        assert len(received) == 1
        assert received[0].type == EventType.EMOTION
        assert received[0].data["dimension"] == "enjoyment"
        assert received[0].data["value"] == 0.8

    def test_emit_test_result(self):
        """Should emit test result events."""
        stream = StreamJSON(player_id="Wings")
        received = []

        stream.subscribe(lambda e: received.append(e))
        stream.emit_test_result(passed=3, total=5)

        assert len(received) == 1
        assert received[0].type == EventType.TEST_RESULT
        assert received[0].data["passed"] == 3
        assert received[0].data["total"] == 5

    def test_emit_completion(self):
        """Should emit player completion events."""
        stream = StreamJSON(player_id="Lief")
        received = []

        stream.subscribe(lambda e: received.append(e))
        stream.emit_completion(time_seconds=145)

        assert len(received) == 1
        assert received[0].type == EventType.PLAYER_COMPLETE
        assert received[0].data["time_seconds"] == 145


class TestEventBroadcaster:
    """Test the EventBroadcaster for multi-player forwarding."""

    def test_create_broadcaster(self):
        """Should create a broadcaster with multiple players."""
        broadcaster = EventBroadcaster()

        assert broadcaster is not None
        assert len(broadcaster.players) == 0

    def test_register_player(self):
        """Should register a player with their process."""
        broadcaster = EventBroadcaster()

        mock_process = Mock()
        mock_process.stdin = Mock()
        mock_process.stdin.write = Mock()
        mock_process.stdin.flush = Mock()

        broadcaster.register_player("Wings", mock_process)

        assert "Wings" in broadcaster.players

    def test_forward_to_other_players(self):
        """Should forward events to other players, not the source."""
        broadcaster = EventBroadcaster()

        # Mock processes with stdin
        mock_lief = Mock()
        mock_lief.stdin = StringIO()
        mock_claude = Mock()
        mock_claude.stdin = StringIO()

        broadcaster.register_player("Wings", None)  # Source, no process
        broadcaster.register_player("Lief", mock_lief)
        broadcaster.register_player("Claude", mock_claude)

        event = StreamEvent(
            type=EventType.KEYSTROKE,
            player="Wings",
            data={"char": "x"}
        )

        broadcaster.forward(event)

        # Lief and Claude should receive, but Wings should not
        # (Check that data was written to their stdin)
        mock_lief.stdin.seek(0)
        mock_claude.stdin.seek(0)

        lief_received = mock_lief.stdin.read()
        claude_received = mock_claude.stdin.read()

        assert len(lief_received) > 0
        assert len(claude_received) > 0

    def test_mark_player_done(self):
        """Should mark player as done and stop forwarding to them."""
        broadcaster = EventBroadcaster()

        mock_process = Mock()
        mock_process.stdin = Mock()
        mock_process.stdin.write = Mock()

        broadcaster.register_player("Wings", mock_process)
        broadcaster.mark_done("Wings")

        event = StreamEvent(
            type=EventType.KEYSTROKE,
            player="Lief",
            data={"char": "y"}
        )

        broadcaster.forward(event)

        # Wings is done, so nothing should be written
        mock_process.stdin.write.assert_not_called()

    def test_handle_broken_pipe(self):
        """Should handle broken pipe gracefully."""
        broadcaster = EventBroadcaster()

        mock_process = Mock()
        mock_process.stdin = Mock()
        mock_process.stdin.write = Mock(side_effect=BrokenPipeError())
        mock_process.stdin.flush = Mock()

        broadcaster.register_player("Wings", mock_process)

        event = StreamEvent(
            type=EventType.KEYSTROKE,
            player="Lief",
            data={"char": "z"}
        )

        # Should not raise exception
        broadcaster.forward(event)


class TestStreamJSONIntegration:
    """Integration tests for Stream-JSON protocol."""

    def test_full_event_cycle(self):
        """Test emitting and receiving events in a cycle."""
        wings_stream = StreamJSON(player_id="Wings")
        lief_stream = StreamJSON(player_id="Lief")

        wings_received = []
        lief_received = []

        wings_stream.subscribe(lambda e: wings_received.append(e))
        lief_stream.subscribe(lambda e: lief_received.append(e))

        # Wings emits, Lief receives
        event = wings_stream.emit(EventType.KEYSTROKE, {"char": "p"})
        lief_stream.receive(event.to_json())

        assert len(lief_received) == 1
        assert lief_received[0].player == "Wings"
        assert lief_received[0].data["char"] == "p"

    def test_event_chaining(self):
        """Test multiple events in sequence."""
        stream = StreamJSON(player_id="Wings")
        events = []

        stream.subscribe(lambda e: events.append(e))

        stream.emit_keystroke("d")
        stream.emit_keystroke("e")
        stream.emit_keystroke("f")

        assert len(events) == 3
        assert events[0].data["char"] == "d"
        assert events[1].data["char"] == "e"
        assert events[2].data["char"] == "f"

    def test_awareness_tracker_integration(self):
        """Test integration with AwarenessTracker."""
        from lmsp.multiplayer.awareness import AwarenessTracker

        stream = StreamJSON(player_id="Wings")
        tracker = AwarenessTracker()

        # Connect stream to tracker
        stream.subscribe(lambda e: tracker.update(e.to_dict()))

        # Emit events
        stream.emit_keystroke("h")
        stream.emit_emotion("enjoyment", 0.9)

        # Tracker should have received and processed
        player = tracker.get_player_state("Wings")
        assert player is not None
        assert player.emotion.get("enjoyment") == 0.9


# Self-teaching note:
#
# This file demonstrates:
# - Test-Driven Development (TDD) - writing tests FIRST
# - Dataclass testing (Level 5)
# - JSON serialization/deserialization (Level 4)
# - Event-driven architecture testing (Level 6)
# - Mock objects for process communication (Level 6)
# - Integration testing (Level 6+)
#
# The Stream-JSON protocol is the foundation for multiplayer awareness.
# Events flow between players via JSON lines over stdin/stdout:
#
#   Player A  --emit-->  {"type": "keystroke", "player": "A", "char": "x"}
#                  |
#   Player B  <--receive--
#
# This enables coop, race, teach, and swarm multiplayer modes!
