"""
Playtest analysis module for processing AI playtest data.

Provides tools for:
- Analyzing playtest sessions from AI players
- Identifying UX issues (confusion, broken flows, missing hints, difficulty spikes)
- Generating structured improvement tasks

Self-teaching note:

This file demonstrates:
- Package initialization with selective exports (Level 2: imports)
- __all__ for explicit public API definition (Level 3: modules)

The learner will encounter this AFTER mastering basic imports.
"""

from lmsp.playtest.analyzer import (
    PlaytestAnalyzer,
    PlaytestSession,
    PlaytestEvent,
    PlaytestIssue,
    ImprovementTask,
    AnalysisResult,
    BatchAnalysisResult,
    IssueType,
)

__all__ = [
    "PlaytestAnalyzer",
    "PlaytestSession",
    "PlaytestEvent",
    "PlaytestIssue",
    "ImprovementTask",
    "AnalysisResult",
    "BatchAnalysisResult",
    "IssueType",
]
