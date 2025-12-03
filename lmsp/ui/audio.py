"""
Audio Feedback System

Provides sound effects for game events to enhance player experience.

Features:
- Success sounds (tests pass, level up, achievement unlock)
- Failure sounds (tests fail, syntax error)
- Progress sounds (XP gain, streak milestone)
- Ambient sounds (typing, menu navigation)
- Volume control and muting
- Platform-specific audio (pygame.mixer)

Self-teaching note:
This file demonstrates:
- pygame.mixer for audio playback (Level 5+)
- Resource management (Level 5: file paths)
- Event-driven audio (Level 6: callbacks)
- Singleton pattern for global audio manager (Level 6)
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Callable
from enum import Enum
from pathlib import Path
import pygame.mixer
from datetime import datetime, timedelta


class SoundType(Enum):
    """Types of sound effects."""

    # Success sounds
    TEST_PASS = "test_pass"
    ALL_TESTS_PASS = "all_tests_pass"
    CHALLENGE_COMPLETE = "challenge_complete"
    LEVEL_UP = "level_up"
    ACHIEVEMENT_UNLOCK = "achievement_unlock"
    PERFECT_SCORE = "perfect_score"

    # Failure sounds
    TEST_FAIL = "test_fail"
    SYNTAX_ERROR = "syntax_error"

    # Progress sounds
    XP_GAIN = "xp_gain"
    STREAK_MILESTONE = "streak_milestone"
    CONCEPT_UNLOCK = "concept_unlock"

    # UI sounds
    BUTTON_CLICK = "button_click"
    MENU_OPEN = "menu_open"
    MENU_CLOSE = "menu_close"
    TYPING = "typing"

    # Ambient sounds
    BACKGROUND_MUSIC = "background_music"


@dataclass
class AudioConfig:
    """Configuration for audio system."""

    master_volume: float = 0.7  # 0.0 to 1.0
    sfx_volume: float = 0.8
    music_volume: float = 0.5
    muted: bool = False

    # Feature flags
    enable_success_sounds: bool = True
    enable_failure_sounds: bool = True
    enable_progress_sounds: bool = True
    enable_ui_sounds: bool = True
    enable_music: bool = False  # Off by default

    # Cooldown to prevent spam
    min_time_between_sounds_ms: int = 100


@dataclass
class Sound:
    """A loaded sound effect."""

    sound_type: SoundType
    pygame_sound: Optional[pygame.mixer.Sound] = None
    volume: float = 1.0

    # Cooldown tracking
    last_played: Optional[datetime] = None
    cooldown_ms: int = 0  # Minimum time between plays

    def can_play(self) -> bool:
        """Check if sound can be played (cooldown)."""
        if self.last_played is None:
            return True

        elapsed = (datetime.now() - self.last_played).total_seconds() * 1000
        return elapsed >= self.cooldown_ms

    def play(self, volume_override: Optional[float] = None):
        """Play the sound effect."""
        if not self.can_play():
            return

        if self.pygame_sound:
            volume = volume_override if volume_override is not None else self.volume
            self.pygame_sound.set_volume(volume)
            self.pygame_sound.play()
            self.last_played = datetime.now()


class AudioManager:
    """
    Manages all audio playback for LMSP.

    Singleton pattern - use audio_manager global instance.

    Usage:
        from lmsp.ui.audio import audio_manager

        # Play success sound
        audio_manager.play(SoundType.TEST_PASS)

        # Adjust volume
        audio_manager.set_master_volume(0.5)

        # Mute/unmute
        audio_manager.toggle_mute()
    """

    def __init__(self, config: Optional[AudioConfig] = None):
        self.config = config or AudioConfig()
        self.sounds: Dict[SoundType, Sound] = {}
        self.initialized = False

        # Initialize pygame mixer
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self.initialized = True
        except (pygame.error, Exception) as e:
            print(f"Warning: Could not initialize audio: {e}")
            self.initialized = False

    def load_sounds(self, sound_dir: Path):
        """
        Load all sound effects from directory.

        Args:
            sound_dir: Directory containing sound files
        """
        if not self.initialized:
            return

        # Expected sound files
        sound_files = {
            SoundType.TEST_PASS: "test_pass.wav",
            SoundType.ALL_TESTS_PASS: "all_tests_pass.wav",
            SoundType.CHALLENGE_COMPLETE: "challenge_complete.wav",
            SoundType.LEVEL_UP: "level_up.wav",
            SoundType.ACHIEVEMENT_UNLOCK: "achievement.wav",
            SoundType.PERFECT_SCORE: "perfect.wav",
            SoundType.TEST_FAIL: "test_fail.wav",
            SoundType.SYNTAX_ERROR: "error.wav",
            SoundType.XP_GAIN: "xp_gain.wav",
            SoundType.STREAK_MILESTONE: "streak.wav",
            SoundType.CONCEPT_UNLOCK: "unlock.wav",
            SoundType.BUTTON_CLICK: "click.wav",
            SoundType.MENU_OPEN: "menu_open.wav",
            SoundType.MENU_CLOSE: "menu_close.wav",
            SoundType.TYPING: "typing.wav",
        }

        for sound_type, filename in sound_files.items():
            sound_path = sound_dir / filename

            if sound_path.exists():
                try:
                    pygame_sound = pygame.mixer.Sound(str(sound_path))

                    # Set cooldowns for rapid-fire sounds
                    cooldown = 100 if sound_type == SoundType.TYPING else 0

                    self.sounds[sound_type] = Sound(
                        sound_type=sound_type,
                        pygame_sound=pygame_sound,
                        cooldown_ms=cooldown
                    )
                except pygame.error as e:
                    print(f"Warning: Could not load {filename}: {e}")

    def play(self, sound_type: SoundType, volume_override: Optional[float] = None):
        """
        Play a sound effect.

        Args:
            sound_type: Type of sound to play
            volume_override: Optional volume override (0.0-1.0)
        """
        if not self.initialized or self.config.muted:
            return

        # Check if this sound type is enabled
        if sound_type in [SoundType.TEST_PASS, SoundType.ALL_TESTS_PASS,
                         SoundType.CHALLENGE_COMPLETE, SoundType.PERFECT_SCORE]:
            if not self.config.enable_success_sounds:
                return
        elif sound_type in [SoundType.TEST_FAIL, SoundType.SYNTAX_ERROR]:
            if not self.config.enable_failure_sounds:
                return
        elif sound_type in [SoundType.XP_GAIN, SoundType.STREAK_MILESTONE,
                           SoundType.CONCEPT_UNLOCK]:
            if not self.config.enable_progress_sounds:
                return
        elif sound_type in [SoundType.BUTTON_CLICK, SoundType.MENU_OPEN,
                           SoundType.MENU_CLOSE, SoundType.TYPING]:
            if not self.config.enable_ui_sounds:
                return

        # Get and play sound
        sound = self.sounds.get(sound_type)
        if sound:
            volume = volume_override if volume_override is not None else self.config.sfx_volume
            volume *= self.config.master_volume
            sound.play(volume)

    def play_success(self, perfect: bool = False):
        """Play success sound (with perfect variant)."""
        if perfect:
            self.play(SoundType.PERFECT_SCORE)
        else:
            self.play(SoundType.TEST_PASS)

    def play_failure(self, is_syntax_error: bool = False):
        """Play failure sound (with syntax error variant)."""
        if is_syntax_error:
            self.play(SoundType.SYNTAX_ERROR)
        else:
            self.play(SoundType.TEST_FAIL)

    def play_achievement(self):
        """Play achievement unlock sound."""
        self.play(SoundType.ACHIEVEMENT_UNLOCK)

    def play_level_up(self):
        """Play level up sound."""
        self.play(SoundType.LEVEL_UP)

    def set_master_volume(self, volume: float):
        """
        Set master volume.

        Args:
            volume: Volume level 0.0 to 1.0
        """
        self.config.master_volume = max(0.0, min(1.0, volume))

    def set_sfx_volume(self, volume: float):
        """Set sound effects volume."""
        self.config.sfx_volume = max(0.0, min(1.0, volume))

    def set_music_volume(self, volume: float):
        """Set music volume."""
        self.config.music_volume = max(0.0, min(1.0, volume))
        if self.initialized:
            pygame.mixer.music.set_volume(self.config.music_volume * self.config.master_volume)

    def toggle_mute(self):
        """Toggle mute on/off."""
        self.config.muted = not self.config.muted

    def mute(self):
        """Mute all audio."""
        self.config.muted = True

    def unmute(self):
        """Unmute audio."""
        self.config.muted = False

    def enable_category(self, category: str, enabled: bool = True):
        """
        Enable/disable a category of sounds.

        Args:
            category: "success", "failure", "progress", "ui", "music"
            enabled: True to enable, False to disable
        """
        if category == "success":
            self.config.enable_success_sounds = enabled
        elif category == "failure":
            self.config.enable_failure_sounds = enabled
        elif category == "progress":
            self.config.enable_progress_sounds = enabled
        elif category == "ui":
            self.config.enable_ui_sounds = enabled
        elif category == "music":
            self.config.enable_music = enabled

    def play_music(self, music_file: Path, loop: bool = True):
        """
        Play background music.

        Args:
            music_file: Path to music file
            loop: True to loop indefinitely
        """
        if not self.initialized or not self.config.enable_music:
            return

        try:
            pygame.mixer.music.load(str(music_file))
            pygame.mixer.music.set_volume(self.config.music_volume * self.config.master_volume)
            pygame.mixer.music.play(loops=-1 if loop else 0)
        except pygame.error as e:
            print(f"Warning: Could not play music: {e}")

    def stop_music(self):
        """Stop background music."""
        if self.initialized:
            pygame.mixer.music.stop()

    def pause_music(self):
        """Pause background music."""
        if self.initialized:
            pygame.mixer.music.pause()

    def resume_music(self):
        """Resume background music."""
        if self.initialized:
            pygame.mixer.music.unpause()


# Global audio manager instance
audio_manager = AudioManager()


# Convenience functions
def play_sound(sound_type: SoundType):
    """Play a sound effect (convenience function)."""
    audio_manager.play(sound_type)


def play_success(perfect: bool = False):
    """Play success sound."""
    audio_manager.play_success(perfect)


def play_failure(is_syntax_error: bool = False):
    """Play failure sound."""
    audio_manager.play_failure(is_syntax_error)


def play_achievement():
    """Play achievement unlock sound."""
    audio_manager.play_achievement()


def play_level_up():
    """Play level up sound."""
    audio_manager.play_level_up()


# Self-teaching note:
#
# This file demonstrates:
# - pygame.mixer for audio playback (Level 5+)
# - Singleton pattern (global audio_manager instance)
# - Resource management (loading sound files)
# - Event-driven design (play sounds on events)
# - Enum for type-safe constants
# - Cooldown system to prevent audio spam
# - Volume control and mixing
#
# Audio feedback enhances UX by:
# - Providing immediate feedback on actions
# - Making success feel rewarding
# - Making progress tangible
# - Adding polish and professionalism
#
# Prerequisites:
# - Level 4: File paths, dictionaries
# - Level 5: Classes, dataclasses, resource management
# - Level 6: Design patterns, event systems
#
# Sound effects should be:
# - Short (< 1 second for UI, < 3 seconds for achievements)
# - Pleasant and not annoying
# - Distinct for different event types
# - Optional (players can mute)
