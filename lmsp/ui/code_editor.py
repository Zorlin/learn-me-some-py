"""
Rich Syntax Highlighting Code Editor Widget

A gorgeous, polished code editor for the terminal using Rich:
- Python syntax highlighting
- Line numbers
- Cursor visualization
- Smooth updating
- Beautiful presentation

This is what players interact with when writing code - it MUST feel good.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from rich.panel import Panel
from rich.syntax import Syntax
from rich.console import Console, RenderableType
from rich.text import Text
from rich.table import Table


@dataclass
class CursorPosition:
    """
    Represents cursor position in the editor.

    Attributes:
        line: Zero-indexed line number
        col: Zero-indexed column number
    """
    line: int = 0
    col: int = 0

    def __eq__(self, other):
        if not isinstance(other, CursorPosition):
            return False
        return self.line == other.line and self.col == other.col


class CodeEditor:
    """
    A Rich-based code editor with syntax highlighting.

    Features:
    - Python syntax highlighting using Rich's Syntax class
    - Line numbers
    - Cursor position tracking and visualization
    - Text editing operations
    - Beautiful rendering in terminal

    Example:
        editor = CodeEditor(initial_code="def hello():\\n    print('world')")
        editor.insert("# A comment\\n")
        panel = editor.render()  # Returns a Rich Panel
    """

    def __init__(
        self,
        initial_code: str = "",
        theme: str = "monokai",
        show_line_numbers: bool = True,
    ):
        """
        Initialize the code editor.

        Args:
            initial_code: Starting code content
            theme: Syntax highlighting theme (monokai, github-light, etc.)
            show_line_numbers: Whether to show line numbers
        """
        self._lines: List[str] = initial_code.split("\n") if initial_code else [""]
        self.cursor = CursorPosition(line=0, col=0)
        self.theme = theme
        self.show_line_numbers = show_line_numbers

    def get_content(self) -> str:
        """Get the complete code content as a string."""
        return "\n".join(self._lines)

    def get_lines(self) -> List[str]:
        """Get the code as a list of lines."""
        return self._lines.copy()

    def set_content(self, code: str) -> None:
        """
        Replace all content with new code.

        Args:
            code: New code content
        """
        self._lines = code.split("\n") if code else [""]
        self.cursor = CursorPosition(line=0, col=0)

    @property
    def line_count(self) -> int:
        """Get the number of lines in the editor."""
        return len(self._lines)

    def insert(self, text: str) -> None:
        """
        Insert text at the current cursor position.

        Args:
            text: Text to insert (can include newlines)
        """
        if "\n" in text:
            # Handle multi-line insertion
            parts = text.split("\n")

            # Split current line at cursor
            current_line = self._lines[self.cursor.line]
            before_cursor = current_line[:self.cursor.col]
            after_cursor = current_line[self.cursor.col:]

            # Build new lines
            new_lines = []
            new_lines.append(before_cursor + parts[0])
            for part in parts[1:-1]:
                new_lines.append(part)
            new_lines.append(parts[-1] + after_cursor)

            # Replace current line and insert new lines
            self._lines[self.cursor.line:self.cursor.line + 1] = new_lines

            # Update cursor position
            self.cursor.line += len(parts) - 1
            self.cursor.col = len(parts[-1])
        else:
            # Simple single-line insertion
            current_line = self._lines[self.cursor.line]
            new_line = current_line[:self.cursor.col] + text + current_line[self.cursor.col:]
            self._lines[self.cursor.line] = new_line
            self.cursor.col += len(text)

    def delete(self) -> None:
        """Delete the character before the cursor (backspace)."""
        if self.cursor.col > 0:
            # Delete character on current line
            current_line = self._lines[self.cursor.line]
            new_line = current_line[:self.cursor.col - 1] + current_line[self.cursor.col:]
            self._lines[self.cursor.line] = new_line
            self.cursor.col -= 1
        elif self.cursor.line > 0:
            # At beginning of line - join with previous line
            current_line = self._lines[self.cursor.line]
            prev_line = self._lines[self.cursor.line - 1]

            # Merge lines
            self._lines[self.cursor.line - 1] = prev_line + current_line
            del self._lines[self.cursor.line]

            # Update cursor
            self.cursor.line -= 1
            self.cursor.col = len(prev_line)

    def move_cursor_right(self) -> None:
        """Move cursor one position to the right."""
        current_line = self._lines[self.cursor.line]
        if self.cursor.col < len(current_line):
            self.cursor.col += 1

    def move_cursor_left(self) -> None:
        """Move cursor one position to the left."""
        if self.cursor.col > 0:
            self.cursor.col -= 1

    def move_cursor_down(self) -> None:
        """Move cursor one line down."""
        if self.cursor.line < len(self._lines) - 1:
            self.cursor.line += 1
            # Adjust column if new line is shorter
            max_col = len(self._lines[self.cursor.line])
            self.cursor.col = min(self.cursor.col, max_col)

    def move_cursor_up(self) -> None:
        """Move cursor one line up."""
        if self.cursor.line > 0:
            self.cursor.line -= 1
            # Adjust column if new line is shorter
            max_col = len(self._lines[self.cursor.line])
            self.cursor.col = min(self.cursor.col, max_col)

    def render(self) -> Panel:
        """
        Render the code editor as a Rich Panel.

        Returns:
            Rich Panel containing syntax-highlighted code with cursor
        """
        code = self.get_content()

        # Create syntax-highlighted code
        syntax = Syntax(
            code,
            "python",
            theme=self.theme,
            line_numbers=self.show_line_numbers,
            word_wrap=False,
            indent_guides=True,
        )

        # Create table to add cursor indicator
        table = Table.grid(padding=0)
        table.add_column()

        # Add syntax-highlighted code
        table.add_row(syntax)

        # Add cursor position indicator
        cursor_text = Text(f"Line {self.cursor.line + 1}, Col {self.cursor.col + 1}", style="dim cyan")
        table.add_row("")
        table.add_row(cursor_text)

        # Wrap in panel
        panel = Panel(
            table,
            title="[bold cyan]Code Editor[/]",
            border_style="cyan",
            padding=(1, 2),
        )

        return panel


# Self-teaching note:
#
# This file demonstrates:
# - Rich UI components (Level 5-6)
# - Dataclasses for structured data (Level 5)
# - Text manipulation and string operations (Level 2-3)
# - Cursor tracking and editing operations (Level 4)
# - Professional code organization (Level 6+)
#
# Key concepts:
# 1. Rich's Syntax class for gorgeous syntax highlighting
# 2. Cursor position tracking for interactive editing
# 3. Text buffer management (list of lines)
# 4. Insertion, deletion, and cursor movement operations
# 5. Rendering to Rich Panel for beautiful display
#
# This editor makes CODING FEEL GOOD - which is critical for a learning game!
#
# Prerequisites:
# - Level 2: Strings, lists, basic operations
# - Level 3: Classes, methods
# - Level 4: Collections, data structures
# - Level 5: Dataclasses, type hints
# - Level 6: UI design, user interaction patterns
