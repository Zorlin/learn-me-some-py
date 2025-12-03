"""
Challenge Presenter with Rich UI and Safe Code Execution

This module provides:
1. Beautiful challenge presentation with Rich panels
2. Safe sandboxed code execution
3. Visual feedback (\u2713/\u2717) for test results
4. Syntax-highlighted code display

The presenter makes challenges feel polished and fun.
"""

from dataclasses import dataclass
from typing import List, Any, Optional
from io import StringIO
import sys
import traceback
import signal
from contextlib import contextmanager, redirect_stdout, redirect_stderr

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text
from rich import box

from lmsp.python.challenges import Challenge, TestCase


@dataclass
class ExecutionResult:
    """Result of executing user code against a test case."""

    passed: bool
    test_name: str
    expected: Any
    actual: Optional[Any]
    error: Optional[str] = None


class TimeoutException(Exception):
    """Raised when code execution times out."""
    pass


def timeout_handler(signum, frame):
    """Signal handler for timeout."""
    raise TimeoutException("Code execution timed out")


@contextmanager
def time_limit(seconds: int):
    """Context manager to limit execution time."""
    if seconds <= 0:
        yield
        return

    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)


class ChallengePresenter:
    """
    Presents challenges beautifully and executes code safely.

    Features:
    - Rich panel displays for challenge information
    - Syntax-highlighted code
    - Safe sandboxed execution
    - Visual test result feedback
    - Timeout protection
    """

    def __init__(self, console: Optional[Console] = None):
        """
        Initialize the presenter.

        Args:
            console: Rich Console instance (creates one if None)
        """
        self.console = console or Console()

    def display_challenge(self, challenge: Challenge) -> None:
        """
        Display challenge information beautifully.

        Args:
            challenge: The challenge to display
        """
        # Create title with level indicator
        title = f"[bold cyan]{challenge.name}[/] [dim](Level {challenge.level})[/]"

        # Build content
        lines = []
        lines.append(f"[bold]{challenge.description_brief}[/]")
        lines.append("")
        lines.append(challenge.description_detailed)
        lines.append("")

        # Prerequisites
        if challenge.prerequisites:
            lines.append("[bold]Prerequisites:[/]")
            for prereq in challenge.prerequisites:
                lines.append(f"  \u2022 {prereq}")
            lines.append("")

        # Rewards
        if challenge.points > 0:
            lines.append(f"[yellow]\u2b50 Points:[/] {challenge.points}")

        content = "\n".join(lines)

        panel = Panel(
            content,
            title=title,
            border_style="cyan",
            box=box.ROUNDED,
            padding=(1, 2),
        )

        self.console.print(panel)

    def display_skeleton(self, challenge: Challenge) -> None:
        """
        Display skeleton code with syntax highlighting.

        Args:
            challenge: The challenge with skeleton code
        """
        syntax = Syntax(
            challenge.skeleton_code,
            "python",
            theme="monokai",
            line_numbers=True,
            word_wrap=False,
        )

        panel = Panel(
            syntax,
            title="[bold]Starting Code[/]",
            border_style="blue",
            box=box.ROUNDED,
        )

        self.console.print(panel)

    def execute_code(
        self,
        code: str,
        challenge: Challenge,
        timeout_seconds: int = 5,
    ) -> List[ExecutionResult]:
        """
        Execute user code safely against test cases.

        Args:
            code: User's Python code
            challenge: The challenge with test cases
            timeout_seconds: Maximum execution time per test

        Returns:
            List of execution results for each test case
        """
        results = []

        # First, try to compile the code
        try:
            compiled_code = compile(code, "<user_code>", "exec")
        except SyntaxError as e:
            # Syntax error - return error for all tests
            error_msg = f"SyntaxError: {e.msg} (line {e.lineno})"
            for test_case in challenge.test_cases:
                results.append(ExecutionResult(
                    passed=False,
                    test_name=test_case.name,
                    expected=test_case.expected,
                    actual=None,
                    error=error_msg,
                ))
            return results

        # Execute against each test case
        for test_case in challenge.test_cases:
            result = self._execute_single_test(
                compiled_code,
                code,
                test_case,
                timeout_seconds,
            )
            results.append(result)

        return results

    def _execute_single_test(
        self,
        compiled_code,
        source_code: str,
        test_case: TestCase,
        timeout_seconds: int,
    ) -> ExecutionResult:
        """Execute code against a single test case."""
        # Create isolated namespace
        namespace = {
            "__builtins__": {
                # Allow safe built-ins only
                "print": print,
                "len": len,
                "range": range,
                "str": str,
                "int": int,
                "float": float,
                "bool": bool,
                "list": list,
                "dict": dict,
                "tuple": tuple,
                "set": set,
                "max": max,
                "min": min,
                "sum": sum,
                "abs": abs,
                "round": round,
                "sorted": sorted,
                "enumerate": enumerate,
                "zip": zip,
                "map": map,
                "filter": filter,
                # Block dangerous operations
                "__import__": None,
                "open": None,
                "eval": None,
                "exec": None,
                "compile": None,
            }
        }

        try:
            # Redirect output
            stdout = StringIO()
            stderr = StringIO()

            with redirect_stdout(stdout), redirect_stderr(stderr):
                with time_limit(timeout_seconds):
                    # Execute user code
                    exec(compiled_code, namespace)

                    # Find the function to test
                    # (assumes function name matches challenge or is obvious)
                    func_name = self._find_function_name(source_code)

                    if func_name and func_name in namespace:
                        func = namespace[func_name]

                        # Call with test input
                        if isinstance(test_case.input, list):
                            actual = func(*test_case.input)
                        else:
                            actual = func(test_case.input)

                        # Compare result
                        passed = actual == test_case.expected

                        return ExecutionResult(
                            passed=passed,
                            test_name=test_case.name,
                            expected=test_case.expected,
                            actual=actual,
                            error=None,
                        )
                    else:
                        # Couldn't find function
                        return ExecutionResult(
                            passed=False,
                            test_name=test_case.name,
                            expected=test_case.expected,
                            actual=None,
                            error=f"Could not find function '{func_name}' in code",
                        )

        except TimeoutException:
            return ExecutionResult(
                passed=False,
                test_name=test_case.name,
                expected=test_case.expected,
                actual=None,
                error="Code execution timed out (infinite loop?)",
            )
        except Exception as e:
            # Runtime error
            error_msg = f"{type(e).__name__}: {str(e)}"
            return ExecutionResult(
                passed=False,
                test_name=test_case.name,
                expected=test_case.expected,
                actual=None,
                error=error_msg,
            )

    def _find_function_name(self, code: str) -> Optional[str]:
        """
        Find the main function name in user code.

        Looks for def statements and returns the first function name found.
        """
        import re
        match = re.search(r'def\s+(\w+)\s*\(', code)
        if match:
            return match.group(1)
        return None

    def display_results(
        self,
        results: List[ExecutionResult],
        challenge: Challenge,
    ) -> None:
        """
        Display test results with visual feedback.

        Args:
            results: List of execution results
            challenge: The challenge being tested
        """
        # Calculate summary
        passed_count = sum(1 for r in results if r.passed)
        total_count = len(results)
        all_passed = passed_count == total_count

        # Create results table
        table = Table(
            title=f"[bold]Test Results: {passed_count}/{total_count} passed[/]",
            box=box.SIMPLE,
            show_header=True,
            header_style="bold",
        )

        table.add_column("Status", justify="center", width=6)
        table.add_column("Test", style="cyan")
        table.add_column("Expected", style="yellow")
        table.add_column("Got", style="magenta")
        table.add_column("Error", style="red")

        # Add rows for each result
        for result in results:
            if result.passed:
                status = "[green]\u2713[/]"
                expected_str = str(result.expected)
                actual_str = str(result.actual)
                error_str = ""
            else:
                status = "[red]\u2717[/]"
                expected_str = str(result.expected)
                actual_str = str(result.actual) if result.actual is not None else "[dim]N/A[/]"
                error_str = result.error or ""

            table.add_row(
                status,
                result.test_name,
                expected_str,
                actual_str,
                error_str,
            )

        # Choose border color based on success
        border_style = "green" if all_passed else "red"

        panel = Panel(
            table,
            border_style=border_style,
            box=box.ROUNDED,
            padding=(1, 1),
        )

        self.console.print(panel)

        # Celebration or encouragement
        if all_passed:
            self.console.print("\n[bold green]\u2728 All tests passed! Excellent work! \u2728[/]\n")
        else:
            self.console.print(f"\n[yellow]Keep trying! {passed_count} out of {total_count} tests passing.[/]")
            self.console.print("[dim]Hint: Check the error messages above for clues.[/]\n")


# Self-teaching note:
#
# This file demonstrates:
# - Safe code execution with sandboxing (Level 6: Security)
# - Context managers for resource management (Level 5: Context managers)
# - Signal handling for timeouts (Level 6: OS interaction)
# - Rich UI for beautiful displays (Level 5-6: UI frameworks)
# - Regular expressions for parsing (Level 4: Regex)
# - Error handling and user feedback (Level 3-4: Exceptions)
# - Dataclasses for structured results (Level 5: Dataclasses)
#
# Key security concepts:
# 1. Restricted __builtins__ prevents dangerous operations
# 2. Timeout protection prevents infinite loops
# 3. Isolated namespace prevents code interference
# 4. Output redirection captures print statements safely
#
# Prerequisites:
# - Level 3: Functions, exceptions, error handling
# - Level 4: Regular expressions, collections
# - Level 5: Context managers, dataclasses
# - Level 6: Security patterns, sandboxing
#
# Professional Python projects use similar patterns for:
# - Online code judges (LeetCode, HackerRank)
# - Jupyter notebooks
# - Testing frameworks
# - Educational platforms
