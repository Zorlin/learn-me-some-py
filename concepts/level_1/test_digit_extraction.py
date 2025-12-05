"""Tests for digit extraction concept."""
import pytest
import sys
from io import StringIO


def run_user_code(code: str, test_input: int = None) -> any:
    """Execute user code and return the result."""
    namespace = {}
    exec(code, namespace)

    if 'solution' in namespace:
        return namespace['solution'](test_input)
    return None


class TestDigitExtraction:
    """Test digit extraction solutions."""

    def test_simple_29(self, user_code):
        """29 → 2 + 9 = 11"""
        result = run_user_code(user_code, 29)
        assert result == 11, f"Expected 11 for n=29, got {result}"

    def test_simple_42(self, user_code):
        """42 → 4 + 2 = 6"""
        result = run_user_code(user_code, 42)
        assert result == 6, f"Expected 6 for n=42, got {result}"

    def test_tens_10(self, user_code):
        """10 → 1 + 0 = 1"""
        result = run_user_code(user_code, 10)
        assert result == 1, f"Expected 1 for n=10, got {result}"

    def test_max_99(self, user_code):
        """99 → 9 + 9 = 18"""
        result = run_user_code(user_code, 99)
        assert result == 18, f"Expected 18 for n=99, got {result}"

    def test_same_digits_55(self, user_code):
        """55 → 5 + 5 = 10"""
        result = run_user_code(user_code, 55)
        assert result == 10, f"Expected 10 for n=55, got {result}"

    def test_result_is_integer(self, user_code):
        """Result should be an integer, not a float."""
        result = run_user_code(user_code, 42)
        assert isinstance(result, int), f"Expected int, got {type(result).__name__}. Did you use / instead of //?"


@pytest.fixture
def user_code(request):
    """Fixture to get user code from test runner."""
    return getattr(request, 'param', '''
def solution(n):
    return n // 10 + n % 10
''')
