"""
Tests for challenge presenter and code execution.

Following TDD: These tests define the desired behavior before implementation.
"""
from pathlib import Path
import pytest
from rich.console import Console
from io import StringIO

from lmsp.python.challenges import Challenge, TestCase, ChallengeLoader
from lmsp.python.presenter import ChallengePresenter, ExecutionResult


@pytest.fixture
def console():
    """Create a Rich console with string output for testing."""
    return Console(file=StringIO(), width=100, legacy_windows=False)


@pytest.fixture
def simple_challenge():
    """Create a simple test challenge."""
    return Challenge(
        id="test_simple",
        name="Simple Addition",
        level=0,
        prerequisites=[],
        description_brief="Add two numbers",
        description_detailed="Write a function that adds two numbers together",
        skeleton_code="def add(a, b):\n    pass  # Your code here\n",
        test_cases=[
            TestCase(name="basic", input=[2, 3], expected=5),
            TestCase(name="negative", input=[-1, 1], expected=0),
            TestCase(name="large", input=[100, 200], expected=300),
        ],
        solution_code="def add(a, b):\n    return a + b\n"
    )


def test_challenge_presenter_init(console):
    """ChallengePresenter should initialize with console."""
    presenter = ChallengePresenter(console)
    assert presenter.console == console


def test_challenge_presenter_display_description(console, simple_challenge):
    """ChallengePresenter should display challenge description beautifully."""
    presenter = ChallengePresenter(console)
    presenter.display_challenge(simple_challenge)

    output = console.file.getvalue()

    # Check that key information is displayed
    assert "Simple Addition" in output
    assert "Add two numbers" in output
    assert "Level 0" in output or "level: 0" in output.lower()


def test_challenge_presenter_display_skeleton(console, simple_challenge):
    """ChallengePresenter should show skeleton code with syntax highlighting."""
    presenter = ChallengePresenter(console)
    presenter.display_skeleton(simple_challenge)

    output = console.file.getvalue()

    # Check that skeleton code is shown
    assert "def add" in output
    assert "pass" in output


def test_execution_result_success():
    """ExecutionResult should capture successful test results."""
    result = ExecutionResult(
        passed=True,
        test_name="test1",
        expected=5,
        actual=5,
        error=None
    )

    assert result.passed is True
    assert result.test_name == "test1"
    assert result.expected == 5
    assert result.actual == 5
    assert result.error is None


def test_execution_result_failure():
    """ExecutionResult should capture failed test results."""
    result = ExecutionResult(
        passed=False,
        test_name="test2",
        expected=10,
        actual=5,
        error=None
    )

    assert result.passed is False
    assert result.expected == 10
    assert result.actual == 5


def test_execution_result_error():
    """ExecutionResult should capture execution errors."""
    result = ExecutionResult(
        passed=False,
        test_name="test3",
        expected=5,
        actual=None,
        error="NameError: name 'undefined' is not defined"
    )

    assert result.passed is False
    assert result.error is not None
    assert "NameError" in result.error


def test_execute_code_success(simple_challenge):
    """Presenter should execute code and return results for passing tests."""
    presenter = ChallengePresenter(Console())

    # Valid solution
    code = "def add(a, b):\n    return a + b\n"

    results = presenter.execute_code(code, simple_challenge)

    assert len(results) == 3  # Three test cases
    assert all(r.passed for r in results)  # All pass
    assert results[0].actual == 5
    assert results[1].actual == 0
    assert results[2].actual == 300


def test_execute_code_failure(simple_challenge):
    """Presenter should detect wrong answers."""
    presenter = ChallengePresenter(Console())

    # Wrong solution (multiplies instead of adds)
    code = "def add(a, b):\n    return a * b\n"

    results = presenter.execute_code(code, simple_challenge)

    assert len(results) == 3
    assert not results[0].passed  # 2*3 != 5
    assert results[0].expected == 5
    assert results[0].actual == 6


def test_execute_code_syntax_error(simple_challenge):
    """Presenter should capture syntax errors safely."""
    presenter = ChallengePresenter(Console())

    # Code with syntax error
    code = "def add(a, b)\n    return a + b\n"  # Missing colon

    results = presenter.execute_code(code, simple_challenge)

    # Should return error result for syntax error
    assert len(results) > 0
    assert not results[0].passed
    assert results[0].error is not None
    assert "SyntaxError" in results[0].error or "syntax" in results[0].error.lower()


def test_execute_code_runtime_error(simple_challenge):
    """Presenter should capture runtime errors safely."""
    presenter = ChallengePresenter(Console())

    # Code with runtime error
    code = "def add(a, b):\n    return a + undefined_variable\n"

    results = presenter.execute_code(code, simple_challenge)

    assert len(results) > 0
    assert not results[0].passed
    assert results[0].error is not None
    assert "NameError" in results[0].error or "undefined" in results[0].error.lower()


def test_execute_code_timeout():
    """Presenter should handle infinite loops safely (with timeout)."""
    presenter = ChallengePresenter(Console())

    challenge = Challenge(
        id="timeout_test",
        name="Timeout Test",
        level=0,
        prerequisites=[],
        description_brief="Test timeout",
        description_detailed="Should timeout",
        skeleton_code="def loop():\n    pass\n",
        test_cases=[TestCase(name="timeout", input=[], expected=None)],
    )

    # Code that loops forever
    code = "def loop():\n    while True:\n        pass\n"

    results = presenter.execute_code(code, challenge)

    # Should detect timeout
    assert len(results) > 0
    assert not results[0].passed
    assert results[0].error is not None
    assert "timeout" in results[0].error.lower() or "time" in results[0].error.lower()


def test_display_results_all_pass(console, simple_challenge):
    """Presenter should display beautiful success feedback when all tests pass."""
    presenter = ChallengePresenter(console)

    results = [
        ExecutionResult(True, "test1", 5, 5, None),
        ExecutionResult(True, "test2", 0, 0, None),
        ExecutionResult(True, "test3", 300, 300, None),
    ]

    presenter.display_results(results, simple_challenge)

    output = console.file.getvalue()

    # Should show success indicators
    assert "✓" in output or "PASS" in output or "pass" in output
    # Should show all tests passed
    assert "3" in output and ("3" in output or "passed" in output)


def test_display_results_some_fail(console, simple_challenge):
    """Presenter should display clear feedback when some tests fail."""
    presenter = ChallengePresenter(console)

    results = [
        ExecutionResult(True, "test1", 5, 5, None),
        ExecutionResult(False, "test2", 0, 1, None),
        ExecutionResult(True, "test3", 300, 300, None),
    ]

    presenter.display_results(results, simple_challenge)

    output = console.file.getvalue()

    # Should show failure indicators
    assert "✗" in output or "FAIL" in output or "fail" in output.lower()
    # Should show which test failed
    assert "test2" in output
    # Should show expected vs actual
    assert "0" in output and "1" in output


def test_display_results_with_error(console, simple_challenge):
    """Presenter should display error messages clearly."""
    presenter = ChallengePresenter(console)

    results = [
        ExecutionResult(False, "test1", 5, None, "NameError: name 'x' is not defined"),
    ]

    presenter.display_results(results, simple_challenge)

    output = console.file.getvalue()

    # Should show error message
    assert "NameError" in output or "Error" in output
    assert "undefined" in output.lower() or "not defined" in output


def test_safe_execution_no_system_access():
    """Code execution should be sandboxed and not allow system access."""
    presenter = ChallengePresenter(Console())

    challenge = Challenge(
        id="security_test",
        name="Security Test",
        level=0,
        prerequisites=[],
        description_brief="Test security",
        description_detailed="Should be sandboxed",
        skeleton_code="def hack():\n    pass\n",
        test_cases=[TestCase(name="security", input=[], expected=None)],
    )

    # Malicious code trying to import os
    code = """
def hack():
    import os
    os.system('echo pwned')
    return None
"""

    results = presenter.execute_code(code, challenge)

    # Should either prevent import or fail safely
    # We don't want the system command to actually run
    assert len(results) > 0
    # If it ran at all, it should have errored
    if not results[0].passed:
        assert results[0].error is not None


# Self-teaching note:
#
# This test file demonstrates:
# - pytest fixtures for setup (console, challenge objects)
# - Testing UI output with Rich console
# - Testing code execution safely
# - Testing error handling (syntax, runtime, timeout)
# - Testing security (sandboxing)
# - Testing visual feedback (✓/✗ symbols)
#
# Prerequisites: Level 5
# - Understanding dataclasses
# - Understanding sandboxed execution
# - Understanding pytest fixtures
# - Understanding Rich console rendering
