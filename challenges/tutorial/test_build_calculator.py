"""Tests for Build a Calculator multi-stage challenge."""


def test_stage1_add(player_code: str):
    """Stage 1: Test add function."""
    namespace = {}
    exec(player_code, namespace)

    add = namespace.get('add')
    assert add is not None, "Function 'add' not found"

    assert add(2, 3) == 5, "add(2, 3) should return 5"
    assert add(-1, 5) == 4, "add(-1, 5) should return 4"
    assert add(0, 0) == 0, "add(0, 0) should return 0"


def test_stage2_subtract(player_code: str):
    """Stage 2: Test subtract function (add must still work)."""
    namespace = {}
    exec(player_code, namespace)

    # add should still work
    add = namespace.get('add')
    assert add is not None, "Function 'add' not found"
    assert add(2, 3) == 5, "add(2, 3) should still return 5"

    # subtract should work
    subtract = namespace.get('subtract')
    assert subtract is not None, "Function 'subtract' not found"

    assert subtract(10, 4) == 6, "subtract(10, 4) should return 6"
    assert subtract(5, 8) == -3, "subtract(5, 8) should return -3"


def test_stage3_multiply(player_code: str):
    """Stage 3: Test multiply function (add and subtract must still work)."""
    namespace = {}
    exec(player_code, namespace)

    # Previous functions should still work
    assert namespace.get('add')(2, 3) == 5
    assert namespace.get('subtract')(10, 4) == 6

    # multiply should work
    multiply = namespace.get('multiply')
    assert multiply is not None, "Function 'multiply' not found"

    assert multiply(4, 5) == 20, "multiply(4, 5) should return 20"
    assert multiply(0, 100) == 0, "multiply(0, 100) should return 0"


def test_stage4_calculate(player_code: str):
    """Stage 4: Test calculate dispatcher function."""
    namespace = {}
    exec(player_code, namespace)

    calculate = namespace.get('calculate')
    assert calculate is not None, "Function 'calculate' not found"

    assert calculate('add', 2, 3) == 5, "calculate('add', 2, 3) should return 5"
    assert calculate('subtract', 10, 4) == 6, "calculate('subtract', 10, 4) should return 6"
    assert calculate('multiply', 4, 5) == 20, "calculate('multiply', 4, 5) should return 20"


def test_stage4_hidden_path(player_code: str):
    """Stage 4 Hidden Path: Check if player used match/case for bonus!"""
    # This test always passes - it's for bonus detection only
    # The validator will check for 'match' keyword to award bonus XP
    if 'match' in player_code and 'case' in player_code:
        # They found the hidden path!
        # Return special marker for the validator to detect
        assert True, "HIDDEN_PATH:match_case"
    else:
        # Normal path - also fine
        assert True


def test_stage5_pattern_matching(player_code: str):
    """Stage 5: Test calculate with pattern matching (same tests, but validates match usage)."""
    namespace = {}
    exec(player_code, namespace)

    calculate = namespace.get('calculate')
    assert calculate is not None, "Function 'calculate' not found"

    # Same functional tests as stage 4
    assert calculate('add', 2, 3) == 5, "calculate('add', 2, 3) should return 5"
    assert calculate('subtract', 10, 4) == 6, "calculate('subtract', 10, 4) should return 6"
    assert calculate('multiply', 4, 5) == 20, "calculate('multiply', 4, 5) should return 20"

    # Check that they actually used match/case (for learning validation)
    # This is a soft check - we want to encourage, not fail
    if 'match' not in player_code:
        print("Hint: Try using 'match operation:' and 'case' statements!")


def test_stage5_bonus_wildcard(player_code: str):
    """Stage 5 Bonus: Check for wildcard case handler."""
    # This test always passes - it's for bonus detection only
    if 'case _:' in player_code or 'case _\n' in player_code:
        # They added a default case - bonus!
        assert True, "BONUS:wildcard_case"
    else:
        assert True
