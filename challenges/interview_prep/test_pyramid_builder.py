"""Tests for Pyramid Builder challenge."""


class TestPyramidBuilder:
    """Tests for pyramid building."""

    def test_no_syntax_errors(self, player_code: str):
        """Code should have no syntax errors."""
        try:
            compile(player_code, "<player>", "exec")
        except SyntaxError as e:
            raise AssertionError(f"Syntax error at line {e.lineno}: {e.msg}")

    def test_defines_solution(self, player_code: str):
        """Code should define a solution() function."""
        assert "def solution" in player_code, "Define a function called 'solution'"

    def test_pyramid_1(self, player_code: str):
        """Pyramid with 1 row should be just '*'."""
        ns = {}
        exec(player_code, ns)
        result = ns['solution'](1)
        assert result == "*", f"For n=1, expected '*', got '{result}'"

    def test_pyramid_3(self, player_code: str):
        """Pyramid with 3 rows."""
        ns = {}
        exec(player_code, ns)
        result = ns['solution'](3)
        expected = "  *\n ***\n*****"
        assert result == expected, f"For n=3, expected:\n{expected}\n\nGot:\n{result}"

    def test_pyramid_5(self, player_code: str):
        """Pyramid with 5 rows."""
        ns = {}
        exec(player_code, ns)
        result = ns['solution'](5)
        expected = "    *\n   ***\n  *****\n *******\n*********"
        assert result == expected, f"For n=5, expected:\n{expected}\n\nGot:\n{result}"
