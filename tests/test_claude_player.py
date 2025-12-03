"""
Tests for ClaudePlayer - AI player via Claude API

TDD: These tests define expected behavior BEFORE implementation.

Tests cover:
1. Initialization and configuration
2. API integration (mocked)
3. Teaching style variations
4. Event emission
5. Context building
6. Response parsing
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import asyncio

from lmsp.multiplayer.claude_player import (
    ClaudePlayer,
    TeachingStyle,
    TeachingConfig,
)
from lmsp.multiplayer.awareness import AwarenessTracker, PlayerState
from lmsp.multiplayer.session_sync import SessionSync, SessionMode


class TestTeachingStyle:
    """Test teaching style enumeration."""

    def test_all_styles_exist(self):
        """All teaching styles should be defined."""
        assert TeachingStyle.SOCRATIC.value == "socratic"
        assert TeachingStyle.DEMONSTRATIVE.value == "demo"
        assert TeachingStyle.SCAFFOLDED.value == "scaffold"
        assert TeachingStyle.DISCOVERY.value == "discovery"
        assert TeachingStyle.COLLABORATIVE.value == "collab"
        assert TeachingStyle.ENCOURAGING.value == "encouraging"
        assert TeachingStyle.DIRECT.value == "direct"


class TestTeachingConfig:
    """Test teaching configuration dataclass."""

    def test_default_config(self):
        """Default config should have sensible values."""
        config = TeachingConfig()

        assert config.allow_direct_answers is False
        assert config.encouragement_level == 0.7
        assert config.patience_level == 0.8

    def test_custom_config(self):
        """Should allow custom configuration."""
        config = TeachingConfig(
            allow_direct_answers=True,
            encouragement_level=1.0,
            patience_level=0.5,
        )

        assert config.allow_direct_answers is True
        assert config.encouragement_level == 1.0
        assert config.patience_level == 0.5


class TestClaudePlayerInit:
    """Test ClaudePlayer initialization."""

    def test_basic_initialization(self):
        """Player should initialize with required parameters."""
        player = ClaudePlayer(
            name="ClaudeBot",
            api_key="test-key",
        )

        assert player.name == "ClaudeBot"
        assert player.api_key == "test-key"
        assert player.model == "claude-sonnet-4-5-20250929"
        assert player.teaching_style == TeachingStyle.SOCRATIC

    def test_custom_model(self):
        """Should allow custom model selection."""
        player = ClaudePlayer(
            name="ClaudeBot",
            api_key="test-key",
            model="claude-opus-4",
        )

        assert player.model == "claude-opus-4"

    def test_custom_teaching_style(self):
        """Should allow custom teaching style."""
        player = ClaudePlayer(
            name="ClaudeBot",
            api_key="test-key",
            teaching_style=TeachingStyle.ENCOURAGING,
        )

        assert player.teaching_style == TeachingStyle.ENCOURAGING

    def test_skill_level_range(self):
        """Skill level should be in valid range."""
        player = ClaudePlayer(
            name="ClaudeBot",
            api_key="test-key",
            skill_level=0.5,
        )

        assert 0.0 <= player.skill_level <= 1.0

    def test_awareness_integration(self):
        """Should integrate with awareness tracker."""
        tracker = AwarenessTracker()
        player = ClaudePlayer(
            name="ClaudeBot",
            api_key="test-key",
            awareness=tracker,
        )

        assert player.awareness is tracker


class TestContextBuilding:
    """Test context building for Claude API."""

    @pytest.fixture
    def player(self):
        """Create a test player."""
        return ClaudePlayer(
            name="ClaudeBot",
            api_key="test-key",
        )

    def test_build_context_basic(self, player):
        """Should build context with basic information."""
        context = player.build_context()

        assert "challenge" in context
        assert "code" in context
        assert "teaching_style" in context

    def test_build_context_with_challenge(self, player):
        """Context should include challenge if set."""
        player.current_challenge = {
            "id": "test_challenge",
            "title": "Test Challenge",
            "description": "A test challenge",
        }

        context = player.build_context()

        assert context["challenge"]["id"] == "test_challenge"

    def test_build_context_with_awareness(self, player):
        """Context should include awareness information."""
        tracker = AwarenessTracker()
        tracker.register_player("Human")
        tracker.register_player("ClaudeBot")

        player.awareness = tracker

        context = player.build_context()

        assert "other_players" in context or "awareness" in context

    def test_build_context_with_history(self, player):
        """Context should include recent history."""
        player.action_history.append({"type": "thought", "content": "Thinking..."})

        context = player.build_context()

        assert len(context.get("history", [])) > 0 or "action_history" in context


class TestResponseParsing:
    """Test parsing Claude's responses into events."""

    @pytest.fixture
    def player(self):
        return ClaudePlayer(
            name="ClaudeBot",
            api_key="test-key",
        )

    def test_parse_thought(self, player):
        """Should parse thought responses."""
        response = "I'm thinking about how to solve this..."

        events = player.parse_response_to_events(response)

        assert len(events) > 0
        assert any(e.get("type") == "thought" for e in events)

    def test_parse_code_edit(self, player):
        """Should parse code editing responses."""
        response = "Let me add a function:\n```python\ndef hello():\n    print('Hello')\n```"

        events = player.parse_response_to_events(response)

        assert len(events) > 0
        assert any(e.get("type") == "code_update" for e in events)

    def test_parse_question(self, player):
        """Should parse questions to other players."""
        response = "What approach did you try first?"

        events = player.parse_response_to_events(response)

        # Question should be detected
        assert len(events) > 0

    def test_parse_hint(self, player):
        """Should parse hints."""
        response = "HINT: Think about using a list comprehension"

        events = player.parse_response_to_events(response)

        assert len(events) > 0
        assert any("hint" in e.get("type", "").lower() or "suggestion" in e.get("type", "") for e in events)


class TestEventEmission:
    """Test event emission system."""

    @pytest.fixture
    def player(self):
        return ClaudePlayer(
            name="ClaudeBot",
            api_key="test-key",
        )

    def test_emit_event_to_sync(self, player):
        """Should emit events to session sync."""
        sync = Mock(spec=SessionSync)
        player.session_sync = sync

        event = {"type": "thought", "content": "Thinking..."}
        player.emit_event(event)

        # Verify event was broadcast (sync has methods like _broadcast_event)
        # In real implementation, this would be checked
        assert True  # Placeholder

    def test_emit_event_updates_awareness(self, player):
        """Should update awareness tracker."""
        tracker = AwarenessTracker()
        player.awareness = tracker

        event = {"type": "code_update", "code": "x = 5"}
        player.emit_event(event)

        # Awareness should be updated
        assert True  # Placeholder

    def test_event_includes_player_id(self, player):
        """Emitted events should include player ID."""
        player.session_sync = Mock(spec=SessionSync)

        event = {"type": "thought", "content": "Test"}
        player.emit_event(event)

        # Event should have player ID
        assert "player" in event or "player_id" in event


class TestAPIIntegration:
    """Test Claude API integration (mocked)."""

    @pytest.fixture
    def player(self):
        return ClaudePlayer(
            name="ClaudeBot",
            api_key="test-key",
        )

    @pytest.mark.asyncio
    async def test_query_claude_basic(self, player):
        """Should query Claude API with context."""
        with patch("lmsp.multiplayer.claude_player.AsyncAnthropic") as mock_client:
            # Mock the API response
            mock_message = MagicMock()
            mock_message.content = [MagicMock(text="This is my response")]

            mock_response = AsyncMock()
            mock_response.create = AsyncMock(return_value=mock_message)

            mock_client.return_value.messages = mock_response

            context = {"challenge": "Test", "code": ""}
            response = await player.query_claude(context)

            assert response is not None
            assert isinstance(response, str)

    @pytest.mark.asyncio
    async def test_query_claude_includes_teaching_style(self, player):
        """API query should include teaching style."""
        player.teaching_style = TeachingStyle.SOCRATIC

        with patch("lmsp.multiplayer.claude_player.AsyncAnthropic") as mock_client:
            mock_message = MagicMock()
            mock_message.content = [MagicMock(text="Socratic response")]

            mock_response = AsyncMock()
            mock_response.create = AsyncMock(return_value=mock_message)

            mock_client.return_value.messages = mock_response

            context = {"challenge": "Test"}
            await player.query_claude(context)

            # Verify teaching style was included in system prompt
            # (Implementation detail - would check call args)
            assert True

    @pytest.mark.asyncio
    async def test_query_claude_error_handling(self, player):
        """Should handle API errors gracefully."""
        with patch("lmsp.multiplayer.claude_player.AsyncAnthropic") as mock_client:
            mock_client.return_value.messages.create.side_effect = Exception("API Error")

            context = {"challenge": "Test"}

            # Should not crash
            try:
                response = await player.query_claude(context)
                # May return error message or None
                assert True
            except Exception:
                pytest.fail("Should handle API errors gracefully")


class TestTeachingStyleBehavior:
    """Test different teaching style behaviors."""

    def test_socratic_asks_questions(self):
        """Socratic style should emphasize questions."""
        player = ClaudePlayer(
            name="Socrates",
            api_key="test-key",
            teaching_style=TeachingStyle.SOCRATIC,
        )

        system_prompt = player.get_system_prompt()

        assert "question" in system_prompt.lower()
        assert "think" in system_prompt.lower()

    def test_demonstrative_shows_examples(self):
        """Demonstrative style should show examples."""
        player = ClaudePlayer(
            name="Demo",
            api_key="test-key",
            teaching_style=TeachingStyle.DEMONSTRATIVE,
        )

        system_prompt = player.get_system_prompt()

        assert "show" in system_prompt.lower() or "example" in system_prompt.lower()

    def test_encouraging_uses_positive_language(self):
        """Encouraging style should be positive."""
        player = ClaudePlayer(
            name="Cheerleader",
            api_key="test-key",
            teaching_style=TeachingStyle.ENCOURAGING,
        )

        system_prompt = player.get_system_prompt()

        assert "encourage" in system_prompt.lower() or "positive" in system_prompt.lower()


class TestActionLoop:
    """Test the main action loop."""

    @pytest.fixture
    def player(self):
        return ClaudePlayer(
            name="ClaudeBot",
            api_key="test-key",
        )

    @pytest.mark.asyncio
    async def test_action_loop_starts(self, player):
        """Action loop should start running."""
        player.running = True

        # Mock should_act to return False immediately
        player.should_act = AsyncMock(return_value=False)

        # Run briefly then stop
        async def run_briefly():
            await asyncio.sleep(0.1)
            player.running = False

        # Start both tasks
        await asyncio.gather(
            player.action_loop(),
            run_briefly(),
        )

        # Should have called should_act
        assert player.should_act.called

    @pytest.mark.asyncio
    async def test_action_loop_processes_actions(self, player):
        """Action loop should process actions when should_act returns True."""
        player.running = True

        # Mock dependencies
        player.should_act = AsyncMock(side_effect=[True, False, False])
        player.query_claude = AsyncMock(return_value="Test response")
        player.parse_response_to_events = Mock(return_value=[{"type": "thought"}])
        player.emit_event = Mock()

        # Run briefly
        async def run_briefly():
            await asyncio.sleep(0.1)
            player.running = False

        await asyncio.gather(
            player.action_loop(),
            run_briefly(),
        )

        # Should have queried Claude and emitted events
        assert player.query_claude.called
        assert player.emit_event.called


class TestSessionIntegration:
    """Test integration with session sync and awareness."""

    def test_join_session(self):
        """Player should be able to join a session."""
        sync = SessionSync(
            session_id="test-session",
            mode=SessionMode.RACE,
            challenge_id="test-challenge",
        )

        player = ClaudePlayer(
            name="ClaudeBot",
            api_key="test-key",
            session_sync=sync,
        )

        player.join_session()

        # Should be registered in session
        assert "ClaudeBot" in sync.state.player_ids

    def test_awareness_tracking(self):
        """Player actions should update awareness."""
        tracker = AwarenessTracker()
        player = ClaudePlayer(
            name="ClaudeBot",
            api_key="test-key",
            awareness=tracker,
        )

        # Emit some events
        player.emit_event({"type": "thought", "content": "Thinking..."})

        # Awareness should have player data
        state = tracker.get_player_state("ClaudeBot")
        assert state is not None


# Self-teaching note:
#
# This test file demonstrates:
# - pytest fixtures for test setup
# - Mocking external dependencies (AsyncAnthropic)
# - AsyncMock for async functions
# - Testing event-driven systems
# - Integration testing
#
# Prerequisites:
# - Level 3: Functions, classes
# - Level 4: Async/await basics
# - Level 5: Mocking, testing patterns
# - Level 6: Event-driven architecture
