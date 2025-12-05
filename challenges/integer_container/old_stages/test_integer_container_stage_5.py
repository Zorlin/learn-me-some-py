"""Tests for Integer Container Stage 5: GET_NEXT"""
import pytest


def run_solution(code: str, queries: list) -> list:
    namespace = {}
    exec(code, namespace)
    return namespace['solution'](queries) if 'solution' in namespace else None


class TestStage5GetNext:
    def test_get_next_basic(self, player_code):
        queries = [["ADD", "1"], ["ADD", "2"], ["ADD", "4"], ["GET_NEXT", "1"]]
        assert run_solution(player_code, queries) == ["1", "1", "1", "2"]

    def test_get_next_none_found(self, player_code):
        queries = [["ADD", "1"], ["ADD", "2"], ["GET_NEXT", "5"]]
        assert run_solution(player_code, queries) == ["1", "1", ""]

    def test_get_next_with_duplicates(self, player_code):
        queries = [["ADD", "2"], ["ADD", "2"], ["ADD", "4"], ["GET_NEXT", "1"], ["GET_NEXT", "2"]]
        assert run_solution(player_code, queries) == ["1", "2", "1", "2", "4"]

    def test_get_next_after_remove(self, player_code):
        queries = [["ADD", "1"], ["ADD", "2"], ["ADD", "3"], ["REMOVE", "2"], ["GET_NEXT", "1"]]
        assert run_solution(player_code, queries) == ["1", "1", "1", "true", "3"]

    def test_get_next_empty(self, player_code):
        queries = [["GET_NEXT", "5"]]
        assert run_solution(player_code, queries) == [""]

    def test_full_example(self, player_code):
        """The complete example from the challenge spec."""
        queries = [
            ["ADD", "1"], ["ADD", "2"], ["ADD", "2"], ["ADD", "4"],
            ["GET_NEXT", "1"], ["GET_NEXT", "2"], ["GET_NEXT", "3"], ["GET_NEXT", "4"],
            ["REMOVE", "2"],
            ["GET_NEXT", "1"], ["GET_NEXT", "2"], ["GET_NEXT", "3"], ["GET_NEXT", "4"]
        ]
        expected = ["1", "1", "2", "1", "2", "4", "4", "", "true", "2", "4", "4", ""]
        assert run_solution(player_code, queries) == expected


@pytest.fixture
def player_code(request):
    return getattr(request, 'param', '''
def solution(queries):
    results, container = [], []
    for query in queries:
        cmd = query[0]
        val = int(query[1]) if len(query) > 1 else None
        if cmd == "ADD":
            container.append(val)
            results.append(str(container.count(val)))
        elif cmd == "REMOVE":
            if val in container:
                container.remove(val)
                results.append("true")
            else:
                results.append("false")
        elif cmd == "COUNT":
            results.append(str(container.count(val)))
        elif cmd == "GET_MEDIAN":
            results.append("" if not container else str(sorted(container)[(len(container)-1)//2]))
        elif cmd == "GET_NEXT":
            greater = [x for x in container if x > val]
            results.append(str(min(greater)) if greater else "")
    return results
''')
