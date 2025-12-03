"""
LMSP Introspection System - Phase 5

Deep analysis capabilities for understanding game state, code, and player behavior.

This module provides:
- Screenshot capture with AST + game state metadata
- Wireframe generation (mental model of screen content)
- Strategic video recording (mosaic WebP tiles)
- TAS features (checkpoint/restore/rewind/step/diff)
- Progressive discovery primitives (/help, /checkpoint, /video)

Self-teaching note:
This file demonstrates:
- Module-level exports (__all__) for clean imports (Level 3: namespaces)
- Lazy imports to avoid circular dependencies (Level 5: advanced imports)
- Type annotations for documentation (Level 5: type hints)
"""

from lmsp.introspection.wireframe import Wireframe
from lmsp.introspection.screenshot import ScreenshotBundle
from lmsp.introspection.mosaic import Mosaic, Frame
from lmsp.introspection.video import VideoRecorder
from lmsp.introspection.tas import TASRecorder, TASEvent
from lmsp.introspection.primitives import (
    get_available_primitives,
    get_primitive_info,
    get_newly_unlocked,
    execute_primitive,
    PrimitiveContext,
    PrimitiveResult,
)

__all__ = [
    # Wireframe - mental model of game state
    "Wireframe",
    # Screenshot - visual capture + context
    "ScreenshotBundle",
    # Mosaic - grid of frames for Claude vision
    "Mosaic",
    "Frame",
    # Video recording
    "VideoRecorder",
    # TAS - Tool-Assisted Learning
    "TASRecorder",
    "TASEvent",
    # Discovery primitives
    "get_available_primitives",
    "get_primitive_info",
    "get_newly_unlocked",
    "execute_primitive",
    "PrimitiveContext",
    "PrimitiveResult",
]
