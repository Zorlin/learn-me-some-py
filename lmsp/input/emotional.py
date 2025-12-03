"""
Emotional Input System
======================

"Pull the right trigger progressively until you feel you've communicated
how happy you are - or if you didn't like that, use the left trigger.
Or press Y to enter a more complex answer."

This module handles emotional granularity via analog input.
Not clicking "happy" or "sad" - EXPRESSING on a spectrum.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Callable
import time


class EmotionalDimension(Enum):
    """The dimensions of emotional feedback we track."""
    ENJOYMENT = "enjoyment"           # RT: How fun was that?
    FRUSTRATION = "frustration"       # LT: How frustrating?
    CONFIDENCE = "confidence"         # How sure are you?
    CURIOSITY = "curiosity"           # Want to explore more?
    FLOW = "flow"                     # Were you in the zone?


@dataclass
class EmotionalSample:
    """A single emotional reading at a moment in time."""
    timestamp: float
    dimension: EmotionalDimension
    value: float  # 0.0 to 1.0, analog from trigger
    context: str  # What were they doing when sampled?

    def __post_init__(self):
        self.value = max(0.0, min(1.0, self.value))


@dataclass
class EmotionalState:
    """Current emotional state of the player."""
    samples: list[EmotionalSample] = field(default_factory=list)

    # Rolling averages per dimension
    _averages: dict[EmotionalDimension, float] = field(default_factory=dict)

    def record(self, dimension: EmotionalDimension, value: float, context: str = ""):
        """Record an emotional sample."""
        sample = EmotionalSample(
            timestamp=time.time(),
            dimension=dimension,
            value=value,
            context=context
        )
        self.samples.append(sample)
        self._update_average(dimension)

    def _update_average(self, dimension: EmotionalDimension):
        """Update rolling average for a dimension."""
        recent = [s for s in self.samples[-50:] if s.dimension == dimension]
        if recent:
            self._averages[dimension] = sum(s.value for s in recent) / len(recent)

    def get_enjoyment(self) -> float:
        """How much are they enjoying this?"""
        return self._averages.get(EmotionalDimension.ENJOYMENT, 0.5)

    def get_frustration(self) -> float:
        """How frustrated are they?"""
        return self._averages.get(EmotionalDimension.FRUSTRATION, 0.0)

    def is_in_flow(self) -> bool:
        """Are they in a flow state? High enjoyment, low frustration."""
        return self.get_enjoyment() > 0.7 and self.get_frustration() < 0.3

    def needs_break(self) -> bool:
        """Should we suggest a break?"""
        return self.get_frustration() > 0.7 or (
            self.get_enjoyment() < 0.3 and len(self.samples) > 20
        )


class EmotionalPrompt:
    """
    A prompt that asks for emotional feedback via controller.

    Usage:
        prompt = EmotionalPrompt(
            question="How are you feeling?",
            right_trigger="Pull to show happiness",
            left_trigger="Pull to show frustration",
            y_button="Press for complex answer"
        )
        response = await prompt.show(controller)
    """

    def __init__(
        self,
        question: str,
        right_trigger: str = "Happy",
        left_trigger: str = "Frustrated",
        y_button: Optional[str] = "More options",
        on_complex: Optional[Callable] = None
    ):
        self.question = question
        self.right_trigger = right_trigger
        self.left_trigger = left_trigger
        self.y_button = y_button
        self.on_complex = on_complex

        self._rt_value = 0.0
        self._lt_value = 0.0
        self._confirmed = False
        self._complex_requested = False

    def update(self, rt: float, lt: float, y_pressed: bool, a_pressed: bool):
        """Update from controller state."""
        self._rt_value = rt
        self._lt_value = lt

        if y_pressed and self.y_button:
            self._complex_requested = True

        if a_pressed and (rt > 0.1 or lt > 0.1):
            self._confirmed = True

    @property
    def is_confirmed(self) -> bool:
        return self._confirmed

    @property
    def wants_complex(self) -> bool:
        return self._complex_requested

    def get_response(self) -> tuple[EmotionalDimension, float]:
        """Get the emotional response."""
        if self._rt_value > self._lt_value:
            return EmotionalDimension.ENJOYMENT, self._rt_value
        else:
            return EmotionalDimension.FRUSTRATION, self._lt_value

    def render(self) -> str:
        """Render the prompt for display."""
        lines = [
            self.question,
            "",
            f"  [RT {'█' * int(self._rt_value * 10):10}] {self.right_trigger}",
            f"  [LT {'█' * int(self._lt_value * 10):10}] {self.left_trigger}",
        ]
        if self.y_button:
            lines.append(f"  [Y] {self.y_button}")
        lines.append("")
        lines.append("  Press A to confirm")
        return "\n".join(lines)


# Example usage and self-teaching comment:
#
# This file demonstrates:
# - Dataclasses (Level 5: Classes)
# - Enums (Level 2: Collections, advanced)
# - Type hints (Professional Python)
# - Properties and methods (Level 5: Classes)
# - Default factory for mutable defaults (gotcha!)
#
# When the player reaches this file in the codebase, they'll have
# already learned the prerequisites to understand it.
