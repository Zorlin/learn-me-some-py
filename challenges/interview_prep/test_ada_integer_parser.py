"""Tests for Ada Integer Parser challenge."""
import pytest


def run_solution(code: str, line: str) -> bool:
    namespace = {}
    exec(code, namespace)
    return namespace['solution'](line) if 'solution' in namespace else None


class TestSimpleDecimal:
    def test_simple_number(self, player_code):
        assert run_solution(player_code, "123") == True

    def test_with_underscores(self, player_code):
        assert run_solution(player_code, "123_456_789") == True

    def test_single_digit(self, player_code):
        assert run_solution(player_code, "0") == True

    def test_leading_underscore(self, player_code):
        # After removing underscore, should be valid
        assert run_solution(player_code, "_123") == True

    def test_empty_after_underscore(self, player_code):
        # Just underscores = invalid
        assert run_solution(player_code, "___") == False


class TestBaseNotation:
    def test_hex_lowercase(self, player_code):
        assert run_solution(player_code, "16#123abc#") == True

    def test_hex_uppercase(self, player_code):
        assert run_solution(player_code, "16#123ABC#") == True

    def test_hex_mixed_case(self, player_code):
        assert run_solution(player_code, "16#aAbBcC#") == True

    def test_binary_valid(self, player_code):
        assert run_solution(player_code, "2#1010#") == True

    def test_binary_invalid_digit(self, player_code):
        assert run_solution(player_code, "2#1012#") == False

    def test_octal_valid(self, player_code):
        assert run_solution(player_code, "8#1234567#") == True

    def test_octal_invalid(self, player_code):
        assert run_solution(player_code, "8#12345678#") == False

    def test_decimal_explicit(self, player_code):
        assert run_solution(player_code, "10#123#") == True

    def test_decimal_invalid_hex_chars(self, player_code):
        assert run_solution(player_code, "10#123abc#") == False

    def test_base_zero(self, player_code):
        assert run_solution(player_code, "10#0#") == True

    def test_empty_digits(self, player_code):
        assert run_solution(player_code, "10##") == False

    def test_base_too_low(self, player_code):
        assert run_solution(player_code, "1#1#") == False

    def test_base_too_high(self, player_code):
        assert run_solution(player_code, "17#123#") == False

    def test_base_with_underscores(self, player_code):
        assert run_solution(player_code, "16#1_2_3#") == True


class TestInvalidFormats:
    def test_multiple_hashes(self, player_code):
        assert run_solution(player_code, "10#10#123ABC#") == False

    def test_missing_closing_hash(self, player_code):
        assert run_solution(player_code, "16#abc") == False

    def test_empty_string(self, player_code):
        assert run_solution(player_code, "") == False

    def test_just_hash(self, player_code):
        assert run_solution(player_code, "#") == False

    def test_letters_in_simple(self, player_code):
        assert run_solution(player_code, "123abc") == False


@pytest.fixture
def player_code(request):
    return getattr(request, 'param', '''
def solution(line: str) -> bool:
    line = line.replace('_', '')

    if '#' in line:
        parts = line.split('#')
        if len(parts) != 3 or parts[2] != '':
            return False

        base_str, digits = parts[0], parts[1]

        if not base_str.isdigit():
            return False
        base = int(base_str)
        if not (2 <= base <= 16):
            return False

        if not digits:
            return False

        valid_chars = '0123456789abcdef'[:base]
        for char in digits.lower():
            if char not in valid_chars:
                return False

        return True
    else:
        return line.isdigit() and len(line) > 0
''')
