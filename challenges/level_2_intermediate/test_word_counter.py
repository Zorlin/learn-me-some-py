"""Tests for Word Frequency Counter multi-stage challenge."""


def test_stage1_count_words_basic(player_code: str):
    """Stage 1: Test basic word counting."""
    namespace = {}
    exec(player_code, namespace)

    count_words = namespace.get('count_words')
    assert count_words is not None, "Function 'count_words' not found"

    result = count_words(["cat", "dog", "cat"])
    assert result == {"cat": 2, "dog": 1}, \
        f'count_words(["cat", "dog", "cat"]) should return {{"cat": 2, "dog": 1}}, got {result}'


def test_stage1_count_words_single(player_code: str):
    """Stage 1: Test counting a single word."""
    namespace = {}
    exec(player_code, namespace)

    count_words = namespace.get('count_words')
    assert count_words is not None, "Function 'count_words' not found"

    result = count_words(["hello"])
    assert result == {"hello": 1}, \
        f'count_words(["hello"]) should return {{"hello": 1}}, got {result}'


def test_stage1_count_words_empty(player_code: str):
    """Stage 1: Test counting empty list."""
    namespace = {}
    exec(player_code, namespace)

    count_words = namespace.get('count_words')
    assert count_words is not None, "Function 'count_words' not found"

    result = count_words([])
    assert result == {}, f'count_words([]) should return {{}}, got {result}'


def test_stage1_count_words_many(player_code: str):
    """Stage 1: Test counting many words."""
    namespace = {}
    exec(player_code, namespace)

    count_words = namespace.get('count_words')
    assert count_words is not None, "Function 'count_words' not found"

    result = count_words(["the", "cat", "sat", "on", "the", "mat", "the"])
    assert result == {"the": 3, "cat": 1, "sat": 1, "on": 1, "mat": 1}, \
        "count_words should count all words correctly"


def test_stage2_get_count(player_code: str):
    """Stage 2: Test looking up word counts."""
    namespace = {}
    exec(player_code, namespace)

    # count_words should still work
    count_words = namespace.get('count_words')
    assert count_words is not None, "Function 'count_words' not found"

    get_count = namespace.get('get_count')
    assert get_count is not None, "Function 'get_count' not found"

    counts = {"cat": 2, "dog": 1}
    assert get_count(counts, "cat") == 2, "get_count(counts, 'cat') should return 2"
    assert get_count(counts, "dog") == 1, "get_count(counts, 'dog') should return 1"


def test_stage2_get_count_missing(player_code: str):
    """Stage 2: Test looking up word that doesn't exist."""
    namespace = {}
    exec(player_code, namespace)

    get_count = namespace.get('get_count')
    assert get_count is not None, "Function 'get_count' not found"

    counts = {"cat": 2, "dog": 1}
    result = get_count(counts, "bird")
    assert result == 0, f"get_count(counts, 'bird') should return 0 for missing word, got {result}"


def test_stage3_get_unique_count(player_code: str):
    """Stage 3: Test counting unique words."""
    namespace = {}
    exec(player_code, namespace)

    # Previous functions should still work
    count_words = namespace.get('count_words')
    assert count_words is not None, "Function 'count_words' not found"

    get_unique_count = namespace.get('get_unique_count')
    assert get_unique_count is not None, "Function 'get_unique_count' not found"

    counts = {"cat": 2, "dog": 1, "bird": 5}
    result = get_unique_count(counts)
    assert result == 3, f"get_unique_count should return 3, got {result}"


def test_stage3_get_unique_count_empty(player_code: str):
    """Stage 3: Test unique count of empty dict."""
    namespace = {}
    exec(player_code, namespace)

    get_unique_count = namespace.get('get_unique_count')
    assert get_unique_count is not None, "Function 'get_unique_count' not found"

    result = get_unique_count({})
    assert result == 0, f"get_unique_count({{}}) should return 0, got {result}"


def test_stage4_get_most_common(player_code: str):
    """Stage 4: Test finding most common word."""
    namespace = {}
    exec(player_code, namespace)

    # All previous functions should still work
    count_words = namespace.get('count_words')
    assert count_words is not None, "Function 'count_words' not found"

    get_most_common = namespace.get('get_most_common')
    assert get_most_common is not None, "Function 'get_most_common' not found"

    counts = {"cat": 5, "dog": 2, "bird": 3}
    result = get_most_common(counts)
    assert result == "cat", f"get_most_common should return 'cat', got {result}"


def test_stage4_get_most_common_tie(player_code: str):
    """Stage 4: Test finding most common with multiple high counts."""
    namespace = {}
    exec(player_code, namespace)

    get_most_common = namespace.get('get_most_common')
    assert get_most_common is not None, "Function 'get_most_common' not found"

    # In case of tie, any of the tied words is acceptable
    counts = {"cat": 3, "dog": 3, "bird": 1}
    result = get_most_common(counts)
    assert result in ["cat", "dog"], f"get_most_common should return 'cat' or 'dog', got {result}"


def test_stage4_get_most_common_empty(player_code: str):
    """Stage 4: Test finding most common in empty dict."""
    namespace = {}
    exec(player_code, namespace)

    get_most_common = namespace.get('get_most_common')
    assert get_most_common is not None, "Function 'get_most_common' not found"

    result = get_most_common({})
    assert result == "", f"get_most_common({{}}) should return empty string, got {result!r}"


def test_stage4_hidden_path_counter(player_code: str):
    """Stage 4 Hidden Path: Check if player used collections.Counter."""
    # This test always passes - it's for bonus detection only
    if 'Counter' in player_code and 'collections' in player_code:
        # They found Counter! Pro move.
        assert True, "HIDDEN_PATH:collections_counter"
    else:
        # Normal path - also fine
        assert True


def test_integration_full_workflow(player_code: str):
    """Integration test: Full workflow with all functions."""
    namespace = {}
    exec(player_code, namespace)

    count_words = namespace.get('count_words')
    get_count = namespace.get('get_count')
    get_unique_count = namespace.get('get_unique_count')
    get_most_common = namespace.get('get_most_common')

    # All functions should exist
    assert all([count_words, get_count, get_unique_count, get_most_common]), \
        "All four functions must be defined"

    # Run a full workflow
    words = ["python", "is", "fun", "python", "is", "powerful", "python"]
    counts = count_words(words)

    assert counts == {"python": 3, "is": 2, "fun": 1, "powerful": 1}
    assert get_count(counts, "python") == 3
    assert get_count(counts, "java") == 0  # Not in list
    assert get_unique_count(counts) == 4
    assert get_most_common(counts) == "python"
