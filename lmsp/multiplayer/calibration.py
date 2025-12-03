"""
Skill Calibration - Fair Racing and AI Difficulty

Calibrates AI performance to match human skill level, creating
fair and engaging competitive races.

Features:
- Thinking time adjustment based on skill level
- Realistic mistake generation
- Approach selection (simple vs. advanced)
- Adaptive difficulty

Self-teaching note:
This file demonstrates:
- Random number generation (Level 4: random module)
- Statistical patterns (Level 6: probability)
- Strategy pattern (Level 6: design patterns)
- Class-based configuration (Level 5: classes)
"""

import random
import re
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Callable


class SkillLevel(Enum):
    """Predefined skill levels."""
    BEGINNER = 0.2
    INTERMEDIATE = 0.5
    ADVANCED = 0.7
    EXPERT = 1.0


@dataclass
class MistakePattern:
    """A realistic mistake pattern."""
    pattern_name: str
    description: str
    probability_at_skill_0: float  # Probability at beginner level
    apply_function: Callable[[str], tuple[str, str]]  # (code) -> (buggy_code, description)


class SkillCalibration:
    """
    Calibrate AI performance to match human skill level.

    Skill level ranges from 0.0 (beginner) to 1.0 (expert).
    """

    @staticmethod
    def calibrate_thinking_time(skill_level: float, base_time: float) -> float:
        """
        Adjust thinking time based on skill level.

        Args:
            skill_level: 0.0 (beginner) to 1.0 (expert)
            base_time: Base thinking time in seconds

        Returns:
            Calibrated thinking time

        Higher skill = faster thinking (to a point).
        """
        # Expert: 0.5x base time
        # Beginner: 2.0x base time
        multiplier = 2.0 - (skill_level * 1.5)
        return base_time * multiplier

    @staticmethod
    def should_make_mistake(skill_level: float) -> bool:
        """
        Determine if AI should make a realistic mistake.

        Args:
            skill_level: 0.0 (beginner) to 1.0 (expert)

        Returns:
            True if should make a mistake

        Lower skill = more mistakes.
        """
        mistake_probability = 0.3 * (1.0 - skill_level)
        return random.random() < mistake_probability

    @staticmethod
    def choose_approach(skill_level: float, challenge: Optional[dict] = None) -> str:
        """
        Choose solution approach based on skill level.

        Args:
            skill_level: 0.0 (beginner) to 1.0 (expert)
            challenge: Optional challenge data

        Returns:
            Approach name

        Lower skill = simpler, more verbose approaches.
        Higher skill = concise, idiomatic Python.
        """
        if skill_level < 0.3:
            # Beginner: Most explicit approach
            return "explicit_loops"

        elif skill_level < 0.6:
            # Intermediate: Mix of styles
            return random.choice(["explicit_loops", "built_in_functions"])

        elif skill_level < 0.8:
            # Advanced: Idiomatic Python
            return "comprehensions"

        else:
            # Expert: Most concise
            return random.choice(["comprehensions", "functional"])

    @staticmethod
    def apply_calibration(
        player: "ClaudePlayer",  # type: ignore
        skill_level: float
    ):
        """
        Apply skill calibration to a Claude player.

        Args:
            player: ClaudePlayer instance
            skill_level: Target skill level

        Updates player's timing, mistakes, and approach preference.
        """
        player.skill_level = skill_level

        # Adjust thinking delays
        player.base_thinking_time = SkillCalibration.calibrate_thinking_time(
            skill_level,
            base_time=2.0
        )

        # Configure mistake generation
        player.mistake_probability = 0.3 * (1.0 - skill_level)

        # Set approach preference
        player.approach_preference = SkillCalibration.choose_approach(
            skill_level,
            challenge=None  # Will be set per challenge
        )

        import logging
        logging.info(
            f"Calibrated {player.name} to skill level {skill_level:.2f}: "
            f"think_time={player.base_thinking_time:.1f}s, "
            f"mistakes={player.mistake_probability:.1%}"
        )


class MistakeGenerator:
    """Generate realistic mistakes for calibrated AI players."""

    # Common mistakes by skill level
    BEGINNER_MISTAKES = [
        "forget_colon",
        "wrong_indentation",
        "undefined_variable",
        "typo_in_keyword"
    ]

    INTERMEDIATE_MISTAKES = [
        "off_by_one",
        "wrong_comparison_operator",
        "forget_return",
        "mutable_default_argument"
    ]

    ADVANCED_MISTAKES = [
        "shallow_copy_issue",
        "late_binding_closure",
        "generator_exhaustion"
    ]

    @staticmethod
    def inject_mistake(
        code: str,
        skill_level: float
    ) -> tuple[str, str]:
        """
        Inject a realistic mistake into code.

        Args:
            code: Clean Python code
            skill_level: AI skill level (0.0 to 1.0)

        Returns:
            (buggy_code, mistake_description)
        """

        # Choose mistake category based on skill level
        if skill_level < 0.4:
            mistakes = MistakeGenerator.BEGINNER_MISTAKES
        elif skill_level < 0.7:
            mistakes = MistakeGenerator.INTERMEDIATE_MISTAKES
        else:
            mistakes = MistakeGenerator.ADVANCED_MISTAKES

        # Pick random mistake type
        mistake_type = random.choice(mistakes)

        # Apply the mistake
        if mistake_type == "forget_colon":
            # Remove colon from function/loop definition
            buggy = re.sub(r'(def \w+\([^)]*\)):', r'\1', code, count=1)
            return buggy, "Forgot colon after function definition"

        elif mistake_type == "wrong_indentation":
            # Dedent one line incorrectly
            lines = code.split('\n')
            if len(lines) > 3:
                idx = random.randint(2, len(lines) - 1)
                if lines[idx].startswith('    '):
                    lines[idx] = lines[idx][4:]  # Remove one indent level
            return '\n'.join(lines), "Wrong indentation"

        elif mistake_type == "off_by_one":
            # Change range(n) to range(n-1) or range(n+1)
            buggy = re.sub(r'range\((\w+)\)', r'range(\1 - 1)', code)
            return buggy, "Off-by-one error in range"

        elif mistake_type == "undefined_variable":
            # Use variable before defining
            buggy = re.sub(r'(\w+)\s*=\s*', r'temp_var = \1\n    \1 = ', code, count=1)
            return buggy, "Used variable before definition"

        elif mistake_type == "typo_in_keyword":
            # Common typos in keywords
            typos = {
                'def': 'deff',
                'return': 'retrun',
                'import': 'improt',
                'while': 'whiel',
            }
            for correct, typo in typos.items():
                if correct in code:
                    buggy = code.replace(correct, typo, 1)
                    return buggy, f"Typo in keyword: {typo}"

        elif mistake_type == "wrong_comparison_operator":
            # Use = instead of ==
            buggy = re.sub(r'if\s+(\w+)\s*==', r'if \1 =', code)
            return buggy, "Used = instead of == in comparison"

        elif mistake_type == "forget_return":
            # Remove return statement
            buggy = re.sub(r'\s*return\s+', r'    # return ', code)
            return buggy, "Forgot to return value"

        elif mistake_type == "mutable_default_argument":
            # Add mutable default argument
            buggy = re.sub(r'def (\w+)\([^)]*\)', r'def \1(items=[])', code, count=1)
            return buggy, "Mutable default argument"

        elif mistake_type == "shallow_copy_issue":
            # Use = instead of .copy()
            buggy = re.sub(r'\.copy\(\)', r'', code)
            return buggy, "Shallow copy issue"

        elif mistake_type == "late_binding_closure":
            # Lambda captures reference not value
            buggy = re.sub(
                r'lambda x: x \* (\w+)',
                r'lambda x, y=\1: x * y',
                code
            )
            return buggy, "Late binding closure issue"

        elif mistake_type == "generator_exhaustion":
            # Reuse exhausted generator
            buggy = re.sub(
                r'for item in (\w+):',
                r'gen = \1\n    for item in gen:\n    # Second loop won\'t work:\n    for item in gen:',
                code
            )
            return buggy, "Generator exhaustion"

        # Fallback: no mistake
        return code, "No mistake injected"

    @staticmethod
    def get_mistake_patterns() -> list[MistakePattern]:
        """
        Get all mistake patterns with apply functions.

        Returns:
            List of MistakePattern objects
        """
        patterns = []

        # Beginner patterns
        patterns.append(MistakePattern(
            pattern_name="forget_colon",
            description="Forgot colon after function definition",
            probability_at_skill_0=0.3,
            apply_function=lambda code: (
                re.sub(r'(def \w+\([^)]*\)):', r'\1', code, count=1),
                "Forgot colon"
            )
        ))

        patterns.append(MistakePattern(
            pattern_name="wrong_indentation",
            description="Incorrect indentation level",
            probability_at_skill_0=0.25,
            apply_function=lambda code: (
                code.replace('    ', '  ', 1) if '    ' in code else (code, "No change"),
                "Wrong indentation"
            )[0:2]
        ))

        # Intermediate patterns
        patterns.append(MistakePattern(
            pattern_name="off_by_one",
            description="Off-by-one error in range",
            probability_at_skill_0=0.15,
            apply_function=lambda code: (
                re.sub(r'range\((\w+)\)', r'range(\1 - 1)', code),
                "Off-by-one error"
            )
        ))

        # Advanced patterns
        patterns.append(MistakePattern(
            pattern_name="mutable_default",
            description="Mutable default argument",
            probability_at_skill_0=0.05,
            apply_function=lambda code: (
                re.sub(r'def (\w+)\((\w+)=None\)', r'def \1(\2=[])', code),
                "Mutable default"
            )
        ))

        return patterns


# Self-teaching note:
#
# This file demonstrates:
# - Random number generation for realistic behavior
# - Regular expressions for code transformation
# - Probability and statistics (mistake rates)
# - Dataclasses with callable fields
# - Enum for predefined levels
# - Static methods for utility functions
#
# Key concepts:
# 1. Skill calibration - adjust AI to match human level
# 2. Probabilistic mistakes - realistic errors based on skill
# 3. Regex transformations - modify code patterns
# 4. Strategy pattern - different approaches by skill
# 5. Mistake injection - educational buggy code
#
# The learner will encounter this AFTER mastering:
# - Level 4: Random, regex basics
# - Level 5: Classes, dataclasses
# - Level 6: Design patterns, probability
#
# This is professional Python for AI calibration - the same patterns
# used in game AI, educational tools, and adaptive systems!
