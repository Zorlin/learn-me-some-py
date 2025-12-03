"""
Tests for Radial Thumbstick Typing System
=========================================

Tests for the revolutionary radial input system that enables
controller-native coding through 8-direction chord combinations.

TDD: These tests were written BEFORE the implementation.
"""

import pytest
from dataclasses import dataclass
from enum import Enum
import math


# ============================================================================
# TESTS FOR DIRECTION DETECTION
# ============================================================================

class TestDirectionDetection:
    """Test that thumbstick positions map to correct directions."""

    def test_neutral_position_is_center(self):
        """Stick at rest should be CENTER."""
        from lmsp.input.radial import Direction, detect_direction

        direction = detect_direction(0.0, 0.0)
        assert direction == Direction.CENTER

    def test_deadzone_returns_center(self):
        """Small movements inside deadzone should be CENTER."""
        from lmsp.input.radial import Direction, detect_direction

        # Small values within deadzone (default 0.3)
        assert detect_direction(0.1, 0.1) == Direction.CENTER
        assert detect_direction(-0.2, 0.1) == Direction.CENTER
        assert detect_direction(0.0, -0.2) == Direction.CENTER

    def test_cardinal_directions(self):
        """Test the four cardinal directions."""
        from lmsp.input.radial import Direction, detect_direction

        # UP (positive Y)
        assert detect_direction(0.0, 1.0) == Direction.UP
        assert detect_direction(0.1, 0.9) == Direction.UP

        # DOWN (negative Y)
        assert detect_direction(0.0, -1.0) == Direction.DOWN
        assert detect_direction(-0.1, -0.9) == Direction.DOWN

        # LEFT (negative X)
        assert detect_direction(-1.0, 0.0) == Direction.LEFT
        assert detect_direction(-0.9, -0.1) == Direction.LEFT

        # RIGHT (positive X)
        assert detect_direction(1.0, 0.0) == Direction.RIGHT
        assert detect_direction(0.9, 0.1) == Direction.RIGHT

    def test_diagonal_directions(self):
        """Test the four diagonal directions."""
        from lmsp.input.radial import Direction, detect_direction

        # UP_RIGHT
        assert detect_direction(0.7, 0.7) == Direction.UP_RIGHT
        assert detect_direction(0.8, 0.6) == Direction.UP_RIGHT

        # UP_LEFT
        assert detect_direction(-0.7, 0.7) == Direction.UP_LEFT
        assert detect_direction(-0.8, 0.6) == Direction.UP_LEFT

        # DOWN_RIGHT
        assert detect_direction(0.7, -0.7) == Direction.DOWN_RIGHT
        assert detect_direction(0.6, -0.8) == Direction.DOWN_RIGHT

        # DOWN_LEFT
        assert detect_direction(-0.7, -0.7) == Direction.DOWN_LEFT
        assert detect_direction(-0.6, -0.8) == Direction.DOWN_LEFT

    def test_custom_deadzone(self):
        """Test custom deadzone threshold."""
        from lmsp.input.radial import Direction, detect_direction

        # With tight deadzone, small movements should register
        assert detect_direction(0.2, 0.0, deadzone=0.1) == Direction.RIGHT

        # With large deadzone, moderate movements stay CENTER
        assert detect_direction(0.4, 0.0, deadzone=0.5) == Direction.CENTER


# ============================================================================
# TESTS FOR CHORD COMBINATIONS
# ============================================================================

class TestChordCombinations:
    """Test two-stick chord combinations."""

    def test_chord_creation(self):
        """Test creating a chord from two directions."""
        from lmsp.input.radial import Direction, Chord

        chord = Chord(Direction.UP, Direction.UP)
        assert chord.left == Direction.UP
        assert chord.right == Direction.UP

    def test_chord_equality(self):
        """Chords with same directions should be equal."""
        from lmsp.input.radial import Direction, Chord

        chord1 = Chord(Direction.UP, Direction.RIGHT)
        chord2 = Chord(Direction.UP, Direction.RIGHT)
        assert chord1 == chord2

    def test_chord_hash(self):
        """Chords should be hashable for use as dict keys."""
        from lmsp.input.radial import Direction, Chord

        chord = Chord(Direction.LEFT, Direction.DOWN)
        mapping = {chord: "test_value"}
        assert mapping[chord] == "test_value"

    def test_total_chord_combinations(self):
        """9 directions x 9 directions = 81 possible chords."""
        from lmsp.input.radial import Direction, Chord

        chords = set()
        for left in Direction:
            for right in Direction:
                chords.add(Chord(left, right))

        assert len(chords) == 81


# ============================================================================
# TESTS FOR PYTHON KEYWORD MAPPINGS
# ============================================================================

class TestKeywordMappings:
    """Test chord-to-keyword mappings."""

    def test_keyword_mapping_exists(self):
        """Default keyword mappings should be available."""
        from lmsp.input.radial import get_keyword_mappings

        mappings = get_keyword_mappings()
        assert isinstance(mappings, dict)
        assert len(mappings) > 0

    def test_def_chord(self):
        """L-Up + R-Up should produce 'def '."""
        from lmsp.input.radial import Direction, Chord, get_keyword_mappings

        chord = Chord(Direction.UP, Direction.UP)
        mappings = get_keyword_mappings()
        assert chord in mappings
        assert mappings[chord] == "def "

    def test_if_chord(self):
        """L-Left + R-Right should produce 'if '."""
        from lmsp.input.radial import Direction, Chord, get_keyword_mappings

        chord = Chord(Direction.LEFT, Direction.RIGHT)
        mappings = get_keyword_mappings()
        assert chord in mappings
        assert mappings[chord] == "if "

    def test_return_chord(self):
        """L-Down + specific right should produce 'return '."""
        from lmsp.input.radial import Direction, Chord, get_keyword_mappings

        chord = Chord(Direction.DOWN, Direction.CENTER)
        mappings = get_keyword_mappings()
        assert chord in mappings
        assert mappings[chord] == "return "

    def test_for_chord(self):
        """Test for loop keyword chord."""
        from lmsp.input.radial import Direction, Chord, get_keyword_mappings

        chord = Chord(Direction.DOWN, Direction.UP)
        mappings = get_keyword_mappings()
        assert chord in mappings
        assert mappings[chord] == "for "

    def test_while_chord(self):
        """Test while loop keyword chord."""
        from lmsp.input.radial import Direction, Chord, get_keyword_mappings

        chord = Chord(Direction.DOWN, Direction.DOWN)
        mappings = get_keyword_mappings()
        assert chord in mappings
        assert mappings[chord] == "while "

    def test_class_chord(self):
        """Test class keyword chord."""
        from lmsp.input.radial import Direction, Chord, get_keyword_mappings

        chord = Chord(Direction.UP, Direction.DOWN)
        mappings = get_keyword_mappings()
        assert chord in mappings
        assert mappings[chord] == "class "

    def test_common_operators_mapped(self):
        """Common operators should have mappings."""
        from lmsp.input.radial import get_keyword_mappings

        mappings = get_keyword_mappings()
        values = set(mappings.values())

        # Essential operators
        assert "=" in values
        assert "==" in values
        assert ":" in values
        assert "(" in values or "()" in values
        assert "[" in values or "[]" in values

    def test_space_chord(self):
        """Center-Center should produce space."""
        from lmsp.input.radial import Direction, Chord, get_keyword_mappings

        chord = Chord(Direction.CENTER, Direction.CENTER)
        mappings = get_keyword_mappings()
        assert chord in mappings
        assert mappings[chord] == " "

    def test_newline_chord(self):
        """Test newline/enter chord."""
        from lmsp.input.radial import Direction, Chord, get_keyword_mappings

        # Looking for newline mapping
        mappings = get_keyword_mappings()
        newline_found = any(v in ("\n", "\\n", "NEWLINE") for v in mappings.values())
        assert newline_found, "No newline mapping found"


# ============================================================================
# TESTS FOR RADIAL MENU
# ============================================================================

class TestRadialMenu:
    """Test radial menu overlay for visual feedback."""

    def test_menu_creation(self):
        """Radial menu should be creatable."""
        from lmsp.input.radial import RadialMenu

        menu = RadialMenu()
        assert menu is not None

    def test_menu_has_segments(self):
        """Menu should have 8 directional segments."""
        from lmsp.input.radial import RadialMenu

        menu = RadialMenu()
        assert len(menu.segments) == 8

    def test_menu_segment_labels(self):
        """Each segment should have a label."""
        from lmsp.input.radial import RadialMenu

        menu = RadialMenu()
        for segment in menu.segments:
            assert hasattr(segment, 'label')
            assert isinstance(segment.label, str)

    def test_menu_highlight_direction(self):
        """Menu should highlight active direction."""
        from lmsp.input.radial import RadialMenu, Direction

        menu = RadialMenu()
        menu.highlight(Direction.UP)
        assert menu.highlighted == Direction.UP

    def test_menu_render_returns_string(self):
        """Menu render should return displayable string."""
        from lmsp.input.radial import RadialMenu

        menu = RadialMenu()
        rendered = menu.render()
        assert isinstance(rendered, str)
        assert len(rendered) > 0

    def test_left_and_right_menu_independent(self):
        """Left and right stick should have separate menus."""
        from lmsp.input.radial import RadialMenuPair

        menus = RadialMenuPair()
        assert hasattr(menus, 'left')
        assert hasattr(menus, 'right')
        assert menus.left is not menus.right


# ============================================================================
# TESTS FOR RADIAL INPUT HANDLER
# ============================================================================

class TestRadialInputHandler:
    """Test the main radial input handler."""

    def test_handler_creation(self):
        """Handler should be creatable."""
        from lmsp.input.radial import RadialInputHandler

        handler = RadialInputHandler()
        assert handler is not None

    def test_handler_processes_stick_input(self):
        """Handler should process raw stick values."""
        from lmsp.input.radial import RadialInputHandler

        handler = RadialInputHandler()

        # Simulate left stick up, right stick up
        result = handler.process(
            left_x=0.0, left_y=1.0,
            right_x=0.0, right_y=1.0,
            confirm=True
        )

        assert result is not None
        assert result == "def "

    def test_handler_requires_confirmation(self):
        """Chord should only output on confirmation button."""
        from lmsp.input.radial import RadialInputHandler

        handler = RadialInputHandler()

        # Without confirm, should return None
        result = handler.process(
            left_x=0.0, left_y=1.0,
            right_x=0.0, right_y=1.0,
            confirm=False
        )

        assert result is None

    def test_handler_tracks_current_chord(self):
        """Handler should expose current pending chord."""
        from lmsp.input.radial import RadialInputHandler, Direction, Chord

        handler = RadialInputHandler()

        handler.process(
            left_x=0.0, left_y=1.0,
            right_x=-1.0, right_y=0.0,
            confirm=False
        )

        assert handler.current_chord == Chord(Direction.UP, Direction.LEFT)

    def test_handler_resets_after_confirm(self):
        """After confirmation, chord should reset."""
        from lmsp.input.radial import RadialInputHandler, Direction

        handler = RadialInputHandler()

        # Confirm a chord
        handler.process(
            left_x=0.0, left_y=1.0,
            right_x=0.0, right_y=1.0,
            confirm=True
        )

        # Check reset
        assert handler.current_chord.left == Direction.CENTER
        assert handler.current_chord.right == Direction.CENTER

    def test_unmapped_chord_returns_none(self):
        """Unmapped chord combinations should return None."""
        from lmsp.input.radial import RadialInputHandler

        handler = RadialInputHandler()

        # Unlikely chord combination that's probably not mapped
        result = handler.process(
            left_x=0.7, left_y=0.7,  # UP_RIGHT
            right_x=-0.7, right_y=-0.7,  # DOWN_LEFT
            confirm=True
        )

        # Should return None or empty string for unmapped
        assert result is None or result == ""


# ============================================================================
# TESTS FOR MUSCLE MEMORY TRAINER
# ============================================================================

class TestMuscleMemoryTrainer:
    """Test the muscle memory training mode."""

    def test_trainer_creation(self):
        """Trainer should be creatable."""
        from lmsp.input.radial import MuscleMemoryTrainer

        trainer = MuscleMemoryTrainer()
        assert trainer is not None

    def test_trainer_generates_challenges(self):
        """Trainer should generate random chord challenges."""
        from lmsp.input.radial import MuscleMemoryTrainer

        trainer = MuscleMemoryTrainer()
        challenge = trainer.next_challenge()

        assert challenge is not None
        assert hasattr(challenge, 'target_keyword')
        assert hasattr(challenge, 'target_chord')

    def test_trainer_validates_attempt(self):
        """Trainer should validate player attempts."""
        from lmsp.input.radial import MuscleMemoryTrainer, Direction, Chord

        trainer = MuscleMemoryTrainer()
        challenge = trainer.next_challenge()

        # Correct attempt
        result = trainer.attempt(challenge.target_chord)
        assert result.correct is True

        # Wrong attempt
        wrong_chord = Chord(Direction.DOWN_LEFT, Direction.DOWN_RIGHT)
        result = trainer.attempt(wrong_chord)
        assert result.correct is False

    def test_trainer_tracks_stats(self):
        """Trainer should track accuracy statistics."""
        from lmsp.input.radial import MuscleMemoryTrainer

        trainer = MuscleMemoryTrainer()

        # Do some attempts
        for _ in range(5):
            challenge = trainer.next_challenge()
            trainer.attempt(challenge.target_chord)

        stats = trainer.get_stats()
        assert 'total_attempts' in stats
        assert 'correct_count' in stats
        assert 'accuracy' in stats
        assert stats['total_attempts'] == 5
        assert stats['accuracy'] == 1.0  # All correct

    def test_trainer_measures_response_time(self):
        """Trainer should measure time to respond."""
        from lmsp.input.radial import MuscleMemoryTrainer
        import time

        trainer = MuscleMemoryTrainer()
        challenge = trainer.next_challenge()

        # Small delay
        time.sleep(0.01)

        result = trainer.attempt(challenge.target_chord)
        assert result.response_time_ms >= 0

    def test_trainer_difficulty_levels(self):
        """Trainer should support difficulty levels."""
        from lmsp.input.radial import MuscleMemoryTrainer, TrainingDifficulty

        trainer = MuscleMemoryTrainer(difficulty=TrainingDifficulty.BEGINNER)
        assert trainer.difficulty == TrainingDifficulty.BEGINNER

        trainer = MuscleMemoryTrainer(difficulty=TrainingDifficulty.ADVANCED)
        assert trainer.difficulty == TrainingDifficulty.ADVANCED

    def test_beginner_uses_simple_keywords(self):
        """Beginner difficulty should use simple keywords only."""
        from lmsp.input.radial import MuscleMemoryTrainer, TrainingDifficulty

        trainer = MuscleMemoryTrainer(difficulty=TrainingDifficulty.BEGINNER)

        simple_keywords = {"def ", "if ", "for ", "return ", "class ", "print("}
        challenges = [trainer.next_challenge() for _ in range(20)]

        for challenge in challenges:
            assert challenge.target_keyword in simple_keywords, \
                f"Beginner got advanced keyword: {challenge.target_keyword}"

    def test_trainer_adapts_to_weaknesses(self):
        """Trainer should focus on weak areas."""
        from lmsp.input.radial import MuscleMemoryTrainer, Direction, Chord

        trainer = MuscleMemoryTrainer()

        # Simulate failing on a specific chord repeatedly
        target_chord = Chord(Direction.LEFT, Direction.RIGHT)
        wrong_chord = Chord(Direction.RIGHT, Direction.LEFT)

        for _ in range(5):
            trainer._record_attempt(target_chord, wrong_chord)

        # Trainer should prioritize weak chords
        weakness_focus = trainer.get_weakness_focus()
        assert target_chord in weakness_focus


# ============================================================================
# TESTS FOR VISUAL RENDERING
# ============================================================================

class TestVisualRendering:
    """Test visual rendering of radial menus."""

    def test_ascii_rendering(self):
        """Should support ASCII art rendering."""
        from lmsp.input.radial import RadialMenu, RenderMode

        menu = RadialMenu(render_mode=RenderMode.ASCII)
        rendered = menu.render()

        # Should contain direction indicators
        assert "UP" in rendered or "↑" in rendered or "^" in rendered

    def test_rich_rendering(self):
        """Should support Rich library rendering."""
        from lmsp.input.radial import RadialMenu, RenderMode

        menu = RadialMenu(render_mode=RenderMode.RICH)
        rendered = menu.render()

        # Rich rendering returns renderable object or styled string
        assert rendered is not None

    def test_dual_menu_rendering(self):
        """Dual menu render should show both sticks."""
        from lmsp.input.radial import RadialMenuPair, Direction

        menus = RadialMenuPair()
        menus.left.highlight(Direction.UP)
        menus.right.highlight(Direction.DOWN)

        rendered = menus.render()
        assert "L-STICK" in rendered or "Left" in rendered.lower()
        assert "R-STICK" in rendered or "Right" in rendered.lower()

    def test_highlight_shows_pending_chord(self):
        """Render should visually indicate pending chord."""
        from lmsp.input.radial import RadialMenuPair, Direction

        menus = RadialMenuPair()
        menus.set_pending_chord(Direction.UP, Direction.RIGHT)

        rendered = menus.render()
        # Should show what keyword will be produced
        assert "def" in rendered.lower() or "=" in rendered


# ============================================================================
# TESTS FOR INTEGRATION
# ============================================================================

class TestRadialIntegration:
    """Test integration with input system."""

    def test_radial_conforms_to_input_protocol(self):
        """Radial handler should work as an InputDevice."""
        from lmsp.input.radial import RadialInputHandler

        handler = RadialInputHandler()

        # Should have standard input methods
        assert hasattr(handler, 'get_text_input')

    def test_radial_produces_text_for_editor(self):
        """Radial input should produce text usable by editor."""
        from lmsp.input.radial import RadialInputHandler

        handler = RadialInputHandler()

        # Simulate typing "def "
        text = handler.process(
            left_x=0.0, left_y=1.0,
            right_x=0.0, right_y=1.0,
            confirm=True
        )

        assert isinstance(text, str)
        assert text.isprintable() or text in ("\n", "\t")


# ============================================================================
# TESTS FOR CONFIGURATION
# ============================================================================

class TestRadialConfiguration:
    """Test radial input configuration options."""

    def test_custom_mappings(self):
        """Should support custom chord mappings."""
        from lmsp.input.radial import RadialInputHandler, Direction, Chord

        custom_mappings = {
            Chord(Direction.UP, Direction.UP): "custom_keyword "
        }

        handler = RadialInputHandler(custom_mappings=custom_mappings)

        result = handler.process(
            left_x=0.0, left_y=1.0,
            right_x=0.0, right_y=1.0,
            confirm=True
        )

        assert result == "custom_keyword "

    def test_configurable_deadzone(self):
        """Deadzone should be configurable."""
        from lmsp.input.radial import RadialInputHandler

        handler = RadialInputHandler(deadzone=0.5)
        assert handler.deadzone == 0.5

    def test_persist_custom_config(self):
        """Custom config should be persistable."""
        from lmsp.input.radial import RadialConfig

        config = RadialConfig(
            deadzone=0.4,
            confirm_button="A"
        )

        # Should be serializable
        serialized = config.to_dict()
        restored = RadialConfig.from_dict(serialized)

        assert restored.deadzone == 0.4
        assert restored.confirm_button == "A"


# Self-teaching note:
#
# This test file demonstrates:
# - pytest test organization (Level 3+: functions, classes)
# - Type hints and dataclasses (Level 5: classes)
# - Enum usage (Level 2: collections)
# - Test fixtures and parametrization (Level 6: patterns)
# - Protocol/interface testing (Level 5: classes)
#
# Writing tests FIRST (TDD) helps you:
# 1. Think through the API before coding
# 2. Document expected behavior
# 3. Ensure testability is built-in
# 4. Catch edge cases early
#
# The learner will encounter these patterns after mastering prerequisites.
