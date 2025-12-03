"""
Tests for the code validator.

The validator is CRITICAL - it's what makes LMSP work.
These tests ensure secure execution and proper validation.
"""

import pytest
from lmsp.python.validator import (
    CodeValidator,
    ValidationResult,
    TestResult,
)
from lmsp.python.challenges import TestCase


class TestCodeValidator:
    """Test the CodeValidator class."""

    def test_validator_creation(self):
        """Validator can be created with default timeout."""
        validator = CodeValidator()
        assert validator.timeout_seconds == 5

    def test_validator_custom_timeout(self):
        """Validator accepts custom timeout."""
        validator = CodeValidator(timeout_seconds=10)
        assert validator.timeout_seconds == 10

    def test_syntax_check_valid(self):
        """Syntax check passes for valid code."""
        validator = CodeValidator()
        valid, error = validator.syntax_check("def solution(x):\n    return x + 1")
        assert valid is True
        assert error is None

    def test_syntax_check_invalid(self):
        """Syntax check fails for invalid code."""
        validator = CodeValidator()
        valid, error = validator.syntax_check("def solution(x):\nreturn x + 1")  # Bad indent
        assert valid is False
        assert error is not None
        assert "Line" in error

    def test_syntax_check_empty(self):
        """Syntax check passes for empty code."""
        validator = CodeValidator()
        valid, error = validator.syntax_check("")
        assert valid is True
        assert error is None


class TestValidationSimple:
    """Test simple validation scenarios."""

    def test_simple_addition(self):
        """Validate simple addition function."""
        validator = CodeValidator()
        code = """
def solution(a, b):
    return a + b
"""
        test_cases = [
            TestCase(name="Add 1+2", input=[1, 2], expected=3),
            TestCase(name="Add 5+7", input=[5, 7], expected=12),
        ]

        result = validator.validate(code, test_cases)

        assert result.success is True
        assert result.error is None
        assert len(result.test_results) == 2
        assert all(r.passed for r in result.test_results)

    def test_failing_test(self):
        """Validation fails when test fails."""
        validator = CodeValidator()
        code = """
def solution(a, b):
    return a - b  # Wrong operation!
"""
        test_cases = [
            TestCase(name="Add 1+2", input=[1, 2], expected=3),
        ]

        result = validator.validate(code, test_cases)

        assert result.success is False
        assert len(result.test_results) == 1
        assert result.test_results[0].passed is False
        assert result.test_results[0].actual == -1

    def test_no_solution_function(self):
        """Validation fails if no solution function defined."""
        validator = CodeValidator()
        code = """
def wrong_name(x):
    return x + 1
"""
        test_cases = [
            TestCase(name="Test", input=[1], expected=2),
        ]

        result = validator.validate(code, test_cases)

        assert result.success is False
        assert "No 'solution' function" in result.error


class TestSecurityRestrictions:
    """Test that security restrictions work."""

    def test_file_io_blocked(self):
        """File I/O operations are blocked."""
        validator = CodeValidator()
        code = """
def solution():
    with open('/etc/passwd', 'r') as f:
        return f.read()
"""
        test_cases = [
            TestCase(name="Test", input=[], expected="shouldn't matter"),
        ]

        result = validator.validate(code, test_cases)

        # Should fail during execution
        assert result.success is False

    def test_import_blocked(self):
        """Imports are blocked in restricted namespace."""
        validator = CodeValidator()
        code = """
import os
def solution():
    return os.getcwd()
"""
        test_cases = [
            TestCase(name="Test", input=[], expected="shouldn't matter"),
        ]

        result = validator.validate(code, test_cases)

        # Should fail - import not available
        assert result.success is False

    def test_eval_blocked(self):
        """eval() is blocked in restricted namespace."""
        validator = CodeValidator()
        code = """
def solution(x):
    return eval(x)
"""
        test_cases = [
            TestCase(name="Test", input=["1+1"], expected=2),
        ]

        result = validator.validate(code, test_cases)

        # Should fail - eval not available
        assert result.success is False


class TestInputFormats:
    """Test different input formats."""

    def test_no_input(self):
        """Function with no arguments."""
        validator = CodeValidator()
        code = """
def solution():
    return 42
"""
        test_cases = [
            TestCase(name="Constant", input=None, expected=42),
        ]

        result = validator.validate(code, test_cases)

        assert result.success is True

    def test_single_arg(self):
        """Function with single argument."""
        validator = CodeValidator()
        code = """
def solution(x):
    return x * 2
"""
        test_cases = [
            TestCase(name="Double 5", input=5, expected=10),
        ]

        result = validator.validate(code, test_cases)

        assert result.success is True

    def test_multiple_args(self):
        """Function with multiple arguments."""
        validator = CodeValidator()
        code = """
def solution(a, b, c):
    return a + b + c
"""
        test_cases = [
            TestCase(name="Sum three", input=[1, 2, 3], expected=6),
        ]

        result = validator.validate(code, test_cases)

        assert result.success is True

    def test_dict_kwargs(self):
        """Function with keyword arguments."""
        validator = CodeValidator()
        code = """
def solution(x=0, y=0):
    return x + y
"""
        test_cases = [
            TestCase(name="Kwargs", input={"x": 5, "y": 3}, expected=8),
        ]

        result = validator.validate(code, test_cases)

        assert result.success is True


class TestExceptionHandling:
    """Test exception handling in validation."""

    def test_runtime_error(self):
        """Runtime errors are caught and reported."""
        validator = CodeValidator()
        code = """
def solution(x):
    return 1 / x  # Will fail for x=0
"""
        test_cases = [
            TestCase(name="Divide by zero", input=[0], expected=0),
        ]

        result = validator.validate(code, test_cases)

        assert result.success is False
        assert result.test_results[0].passed is False
        assert result.test_results[0].error is not None

    def test_type_error(self):
        """Type errors are caught and reported."""
        validator = CodeValidator()
        code = """
def solution(x):
    return x + "string"  # Will fail for non-string x
"""
        test_cases = [
            TestCase(name="Type mismatch", input=[5], expected="5string"),
        ]

        result = validator.validate(code, test_cases)

        assert result.success is False

    def test_index_error(self):
        """Index errors are caught and reported."""
        validator = CodeValidator()
        code = """
def solution(lst):
    return lst[999]  # Out of bounds
"""
        test_cases = [
            TestCase(name="Index error", input=[[1, 2, 3]], expected=0),
        ]

        result = validator.validate(code, test_cases)

        assert result.success is False


class TestDataTypes:
    """Test validation with different data types."""

    def test_strings(self):
        """String operations."""
        validator = CodeValidator()
        code = """
def solution(s):
    return s.upper()
"""
        test_cases = [
            TestCase(name="Uppercase", input=["hello"], expected="HELLO"),
        ]

        result = validator.validate(code, test_cases)

        assert result.success is True

    def test_lists(self):
        """List operations."""
        validator = CodeValidator()
        code = """
def solution(lst):
    return len(lst)
"""
        test_cases = [
            TestCase(name="List length", input=[[1, 2, 3, 4]], expected=4),
        ]

        result = validator.validate(code, test_cases)

        assert result.success is True

    def test_dicts(self):
        """Dict operations."""
        validator = CodeValidator()
        code = """
def solution(d, key):
    return d.get(key, "not found")
"""
        test_cases = [
            TestCase(name="Dict access", input=[{"a": 1}, "a"], expected=1),
            TestCase(name="Dict missing", input=[{"a": 1}, "b"], expected="not found"),
        ]

        result = validator.validate(code, test_cases)

        assert result.success is True


class TestValidationResult:
    """Test ValidationResult dataclass."""

    def test_tests_passing_property(self):
        """tests_passing property counts passed tests."""
        result = ValidationResult(
            success=True,
            output="",
            error=None,
            time_seconds=0.1,
            test_results=[
                TestResult("test1", True, 1, 1, None),
                TestResult("test2", True, 2, 2, None),
                TestResult("test3", False, 3, 4, "wrong"),
            ]
        )

        assert result.tests_passing == 2

    def test_tests_total_property(self):
        """tests_total property counts all tests."""
        result = ValidationResult(
            success=False,
            output="",
            error=None,
            time_seconds=0.1,
            test_results=[
                TestResult("test1", True, 1, 1, None),
                TestResult("test2", False, 2, 3, "wrong"),
            ]
        )

        assert result.tests_total == 2


class TestSafeBuiltins:
    """Test that safe builtins are available."""

    def test_list_comprehension(self):
        """List comprehensions work (need range, etc)."""
        validator = CodeValidator()
        code = """
def solution(n):
    return [x * 2 for x in range(n)]
"""
        test_cases = [
            TestCase(name="Comprehension", input=[5], expected=[0, 2, 4, 6, 8]),
        ]

        result = validator.validate(code, test_cases)

        assert result.success is True

    def test_map_filter(self):
        """map() and filter() are available."""
        validator = CodeValidator()
        code = """
def solution(lst):
    evens = list(filter(lambda x: x % 2 == 0, lst))
    doubled = list(map(lambda x: x * 2, evens))
    return doubled
"""
        test_cases = [
            TestCase(name="Map filter", input=[[1, 2, 3, 4, 5]], expected=[4, 8]),
        ]

        result = validator.validate(code, test_cases)

        assert result.success is True

    def test_sorted_builtin(self):
        """sorted() is available."""
        validator = CodeValidator()
        code = """
def solution(lst):
    return sorted(lst, reverse=True)
"""
        test_cases = [
            TestCase(name="Sort reverse", input=[[3, 1, 4, 1, 5]], expected=[5, 4, 3, 1, 1]),
        ]

        result = validator.validate(code, test_cases)

        assert result.success is True


# Self-teaching note:
#
# This test file demonstrates:
# - pytest test organization (classes, methods)
# - Comprehensive test coverage (happy path, edge cases, errors)
# - Security testing (verifying restrictions work)
# - Dataclass testing (properties, initialization)
# - Exception handling testing
# - Multiple input format testing
#
# Key testing patterns:
# - Arrange-Act-Assert (AAA pattern)
# - Test one thing per test method
# - Clear test names that explain what's being tested
# - Test both success and failure cases
# - Test security boundaries
#
# Prerequisites:
# - Level 3: Functions, testing basics
# - Level 4: Classes, pytest
# - Level 5: Dataclasses, test organization
#
# This is TDD in action - tests define the contract!
