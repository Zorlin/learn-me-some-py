"""Tests for Lucky Numbers challenge (multi-stage)."""


class TestLuckyNumbers:
    """Tests for lucky number detection and list generation."""

    def test_no_syntax_errors(self, player_code: str):
        """Code should have no syntax errors."""
        try:
            compile(player_code, "<player>", "exec")
        except SyntaxError as e:
            raise AssertionError(f"Syntax error at line {e.lineno}: {e.msg}")

    def test_defines_is_lucky(self, player_code: str):
        """Code should define is_lucky() function."""
        assert "def is_lucky" in player_code, "Define a function called 'is_lucky'"

    def test_defines_solution(self, player_code: str):
        """Code should define solution() function."""
        assert "def solution" in player_code, "Define a function called 'solution'"

    # Stage 1: is_lucky() tests
    def test_seven_is_lucky(self, player_code: str):
        """7 is lucky (divisible by 7)."""
        ns = {}
        exec(player_code, ns)
        assert ns['is_lucky'](7) == True, "7 should be lucky (divisible by 7)"

    def test_fourteen_is_lucky(self, player_code: str):
        """14 is lucky (divisible by 7)."""
        ns = {}
        exec(player_code, ns)
        assert ns['is_lucky'](14) == True, "14 should be lucky (divisible by 7)"

    def test_seventeen_is_lucky(self, player_code: str):
        """17 is lucky (contains digit 7)."""
        ns = {}
        exec(player_code, ns)
        assert ns['is_lucky'](17) == True, "17 should be lucky (contains 7)"

    def test_eight_not_lucky(self, player_code: str):
        """8 is not lucky."""
        ns = {}
        exec(player_code, ns)
        assert ns['is_lucky'](8) == False, "8 should NOT be lucky"

    def test_seventy_seven_is_lucky(self, player_code: str):
        """77 is lucky (both conditions)."""
        ns = {}
        exec(player_code, ns)
        assert ns['is_lucky'](77) == True, "77 should be lucky (divisible by 7 AND contains 7)"

    # Stage 2: solution() tests
    def test_solution_returns_list(self, player_code: str):
        """solution() should return a list."""
        ns = {}
        exec(player_code, ns)
        result = ns['solution']()
        assert isinstance(result, list), f"solution() should return a list, got {type(result)}"

    def test_solution_has_100_items(self, player_code: str):
        """solution() should return exactly 100 items."""
        ns = {}
        exec(player_code, ns)
        result = ns['solution']()
        assert len(result) == 100, f"Expected 100 items, got {len(result)}"

    def test_solution_first_six(self, player_code: str):
        """First 6 items should be '1' through '6'."""
        ns = {}
        exec(player_code, ns)
        result = ns['solution']()
        expected = ['1', '2', '3', '4', '5', '6']
        assert result[:6] == expected, f"First 6 items wrong. Expected {expected}, got {result[:6]}"

    def test_solution_seventh_is_lucky(self, player_code: str):
        """7th item should be 'Lucky!'."""
        ns = {}
        exec(player_code, ns)
        result = ns['solution']()
        assert result[6] == "Lucky!", f"Item 7 should be 'Lucky!', got '{result[6]}'"

    def test_solution_count_lucky(self, player_code: str):
        """Should have correct count of Lucky! entries."""
        ns = {}
        exec(player_code, ns)
        result = ns['solution']()
        lucky_count = sum(1 for x in result if x == "Lucky!")
        # 7,14,17,21,27,28,35,37,42,47,49,56,57,63,67,70-79(10),84,87,91,97,98 = 30
        assert lucky_count == 30, f"Expected 30 Lucky! entries, got {lucky_count}"
