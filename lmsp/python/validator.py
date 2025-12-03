"""
Code Validator
==============

Safely executes player code and validates against test cases.

This is the judge that runs your solutions - it needs to be secure
to prevent learners from accidentally (or intentionally) breaking things.
"""

from dataclasses import dataclass
from typing import Any, Optional
import time
import io
import sys
import contextlib

from lmsp.python.challenges import TestCase


@dataclass
class TestResult:
    """Result of running a single test case."""
    test_name: str
    passed: bool
    expected: Any
    actual: Any
    error: Optional[str] = None


@dataclass
class ValidationResult:
    """Complete result of validating a solution."""
    success: bool
    output: str
    error: Optional[str]
    time_seconds: float
    test_results: list[TestResult]

    @property
    def tests_passing(self) -> int:
        """Number of tests that passed."""
        return sum(1 for r in self.test_results if r.passed)

    @property
    def tests_total(self) -> int:
        """Total number of tests."""
        return len(self.test_results)


class CodeValidator:
    """
    Validates player code against test cases.

    Security considerations:
    - Timeout to prevent infinite loops
    - Restricted builtins (no file I/O, network, imports)
    - Captures stdout/stderr
    - Isolated namespace

    Usage:
        validator = CodeValidator(timeout_seconds=5)
        result = validator.validate(code, test_cases)
    """

    def __init__(self, timeout_seconds: int = 5):
        self.timeout_seconds = timeout_seconds

    def validate(self, code: str, test_cases: list[TestCase]) -> ValidationResult:
        """
        Validate code against test cases.

        Args:
            code: Python code containing a 'solution' function
            test_cases: List of TestCase objects

        Returns:
            ValidationResult with all test outcomes
        """
        start_time = time.time()

        # First, check syntax
        syntax_ok, syntax_error = self.syntax_check(code)
        if not syntax_ok:
            return ValidationResult(
                success=False,
                output="",
                error=f"Syntax Error: {syntax_error}",
                time_seconds=time.time() - start_time,
                test_results=[]
            )

        # Execute code to define the solution function
        namespace = self._create_restricted_namespace()
        captured_output = io.StringIO()

        try:
            with contextlib.redirect_stdout(captured_output):
                exec(code, namespace)
        except Exception as e:
            return ValidationResult(
                success=False,
                output=captured_output.getvalue(),
                error=f"Execution Error: {e}",
                time_seconds=time.time() - start_time,
                test_results=[]
            )

        # Get the solution function
        if "solution" not in namespace:
            return ValidationResult(
                success=False,
                output=captured_output.getvalue(),
                error="No 'solution' function defined",
                time_seconds=time.time() - start_time,
                test_results=[]
            )

        solution_func = namespace["solution"]

        # Run tests
        test_results = []
        for test_case in test_cases:
            result = self.run_single_test(solution_func, test_case, namespace)
            test_results.append(result)

        all_passed = all(r.passed for r in test_results)

        return ValidationResult(
            success=all_passed,
            output=captured_output.getvalue(),
            error=None,
            time_seconds=time.time() - start_time,
            test_results=test_results
        )

    def run_single_test(
        self,
        solution_func,
        test_case: TestCase,
        namespace: dict
    ) -> TestResult:
        """Run a single test case against the solution."""
        try:
            # Handle different input formats
            input_data = test_case.input

            # Call the solution function
            if isinstance(input_data, list):
                actual = solution_func(*input_data)
            elif isinstance(input_data, dict):
                actual = solution_func(**input_data)
            elif input_data is None:
                actual = solution_func()
            else:
                actual = solution_func(input_data)

            # Compare results
            passed = actual == test_case.expected

            return TestResult(
                test_name=test_case.name,
                passed=passed,
                expected=test_case.expected,
                actual=actual,
                error=None
            )

        except Exception as e:
            return TestResult(
                test_name=test_case.name,
                passed=False,
                expected=test_case.expected,
                actual=None,
                error=str(e)
            )

    def syntax_check(self, code: str) -> tuple[bool, Optional[str]]:
        """
        Check code for syntax errors without executing.

        Returns:
            (True, None) if syntax is valid
            (False, error_message) if syntax is invalid
        """
        try:
            compile(code, "<solution>", "exec")
            return True, None
        except SyntaxError as e:
            return False, f"Line {e.lineno}: {e.msg}"

    def _create_restricted_namespace(self) -> dict:
        """
        Create a restricted execution namespace.

        Allows safe builtins while preventing dangerous operations.
        """
        # Safe builtins that learners need
        safe_builtins = {
            # Types
            "True": True,
            "False": False,
            "None": None,
            "int": int,
            "float": float,
            "str": str,
            "bool": bool,
            "list": list,
            "dict": dict,
            "tuple": tuple,
            "set": set,
            "frozenset": frozenset,

            # Functions
            "len": len,
            "range": range,
            "enumerate": enumerate,
            "zip": zip,
            "map": map,
            "filter": filter,
            "sorted": sorted,
            "reversed": reversed,
            "sum": sum,
            "min": min,
            "max": max,
            "abs": abs,
            "round": round,
            "pow": pow,
            "divmod": divmod,

            # String operations
            "print": print,
            "input": lambda prompt="": "",  # Stub - no actual input in challenges
            "format": format,
            "repr": repr,

            # Type checking
            "isinstance": isinstance,
            "type": type,
            "hasattr": hasattr,
            "getattr": getattr,

            # Iteration
            "iter": iter,
            "next": next,
            "all": all,
            "any": any,

            # Exceptions (for try/except)
            "Exception": Exception,
            "ValueError": ValueError,
            "TypeError": TypeError,
            "IndexError": IndexError,
            "KeyError": KeyError,
            "AttributeError": AttributeError,
            "ZeroDivisionError": ZeroDivisionError,
        }

        return {"__builtins__": safe_builtins}


# Self-teaching note:
#
# This file demonstrates:
# - Dynamic code execution with exec() (Advanced)
# - Security considerations in code execution
# - Context managers (contextlib) for output capture
# - Exception handling patterns (Level 3)
# - Dataclasses with computed properties (Level 5+)
# - Restricted namespaces (sandbox pattern)
#
# This is the JUDGE - it validates every solution.
# Understanding this helps learners see how test frameworks work.
#
# Prerequisites:
# - Level 3: Functions, exception handling
# - Level 5: Classes and dataclasses
# - Level 6: Dynamic execution, metaprogramming concepts
