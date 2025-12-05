"""Tests for Efficient Fibonacci challenge."""

import time


class TestEfficientFibonacci:
    """Tests for efficient_fibonacci(n) function."""

    def test_no_syntax_errors(self, player_code: str):
        """Code should have no syntax errors."""
        try:
            compile(player_code, "<player>", "exec")
        except SyntaxError as e:
            raise AssertionError(f"Syntax error at line {e.lineno}: {e.msg}")

    def test_defines_efficient_fibonacci(self, player_code: str):
        """Code should define efficient_fibonacci() function."""
        assert "def efficient_fibonacci" in player_code, "Define a function called 'efficient_fibonacci'"

    def test_no_recursion(self, player_code: str):
        """Code should NOT use recursion (no self-calls)."""
        # Check that the function doesn't call itself
        # This is a simple heuristic - look for the function name after 'return' or in expressions
        lines = player_code.split('\n')
        in_function = False
        for line in lines:
            if 'def efficient_fibonacci' in line:
                in_function = True
                continue
            if in_function and line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                break  # Left the function
            if in_function and 'efficient_fibonacci(' in line and 'def ' not in line:
                raise AssertionError(
                    "This challenge requires an ITERATIVE solution - no recursion allowed! "
                    "Use a for loop with prev, curr = curr, prev + curr"
                )

    def test_fib_0(self, player_code: str):
        """F(0) = 0"""
        ns = {}
        exec(player_code, ns)
        assert ns['efficient_fibonacci'](0) == 0, "efficient_fibonacci(0) should return 0"

    def test_fib_1(self, player_code: str):
        """F(1) = 1"""
        ns = {}
        exec(player_code, ns)
        assert ns['efficient_fibonacci'](1) == 1, "efficient_fibonacci(1) should return 1"

    def test_fib_2(self, player_code: str):
        """F(2) = 1"""
        ns = {}
        exec(player_code, ns)
        assert ns['efficient_fibonacci'](2) == 1, "efficient_fibonacci(2) should return 1"

    def test_fib_10(self, player_code: str):
        """F(10) = 55"""
        ns = {}
        exec(player_code, ns)
        assert ns['efficient_fibonacci'](10) == 55, "efficient_fibonacci(10) should return 55"

    def test_fib_50(self, player_code: str):
        """F(50) = 12586269025 - would take FOREVER with recursion!"""
        ns = {}
        exec(player_code, ns)
        result = ns['efficient_fibonacci'](50)
        expected = 12586269025
        assert result == expected, f"efficient_fibonacci(50) should return {expected}, got {result}"

    def test_fib_100(self, player_code: str):
        """F(100) - truly impossible with recursion."""
        ns = {}
        exec(player_code, ns)
        result = ns['efficient_fibonacci'](100)
        expected = 354224848179261915075
        assert result == expected, f"efficient_fibonacci(100) should return {expected}, got {result}"

    def test_performance(self, player_code: str):
        """Must compute F(1000) in under 0.1 seconds."""
        ns = {}
        exec(player_code, ns)

        start = time.time()
        result = ns['efficient_fibonacci'](1000)
        elapsed = time.time() - start

        assert elapsed < 0.1, f"Too slow! F(1000) took {elapsed:.3f}s - recursion would take centuries"
        # Just verify it returns something reasonable (a very large number)
        assert result > 10**200, "F(1000) should be a huge number with 200+ digits"
