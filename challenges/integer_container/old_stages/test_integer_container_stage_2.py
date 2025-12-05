"""Tests for Integer Container Stage 2: REMOVE"""
import pytest


def run_solution(code: str, queries: list) -> list:
    namespace = {}
    exec(code, namespace)
    return namespace['solution'](queries) if 'solution' in namespace else None


class TestStage2Remove:
    def test_basic_remove(self, player_code):
        queries = [["ADD", "5"], ["REMOVE", "5"]]
        assert run_solution(player_code, queries) == ["", "true"]

    def test_remove_not_found(self, player_code):
        queries = [["REMOVE", "5"]]
        assert run_solution(player_code, queries) == ["false"]

    def test_remove_one_of_many(self, player_code):
        queries = [["ADD", "5"], ["ADD", "5"], ["REMOVE", "5"], ["REMOVE", "5"], ["REMOVE", "5"]]
        assert run_solution(player_code, queries) == ["", "", "true", "true", "false"]

    def test_mixed_operations(self, player_code):
        queries = [["ADD", "1"], ["ADD", "2"], ["REMOVE", "1"], ["REMOVE", "1"], ["ADD", "1"], ["REMOVE", "1"]]
        assert run_solution(player_code, queries) == ["", "", "true", "false", "", "true"]


@pytest.fixture
def player_code(request):
    return getattr(request, 'param', '''
def solution(queries):
    results, container = [], []
    for query in queries:
        cmd, val = query[0], int(query[1])
        if cmd == "ADD":
            container.append(val)
            results.append("")
        elif cmd == "REMOVE":
            if val in container:
                container.remove(val)
                results.append("true")
            else:
                results.append("false")
    return results
''')
