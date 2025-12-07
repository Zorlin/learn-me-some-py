"""
Integer Container - Multi-Stage Progressive Challenge Tests

Tests are organized by stage. Each stage's tests build on previous stages.
The solution must pass ALL tests for the current stage AND all previous stages.
"""

import pytest
import sys
import os

# Add parent directories to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class TestStage1:
    """Stage 1: ADD and EXISTS commands"""

    def test_stage1_basic_add_exists(self, solution):
        queries = [["ADD", "1"], ["ADD", "2"], ["EXISTS", "1"], ["EXISTS", "3"]]
        # Stage 1 ADD returns "", Stage 3+ returns count - accept both
        result = solution(queries)
        # Check EXISTS results are correct
        assert result[2] == "true", "EXISTS should return 'true' for value that was added"
        assert result[3] == "false", "EXISTS should return 'false' for value not in container"

    def test_stage1_empty_exists(self, solution):
        result = solution([["EXISTS", "1"]])
        assert result == ["false"], "EXISTS on empty container should return 'false'"

    def test_stage1_add_then_exists(self, solution):
        queries = [["ADD", "5"], ["EXISTS", "5"]]
        result = solution(queries)
        assert result[1] == "true", "EXISTS should find value after ADD"

    def test_stage1_duplicates_allowed(self, solution):
        queries = [["ADD", "5"], ["ADD", "5"], ["EXISTS", "5"]]
        result = solution(queries)
        assert result[2] == "true", "Container should allow duplicates"

    def test_stage1_negative_numbers(self, solution):
        queries = [["ADD", "-10"], ["EXISTS", "-10"], ["EXISTS", "10"]]
        result = solution(queries)
        assert result[1] == "true", "Should handle negative numbers"
        assert result[2] == "false", "-10 is not 10"


class TestStage2:
    """Stage 2: REMOVE command"""

    def test_stage2_basic_remove(self, solution):
        queries = [["ADD", "5"], ["REMOVE", "5"]]
        result = solution(queries)
        assert result[1] == "true", "REMOVE should return 'true' when value found"

    def test_stage2_remove_not_found(self, solution):
        result = solution([["REMOVE", "5"]])
        assert result == ["false"], "REMOVE should return 'false' when value not found"

    def test_stage2_remove_one_of_many(self, solution):
        queries = [["ADD", "5"], ["ADD", "5"], ["REMOVE", "5"], ["REMOVE", "5"], ["REMOVE", "5"]]
        result = solution(queries)
        assert result[2] == "true", "First REMOVE should succeed"
        assert result[3] == "true", "Second REMOVE should succeed (had 2 fives)"
        assert result[4] == "false", "Third REMOVE should fail (no more fives)"

    def test_stage2_remove_then_exists(self, solution):
        queries = [["ADD", "5"], ["REMOVE", "5"], ["EXISTS", "5"]]
        result = solution(queries)
        assert result[2] == "false", "EXISTS should be false after REMOVE"

    def test_stage2_mixed_operations(self, solution):
        queries = [["ADD", "1"], ["ADD", "2"], ["REMOVE", "1"], ["REMOVE", "1"], ["ADD", "1"], ["REMOVE", "1"]]
        result = solution(queries)
        assert result[2] == "true", "First remove of 1 should succeed"
        assert result[3] == "false", "Second remove of 1 should fail"
        assert result[5] == "true", "Remove after re-add should succeed"


class TestStage3:
    """Stage 3: COUNT command (and ADD returns count)"""

    def test_stage3_count_basics(self, solution):
        queries = [["ADD", "5"], ["ADD", "5"], ["COUNT", "5"]]
        result = solution(queries)
        assert result[0] == "1", "First ADD should return '1'"
        assert result[1] == "2", "Second ADD should return '2'"
        assert result[2] == "2", "COUNT should return '2'"

    def test_stage3_count_zero(self, solution):
        result = solution([["COUNT", "5"]])
        assert result == ["0"], "COUNT of non-existent value should be '0'"

    def test_stage3_count_after_remove(self, solution):
        queries = [["ADD", "1"], ["ADD", "1"], ["ADD", "1"], ["REMOVE", "1"], ["COUNT", "1"]]
        result = solution(queries)
        assert result[0] == "1"
        assert result[1] == "2"
        assert result[2] == "3"
        assert result[3] == "true"
        assert result[4] == "2", "COUNT should be 2 after removing one of three"

    def test_stage3_count_different_values(self, solution):
        queries = [["ADD", "1"], ["ADD", "2"], ["ADD", "1"], ["COUNT", "1"], ["COUNT", "2"], ["COUNT", "3"]]
        result = solution(queries)
        assert result[3] == "2", "COUNT of 1 should be 2"
        assert result[4] == "1", "COUNT of 2 should be 1"
        assert result[5] == "0", "COUNT of 3 should be 0"


class TestStage4:
    """Stage 4: GET_MEDIAN command"""

    def test_stage4_median_empty(self, solution):
        result = solution([["GET_MEDIAN"]])
        assert result == [""], "Median of empty container should be ''"

    def test_stage4_median_one_element(self, solution):
        queries = [["ADD", "5"], ["GET_MEDIAN"]]
        result = solution(queries)
        assert result[1] == "5", "Median of single element is that element"

    def test_stage4_median_odd(self, solution):
        queries = [["ADD", "5"], ["ADD", "10"], ["ADD", "1"], ["GET_MEDIAN"]]
        result = solution(queries)
        # Sorted: [1, 5, 10], middle is 5
        assert result[3] == "5", "Median of [1,5,10] should be 5"

    def test_stage4_median_even_left(self, solution):
        queries = [["ADD", "5"], ["ADD", "10"], ["ADD", "1"], ["ADD", "4"], ["GET_MEDIAN"]]
        result = solution(queries)
        # Sorted: [1, 4, 5, 10], left middle is 4
        assert result[4] == "4", "Median of [1,4,5,10] should be 4 (left middle)"

    def test_stage4_median_after_remove(self, solution):
        queries = [["ADD", "5"], ["ADD", "10"], ["ADD", "1"], ["ADD", "4"], ["REMOVE", "1"], ["GET_MEDIAN"]]
        result = solution(queries)
        # After remove: [5, 10, 4], sorted: [4, 5, 10], median: 5
        assert result[5] == "5"

    def test_stage4_median_with_negatives(self, solution):
        queries = [["ADD", "-5"], ["ADD", "0"], ["ADD", "5"], ["GET_MEDIAN"]]
        result = solution(queries)
        assert result[3] == "0", "Median of [-5,0,5] should be 0"

    def test_stage4_median_with_duplicates(self, solution):
        queries = [["ADD", "1"], ["ADD", "1"], ["ADD", "1"], ["ADD", "5"], ["GET_MEDIAN"]]
        result = solution(queries)
        # Sorted: [1, 1, 1, 5], left middle index is (4-1)//2 = 1, value is 1
        assert result[4] == "1"


class TestStage5:
    """Stage 5: GET_NEXT command"""

    def test_stage5_get_next_basic(self, solution):
        queries = [["ADD", "1"], ["ADD", "2"], ["ADD", "4"], ["GET_NEXT", "1"]]
        result = solution(queries)
        assert result[3] == "2", "Smallest > 1 is 2"

    def test_stage5_get_next_none_found(self, solution):
        queries = [["ADD", "1"], ["ADD", "2"], ["GET_NEXT", "5"]]
        result = solution(queries)
        assert result[2] == "", "No value > 5, should return ''"

    def test_stage5_get_next_with_duplicates(self, solution):
        queries = [["ADD", "2"], ["ADD", "2"], ["ADD", "4"], ["GET_NEXT", "1"], ["GET_NEXT", "2"]]
        result = solution(queries)
        assert result[3] == "2", "Smallest > 1 is 2"
        assert result[4] == "4", "Smallest > 2 is 4 (not another 2)"

    def test_stage5_get_next_after_remove(self, solution):
        queries = [["ADD", "1"], ["ADD", "2"], ["ADD", "3"], ["REMOVE", "2"], ["GET_NEXT", "1"]]
        result = solution(queries)
        assert result[4] == "3", "After removing 2, smallest > 1 is 3"

    def test_stage5_get_next_empty(self, solution):
        result = solution([["GET_NEXT", "5"]])
        assert result == [""], "GET_NEXT on empty container should return ''"

    def test_stage5_get_next_boundary(self, solution):
        queries = [["ADD", "1"], ["ADD", "2"], ["ADD", "3"], ["GET_NEXT", "3"]]
        result = solution(queries)
        assert result[3] == "", "Nothing > 3, should return ''"

    def test_stage5_full_workflow(self, solution):
        """Complete test covering all commands"""
        queries = [
            ["ADD", "1"], ["ADD", "2"], ["ADD", "2"], ["ADD", "4"],
            ["EXISTS", "2"], ["COUNT", "2"],
            ["GET_MEDIAN"],  # Sorted [1,2,2,4], left middle is 2
            ["GET_NEXT", "1"], ["GET_NEXT", "2"], ["GET_NEXT", "4"],
            ["REMOVE", "2"],
            ["COUNT", "2"], ["GET_NEXT", "1"]
        ]
        result = solution(queries)
        assert result[4] == "true", "EXISTS 2"
        assert result[5] == "2", "COUNT 2"
        assert result[6] == "2", "MEDIAN of [1,2,2,4]"
        assert result[7] == "2", "GET_NEXT 1 -> 2"
        assert result[8] == "4", "GET_NEXT 2 -> 4"
        assert result[9] == "", "GET_NEXT 4 -> ''"
        assert result[10] == "true", "REMOVE 2"
        assert result[11] == "1", "COUNT 2 after remove"
        assert result[12] == "2", "GET_NEXT 1 -> 2 (one 2 left)"


# Fixture to load the user's solution
@pytest.fixture
def solution(player_code):
    """Load the user's solution function from player code."""
    # Execute player code to get the solution function
    ns = {}
    exec(player_code, ns)
    if 'solution' not in ns:
        raise AssertionError("Define a function called 'solution'")
    return ns['solution']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
