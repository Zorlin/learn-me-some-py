"""Tests for Fibonacci Sequence challenge."""


class TestFibonacci:
    """Tests for fibonacci(n) function."""

    def test_no_syntax_errors(self, player_code: str):
        """Code should have no syntax errors."""
        try:
            compile(player_code, "<player>", "exec")
        except SyntaxError as e:
            raise AssertionError(f"Syntax error at line {e.lineno}: {e.msg}")

    def test_defines_fibonacci(self, player_code: str):
        """Code should define fibonacci() function."""
        assert "def fibonacci" in player_code, "Define a function called 'fibonacci'"

    def test_defines_fibonacci_list(self, player_code: str):
        """Code should define fibonacci_list() function."""
        assert "def fibonacci_list" in player_code, "Define a function called 'fibonacci_list'"

    def test_fib_0(self, player_code: str):
        """F(0) = 0"""
        ns = {}
        exec(player_code, ns)
        assert ns['fibonacci'](0) == 0, "fibonacci(0) should return 0"

    def test_fib_1(self, player_code: str):
        """F(1) = 1"""
        ns = {}
        exec(player_code, ns)
        assert ns['fibonacci'](1) == 1, "fibonacci(1) should return 1"

    def test_fib_2(self, player_code: str):
        """F(2) = 1"""
        ns = {}
        exec(player_code, ns)
        assert ns['fibonacci'](2) == 1, "fibonacci(2) should return 1"

    def test_fib_5(self, player_code: str):
        """F(5) = 5"""
        ns = {}
        exec(player_code, ns)
        assert ns['fibonacci'](5) == 5, "fibonacci(5) should return 5"

    def test_fib_10(self, player_code: str):
        """F(10) = 55"""
        ns = {}
        exec(player_code, ns)
        assert ns['fibonacci'](10) == 55, "fibonacci(10) should return 55"


class TestFibonacciList:
    """Tests for fibonacci_list(n) function."""

    def test_list_0(self, player_code: str):
        """fibonacci_list(0) = []"""
        ns = {}
        exec(player_code, ns)
        result = ns['fibonacci_list'](0)
        assert result == [], f"fibonacci_list(0) should return [], got {result}"

    def test_list_1(self, player_code: str):
        """fibonacci_list(1) = [0]"""
        ns = {}
        exec(player_code, ns)
        result = ns['fibonacci_list'](1)
        assert result == [0], f"fibonacci_list(1) should return [0], got {result}"

    def test_list_5(self, player_code: str):
        """fibonacci_list(5) = [0, 1, 1, 2, 3]"""
        ns = {}
        exec(player_code, ns)
        result = ns['fibonacci_list'](5)
        expected = [0, 1, 1, 2, 3]
        assert result == expected, f"fibonacci_list(5) should return {expected}, got {result}"

    def test_list_10(self, player_code: str):
        """fibonacci_list(10) = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]"""
        ns = {}
        exec(player_code, ns)
        result = ns['fibonacci_list'](10)
        expected = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
        assert result == expected, f"fibonacci_list(10) should return {expected}, got {result}"
