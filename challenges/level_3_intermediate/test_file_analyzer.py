"""Pytest tests for File Content Analyzer challenge."""
import subprocess
import sys

def run_player_code(code: str) -> tuple[str, str, int]:
    """Execute player code and capture output."""
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=5
    )
    return result.stdout, result.stderr, result.returncode

class TestFileAnalyzer:
    """Tests for the file content analyzer challenge."""

    def test_no_syntax_errors(self, player_code: str):
        """Code should have no syntax errors."""
        try:
            compile(player_code, "<player>", "exec")
        except SyntaxError as e:
            raise AssertionError(f"Syntax error at line {e.lineno}: {e.msg}")

    def test_code_runs(self, player_code: str):
        """Code should execute without runtime errors."""
        stdout, stderr, returncode = run_player_code(player_code)
        assert returncode == 0, f"Code failed with error: {stderr}"

    def test_has_solution_function(self, player_code: str):
        """Code should define a solution function."""
        assert "def solution" in player_code, "Define a 'solution' function"

    def test_count_lines(self, player_code: str):
        """Solution should count lines correctly."""
        test_code = f'''
{player_code}

# Test LINES command
file_contents = "Hello world!\\nHello Python.\\nWorld of code."
commands = ["LINES"]
result = solution(file_contents, commands)
for r in result:
    print(r)
'''
        stdout, _, _ = run_player_code(test_code)
        assert "3" in stdout

    def test_count_words(self, player_code: str):
        """Solution should count words correctly."""
        test_code = f'''
{player_code}

# Test WORDS command
file_contents = "Hello world!\\nHello Python.\\nWorld of code."
commands = ["WORDS"]
result = solution(file_contents, commands)
for r in result:
    print(r)
'''
        stdout, _, _ = run_player_code(test_code)
        assert "7" in stdout

    def test_count_chars(self, player_code: str):
        """Solution should count characters correctly."""
        test_code = f'''
{player_code}

# Test CHARS command
file_contents = "Hello world!\\nHello Python.\\nWorld of code."
commands = ["CHARS"]
result = solution(file_contents, commands)
for r in result:
    print(r)
'''
        stdout, _, _ = run_player_code(test_code)
        assert "41" in stdout

    def test_find_longest_word(self, player_code: str):
        """Solution should find the longest word."""
        test_code = f'''
{player_code}

# Test LONGEST command
file_contents = "The quick brown fox jumps"
commands = ["LONGEST"]
result = solution(file_contents, commands)
for r in result:
    print(r)
'''
        stdout, _, _ = run_player_code(test_code)
        assert "brown" in stdout or "jumps" in stdout

    def test_find_most_frequent(self, player_code: str):
        """Solution should find the most frequent word."""
        test_code = f'''
{player_code}

# Test FREQUENT command
file_contents = "hello world hello python world world"
commands = ["FREQUENT"]
result = solution(file_contents, commands)
for r in result:
    print(r)
'''
        stdout, _, _ = run_player_code(test_code)
        assert "world" in stdout

    def test_case_insensitive_frequency(self, player_code: str):
        """Solution should handle case-insensitive frequency."""
        test_code = f'''
{player_code}

# Test case insensitive
file_contents = "Hello HELLO hello World"
commands = ["FREQUENT"]
result = solution(file_contents, commands)
for r in result:
    print(r)
'''
        stdout, _, _ = run_player_code(test_code)
        assert "hello" in stdout

    def test_complete_analysis(self, player_code: str):
        """Solution should handle complete analysis."""
        test_code = f'''
{player_code}

# Test complete analysis
file_contents = "Python is great.\\nPython is powerful.\\nI love Python!"
commands = ["LINES", "WORDS", "LONGEST", "FREQUENT"]
result = solution(file_contents, commands)
for r in result:
    print(r)
'''
        stdout, _, _ = run_player_code(test_code)
        assert "3" in stdout
        assert "9" in stdout
        assert "powerful" in stdout
        assert "python" in stdout

    def test_empty_file(self, player_code: str):
        """Solution should handle empty file gracefully."""
        test_code = f'''
{player_code}

# Test empty file
file_contents = ""
commands = ["LINES", "WORDS", "CHARS"]
result = solution(file_contents, commands)
for r in result:
    print(r)
'''
        stdout, _, _ = run_player_code(test_code)
        assert "0" in stdout

    def test_handles_punctuation(self, player_code: str):
        """Solution should handle punctuation correctly."""
        test_code = f'''
{player_code}

# Test with punctuation
file_contents = "Hello, world! Python? Yes."
commands = ["WORDS", "LONGEST"]
result = solution(file_contents, commands)
for r in result:
    print(r)
'''
        stdout, _, _ = run_player_code(test_code)
        # Should count words properly
        assert stdout.count("4") > 0 or stdout.count("5") > 0
        # Should handle punctuation in longest word
        assert any(word in stdout for word in ["Hello", "world", "Python", "Yes"])

    def test_function_signature(self, player_code: str):
        """Solution should accept two parameters: file_contents and commands."""
        test_code = f'''
{player_code}

# Test function signature
import inspect
sig = inspect.signature(solution)
params = list(sig.parameters.keys())
print(params, end="")
'''
        stdout, _, _ = run_player_code(test_code)
        assert "file_contents" in stdout
        assert "commands" in stdout
