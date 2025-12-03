"""
Tests for the Audio Feedback System.

Tests sound effects, volume control, and event-driven audio.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from pathlib import Path

from lmsp.ui.audio import (
    SoundType,
    AudioConfig,
    Sound,
    AudioManager,
    audio_manager,
    play_sound,
    play_success,
    play_failure,
    play_achievement,
    play_level_up,
)


class TestSoundType:
    """Test sound type enumeration."""

    def test_all_success_sounds_defined(self):
        """All success sound types should be defined."""
        assert hasattr(SoundType, "TEST_PASS")
        assert hasattr(SoundType, "ALL_TESTS_PASS")
        assert hasattr(SoundType, "CHALLENGE_COMPLETE")
        assert hasattr(SoundType, "LEVEL_UP")
        assert hasattr(SoundType, "ACHIEVEMENT_UNLOCK")
        assert hasattr(SoundType, "PERFECT_SCORE")

    def test_all_failure_sounds_defined(self):
        """All failure sound types should be defined."""
        assert hasattr(SoundType, "TEST_FAIL")
        assert hasattr(SoundType, "SYNTAX_ERROR")

    def test_all_progress_sounds_defined(self):
        """All progress sound types should be defined."""
        assert hasattr(SoundType, "XP_GAIN")
        assert hasattr(SoundType, "STREAK_MILESTONE")
        assert hasattr(SoundType, "CONCEPT_UNLOCK")

    def test_all_ui_sounds_defined(self):
        """All UI sound types should be defined."""
        assert hasattr(SoundType, "BUTTON_CLICK")
        assert hasattr(SoundType, "MENU_OPEN")
        assert hasattr(SoundType, "MENU_CLOSE")
        assert hasattr(SoundType, "TYPING")


class TestAudioConfig:
    """Test audio configuration."""

    def test_default_config(self):
        """Should create config with sensible defaults."""
        config = AudioConfig()

        assert config.master_volume == 0.7
        assert config.sfx_volume == 0.8
        assert config.music_volume == 0.5
        assert config.muted is False

    def test_feature_flags_default(self):
        """Feature flags should have reasonable defaults."""
        config = AudioConfig()

        assert config.enable_success_sounds is True
        assert config.enable_failure_sounds is True
        assert config.enable_progress_sounds is True
        assert config.enable_ui_sounds is True
        assert config.enable_music is False  # Off by default

    def test_custom_config(self):
        """Should allow custom configuration."""
        config = AudioConfig(
            master_volume=0.5,
            muted=True,
            enable_music=True
        )

        assert config.master_volume == 0.5
        assert config.muted is True
        assert config.enable_music is True


class TestSound:
    """Test sound dataclass."""

    def test_sound_creation(self):
        """Should create sound with all fields."""
        sound = Sound(
            sound_type=SoundType.TEST_PASS,
            volume=0.8,
            cooldown_ms=100
        )

        assert sound.sound_type == SoundType.TEST_PASS
        assert sound.volume == 0.8
        assert sound.cooldown_ms == 100
        assert sound.last_played is None

    def test_can_play_initial(self):
        """Should allow play when never played."""
        sound = Sound(sound_type=SoundType.TEST_PASS)

        assert sound.can_play() is True

    def test_can_play_respects_cooldown(self):
        """Should respect cooldown period."""
        sound = Sound(
            sound_type=SoundType.TYPING,
            cooldown_ms=100
        )

        # Simulate play
        sound.last_played = datetime.now()

        # Should not allow immediate replay
        assert sound.can_play() is False

    def test_can_play_after_cooldown(self):
        """Should allow play after cooldown expires."""
        sound = Sound(
            sound_type=SoundType.TYPING,
            cooldown_ms=100
        )

        # Simulate play 200ms ago
        sound.last_played = datetime.now() - timedelta(milliseconds=200)

        # Should allow play
        assert sound.can_play() is True

    @patch('pygame.mixer.Sound')
    def test_play_method(self, mock_pygame_sound):
        """Should play sound with correct volume."""
        pygame_sound_instance = MagicMock()

        sound = Sound(
            sound_type=SoundType.TEST_PASS,
            pygame_sound=pygame_sound_instance,
            volume=0.8
        )

        sound.play()

        # Should set volume and play
        pygame_sound_instance.set_volume.assert_called_once_with(0.8)
        pygame_sound_instance.play.assert_called_once()

    @patch('pygame.mixer.Sound')
    def test_play_with_volume_override(self, mock_pygame_sound):
        """Should allow volume override."""
        pygame_sound_instance = MagicMock()

        sound = Sound(
            sound_type=SoundType.TEST_PASS,
            pygame_sound=pygame_sound_instance,
            volume=0.8
        )

        sound.play(volume_override=0.5)

        # Should use override volume
        pygame_sound_instance.set_volume.assert_called_once_with(0.5)


class TestAudioManager:
    """Test audio manager."""

    @pytest.fixture
    def manager(self):
        """Create fresh manager for each test."""
        with patch('pygame.mixer.init'):
            return AudioManager()

    def test_initialization(self, manager):
        """Should initialize with default config."""
        assert manager.config is not None
        assert manager.sounds == {}
        assert manager.initialized is True

    @patch('pygame.mixer.init', side_effect=Exception("No audio device"))
    def test_initialization_failure(self, mock_init):
        """Should handle initialization failure gracefully."""
        manager = AudioManager()

        assert manager.initialized is False

    def test_load_sounds(self, manager, tmp_path):
        """Should load sound files from directory."""
        # Create dummy sound file
        sound_dir = tmp_path / "sounds"
        sound_dir.mkdir()
        sound_file = sound_dir / "test_pass.wav"
        sound_file.write_text("dummy")

        with patch('pygame.mixer.Sound') as mock_sound:
            manager.load_sounds(sound_dir)

            # Should attempt to load
            mock_sound.assert_called()

    def test_play_when_not_initialized(self, manager):
        """Should not crash when audio not initialized."""
        manager.initialized = False

        # Should not raise
        manager.play(SoundType.TEST_PASS)

    def test_play_when_muted(self, manager):
        """Should not play when muted."""
        manager.config.muted = True
        manager.sounds[SoundType.TEST_PASS] = Mock()

        manager.play(SoundType.TEST_PASS)

        # Sound should not be played
        manager.sounds[SoundType.TEST_PASS].play.assert_not_called()

    def test_play_respects_category_flags(self, manager):
        """Should respect category enable flags."""
        manager.config.enable_success_sounds = False
        sound_mock = MagicMock()
        manager.sounds[SoundType.TEST_PASS] = sound_mock

        manager.play(SoundType.TEST_PASS)

        # Should not play
        sound_mock.play.assert_not_called()

    def test_play_with_volume_multiplication(self, manager):
        """Should multiply sfx and master volumes."""
        manager.config.master_volume = 0.5
        manager.config.sfx_volume = 0.8

        sound_mock = MagicMock()
        manager.sounds[SoundType.TEST_PASS] = sound_mock

        manager.play(SoundType.TEST_PASS)

        # Should play with combined volume (0.5 * 0.8 = 0.4)
        sound_mock.play.assert_called_once_with(0.4)

    def test_play_success(self, manager):
        """Should play success sound."""
        manager.play = Mock()

        manager.play_success()

        manager.play.assert_called_once_with(SoundType.TEST_PASS)

    def test_play_success_perfect(self, manager):
        """Should play perfect score for perfect success."""
        manager.play = Mock()

        manager.play_success(perfect=True)

        manager.play.assert_called_once_with(SoundType.PERFECT_SCORE)

    def test_play_failure(self, manager):
        """Should play failure sound."""
        manager.play = Mock()

        manager.play_failure()

        manager.play.assert_called_once_with(SoundType.TEST_FAIL)

    def test_play_failure_syntax_error(self, manager):
        """Should play syntax error sound."""
        manager.play = Mock()

        manager.play_failure(is_syntax_error=True)

        manager.play.assert_called_once_with(SoundType.SYNTAX_ERROR)

    def test_play_achievement(self, manager):
        """Should play achievement sound."""
        manager.play = Mock()

        manager.play_achievement()

        manager.play.assert_called_once_with(SoundType.ACHIEVEMENT_UNLOCK)

    def test_play_level_up(self, manager):
        """Should play level up sound."""
        manager.play = Mock()

        manager.play_level_up()

        manager.play.assert_called_once_with(SoundType.LEVEL_UP)

    def test_set_master_volume(self, manager):
        """Should set master volume."""
        manager.set_master_volume(0.5)

        assert manager.config.master_volume == 0.5

    def test_set_master_volume_clamps(self, manager):
        """Should clamp volume to 0.0-1.0 range."""
        manager.set_master_volume(1.5)
        assert manager.config.master_volume == 1.0

        manager.set_master_volume(-0.5)
        assert manager.config.master_volume == 0.0

    def test_set_sfx_volume(self, manager):
        """Should set SFX volume."""
        manager.set_sfx_volume(0.6)

        assert manager.config.sfx_volume == 0.6

    def test_toggle_mute(self, manager):
        """Should toggle mute state."""
        assert manager.config.muted is False

        manager.toggle_mute()
        assert manager.config.muted is True

        manager.toggle_mute()
        assert manager.config.muted is False

    def test_mute(self, manager):
        """Should mute audio."""
        manager.mute()

        assert manager.config.muted is True

    def test_unmute(self, manager):
        """Should unmute audio."""
        manager.config.muted = True

        manager.unmute()

        assert manager.config.muted is False

    def test_enable_category(self, manager):
        """Should enable/disable sound categories."""
        manager.enable_category("success", enabled=False)
        assert manager.config.enable_success_sounds is False

        manager.enable_category("failure", enabled=False)
        assert manager.config.enable_failure_sounds is False

        manager.enable_category("progress", enabled=False)
        assert manager.config.enable_progress_sounds is False

        manager.enable_category("ui", enabled=False)
        assert manager.config.enable_ui_sounds is False

        manager.enable_category("music", enabled=True)
        assert manager.config.enable_music is True

    @patch('pygame.mixer.music')
    def test_play_music(self, mock_music, manager, tmp_path):
        """Should play background music."""
        music_file = tmp_path / "music.mp3"
        music_file.write_text("dummy")

        manager.config.enable_music = True
        manager.play_music(music_file, loop=True)

        mock_music.load.assert_called_once_with(str(music_file))
        mock_music.play.assert_called_once_with(loops=-1)

    @patch('pygame.mixer.music')
    def test_play_music_disabled(self, mock_music, manager, tmp_path):
        """Should not play music when disabled."""
        music_file = tmp_path / "music.mp3"
        music_file.write_text("dummy")

        manager.config.enable_music = False
        manager.play_music(music_file)

        mock_music.load.assert_not_called()

    @patch('pygame.mixer.music')
    def test_stop_music(self, mock_music, manager):
        """Should stop background music."""
        manager.stop_music()

        mock_music.stop.assert_called_once()

    @patch('pygame.mixer.music')
    def test_pause_music(self, mock_music, manager):
        """Should pause background music."""
        manager.pause_music()

        mock_music.pause.assert_called_once()

    @patch('pygame.mixer.music')
    def test_resume_music(self, mock_music, manager):
        """Should resume background music."""
        manager.resume_music()

        mock_music.unpause.assert_called_once()


class TestGlobalAudioManager:
    """Test the global audio manager instance."""

    def test_global_instance_exists(self):
        """Should have global audio_manager instance."""
        assert audio_manager is not None
        assert isinstance(audio_manager, AudioManager)


class TestConvenienceFunctions:
    """Test convenience functions."""

    @patch('lmsp.ui.audio.audio_manager')
    def test_play_sound(self, mock_manager):
        """Should call manager play method."""
        play_sound(SoundType.TEST_PASS)

        mock_manager.play.assert_called_once_with(SoundType.TEST_PASS)

    @patch('lmsp.ui.audio.audio_manager')
    def test_play_success_function(self, mock_manager):
        """Should call manager play_success method."""
        play_success(perfect=True)

        mock_manager.play_success.assert_called_once_with(True)

    @patch('lmsp.ui.audio.audio_manager')
    def test_play_failure_function(self, mock_manager):
        """Should call manager play_failure method."""
        play_failure(is_syntax_error=True)

        mock_manager.play_failure.assert_called_once_with(True)

    @patch('lmsp.ui.audio.audio_manager')
    def test_play_achievement_function(self, mock_manager):
        """Should call manager play_achievement method."""
        play_achievement()

        mock_manager.play_achievement.assert_called_once()

    @patch('lmsp.ui.audio.audio_manager')
    def test_play_level_up_function(self, mock_manager):
        """Should call manager play_level_up method."""
        play_level_up()

        mock_manager.play_level_up.assert_called_once()


class TestAudioIntegration:
    """Test audio system integration patterns."""

    @pytest.fixture
    def manager(self):
        """Create manager with mocked pygame."""
        with patch('pygame.mixer.init'):
            return AudioManager()

    def test_success_flow(self, manager):
        """Test typical success audio flow."""
        # Setup
        manager.play = Mock()

        # Simulate test passing
        manager.play_success()

        # Verify sound played
        manager.play.assert_called_with(SoundType.TEST_PASS)

    def test_failure_flow(self, manager):
        """Test typical failure audio flow."""
        # Setup
        manager.play = Mock()

        # Simulate syntax error
        manager.play_failure(is_syntax_error=True)

        # Verify sound played
        manager.play.assert_called_with(SoundType.SYNTAX_ERROR)

    def test_achievement_unlock_flow(self, manager):
        """Test achievement unlock audio."""
        # Setup
        manager.play = Mock()

        # Simulate achievement unlock
        manager.play_achievement()

        # Verify sound played
        manager.play.assert_called_with(SoundType.ACHIEVEMENT_UNLOCK)

    def test_level_up_flow(self, manager):
        """Test level up audio."""
        # Setup
        manager.play = Mock()

        # Simulate level up
        manager.play_level_up()

        # Verify sound played
        manager.play.assert_called_with(SoundType.LEVEL_UP)


# Self-teaching note:
#
# This file demonstrates:
# - pytest fixtures for test setup
# - unittest.mock for mocking external dependencies (pygame)
# - Testing singleton patterns
# - Testing audio systems without actual hardware
# - Testing cooldown mechanisms
# - Testing volume control and mixing
# - Testing configuration and feature flags
#
# Prerequisites:
# - Level 3: Functions and classes
# - Level 4: Collections and datetime
# - Level 5: Dataclasses and testing patterns
# - Level 6: Mocking and integration testing
#
# Audio testing requires mocking because:
# - CI environments don't have audio devices
# - Tests should be fast and silent
# - We test logic, not pygame implementation
# - Mocking verifies API usage correctly
