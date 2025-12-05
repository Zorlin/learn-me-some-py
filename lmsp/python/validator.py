"""
Code Validator
==============

Safely executes player code and validates against test cases.

Supports two validation modes:
1. Legacy mode: Uses TOML-defined test cases with a solution() function
2. Pytest mode: Uses per-challenge test_*.py files for tailored validation

This is the judge that runs your solutions - it needs to be secure
to prevent learners from accidentally (or intentionally) breaking things.
"""

from dataclasses import dataclass
from typing import Any, Optional
import time
import io
import sys
import contextlib
import subprocess
import tempfile
import json
from pathlib import Path

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
    stdout: str = ""  # Captured print() output from user code

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

        Supports two modes:
        1. Function mode: Code defines a 'solution' function, tests pass inputs
        2. Script mode: Code is executed, stdout is compared to expected output
           (For Level 0 challenges that just print results)

        Args:
            code: Python code (with solution function or simple script)
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

        # Determine validation mode from test cases BEFORE executing code
        # (Interactive mode uses input() which would fail without stdin mock)
        def is_interactive_mode_test(tc):
            has_input = tc.input is not None and tc.input != []
            expected_is_output = (
                isinstance(tc.expected, str) or
                (isinstance(tc.expected, list) and all(isinstance(e, str) for e in tc.expected))
            )
            return has_input and expected_is_output

        use_interactive_mode = test_cases and all(
            is_interactive_mode_test(tc) for tc in test_cases
        )

        if use_interactive_mode:
            # Interactive mode: mock stdin, run code for each test, compare stdout
            # Must handle BEFORE regular exec since input() would block/fail
            return self._validate_interactive_mode(
                code, test_cases, start_time
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

        # Check if we have a solution function or should use script mode
        has_solution_func = "solution" in namespace
        output_text = captured_output.getvalue()

        # Script mode: tests expect stdout output (expected is string/list, no/empty input)
        def is_script_mode_test(tc):
            # Input should be None or empty list
            no_input = tc.input is None or tc.input == []
            # Expected should be string or list of strings
            expected_is_output = (
                isinstance(tc.expected, str) or
                (isinstance(tc.expected, list) and all(isinstance(e, str) for e in tc.expected))
            )
            return no_input and expected_is_output

        use_script_mode = not has_solution_func and test_cases and all(
            is_script_mode_test(tc) for tc in test_cases
        )

        if use_script_mode:
            # Script mode: compare stdout to expected output
            return self._validate_script_mode(
                output_text, test_cases, start_time
            )

        # Function mode: require solution function
        if not has_solution_func:
            # Try to be helpful about what's wrong
            if output_text.strip():
                # Code produced output - might be script mode attempt
                return ValidationResult(
                    success=False,
                    output=output_text,
                    error="No 'solution' function defined. If this is a Level 0 challenge, make sure your output matches exactly.",
                    time_seconds=time.time() - start_time,
                    test_results=[]
                )
            return ValidationResult(
                success=False,
                output=output_text,
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
            output=output_text,
            error=None,
            time_seconds=time.time() - start_time,
            test_results=test_results
        )

    def _validate_script_mode(
        self,
        output: str,
        test_cases: list[TestCase],
        start_time: float
    ) -> ValidationResult:
        """
        Validate script output against expected strings.

        For Level 0 challenges where learners just print output.
        """
        test_results = []
        output_lines = output.strip().split('\n') if output.strip() else []

        for i, test_case in enumerate(test_cases):
            # Handle expected as string or list of strings
            if isinstance(test_case.expected, list):
                # For list expected, join with newlines for comparison
                expected = '\n'.join(str(e).strip() for e in test_case.expected)
            else:
                expected = str(test_case.expected).strip()

            # Get actual output (whole output or specific line)
            if len(test_cases) == 1:
                actual = output.strip()
            elif i < len(output_lines):
                actual = output_lines[i].strip()
            else:
                actual = ""

            passed = actual == expected

            test_results.append(TestResult(
                test_name=test_case.name or f"Output {i+1}",
                passed=passed,
                expected=expected,
                actual=actual,
                error=None if passed else f"Expected '{expected}', got '{actual}'"
            ))

        all_passed = all(r.passed for r in test_results)

        return ValidationResult(
            success=all_passed,
            output=output,
            error=None,
            time_seconds=time.time() - start_time,
            test_results=test_results
        )

    def _validate_interactive_mode(
        self,
        code: str,
        test_cases: list[TestCase],
        start_time: float
    ) -> ValidationResult:
        """
        Validate interactive scripts that use input().

        For challenges where learners read input with input() and print output.
        Each test case provides stdin input and expects stdout output.
        """
        test_results = []
        all_output = []

        for test_case in test_cases:
            # Prepare input values as a queue
            input_values = list(test_case.input)
            input_index = [0]  # Use list to allow mutation in closure

            # Create a silent input() that doesn't print prompts
            def mock_input(prompt=""):
                if input_index[0] < len(input_values):
                    value = str(input_values[input_index[0]])
                    input_index[0] += 1
                    return value
                raise EOFError("No more input values")

            captured_output = io.StringIO()

            # Create fresh namespace with our mock input()
            namespace = self._create_restricted_namespace()
            namespace['input'] = mock_input

            try:
                with contextlib.redirect_stdout(captured_output):
                    exec(code, namespace)

                actual_output = captured_output.getvalue().strip()
                all_output.append(actual_output)

                # Handle expected as string or list of strings
                if isinstance(test_case.expected, list):
                    expected = '\n'.join(str(e).strip() for e in test_case.expected)
                else:
                    expected = str(test_case.expected).strip()

                passed = actual_output == expected

                test_results.append(TestResult(
                    test_name=test_case.name or "test",
                    passed=passed,
                    expected=expected,
                    actual=actual_output,
                    error=None if passed else f"Expected '{expected}', got '{actual_output}'"
                ))

            except Exception as e:
                test_results.append(TestResult(
                    test_name=test_case.name or "test",
                    passed=False,
                    expected=test_case.expected,
                    actual=None,
                    error=f"Execution Error: {e}"
                ))

        all_passed = all(r.passed for r in test_results)

        return ValidationResult(
            success=all_passed,
            output='\n---\n'.join(all_output),
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


class PytestValidator:
    """
    Validates player code using pytest test files.

    Each challenge can have its own test_*.py file with tailored tests.
    This allows validation methods appropriate to each challenge type.
    """

    def __init__(self, challenges_dir: Path, timeout_seconds: int = 30):
        self.challenges_dir = Path(challenges_dir)
        self.timeout_seconds = timeout_seconds

    def validate(
        self,
        code: str,
        challenge_id: str,
        test_file: str,
        test_pattern: str | None = None
    ) -> ValidationResult:
        """
        Validate player code using pytest.

        Args:
            code: Player's code
            challenge_id: ID of the challenge
            test_file: Name of the test file (e.g., "test_simple_math.py")
            test_pattern: Optional pattern to filter tests (e.g., "test_stage1" for stage 1)

        Returns:
            ValidationResult with test outcomes
        """
        start_time = time.time()

        # Find the test file
        test_path = self._find_test_file(challenge_id, test_file)
        if not test_path:
            return ValidationResult(
                success=False,
                output="",
                error=f"Test file not found: {test_file}",
                time_seconds=time.time() - start_time,
                test_results=[]
            )

        # Create temp directory with player code and test
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Write player code to file
            player_file = tmpdir / "player_solution.py"
            player_file.write_text(code)

            # Write conftest.py to provide player_code fixture
            conftest = tmpdir / "conftest.py"
            escaped_code = code.replace('"', '\\"')
            conftest.write_text(f'''
import pytest

@pytest.fixture
def player_code():
    """Fixture providing the player's code as a string."""
    return """{escaped_code}"""

@pytest.fixture
def player_file():
    """Fixture providing path to player's code file."""
    return "{player_file}"
''')

            # Copy test file
            test_dest = tmpdir / test_file
            test_dest.write_text(test_path.read_text())

            # Run pytest with JSON output
            result = self._run_pytest(tmpdir, test_file, test_pattern)

            return ValidationResult(
                success=result["success"],
                output=result["output"],
                error=result.get("error"),
                time_seconds=time.time() - start_time,
                test_results=result["test_results"],
                stdout=result.get("stdout", "")
            )

    def _find_test_file(self, item_id: str, test_file: str) -> Optional[Path]:
        """Find the test file for a challenge or concept lesson."""
        # Search for the test file anywhere in the directory tree
        for path in self.challenges_dir.rglob(test_file):
            # Prefer match where item_id appears in path
            if item_id in str(path.parent) or item_id in str(path):
                return path

        # Fall back to first match
        for path in self.challenges_dir.rglob(test_file):
            return path

        return None

    def _run_pytest(
        self,
        test_dir: Path,
        test_file: str,
        test_pattern: str | None = None
    ) -> dict:
        """Run pytest and parse results.

        Args:
            test_dir: Directory containing test files
            test_file: Name of the test file to run
            test_pattern: Optional pattern to filter tests (passed to pytest -k)
        """
        try:
            cmd = [
                sys.executable, "-m", "pytest",
                str(test_dir / test_file),
                "-v",
                "--tb=short",
                "-q"
            ]

            # Add test pattern filter if specified
            if test_pattern:
                cmd.extend(["-k", test_pattern])

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                cwd=str(test_dir)
            )

            output = result.stdout + result.stderr
            test_results = self._parse_pytest_output(output)
            stdout = self._extract_captured_stdout(output)
            success = result.returncode == 0

            return {
                "success": success,
                "output": output,
                "stdout": stdout,
                "error": None if success else "Some tests failed",
                "test_results": test_results
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "stdout": "",
                "error": f"Tests timed out after {self.timeout_seconds}s",
                "test_results": []
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "stdout": "",
                "error": f"Pytest error: {e}",
                "test_results": []
            }

    def _extract_captured_stdout(self, output: str) -> str:
        """Extract captured stdout sections from pytest output.

        Pytest captures print() statements and shows them like:
        --------------------------- Captured stdout call ---------------------------
        Hello World
        some output
        """
        import re

        stdout_parts = []

        # Match "Captured stdout call", "Captured stdout setup", etc.
        pattern = r'-+ Captured stdout (?:call|setup|teardown) -+\n(.*?)(?=-{20,}|$|\n\n[A-Z])'
        matches = re.findall(pattern, output, re.DOTALL)

        for match in matches:
            # Clean up the captured output
            cleaned = match.strip()
            if cleaned:
                stdout_parts.append(cleaned)

        return '\n'.join(stdout_parts)

    def _parse_pytest_output(self, output: str) -> list[TestResult]:
        """Parse pytest output to extract test results."""
        import re
        results = []
        lines = output.split('\n')

        # First, try to parse verbose format (::test_name PASSED/FAILED)
        for line in lines:
            if '::' in line and (' PASSED' in line or ' FAILED' in line):
                parts = line.split('::')
                if len(parts) >= 2:
                    test_name = parts[-1].split()[0]
                    passed = 'PASSED' in line
                    results.append(TestResult(
                        test_name=test_name,
                        passed=passed,
                        expected=None,
                        actual=None,
                        error=None if passed else "Test failed"
                    ))

        # If no verbose results found, parse summary line
        if not results:
            for line in lines:
                # Match patterns like "6 passed", "3 passed, 2 failed"
                passed_match = re.search(r'(\d+) passed', line)
                failed_match = re.search(r'(\d+) failed', line)

                if passed_match or failed_match:
                    passed_count = int(passed_match.group(1)) if passed_match else 0
                    failed_count = int(failed_match.group(1)) if failed_match else 0

                    # Create synthetic test results
                    for i in range(passed_count):
                        results.append(TestResult(
                            test_name=f"test_{i+1}",
                            passed=True,
                            expected=None,
                            actual=None,
                            error=None
                        ))
                    for i in range(failed_count):
                        results.append(TestResult(
                            test_name=f"failed_test_{i+1}",
                            passed=False,
                            expected=None,
                            actual=None,
                            error="Test failed"
                        ))
                    break

        return results


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
