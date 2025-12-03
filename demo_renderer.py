#!/usr/bin/env python
"""
Demo script to showcase the LMSP renderer.

Run this to see what the game's UI will look like!
"""

from lmsp.game.renderer import RichRenderer
from lmsp.python.challenges import Challenge, TestCase
from lmsp.python.validator import ValidationResult, TestResult
from lmsp.input.emotional import EmotionalPrompt
from lmsp.adaptive.engine import AdaptiveRecommendation


def demo():
    """Run through all renderer capabilities."""
    renderer = RichRenderer()

    # 1. Show a challenge
    challenge = Challenge(
        id="loops_001",
        name="Your First Loop",
        level=1,
        prerequisites=[],
        description_brief="Learn to iterate with for loops",
        description_detailed=(
            "A for loop lets you repeat code for each item in a sequence.\n\n"
            "In this challenge, you'll write a function that prints numbers from 1 to 10.\n\n"
            "Concepts covered:\n"
            "  • for loops\n"
            "  • range() function\n"
            "  • print() function"
        ),
        skeleton_code=(
            "def solution():\n"
            "    # Write a for loop that prints 1 through 10\n"
            "    pass"
        ),
        test_cases=[
            TestCase(name="basic", input=None, expected="1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n"),
        ],
        hints={
            1: "Use range() to generate numbers",
            2: "for i in range(1, 11) will give you 1-10",
            3: "Don't forget to print each number!"
        }
    )

    print("\n" + "=" * 80)
    print("1. CHALLENGE DISPLAY")
    print("=" * 80)
    renderer.render_challenge(challenge)
    input("\nPress Enter to continue...")

    # 2. Show code editor
    code = """def solution():
    for i in range(1, 11):
        print(i)"""

    print("\n" + "=" * 80)
    print("2. CODE EDITOR")
    print("=" * 80)
    renderer.render_code_editor(code, (2, 8))
    input("\nPress Enter to continue...")

    # 3. Show test results (passing)
    print("\n" + "=" * 80)
    print("3. TEST RESULTS (ALL PASS)")
    print("=" * 80)
    results_pass = ValidationResult(
        success=True,
        output="1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n",
        error=None,
        time_seconds=0.042,
        test_results=[
            TestResult(
                test_name="basic",
                passed=True,
                expected="1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n",
                actual="1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n"
            ),
            TestResult(
                test_name="edge_case",
                passed=True,
                expected="correct",
                actual="correct"
            ),
        ]
    )
    renderer.render_test_results(results_pass)
    input("\nPress Enter to continue...")

    # 4. Show test results (failing)
    print("\n" + "=" * 80)
    print("4. TEST RESULTS (SOME FAIL)")
    print("=" * 80)
    results_fail = ValidationResult(
        success=False,
        output="1\n2\n3\n",
        error=None,
        time_seconds=0.018,
        test_results=[
            TestResult(
                test_name="basic",
                passed=False,
                expected="1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n",
                actual="1\n2\n3\n"
            ),
            TestResult(
                test_name="error_case",
                passed=False,
                expected=42,
                actual=None,
                error="ZeroDivisionError: division by zero"
            ),
        ]
    )
    renderer.render_test_results(results_fail)
    input("\nPress Enter to continue...")

    # 5. Show emotional prompt
    print("\n" + "=" * 80)
    print("5. EMOTIONAL PROMPT")
    print("=" * 80)
    prompt = EmotionalPrompt(
        question="How did that challenge feel?",
        right_trigger="I enjoyed it!",
        left_trigger="That was frustrating",
        y_button="Tell me more about how you felt"
    )
    # Simulate some trigger pressure
    prompt._rt_value = 0.7
    prompt._lt_value = 0.2
    renderer.render_emotional_prompt(prompt)
    input("\nPress Enter to continue...")

    # 6. Show adaptive recommendation
    print("\n" + "=" * 80)
    print("6. ADAPTIVE RECOMMENDATION")
    print("=" * 80)
    recommendation = AdaptiveRecommendation(
        action="challenge",
        concept="list_comprehensions",
        challenge_id="lists_003",
        reason="You're doing great with loops! Let's level up to list comprehensions.",
        confidence=0.85
    )
    renderer.render_recommendation(recommendation)
    input("\nPress Enter to continue...")

    # 7. Show different message types
    print("\n" + "=" * 80)
    print("7. MESSAGES")
    print("=" * 80)
    renderer.show_message("Welcome to LMSP!", "info")
    renderer.show_message("Challenge completed!", "success")
    renderer.show_message("Consider taking a break", "warning")
    renderer.show_message("Syntax error in your code", "error")
    print()

    print("\n" + "=" * 80)
    print("Demo complete! This is what LMSP will look like.")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    demo()
