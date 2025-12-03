"""
Tests for Game Engine
=====================

Tests for the main game loop, state machine, and system integration.

TDD: These tests define the expected behavior of the game engine.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from io import StringIO

from lmsp.game.engine import (
    GameEngine,
    GamePhase,
    GameConfig,
    InputHandler,
    KeyboardInputHandler,
)
from lmsp.game.state import GameState, GameSession, GameEvent
from lmsp.game.renderer import MinimalRenderer
from lmsp.python.validator import ValidationResult, TestResult
from lmsp.adaptive.engine import LearnerProfile, AdaptiveRecommendation


class MockInputHandler:
    """Mock input handler for testing."""

    def __init__(self, responses: list[str] = None):
        self.responses = responses or []
        self.call_index = 0

    def get_line(self, prompt: str = "") -> str:
        """Return the next pre-configured response."""
        if self.call_index < len(self.responses):
            response = self.responses[self.call_index]
            self.call_index += 1
            return response
        return ""

    def get_char(self) -> str:
        """Return the next pre-configured response."""
        return self.get_line()


class TestGamePhase:
    """Test game phase enumeration."""

    def test_all_phases_defined(self):
        """All required phases should be defined."""
        phases = list(GamePhase)
        assert len(phases) >= 7

        required = [
            "MENU", "SELECTING_CHALLENGE", "CODING",
            "RUNNING_TESTS", "VIEWING_RESULTS",
            "EMOTIONAL_FEEDBACK", "COMPLETED"
        ]
        for phase_name in required:
            assert hasattr(GamePhase, phase_name)

    def test_phase_values_unique(self):
        """Phase values should be unique."""
        values = [p.value for p in GamePhase]
        assert len(values) == len(set(values))


class TestGameConfig:
    """Test game configuration dataclass."""

    def test_default_config(self):
        """Default config should have sensible values."""
        config = GameConfig()

        assert config.concepts_dir == Path("concepts")
        assert config.challenges_dir == Path("challenges")
        assert config.timeout_seconds == 5
        assert config.auto_save is True
        assert config.debug_mode is False

    def test_custom_config(self):
        """Custom config should override defaults."""
        config = GameConfig(
            concepts_dir=Path("/custom/concepts"),
            challenges_dir=Path("/custom/challenges"),
            timeout_seconds=10,
            debug_mode=True,
        )

        assert config.concepts_dir == Path("/custom/concepts")
        assert config.timeout_seconds == 10
        assert config.debug_mode is True


class TestKeyboardInputHandler:
    """Test the keyboard input handler."""

    def test_get_line_calls_input(self):
        """get_line should call Python's input()."""
        handler = KeyboardInputHandler()

        with patch('builtins.input', return_value="test"):
            result = handler.get_line("prompt")
            assert result == "test"

    def test_get_char_calls_input(self):
        """get_char should call Python's input() (simple version)."""
        handler = KeyboardInputHandler()

        with patch('builtins.input', return_value="x"):
            result = handler.get_char()
            assert result == "x"


class TestGameEngineInit:
    """Test game engine initialization."""

    @pytest.fixture
    def profile(self):
        """Create a test learner profile."""
        return LearnerProfile(player_id="test_player")

    @pytest.fixture
    def mock_renderer(self):
        """Create a mock renderer."""
        renderer = Mock()
        renderer.clear = Mock()
        renderer.show_message = Mock()
        renderer.render_challenge = Mock()
        renderer.render_test_results = Mock()
        renderer.render_recommendation = Mock()
        renderer.render_code_editor = Mock()
        return renderer

    def test_engine_creation(self, profile, mock_renderer):
        """Engine should be created with required components."""
        mock_input = MockInputHandler()

        engine = GameEngine(
            profile=profile,
            renderer=mock_renderer,
            input_handler=mock_input,
        )

        assert engine.profile == profile
        assert engine.phase == GamePhase.MENU
        assert engine.session is None
        assert engine.current_challenge is None

    def test_engine_with_default_config(self, profile, mock_renderer):
        """Engine should use default config when none provided."""
        engine = GameEngine(
            profile=profile,
            renderer=mock_renderer,
            input_handler=MockInputHandler(),
        )

        assert engine.config.timeout_seconds == 5

    def test_engine_with_custom_config(self, profile, mock_renderer):
        """Engine should use custom config when provided."""
        config = GameConfig(timeout_seconds=10)

        engine = GameEngine(
            profile=profile,
            config=config,
            renderer=mock_renderer,
            input_handler=MockInputHandler(),
        )

        assert engine.config.timeout_seconds == 10

    def test_engine_creates_validator(self, profile, mock_renderer):
        """Engine should create validator with config timeout."""
        engine = GameEngine(
            profile=profile,
            renderer=mock_renderer,
            input_handler=MockInputHandler(),
        )

        assert engine.validator is not None
        assert engine.validator.timeout_seconds == 5

    def test_engine_creates_adaptive_engine(self, profile, mock_renderer):
        """Engine should create adaptive engine with profile."""
        engine = GameEngine(
            profile=profile,
            renderer=mock_renderer,
            input_handler=MockInputHandler(),
        )

        assert engine.adaptive_engine is not None


class TestGameEnginePhases:
    """Test game phase transitions."""

    @pytest.fixture
    def engine(self):
        """Create an engine for testing."""
        profile = LearnerProfile(player_id="test_player")
        renderer = Mock()
        renderer.clear = Mock()
        renderer.show_message = Mock()
        renderer.render_challenge = Mock()
        renderer.render_test_results = Mock()
        renderer.render_recommendation = Mock()
        renderer.render_code_editor = Mock()

        return GameEngine(
            profile=profile,
            renderer=renderer,
            input_handler=MockInputHandler(["4"]),  # Quit immediately
        )

    def test_starts_in_menu_phase(self, engine):
        """Engine should start in MENU phase."""
        assert engine.phase == GamePhase.MENU

    def test_menu_choice_2_goes_to_selection(self):
        """Menu choice 2 should go to challenge selection."""
        profile = LearnerProfile(player_id="test")
        renderer = Mock()
        renderer.clear = Mock()
        renderer.show_message = Mock()
        renderer.render_recommendation = Mock()

        # Choose 2 (select challenge), then back, then quit
        inputs = MockInputHandler(["2", "back", "4"])

        engine = GameEngine(
            profile=profile,
            renderer=renderer,
            input_handler=inputs,
        )

        # Run one tick (menu)
        engine._handle_menu()
        assert engine.phase == GamePhase.SELECTING_CHALLENGE

    def test_menu_choice_4_stops_engine(self):
        """Menu choice 4 should stop the engine."""
        profile = LearnerProfile(player_id="test")
        renderer = Mock()
        renderer.clear = Mock()
        renderer.show_message = Mock()

        inputs = MockInputHandler(["4"])

        engine = GameEngine(
            profile=profile,
            renderer=renderer,
            input_handler=inputs,
        )

        engine._handle_menu()
        assert engine._running is False


class TestGameEngineCodeEditing:
    """Test code editing functionality."""

    @pytest.fixture
    def engine_with_challenge(self):
        """Create an engine with an active challenge."""
        profile = LearnerProfile(player_id="test")
        renderer = Mock()
        renderer.clear = Mock()
        renderer.show_message = Mock()
        renderer.render_challenge = Mock()
        renderer.render_code_editor = Mock()
        renderer.render_test_results = Mock()

        engine = GameEngine(
            profile=profile,
            renderer=renderer,
            input_handler=MockInputHandler([]),
        )

        # Create a mock challenge
        mock_challenge = Mock()
        mock_challenge.id = "test_challenge"
        mock_challenge.name = "Test Challenge"
        mock_challenge.level = 1
        mock_challenge.skeleton_code = "def solution():\n    pass"
        mock_challenge.test_cases = []
        mock_challenge.prerequisites = []
        mock_challenge.hints = {}

        # Set up the engine with challenge
        engine.current_challenge = mock_challenge
        engine.session = GameSession(player_id="test", challenge_id="test_challenge")
        engine.session.start()
        engine.code_buffer = ["def solution():", "    pass"]
        engine.phase = GamePhase.CODING

        return engine

    def test_code_buffer_initialized(self, engine_with_challenge):
        """Code buffer should be initialized from skeleton."""
        assert len(engine_with_challenge.code_buffer) == 2
        assert engine_with_challenge.code_buffer[0] == "def solution():"

    def test_quick_line_edit(self, engine_with_challenge):
        """Quick line edit should update buffer."""
        engine_with_challenge._quick_line_edit("line 2     return 42")

        assert engine_with_challenge.code_buffer[1] == "    return 42"

    def test_quick_line_edit_extends_buffer(self, engine_with_challenge):
        """Quick line edit should extend buffer if needed."""
        engine_with_challenge._quick_line_edit("line 5 # comment")

        # Buffer should have grown
        assert len(engine_with_challenge.code_buffer) >= 5
        assert engine_with_challenge.code_buffer[4] == "# comment"


class TestGameEngineSubmission:
    """Test code submission and validation."""

    @pytest.fixture
    def engine_with_challenge(self):
        """Create an engine with an active challenge."""
        profile = LearnerProfile(player_id="test")
        renderer = Mock()
        renderer.clear = Mock()
        renderer.show_message = Mock()
        renderer.render_challenge = Mock()
        renderer.render_code_editor = Mock()
        renderer.render_test_results = Mock()

        engine = GameEngine(
            profile=profile,
            renderer=renderer,
            input_handler=MockInputHandler([]),
        )

        # Create a mock challenge with test cases
        mock_challenge = Mock()
        mock_challenge.id = "test_challenge"
        mock_challenge.name = "Test Challenge"
        mock_challenge.level = 1
        mock_challenge.skeleton_code = "def add(a, b):\n    pass"
        mock_challenge.test_cases = [
            {"function": "add", "args": [1, 2], "expected": 3},
            {"function": "add", "args": [0, 0], "expected": 0},
        ]
        mock_challenge.prerequisites = []
        mock_challenge.hints = {}

        engine.current_challenge = mock_challenge
        engine.session = GameSession(player_id="test", challenge_id="test_challenge")
        engine.session.start()
        engine.code_buffer = ["def add(a, b):", "    return a + b"]
        engine.phase = GamePhase.CODING

        return engine

    def test_submit_code_validates(self, engine_with_challenge):
        """submit_code should validate against test cases."""
        code = "def add(a, b):\n    return a + b"
        result = engine_with_challenge.submit_code(code)

        assert isinstance(result, ValidationResult)

    def test_submit_code_without_challenge_raises(self):
        """submit_code should raise if no challenge active."""
        profile = LearnerProfile(player_id="test")
        renderer = Mock()
        renderer.clear = Mock()
        renderer.show_message = Mock()

        engine = GameEngine(
            profile=profile,
            renderer=renderer,
            input_handler=MockInputHandler([]),
        )

        with pytest.raises(ValueError, match="No active challenge"):
            engine.submit_code("x = 1")


class TestGameEngineCallbacks:
    """Test event callbacks."""

    def test_on_challenge_complete_callback(self):
        """Challenge complete callback should be called."""
        profile = LearnerProfile(player_id="test")
        renderer = Mock()
        renderer.clear = Mock()
        renderer.show_message = Mock()
        renderer.render_challenge = Mock()
        renderer.render_test_results = Mock()

        engine = GameEngine(
            profile=profile,
            renderer=renderer,
            input_handler=MockInputHandler([]),
        )

        # Track callback invocations
        callback_invocations = []

        def callback(challenge, result):
            callback_invocations.append((challenge, result))

        engine.on_challenge_complete(callback)

        # Simulate challenge completion
        mock_challenge = Mock()
        mock_challenge.prerequisites = ["basics"]
        engine.current_challenge = mock_challenge

        mock_result = Mock()
        engine._last_result = mock_result

        engine.session = Mock()
        engine.session.get_duration = Mock(return_value=Mock(total_seconds=Mock(return_value=60)))
        engine.session.state = Mock()
        engine.session.state.hints_used = 0
        engine.session.record_event = Mock()

        # Trigger callbacks
        for cb in engine._on_challenge_complete:
            cb(engine.current_challenge, mock_result)

        assert len(callback_invocations) == 1
        assert callback_invocations[0][0] == mock_challenge


class TestGameEngineStop:
    """Test stopping the game engine."""

    def test_stop_sets_running_false(self):
        """stop() should set _running to False."""
        profile = LearnerProfile(player_id="test")
        renderer = Mock()
        renderer.clear = Mock()
        renderer.show_message = Mock()

        engine = GameEngine(
            profile=profile,
            renderer=renderer,
            input_handler=MockInputHandler([]),
        )

        engine._running = True
        engine.stop()

        assert engine._running is False


class TestMinimalRendererIntegration:
    """Test integration with MinimalRenderer."""

    def test_engine_with_minimal_renderer(self):
        """Engine should work with MinimalRenderer."""
        profile = LearnerProfile(player_id="test")
        renderer = MinimalRenderer()

        engine = GameEngine(
            profile=profile,
            renderer=renderer,
            input_handler=MockInputHandler(["4"]),  # Quit
        )

        assert engine.renderer is renderer


# Self-teaching note:
#
# This test file demonstrates:
# - Mocking for isolated testing (unittest.mock)
# - Fixtures for test setup (pytest.fixture)
# - Testing state machines (phase transitions)
# - Testing callbacks and event handlers
# - Integration testing patterns
#
# Key testing concepts:
# 1. Mock objects isolate units under test
# 2. Fixtures reduce test setup duplication
# 3. State machine tests verify transitions
# 4. Callback tests verify event handling
# 5. Integration tests verify components work together
#
# The learner will encounter this after mastering:
# - Level 4: Testing basics
# - Level 5: Classes and mocking
# - Level 6: Design patterns
