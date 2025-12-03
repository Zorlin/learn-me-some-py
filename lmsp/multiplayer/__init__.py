"""
LMSP Multiplayer System

Phase 4: Player-Zero Integration for Multiplayer Learning

This module provides multiplayer capabilities including:
- Claude AI players via API
- Session sync for shared state
- Split-screen UI
- Player awareness (cursors, thoughts, emotions)
- Chat and communication
- Multiple session modes (coop, race, teach, spectator, swarm)

Self-teaching note:
This file demonstrates:
- Module-level exports (Level 0: import system)
- __all__ for controlling what gets imported (Level 3: namespaces)
- Type annotations for classes and functions (Level 5: type hints)
- Graceful degradation for optional dependencies (professional pattern)
"""

from lmsp.multiplayer.awareness import AwarenessTracker, PlayerState

# Multiplayer is optional - only import if anthropic available
_multiplayer_available = False
try:
    from lmsp.multiplayer.claude_player import ClaudePlayer, TeachingStyle
    from lmsp.multiplayer.session_sync import SessionSync, SessionMode
    from lmsp.multiplayer.calibration import SkillCalibration, MistakeGenerator
    _multiplayer_available = True
except ImportError:
    # anthropic not installed - multiplayer disabled
    ClaudePlayer = None
    TeachingStyle = None
    SessionSync = None
    SessionMode = None
    SkillCalibration = None
    MistakeGenerator = None

__all__ = [
    "ClaudePlayer",
    "TeachingStyle",
    "AwarenessTracker",
    "PlayerState",
    "SessionSync",
    "SessionMode",
    "SkillCalibration",
    "MistakeGenerator",
    "_multiplayer_available",
]
