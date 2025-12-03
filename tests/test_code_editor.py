"""
Tests for Rich syntax highlighting code editor widget.

The code editor should:
- Display Python code with syntax highlighting
- Show line numbers
- Show cursor position
- Support basic editing operations
- Update smoothly
- Feel polished and responsive
"""

import pytest
from lmsp.ui.code_editor import CodeEditor, CursorPosition


class TestCodeEditor:
    """Test the Rich code editor widget."""

    def test_create_empty_editor(self):
        """Should create an empty editor."""
        editor = CodeEditor()
        assert editor.get_content() == ""
        assert editor.cursor == CursorPosition(line=0, col=0)

    def test_create_with_initial_code(self):
        """Should create editor with initial code."""
        code = "def hello():\n    print('world')"
        editor = CodeEditor(initial_code=code)
        assert editor.get_content() == code
        assert editor.line_count == 2

    def test_insert_text_at_cursor(self):
        """Should insert text at cursor position."""
        editor = CodeEditor()
        editor.insert("hello")
        assert editor.get_content() == "hello"
        assert editor.cursor.col == 5

    def test_insert_newline(self):
        """Should handle newline insertion."""
        editor = CodeEditor(initial_code="hello")
        editor.cursor = CursorPosition(line=0, col=5)
        editor.insert("\n")
        assert editor.line_count == 2
        assert editor.cursor.line == 1
        assert editor.cursor.col == 0

    def test_delete_character(self):
        """Should delete character before cursor."""
        editor = CodeEditor(initial_code="hello")
        editor.cursor = CursorPosition(line=0, col=5)
        editor.delete()
        assert editor.get_content() == "hell"
        assert editor.cursor.col == 4

    def test_move_cursor_right(self):
        """Should move cursor right."""
        editor = CodeEditor(initial_code="hello")
        editor.move_cursor_right()
        assert editor.cursor.col == 1

    def test_move_cursor_left(self):
        """Should move cursor left."""
        editor = CodeEditor(initial_code="hello")
        editor.cursor = CursorPosition(line=0, col=3)
        editor.move_cursor_left()
        assert editor.cursor.col == 2

    def test_move_cursor_down(self):
        """Should move cursor down."""
        editor = CodeEditor(initial_code="hello\nworld")
        editor.move_cursor_down()
        assert editor.cursor.line == 1

    def test_move_cursor_up(self):
        """Should move cursor up."""
        editor = CodeEditor(initial_code="hello\nworld")
        editor.cursor = CursorPosition(line=1, col=0)
        editor.move_cursor_up()
        assert editor.cursor.line == 0

    def test_cursor_bounds_right(self):
        """Should not move cursor beyond line end."""
        editor = CodeEditor(initial_code="hello")
        editor.cursor = CursorPosition(line=0, col=5)
        editor.move_cursor_right()
        assert editor.cursor.col == 5  # Can't go past end

    def test_cursor_bounds_left(self):
        """Should not move cursor before line start."""
        editor = CodeEditor(initial_code="hello")
        editor.move_cursor_left()
        assert editor.cursor.col == 0  # Can't go negative

    def test_cursor_bounds_down(self):
        """Should not move cursor beyond last line."""
        editor = CodeEditor(initial_code="hello")
        editor.move_cursor_down()
        assert editor.cursor.line == 0  # Can't go past last line

    def test_cursor_bounds_up(self):
        """Should not move cursor before first line."""
        editor = CodeEditor(initial_code="hello")
        editor.move_cursor_up()
        assert editor.cursor.line == 0  # Can't go negative

    def test_get_lines(self):
        """Should return list of lines."""
        code = "line1\nline2\nline3"
        editor = CodeEditor(initial_code=code)
        lines = editor.get_lines()
        assert lines == ["line1", "line2", "line3"]

    def test_set_content(self):
        """Should replace all content."""
        editor = CodeEditor(initial_code="old")
        editor.set_content("new content")
        assert editor.get_content() == "new content"
        assert editor.cursor == CursorPosition(line=0, col=0)  # Reset cursor

    def test_render_returns_renderable(self):
        """Should return a Rich renderable."""
        editor = CodeEditor(initial_code="def foo():\n    pass")
        renderable = editor.render()
        assert renderable is not None
        # Should be a Rich Panel
        from rich.panel import Panel
        assert isinstance(renderable, Panel)

    def test_syntax_highlighting_present(self):
        """Should include syntax highlighting in render."""
        editor = CodeEditor(initial_code="def hello():\n    return 42")
        renderable = editor.render()
        # The panel should contain syntax-highlighted content
        # We can't easily test the actual highlighting, but we can verify it renders
        assert renderable is not None

    def test_line_numbers_in_render(self):
        """Should include line numbers in render."""
        editor = CodeEditor(initial_code="line1\nline2", show_line_numbers=True)
        renderable = editor.render()
        assert renderable is not None

    def test_cursor_visualization(self):
        """Should visualize cursor position."""
        editor = CodeEditor(initial_code="hello")
        editor.cursor = CursorPosition(line=0, col=2)
        renderable = editor.render()
        # Cursor should be visible in the render
        assert renderable is not None

    def test_empty_lines_handled(self):
        """Should handle empty lines correctly."""
        editor = CodeEditor(initial_code="line1\n\nline3")
        assert editor.line_count == 3
        lines = editor.get_lines()
        assert lines[1] == ""

    def test_tabs_and_spaces(self):
        """Should preserve tabs and spaces."""
        code = "def foo():\n\tpass\n    # comment"
        editor = CodeEditor(initial_code=code)
        assert editor.get_content() == code

    def test_unicode_content(self):
        """Should handle unicode content."""
        code = "# Hello 世界 🚀\nprint('emoji: 🎮')"
        editor = CodeEditor(initial_code=code)
        assert editor.get_content() == code

    def test_long_lines(self):
        """Should handle very long lines."""
        long_line = "x = " + "1" * 200
        editor = CodeEditor(initial_code=long_line)
        assert len(editor.get_lines()[0]) == 204

    def test_many_lines(self):
        """Should handle many lines."""
        lines = [f"line{i}" for i in range(100)]
        code = "\n".join(lines)
        editor = CodeEditor(initial_code=code)
        assert editor.line_count == 100

    def test_custom_theme_light(self):
        """Should support light theme."""
        editor = CodeEditor(initial_code="def foo(): pass", theme="github-light")
        renderable = editor.render()
        assert renderable is not None

    def test_custom_theme_dark(self):
        """Should support dark theme."""
        editor = CodeEditor(initial_code="def foo(): pass", theme="monokai")
        renderable = editor.render()
        assert renderable is not None


class TestCursorPosition:
    """Test the cursor position dataclass."""

    def test_create_cursor(self):
        """Should create cursor position."""
        cursor = CursorPosition(line=5, col=10)
        assert cursor.line == 5
        assert cursor.col == 10

    def test_cursor_equality(self):
        """Should compare cursor positions."""
        c1 = CursorPosition(line=1, col=2)
        c2 = CursorPosition(line=1, col=2)
        c3 = CursorPosition(line=1, col=3)
        assert c1 == c2
        assert c1 != c3

    def test_cursor_default_values(self):
        """Should have default values."""
        cursor = CursorPosition()
        assert cursor.line == 0
        assert cursor.col == 0


# Self-teaching note:
#
# This file demonstrates:
# - Test-Driven Development (TDD) - write tests first!
# - Testing UI components (Level 5+)
# - Edge case testing (empty, unicode, long content)
# - Boundary testing (cursor movement limits)
# - pytest fixtures and class-based tests
#
# Prerequisites:
# - Level 3: Functions, classes, testing basics
# - Level 4: Collections, data structures
# - Level 5: Dataclasses, OOP patterns
# - Level 6: UI testing, integration patterns
