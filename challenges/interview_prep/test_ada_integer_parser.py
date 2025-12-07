"""
Ada Integer Parser - Multi-Stage Progressive Challenge Tests

Tests are organized by stage. Each stage's tests build on previous stages.
The solution must pass ALL tests for the current stage AND all previous stages.
"""

import pytest


class TestStage1:
    """Stage 1: Simple digits - just check if it's all digits"""

    def test_stage1_simple_number(self, solution):
        assert solution("123") == True, "Simple digits should be valid"

    def test_stage1_single_digit(self, solution):
        assert solution("0") == True, "Single digit should be valid"

    def test_stage1_empty_string(self, solution):
        assert solution("") == False, "Empty string should be invalid"

    def test_stage1_letters(self, solution):
        assert solution("abc") == False, "Letters are not digits"

    def test_stage1_mixed(self, solution):
        assert solution("123abc") == False, "Mixed letters and digits invalid"


class TestStage2:
    """Stage 2: Handle underscores as visual separators"""

    def test_stage2_with_underscores(self, solution):
        assert solution("123_456_789") == True, "Underscores are valid separators"

    def test_stage2_leading_underscore(self, solution):
        assert solution("_123") == True, "Leading underscore is fine"

    def test_stage2_trailing_underscore(self, solution):
        assert solution("123_") == True, "Trailing underscore is fine"

    def test_stage2_just_underscores(self, solution):
        assert solution("___") == False, "Just underscores = no digits = invalid"

    def test_stage2_still_works_without(self, solution):
        assert solution("42") == True, "Still works without underscores"


class TestStage3:
    """Stage 3: Detect and parse base#digits# format"""

    def test_stage3_valid_base_format(self, solution):
        assert solution("10#123#") == True, "Valid base notation structure"

    def test_stage3_hex_format(self, solution):
        assert solution("16#abc#") == True, "Hex format structure valid"

    def test_stage3_missing_closing_hash(self, solution):
        assert solution("10#123") == False, "Missing closing # is invalid"

    def test_stage3_empty_digits(self, solution):
        assert solution("10##") == False, "Empty digits section is invalid"

    def test_stage3_empty_base(self, solution):
        assert solution("#123#") == False, "Empty base section is invalid"

    def test_stage3_multiple_hashes(self, solution):
        assert solution("10#12#34#") == False, "Too many # symbols is invalid"

    def test_stage3_simple_still_works(self, solution):
        assert solution("123") == True, "Simple decimal still works"


class TestStage4:
    """Stage 4: Validate base is 2-16"""

    def test_stage4_base_10_valid(self, solution):
        assert solution("10#123#") == True, "Base 10 is valid"

    def test_stage4_base_2_valid(self, solution):
        assert solution("2#101#") == True, "Base 2 is valid"

    def test_stage4_base_16_valid(self, solution):
        assert solution("16#abc#") == True, "Base 16 is valid"

    def test_stage4_base_too_high(self, solution):
        assert solution("17#123#") == False, "Base 17 > 16, invalid"

    def test_stage4_base_too_low(self, solution):
        assert solution("1#0#") == False, "Base 1 < 2, invalid"

    def test_stage4_base_zero(self, solution):
        assert solution("0#0#") == False, "Base 0 < 2, invalid"

    def test_stage4_base_not_numeric(self, solution):
        assert solution("abc#123#") == False, "Non-numeric base is invalid"


class TestStage5:
    """Stage 5: Validate digits are valid for the given base"""

    def test_stage5_binary_valid(self, solution):
        assert solution("2#1010#") == True, "Valid binary"

    def test_stage5_binary_invalid(self, solution):
        assert solution("2#1012#") == False, "2 is not valid in binary"

    def test_stage5_octal_valid(self, solution):
        assert solution("8#1234567#") == True, "Valid octal"

    def test_stage5_octal_invalid(self, solution):
        assert solution("8#12345678#") == False, "8 is not valid in octal"

    def test_stage5_decimal_valid(self, solution):
        assert solution("10#123#") == True, "Valid decimal"

    def test_stage5_decimal_invalid(self, solution):
        assert solution("10#abc#") == False, "Letters not valid in decimal"

    def test_stage5_hex_lowercase(self, solution):
        assert solution("16#abc#") == True, "Lowercase hex valid"

    def test_stage5_hex_uppercase(self, solution):
        assert solution("16#ABC#") == True, "Uppercase hex valid"

    def test_stage5_hex_mixed_case(self, solution):
        assert solution("16#aB3cD#") == True, "Mixed case hex valid"

    def test_stage5_hex_invalid(self, solution):
        assert solution("16#ghijk#") == False, "g-k not valid in hex"

    def test_stage5_with_underscores_in_digits(self, solution):
        assert solution("16#a_b_c#") == True, "Underscores allowed in digits"

    def test_stage5_full_simple_decimal(self, solution):
        assert solution("123_456_789") == True, "Full simple decimal still works"

    def test_stage5_full_workflow(self, solution):
        """Complete test covering all cases"""
        # Valid cases
        assert solution("42") == True
        assert solution("1_000_000") == True
        assert solution("2#1010#") == True
        assert solution("8#777#") == True
        assert solution("10#999#") == True
        assert solution("16#DEADBEEF#") == True

        # Invalid cases
        assert solution("") == False
        assert solution("2#222#") == False
        assert solution("10#ABC#") == False
        assert solution("17#123#") == False


# Fixture to load the user's solution
@pytest.fixture
def solution(player_code):
    """Load the user's solution function from player code."""
    ns = {}
    exec(player_code, ns)
    if 'solution' not in ns:
        raise AssertionError("Define a function called 'solution'")
    return ns['solution']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
