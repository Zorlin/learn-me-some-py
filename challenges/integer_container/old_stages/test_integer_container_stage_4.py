"""Tests for Integer Container Stage 4: GET_MEDIAN"""
import pytest


def run_solution(code: str, queries: list) -> list:
    namespace = {}
    exec(code, namespace)
    return namespace['solution'](queries) if 'solution' in namespace else None


class TestStage4Median:
    def test_median_empty(self, player_code):
        queries = [["GET_MEDIAN"]]
        assert run_solution(player_code, queries) == [""]

    def test_median_one_element(self, player_code):
        queries = [["ADD", "5"], ["GET_MEDIAN"]]
        assert run_solution(player_code, queries) == ["1", "5"]

    def test_median_odd(self, player_code):
        queries = [["ADD", "5"], ["ADD", "10"], ["ADD", "1"], ["GET_MEDIAN"]]
        assert run_solution(player_code, queries) == ["1", "1", "1", "5"]

    def test_median_even_left(self, player_code):
        queries = [["ADD", "5"], ["ADD", "10"], ["ADD", "1"], ["ADD", "4"], ["GET_MEDIAN"]]
        # Sorted: [1, 4, 5, 10], middle index (4-1)//2 = 1, value = 4
        assert run_solution(player_code, queries) == ["1", "1", "1", "1", "4"]

    def test_median_after_remove(self, player_code):
        queries = [["ADD", "5"], ["ADD", "10"], ["ADD", "1"], ["ADD", "4"], ["REMOVE", "1"], ["GET_MEDIAN"]]
        assert run_solution(player_code, queries) == ["1", "1", "1", "1", "true", "5"]

    def test_median_with_negatives(self, player_code):
        queries = [["ADD", "-5"], ["ADD", "0"], ["ADD", "5"], ["GET_MEDIAN"]]
        assert run_solution(player_code, queries) == ["1", "1", "1", "0"]


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
            if not container:
                results.append("")
            else:
                s = sorted(container)
                results.append(str(s[(len(s)-1)//2]))
    return results
''')
