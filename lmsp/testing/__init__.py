"""
Testing utilities for LMSP.

This module provides helpers for integration testing, particularly
Playwright MCP integration for web UI testing, and AI-driven UX discovery.
"""

from lmsp.testing.playwright_helpers import (
    PlaywrightLMSPHelper,
    ChallengeStateAssertions,
    EmotionalFeedbackAssertions,
    AchievementAssertions,
    CodeEditorAssertions,
)

from lmsp.testing.web_playtester import WebPlaytester

__all__ = [
    "PlaywrightLMSPHelper",
    "ChallengeStateAssertions",
    "EmotionalFeedbackAssertions",
    "AchievementAssertions",
    "CodeEditorAssertions",
    "WebPlaytester",
]
