"""
TAS (Tool-Assisted Speedrun) Recording for Player-Zero

Enhanced TAS recording specifically for playtest replay and analysis.

Exports:
- PlaytestRecorder: Main recorder for capturing playtest sessions
- PlaytestEvent: Individual event data structure
- PlaytestSession: Complete session data
- EventType: Event type enumeration
- StruggleIndicator: Struggle detection types
"""

from lmsp.multiplayer.player_zero.tas.recorder import (
    PlaytestRecorder,
    PlaytestEvent,
    PlaytestSession,
    EventType,
    StruggleIndicator,
)

__all__ = [
    "PlaytestRecorder",
    "PlaytestEvent",
    "PlaytestSession",
    "EventType",
    "StruggleIndicator",
]
