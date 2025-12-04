"""
Pytest tests for Type Conversion concept (Multi-Stage).

Stage 1: String to Number (int)
Stage 2: Number to String (str)
Stage 3: Float Conversion
"""
import subprocess
import sys


def run_player_code(code: str, stdin: str = "98.6\n") -> tuple[str, str, int]:
    """Execute player code and capture output.

    Provides default stdin for input() calls (98.6 for temperature conversion).
    """
    result = subprocess.run(
        [sys.executable, "-c", code],
        input=stdin,
        capture_output=True,
        text=True,
        timeout=5
    )
    return result.stdout, result.stderr, result.returncode


# ═══════════════════════════════════════════════════════════════════════════
# STAGE 1: String to Number (int)
# ═══════════════════════════════════════════════════════════════════════════

class TestStage1:
    """Stage 1: Convert string to integer and do math."""

    def test_stage1_no_syntax_errors(self, player_code: str):
        """Code should have no syntax errors."""
        try:
            compile(player_code, "<player>", "exec")
        except SyntaxError as e:
            raise AssertionError(f"Syntax error at line {e.lineno}: {e.msg}")

    def test_stage1_uses_int(self, player_code: str):
        """Code should use int() to convert the string."""
        assert "int(" in player_code, "Use int() to convert the string '25' to a number"

    def test_stage1_calculates_future_age(self, player_code: str):
        """Code should calculate age + 5."""
        stdout, stderr, returncode = run_player_code(player_code)
        assert returncode == 0, f"Code failed: {stderr}"
        # Should output 30 somewhere (25 + 5)
        assert "30" in stdout, "Expected output to include 30 (age 25 + 5 years)"

    def test_stage1_prints_message(self, player_code: str):
        """Code should print a message about the future age."""
        stdout, stderr, returncode = run_player_code(player_code)
        assert returncode == 0, f"Code failed: {stderr}"
        # Should have "5 years" or "In 5 years" or similar
        assert "30" in stdout, "Print the future age (30)"


# ═══════════════════════════════════════════════════════════════════════════
# STAGE 2: Number to String (str)
# ═══════════════════════════════════════════════════════════════════════════

class TestStage2:
    """Stage 2: Convert number to string for concatenation."""

    def test_stage2_uses_str_or_fstring(self, player_code: str):
        """Code should use str() or f-string to combine text with numbers."""
        has_str = "str(" in player_code
        has_fstring = 'f"' in player_code or "f'" in player_code
        assert has_str or has_fstring, \
            "Use str(total) to convert the number to text, or use an f-string"

    def test_stage2_prints_score_message(self, player_code: str):
        """Code should print a message with the score."""
        stdout, stderr, returncode = run_player_code(player_code)
        assert returncode == 0, f"Code failed: {stderr}"
        # Should output 150 somewhere
        assert "150" in stdout, "Expected output to include 150 (100 + 50)"

    def test_stage2_includes_points(self, player_code: str):
        """Code should include 'points' in the message."""
        stdout, stderr, returncode = run_player_code(player_code)
        assert returncode == 0, f"Code failed: {stderr}"
        stdout_lower = stdout.lower()
        assert "point" in stdout_lower, "Include 'points' in your score message"


# ═══════════════════════════════════════════════════════════════════════════
# STAGE 3: Float Conversion
# ═══════════════════════════════════════════════════════════════════════════

class TestStage3:
    """Stage 3: Convert to float for temperature calculation."""

    def test_stage3_uses_float(self, player_code: str):
        """Code should use float() for decimal conversion."""
        assert "float(" in player_code, \
            "Use float() to convert '98.6' to a decimal number"

    def test_stage3_uses_formula(self, player_code: str):
        """Code should use the Celsius conversion formula."""
        assert "32" in player_code, "The formula needs to subtract 32"
        # Check for the 5/9 ratio
        has_fraction = ("5/9" in player_code or "5 / 9" in player_code or
                       "5.0/9" in player_code or "5/9.0" in player_code)
        has_multiply = "*" in player_code
        assert has_fraction or has_multiply, \
            "Use the formula (F - 32) * 5/9 to convert to Celsius"

    def test_stage3_calculates_celsius(self, player_code: str):
        """Code should calculate and print the Celsius value."""
        stdout, stderr, returncode = run_player_code(player_code)
        assert returncode == 0, f"Code failed: {stderr}"

        # 98.6°F = 37.0°C
        # Accept 37, 37.0, or close approximations
        output = stdout.strip()
        try:
            # Find any number that looks like the celsius value
            import re
            numbers = re.findall(r'[\d.]+', output)
            found_celsius = False
            for num_str in numbers:
                try:
                    num = float(num_str)
                    if 36.9 <= num <= 37.1:  # Close to 37
                        found_celsius = True
                        break
                except ValueError:
                    continue
            assert found_celsius, \
                f"Expected Celsius value around 37.0, got output: {output}"
        except Exception:
            assert "37" in output, \
                f"Expected output to include Celsius value (37), got: {output}"

    def test_stage3_prints_result(self, player_code: str):
        """Code should print the celsius result."""
        assert "print(" in player_code, "Print the calculated Celsius value"


# ═══════════════════════════════════════════════════════════════════════════
# STAGE 4: Real-World Input (Capstone)
# ═══════════════════════════════════════════════════════════════════════════

class TestStage4:
    """Stage 4: Combine input, conversion, math, and output."""

    def test_stage4_uses_input(self, player_code: str):
        """Code should use input() to get user data."""
        assert "input(" in player_code, "Use input() to get temperature from the user"

    def test_stage4_uses_float_with_input(self, player_code: str):
        """Code should convert input to float."""
        # Check for float(input(...)) pattern
        assert "float(" in player_code, "Convert the input to float for decimal temperatures"

    def test_stage4_converts_temperature(self, player_code: str):
        """Code should convert Fahrenheit to Celsius with mocked input."""
        # Provide 98.6 as input, expect output around 37
        result = subprocess.run(
            [sys.executable, "-c", player_code],
            input="98.6\n",
            capture_output=True,
            text=True,
            timeout=5
        )
        assert result.returncode == 0, f"Code failed: {result.stderr}"

        # Should output something with 37 (the Celsius value)
        output = result.stdout
        assert "37" in output, f"Expected Celsius value (37) in output, got: {output}"

    def test_stage4_shows_both_values(self, player_code: str):
        """Code should display both Fahrenheit and Celsius."""
        result = subprocess.run(
            [sys.executable, "-c", player_code],
            input="98.6\n",
            capture_output=True,
            text=True,
            timeout=5
        )
        assert result.returncode == 0, f"Code failed: {result.stderr}"

        output = result.stdout
        # Should show both the input (98.6) and output (37)
        has_fahrenheit = "98.6" in output or "98" in output
        has_celsius = "37" in output
        assert has_fahrenheit and has_celsius, \
            f"Output should show both F and C values. Got: {output}"

    def test_stage4_uses_fstring_or_format(self, player_code: str):
        """Code should format output nicely."""
        has_fstring = 'f"' in player_code or "f'" in player_code
        has_format = ".format(" in player_code
        has_percent = "%" in player_code and "print" in player_code

        assert has_fstring or has_format or has_percent, \
            "Use an f-string or format() for nice output"
