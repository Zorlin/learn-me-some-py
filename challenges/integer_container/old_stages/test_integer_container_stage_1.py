"""Tests for Integer Container Stage 1: ADD and EXISTS"""
import pytest


def run_solution(code: str, queries: list) -> list:
    """Execute user code and return results."""
    namespace = {}
    exec(code, namespace)
    if 'solution' in namespace:
        return namespace['solution'](queries)
    return None


class TestStage1AddExists:
    """Test ADD and EXISTS operations."""

    def test_basic_add_exists(self, player_code):
        queries = [["ADD", "1"], ["ADD", "2"], ["EXISTS", "1"], ["EXISTS", "3"]]
        result = run_solution(player_code, queries)
        assert result == ["", "", "true", "false"], f"Expected ['', '', 'true', 'false'], got {result}"

    def test_empty_exists(self, player_code):
        queries = [["EXISTS", "1"]]
        result = run_solution(player_code, queries)
        assert result == ["false"], f"Expected ['false'], got {result}"

    def test_add_then_exists(self, player_code):
        queries = [["ADD", "5"], ["EXISTS", "5"]]
        result = run_solution(player_code, queries)
        assert result == ["", "true"], f"Expected ['', 'true'], got {result}"

    def test_duplicates_allowed(self, player_code):
        queries = [["ADD", "5"], ["ADD", "5"], ["EXISTS", "5"]]
        result = run_solution(player_code, queries)
        assert result == ["", "", "true"], f"Expected ['', '', 'true'], got {result}"

    def test_negative_numbers(self, player_code):
        queries = [["ADD", "-10"], ["EXISTS", "-10"], ["EXISTS", "10"]]
        result = run_solution(player_code, queries)
        assert result == ["", "true", "false"], f"Expected ['', 'true', 'false'], got {result}"

    def test_returns_strings_not_booleans(self, player_code):
        """Results must be strings, not Python booleans."""
        queries = [["EXISTS", "1"]]
        result = run_solution(player_code, queries)
        assert result[0] == "false", f"Expected string 'false', got {result[0]}"
        assert isinstance(result[0], str), f"Expected str, got {type(result[0]).__name__}"


@pytest.fixture
def player_code(request):
    return getattr(request, 'param', '''
def solution(queries):
    results = []
    container = []
    for query in queries:
        command = query[0]
        value = int(query[1])
        if command == "ADD":
            container.append(value)
            results.append("")
        elif command == "EXISTS":
            results.append("true" if value in container else "false")
    return results
''')
