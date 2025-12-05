"""Tests for Integer Container Stage 3: COUNT"""
import pytest


def run_solution(code: str, queries: list) -> list:
    namespace = {}
    exec(code, namespace)
    return namespace['solution'](queries) if 'solution' in namespace else None


class TestStage3Count:
    def test_count_basics(self, player_code):
        queries = [["ADD", "5"], ["ADD", "5"], ["COUNT", "5"]]
        assert run_solution(player_code, queries) == ["1", "2", "2"]

    def test_count_zero(self, player_code):
        queries = [["COUNT", "5"]]
        assert run_solution(player_code, queries) == ["0"]

    def test_count_after_remove(self, player_code):
        queries = [["ADD", "1"], ["ADD", "1"], ["ADD", "1"], ["REMOVE", "1"], ["COUNT", "1"]]
        assert run_solution(player_code, queries) == ["1", "2", "3", "true", "2"]

    def test_count_different_values(self, player_code):
        queries = [["ADD", "1"], ["ADD", "2"], ["ADD", "1"], ["COUNT", "1"], ["COUNT", "2"], ["COUNT", "3"]]
        assert run_solution(player_code, queries) == ["1", "1", "2", "2", "1", "0"]


@pytest.fixture
def player_code(request):
    return getattr(request, 'param', '''
def solution(queries):
    results, container = [], []
    for query in queries:
        cmd, val = query[0], int(query[1])
        if cmd == "ADD":
            container.append(val)
            results.append(str(container.count(val)))
        elif cmd == "REMOVE":
            results.append("true" if val in container and not container.remove(val) else "false") if val in container else results.append("false")
        elif cmd == "COUNT":
            results.append(str(container.count(val)))
    return results
''')
