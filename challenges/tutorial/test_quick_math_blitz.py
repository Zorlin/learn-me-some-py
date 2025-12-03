"""Tests for Quick Math Blitz challenge."""
import sys
from io import StringIO


def test_quick_math_blitz(player_code: str):
    """Test that all 5 math results are correct."""
    # Capture stdout
    old_stdout = sys.stdout
    sys.stdout = StringIO()

    try:
        exec(player_code, {})
        output = sys.stdout.getvalue()
    finally:
        sys.stdout = old_stdout

    lines = [line.strip() for line in output.strip().split('\n') if line.strip()]

    # Expected results
    expected = ['42', '63', '96', '12.0', '210']  # 12.0 because division returns float

    assert len(lines) >= 5, f"Expected 5 results, got {len(lines)}"

    # Check each result (allow 12 or 12.0 for division)
    assert lines[0] == '42', f"result1 should be 42, got {lines[0]}"
    assert lines[1] == '63', f"result2 should be 63, got {lines[1]}"
    assert lines[2] == '96', f"result3 should be 96, got {lines[2]}"
    assert lines[3] in ('12', '12.0'), f"result4 should be 12, got {lines[3]}"
    assert lines[4] == '210', f"result5 should be 210, got {lines[4]}"
