"""
Rich Live Game Loop - Event-Driven Architecture
================================================

The GORGEOUS, non-blocking game loop using Rich's Live displays.

NO more janky input() prompts! This uses:
- Rich Live displays for real-time updating
- Event-driven keyboard handling (no blocking)
- Beautiful panels and layouts
- Smooth transitions

This is what a modern TUI game should look like.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional, Callable, Dict, List
from pathlib import Path
import sys
import time
import select
import termios
import tty
import socket
import threading
import json
import os
import fcntl

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich.table import Table
from rich.syntax import Syntax
from rich import box

try:
    import readchar
    HAS_READCHAR = True
except ImportError:
    HAS_READCHAR = False


class GamePhase(Enum):
    """Current phase of the game."""
    TUTORIAL = auto()  # Level Zero - learn the controls!
    MENU = auto()
    CHALLENGE_SELECTION = auto()
    CODING = auto()
    RUNNING_TESTS = auto()
    VIEWING_RESULTS = auto()
    EMOTIONAL_FEEDBACK = auto()
    REMOTE_SETTINGS = auto()
    PAUSED = auto()


class GameAction(Enum):
    """Actions that can be triggered."""
    START_LEARNING = auto()
    SELECT_CHALLENGE = auto()
    VIEW_PROGRESS = auto()
    REMOTE_CONTROL = auto()
    QUIT = auto()
    NONE = auto()


class RemoteControlServer:
    """
    Embedded server for receiving gamepad inputs over network.

    Supports password authentication via keyboard or gamepad sequence.
    """

    # Gamepad button mappings
    BUTTON_TO_KEY = {
        "A": "\n",       # Enter
        "B": "\x1b",     # Escape
        "X": "x",
        "Y": "y",
        "START": "\n",
        "BACK": "\x1b",
        "LB": "[",
        "RB": "]",
    }

    HAT_TO_KEY = {
        "UP": "UP",
        "DOWN": "DOWN",
        "LEFT": "LEFT",
        "RIGHT": "RIGHT",
    }

    def __init__(self, port: int = 9999, password: Optional[str] = None):
        self.port = port
        self.password = password
        self.running = False
        self.sock: Optional[socket.socket] = None
        self.clients: List[socket.socket] = []
        self.authenticated_clients: set = set()
        self.input_queue: List[str] = []
        self.lock = threading.Lock()
        self._accept_thread: Optional[threading.Thread] = None

    def start(self) -> bool:
        """Start the server."""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind(("0.0.0.0", self.port))
            self.sock.listen(5)
            self.sock.setblocking(False)
            self.running = True

            self._accept_thread = threading.Thread(target=self._accept_loop, daemon=True)
            self._accept_thread.start()
            return True
        except Exception as e:
            return False

    def stop(self):
        """Stop the server."""
        self.running = False
        if self.sock:
            self.sock.close()
        for client in self.clients:
            try:
                client.close()
            except:
                pass
        self.clients.clear()
        self.authenticated_clients.clear()

    def _accept_loop(self):
        """Accept incoming connections."""
        while self.running:
            try:
                readable, _, _ = select.select([self.sock], [], [], 0.1)
                if readable:
                    client, addr = self.sock.accept()
                    client.setblocking(False)
                    self.clients.append(client)
                    # If no password, auto-authenticate
                    if not self.password:
                        self.authenticated_clients.add(id(client))
                    threading.Thread(
                        target=self._handle_client,
                        args=(client, addr),
                        daemon=True
                    ).start()
            except Exception:
                pass

    def _handle_client(self, client: socket.socket, addr):
        """Handle a client connection."""
        buffer = ""
        client_id = id(client)

        while self.running and client in self.clients:
            try:
                readable, _, _ = select.select([client], [], [], 0.1)
                if not readable:
                    continue

                data = client.recv(4096)
                if not data:
                    break

                buffer += data.decode("utf-8", errors="ignore")

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if line.strip():
                        self._process_message(client, client_id, line.strip())

            except (BlockingIOError, socket.error):
                continue
            except Exception:
                break

        # Cleanup
        if client in self.clients:
            self.clients.remove(client)
        self.authenticated_clients.discard(client_id)
        try:
            client.close()
        except:
            pass

    def _process_message(self, client: socket.socket, client_id: int, msg: str):
        """Process a message from client."""
        try:
            data = json.loads(msg)
        except json.JSONDecodeError:
            return

        msg_type = data.get("type", "")

        # Handle authentication
        if msg_type == "auth":
            pwd = data.get("password", "")
            if pwd == self.password:
                self.authenticated_clients.add(client_id)
                client.sendall(b'{"status":"ok"}\n')
            else:
                client.sendall(b'{"status":"denied"}\n')
            return

        # Require authentication for input events
        if client_id not in self.authenticated_clients:
            client.sendall(b'{"status":"auth_required"}\n')
            return

        # Process input events
        name = data.get("name", "")
        value = data.get("value", 0)

        if value < 0.5:  # Button released, ignore
            return

        key = None
        if msg_type == "button":
            key = self.BUTTON_TO_KEY.get(name)
        elif msg_type == "hat":
            key = self.HAT_TO_KEY.get(name)
        elif msg_type == "axis":
            # Handle analog triggers as buttons when > 0.5
            if name == "LT" and value > 0.5:
                key = "LT"
            elif name == "RT" and value > 0.5:
                key = "RT"

        if key:
            with self.lock:
                self.input_queue.append(key)

    def get_pending_inputs(self) -> List[str]:
        """Get and clear pending input events."""
        with self.lock:
            inputs = self.input_queue.copy()
            self.input_queue.clear()
        return inputs

    @property
    def client_count(self) -> int:
        """Number of connected clients."""
        return len(self.clients)

    @property
    def auth_count(self) -> int:
        """Number of authenticated clients."""
        return len(self.authenticated_clients)


@dataclass
class MenuOption:
    """A menu option with key binding."""
    key: str
    label: str
    action: GameAction


@dataclass
class LiveGameState:
    """Complete game state."""
    phase: GamePhase = GamePhase.MENU  # Start on menu
    menu_index: int = 0
    challenge_index: int = 0
    challenge_id: Optional[str] = None
    challenge_name: str = ""
    challenge_description: str = ""
    code_lines: List[str] = field(default_factory=lambda: [""])
    cursor_line: int = 0
    cursor_col: int = 0
    tests_passing: int = 0
    tests_total: int = 0
    test_error: str = ""
    xp: int = 0
    level: int = 1
    message: str = ""
    running: bool = True
    # Remote control
    remote_enabled: bool = False
    remote_port: int = 9999
    remote_password: str = ""
    remote_password_input: str = ""
    remote_setting_index: int = 0  # 0=toggle, 1=port, 2=password, 3=back
    # Tab completion
    tab_complete_enabled: bool = True
    tab_complete_hold_start: float = 0.0  # For 3-second toggle


class LiveGameLoop:
    """
    Event-driven game loop with Rich Live displays.

    NO blocking input() calls - everything is event-driven and gorgeous!
    """

    def __init__(self, console: Optional[Console] = None):
        """
        Initialize the live game loop.

        Args:
            console: Rich console for output
        """
        self.console = console or Console()
        self.state = LiveGameState()
        self._old_settings = None
        self.remote_server: Optional[RemoteControlServer] = None

        # Menu options
        self.menu_options = [
            MenuOption("1", "🚀 Start Learning (recommended)", GameAction.START_LEARNING),
            MenuOption("2", "📋 Select Challenge", GameAction.SELECT_CHALLENGE),
            MenuOption("3", "📊 View Progress", GameAction.VIEW_PROGRESS),
            MenuOption("4", "🎮 Remote Control", GameAction.REMOTE_CONTROL),
            MenuOption("5", "🚪 Quit", GameAction.QUIT),
        ]

        # Challenge data
        self.available_challenges: List[dict] = []
        self._load_challenges()

    def _load_challenges(self):
        """Load available challenges."""
        try:
            from lmsp.python.challenges import ChallengeLoader
            challenges_dir = Path(__file__).parent.parent.parent / "challenges"
            if challenges_dir.exists():
                loader = ChallengeLoader(challenges_dir)
                for cid in loader.list_challenges()[:20]:
                    try:
                        challenge = loader.load(cid)
                        self.available_challenges.append({
                            "id": cid,
                            "name": challenge.name,
                            "level": challenge.level,
                            "description": challenge.description_brief,
                            "skeleton": challenge.skeleton_code,
                        })
                    except Exception:
                        continue
        except Exception as e:
            self.state.message = f"Could not load challenges: {e}"

    def _setup_terminal(self):
        """Put terminal in raw mode for immediate key reading."""
        if sys.stdin.isatty():
            self._old_settings = termios.tcgetattr(sys.stdin)
            tty.setcbreak(sys.stdin.fileno())  # cbreak mode (not full raw)

    def _restore_terminal(self):
        """Restore normal terminal mode."""
        if self._old_settings:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self._old_settings)

    def _read_key(self) -> Optional[str]:
        """Read a key without blocking."""
        if sys.stdin in select.select([sys.stdin], [], [], 0.05)[0]:
            try:
                ch = sys.stdin.read(1)
                # Handle escape sequences (arrow keys)
                if ch == '\x1b':
                    # Read up to 2 more bytes (escape sequences are max 3 bytes)
                    # Use os.read which is non-blocking in cbreak mode
                    import os
                    import fcntl

                    # Set non-blocking temporarily
                    fd = sys.stdin.fileno()
                    old_flags = fcntl.fcntl(fd, fcntl.F_GETFL)
                    fcntl.fcntl(fd, fcntl.F_SETFL, old_flags | os.O_NONBLOCK)

                    try:
                        rest = os.read(fd, 5).decode('utf-8', errors='ignore')
                    except (BlockingIOError, OSError):
                        rest = ''
                    finally:
                        fcntl.fcntl(fd, fcntl.F_SETFL, old_flags)

                    # Check for arrow keys: [A, [B, [C, [D
                    if rest == '[A':
                        return 'UP'
                    elif rest == '[B':
                        return 'DOWN'
                    elif rest == '[C':
                        return 'RIGHT'
                    elif rest == '[D':
                        return 'LEFT'
                    elif rest == '[Z':
                        return 'SHIFT_TAB'  # Shift+Tab
                    elif rest == '':
                        # Just ESC pressed alone
                        return 'ESC'
                    # Unknown escape sequence - ignore
                    return None
                return ch
            except Exception:
                return None
        return None

    def run(self):
        """Run the event-driven game loop."""
        self._setup_terminal()

        try:
            with Live(
                self._render(),
                console=self.console,
                refresh_per_second=30,
                screen=True,
                transient=False,
            ) as live:
                while self.state.running:
                    # Read local keyboard input
                    key = self._read_key()
                    if key:
                        self._handle_input(key)

                    # Read remote gamepad input
                    if self.remote_server:
                        for remote_key in self.remote_server.get_pending_inputs():
                            self._handle_input(remote_key)

                    # Update display
                    live.update(self._render())

                    # Small sleep to prevent CPU spinning
                    time.sleep(0.016)  # ~60fps

        finally:
            self._cleanup_remote()
            self._restore_terminal()

    def _handle_input(self, key: str):
        """Handle keyboard input based on current phase."""
        # Universal quit
        if key == '\x03':  # Ctrl+C
            self._cleanup_remote()
            self.state.running = False
            return

        if self.state.phase == GamePhase.MENU:
            self._handle_menu_input(key)
        elif self.state.phase == GamePhase.CHALLENGE_SELECTION:
            self._handle_challenge_select_input(key)
        elif self.state.phase == GamePhase.CODING:
            self._handle_coding_input(key)
        elif self.state.phase == GamePhase.VIEWING_RESULTS:
            self._handle_results_input(key)
        elif self.state.phase == GamePhase.EMOTIONAL_FEEDBACK:
            self._handle_feedback_input(key)
        elif self.state.phase == GamePhase.REMOTE_SETTINGS:
            self._handle_remote_settings_input(key)

    def _handle_menu_input(self, key: str):
        """Handle menu phase input."""
        if key == 'UP' or key == 'k':
            self.state.menu_index = max(0, self.state.menu_index - 1)
        elif key == 'DOWN' or key == 'j':
            self.state.menu_index = min(len(self.menu_options) - 1, self.state.menu_index + 1)
        elif key in ('\r', '\n', ' '):
            self._execute_menu_action()
        elif key in ('1', '2', '3', '4', '5'):
            self.state.menu_index = int(key) - 1
            self._execute_menu_action()
        elif key in ('q', 'Q', 'ESC'):
            self.state.running = False

    def _execute_menu_action(self):
        """Execute selected menu action."""
        action = self.menu_options[self.state.menu_index].action
        if action == GameAction.START_LEARNING:
            if self.available_challenges:
                self._start_challenge(self.available_challenges[0]["id"])
            else:
                self.state.message = "No challenges available"
        elif action == GameAction.SELECT_CHALLENGE:
            self.state.phase = GamePhase.CHALLENGE_SELECTION
        elif action == GameAction.VIEW_PROGRESS:
            self.state.message = f"Level {self.state.level} | XP: {self.state.xp}"
        elif action == GameAction.REMOTE_CONTROL:
            self.state.phase = GamePhase.REMOTE_SETTINGS
            self.state.remote_setting_index = 0
        elif action == GameAction.QUIT:
            self._cleanup_remote()
            self.state.running = False

    def _cleanup_remote(self):
        """Stop remote server if running."""
        if self.remote_server:
            self.remote_server.stop()
            self.remote_server = None
            self.state.remote_enabled = False

    def _toggle_remote(self):
        """Toggle remote control server."""
        if self.state.remote_enabled:
            self._cleanup_remote()
            self.state.message = "Remote control disabled"
        else:
            pwd = self.state.remote_password if self.state.remote_password else None
            self.remote_server = RemoteControlServer(
                port=self.state.remote_port,
                password=pwd
            )
            if self.remote_server.start():
                self.state.remote_enabled = True
                self.state.message = f"Remote control enabled on port {self.state.remote_port}"
            else:
                self.remote_server = None
                self.state.message = f"Failed to start on port {self.state.remote_port}"

    def _handle_remote_settings_input(self, key: str):
        """Handle remote settings input."""
        if key == 'UP' or key == 'k':
            self.state.remote_setting_index = max(0, self.state.remote_setting_index - 1)
        elif key == 'DOWN' or key == 'j':
            self.state.remote_setting_index = min(3, self.state.remote_setting_index + 1)
        elif key in ('\r', '\n', ' '):
            if self.state.remote_setting_index == 0:
                # Toggle enable/disable
                self._toggle_remote()
            elif self.state.remote_setting_index == 3:
                # Back
                self.state.phase = GamePhase.MENU
        elif key == 'ESC' or key == 'b':
            self.state.phase = GamePhase.MENU
        # Handle port input when on port setting
        elif self.state.remote_setting_index == 1:
            if key.isdigit():
                new_port = self.state.remote_port * 10 + int(key)
                if new_port <= 65535:
                    self.state.remote_port = new_port
            elif key == '\x7f' or key == '\b':
                self.state.remote_port = self.state.remote_port // 10
        # Handle password input when on password setting
        elif self.state.remote_setting_index == 2:
            if key == '\x7f' or key == '\b':
                self.state.remote_password = self.state.remote_password[:-1]
            elif len(key) == 1 and ord(key) >= 32:
                self.state.remote_password += key

    def _handle_challenge_select_input(self, key: str):
        """Handle challenge selection input."""
        if key == 'UP' or key == 'k':
            self.state.challenge_index = max(0, self.state.challenge_index - 1)
        elif key == 'DOWN' or key == 'j':
            max_idx = len(self.available_challenges) - 1
            self.state.challenge_index = min(max_idx, self.state.challenge_index + 1)
        elif key in ('\r', '\n', ' '):
            if self.available_challenges:
                cid = self.available_challenges[self.state.challenge_index]["id"]
                self._start_challenge(cid)
        elif key in ('b', 'ESC'):
            self.state.phase = GamePhase.MENU

    def _start_challenge(self, challenge_id: str):
        """Start a challenge."""
        challenge = next((c for c in self.available_challenges if c["id"] == challenge_id), None)
        if challenge:
            self.state.challenge_id = challenge_id
            self.state.challenge_name = challenge["name"]
            self.state.challenge_description = challenge["description"]
            self.state.code_lines = challenge["skeleton"].split('\n')
            self.state.cursor_line = 0
            self.state.cursor_col = 0
            self.state.tests_passing = 0
            self.state.tests_total = 0
            self.state.test_error = ""
            self.state.phase = GamePhase.CODING

    # Python keywords and builtins for completion
    COMPLETIONS = [
        # Keywords
        "def ", "class ", "if ", "elif ", "else:", "for ", "while ",
        "return ", "import ", "from ", "try:", "except ", "finally:",
        "with ", "as ", "yield ", "lambda ", "pass", "break", "continue",
        "and ", "or ", "not ", "in ", "is ", "True", "False", "None",
        # Builtins
        "print(", "len(", "range(", "str(", "int(", "float(", "list(",
        "dict(", "set(", "tuple(", "input(", "open(", "enumerate(",
        "zip(", "map(", "filter(", "sorted(", "sum(", "min(", "max(",
        "abs(", "round(", "type(", "isinstance(", "hasattr(", "getattr(",
        # Common patterns
        "def solution(", "__name__ == ", "__init__(self", "self.",
    ]

    def _handle_coding_input(self, key: str):
        """Handle coding phase input."""
        # Track Shift+Tab hold time for toggle
        if key == 'SHIFT_TAB':
            now = time.time()
            if self.state.tab_complete_hold_start == 0:
                self.state.tab_complete_hold_start = now
            elif now - self.state.tab_complete_hold_start >= 3.0:
                # Held for 3 seconds - toggle completion
                self.state.tab_complete_enabled = not self.state.tab_complete_enabled
                self.state.message = f"Tab completion {'ON' if self.state.tab_complete_enabled else 'OFF'}"
                self.state.tab_complete_hold_start = 0
            else:
                # Single press - do completion if enabled
                if self.state.tab_complete_enabled:
                    self._do_tab_complete()
                self.state.tab_complete_hold_start = 0
            return
        else:
            # Reset hold timer on any other key
            self.state.tab_complete_hold_start = 0

        # Navigation
        if key == 'UP':
            self.state.cursor_line = max(0, self.state.cursor_line - 1)
            max_col = len(self.state.code_lines[self.state.cursor_line])
            self.state.cursor_col = min(self.state.cursor_col, max_col)
        elif key == 'DOWN':
            max_line = len(self.state.code_lines) - 1
            self.state.cursor_line = min(max_line, self.state.cursor_line + 1)
            max_col = len(self.state.code_lines[self.state.cursor_line])
            self.state.cursor_col = min(self.state.cursor_col, max_col)
        elif key == 'RIGHT':
            max_col = len(self.state.code_lines[self.state.cursor_line])
            self.state.cursor_col = min(max_col, self.state.cursor_col + 1)
        elif key == 'LEFT':
            self.state.cursor_col = max(0, self.state.cursor_col - 1)
        # Backspace
        elif key == '\x7f' or key == '\b':
            self._handle_backspace()
        # Enter
        elif key in ('\r', '\n'):
            self._handle_newline()
        # Tab
        elif key == '\t':
            self._insert_text('    ')
        # Run tests (Ctrl+R)
        elif key == '\x12':
            self._run_tests()
        # Escape to menu
        elif key == 'ESC':
            self.state.phase = GamePhase.MENU
        # Regular character
        elif len(key) == 1 and ord(key) >= 32:
            self._insert_text(key)

    def _do_tab_complete(self):
        """Perform tab completion at cursor position."""
        line = self.state.code_lines[self.state.cursor_line]
        before_cursor = line[:self.state.cursor_col]

        # Find the word being typed (after last space or start)
        word_start = max(before_cursor.rfind(' '), before_cursor.rfind('('), before_cursor.rfind('.')) + 1
        partial = before_cursor[word_start:]

        if not partial:
            return

        # Find matching completions
        matches = [c for c in self.COMPLETIONS if c.lower().startswith(partial.lower())]

        if len(matches) == 1:
            # Single match - complete it
            completion = matches[0][len(partial):]
            self._insert_text(completion)
            self.state.message = f"Completed: {matches[0]}"
        elif len(matches) > 1:
            # Multiple matches - show them
            self.state.message = f"Matches: {', '.join(matches[:5])}{'...' if len(matches) > 5 else ''}"
        else:
            self.state.message = "No completions"

    def _insert_text(self, text: str):
        """Insert text at cursor."""
        line = self.state.code_lines[self.state.cursor_line]
        new_line = line[:self.state.cursor_col] + text + line[self.state.cursor_col:]
        self.state.code_lines[self.state.cursor_line] = new_line
        self.state.cursor_col += len(text)

    def _handle_backspace(self):
        """Handle backspace."""
        if self.state.cursor_col > 0:
            line = self.state.code_lines[self.state.cursor_line]
            new_line = line[:self.state.cursor_col - 1] + line[self.state.cursor_col:]
            self.state.code_lines[self.state.cursor_line] = new_line
            self.state.cursor_col -= 1
        elif self.state.cursor_line > 0:
            current = self.state.code_lines[self.state.cursor_line]
            prev = self.state.code_lines[self.state.cursor_line - 1]
            self.state.cursor_col = len(prev)
            self.state.code_lines[self.state.cursor_line - 1] = prev + current
            del self.state.code_lines[self.state.cursor_line]
            self.state.cursor_line -= 1

    def _handle_newline(self):
        """Handle enter key."""
        line = self.state.code_lines[self.state.cursor_line]
        before = line[:self.state.cursor_col]
        after = line[self.state.cursor_col:]
        # Auto-indent
        indent = ""
        for ch in before:
            if ch in ' \t':
                indent += ch
            else:
                break
        self.state.code_lines[self.state.cursor_line] = before
        self.state.code_lines.insert(self.state.cursor_line + 1, indent + after)
        self.state.cursor_line += 1
        self.state.cursor_col = len(indent)

    def _run_tests(self):
        """Run tests on current code."""
        self.state.phase = GamePhase.RUNNING_TESTS
        self.state.message = "Running tests..."

        try:
            from lmsp.python.validator import CodeValidator, PytestValidator
            from lmsp.python.challenges import ChallengeLoader

            challenges_dir = Path(__file__).parent.parent.parent / "challenges"
            loader = ChallengeLoader(challenges_dir)
            challenge = loader.load(self.state.challenge_id)

            code = '\n'.join(self.state.code_lines)

            # Use the appropriate validator based on challenge config
            if challenge.validation_type == "pytest" and challenge.test_file:
                validator = PytestValidator(challenges_dir, timeout_seconds=30)
                result = validator.validate(code, challenge.id, challenge.test_file)
            else:
                validator = CodeValidator(timeout_seconds=5)
                result = validator.validate(code, challenge.test_cases)

            self.state.tests_passing = result.tests_passing
            self.state.tests_total = result.tests_total
            self.state.test_error = result.error or ""

            if result.success:
                self.state.xp += challenge.points
                self.state.message = f"🎉 All tests pass! +{challenge.points} XP"
                self.state.phase = GamePhase.EMOTIONAL_FEEDBACK
            else:
                self.state.message = result.error or "Some tests failed"
                self.state.phase = GamePhase.VIEWING_RESULTS
        except Exception as e:
            self.state.test_error = str(e)
            self.state.message = f"Error: {e}"
            self.state.phase = GamePhase.VIEWING_RESULTS

    def _handle_results_input(self, key: str):
        """Handle results phase input."""
        if key in ('\r', '\n', ' ', 'ESC'):
            self.state.phase = GamePhase.CODING

    def _handle_feedback_input(self, key: str):
        """Handle feedback phase input."""
        if key in ('\r', '\n', ' ', 'ESC'):
            self.state.phase = GamePhase.MENU
            self.state.message = "Thanks for the feedback!"

    # ========== RENDERING ==========

    def _render(self) -> Layout:
        """Render the complete game screen."""
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=4),
        )

        # Header
        header = self._render_header()
        layout["header"].update(header)

        # Main content based on phase
        if self.state.phase == GamePhase.MENU:
            layout["main"].update(self._render_menu())
        elif self.state.phase == GamePhase.CHALLENGE_SELECTION:
            layout["main"].update(self._render_challenge_select())
        elif self.state.phase == GamePhase.CODING:
            layout["main"].split_row(
                Layout(name="code", ratio=2),
                Layout(name="info", ratio=1),
            )
            layout["main"]["code"].update(self._render_code_editor())
            layout["main"]["info"].split_column(
                Layout(name="challenge"),
                Layout(name="tests"),
            )
            layout["main"]["info"]["challenge"].update(self._render_challenge_info())
            layout["main"]["info"]["tests"].update(self._render_tests())
        elif self.state.phase == GamePhase.RUNNING_TESTS:
            layout["main"].update(Panel("⏳ Running tests...", title="[bold]Tests[/]", border_style="yellow"))
        elif self.state.phase == GamePhase.VIEWING_RESULTS:
            layout["main"].update(self._render_results())
        elif self.state.phase == GamePhase.EMOTIONAL_FEEDBACK:
            layout["main"].update(self._render_feedback())
        elif self.state.phase == GamePhase.REMOTE_SETTINGS:
            layout["main"].update(self._render_remote_settings())

        # Footer
        layout["footer"].update(self._render_footer())

        return layout

    def _render_header(self) -> Panel:
        """Render header."""
        text = Text()
        text.append("🎮 LMSP", style="bold cyan")
        text.append(" - Learn Me Some Py", style="dim")
        text.append("  |  ", style="dim")
        text.append(f"Level {self.state.level}", style="bold yellow")
        text.append("  |  ", style="dim")
        text.append(f"XP: {self.state.xp}", style="bold green")
        return Panel(text, style="on #000000", box=box.SIMPLE)

    def _render_menu(self) -> Panel:
        """Render main menu."""
        content = Text()
        content.append("Welcome to LMSP!\n\n", style="bold cyan")
        content.append("The game that teaches you to build it.\n\n", style="italic dim")

        for i, option in enumerate(self.menu_options):
            if i == self.state.menu_index:
                content.append(f"  ▶ {option.label}\n", style="bold cyan reverse")
            else:
                content.append(f"    {option.label}\n", style="white")

        content.append("\n\n")
        content.append("↑↓ navigate | Enter select | q quit", style="dim")

        return Panel(content, title="[bold]Main Menu[/]", border_style="cyan", padding=(1, 2))

    def _render_challenge_select(self) -> Panel:
        """Render challenge selection."""
        content = Text()
        content.append("Select a Challenge\n\n", style="bold cyan")

        if not self.available_challenges:
            content.append("No challenges available.", style="dim")
        else:
            for i, ch in enumerate(self.available_challenges):
                if i == self.state.challenge_index:
                    content.append(f"  ▶ [Lv.{ch['level']}] {ch['name']}\n", style="bold cyan reverse")
                else:
                    content.append(f"    [Lv.{ch['level']}] {ch['name']}\n", style="white")

        content.append("\n")
        content.append("↑↓ navigate | Enter select | b back", style="dim")

        return Panel(content, title="[bold]Challenges[/]", border_style="green", padding=(1, 2))

    def _render_code_editor(self) -> Panel:
        """Render code editor."""
        code = '\n'.join(self.state.code_lines)
        if code.strip():
            syntax = Syntax(code, "python", theme="monokai", line_numbers=True, background_color="#000000")
        else:
            syntax = Text("# Start typing...", style="dim italic")

        cursor_info = Text(f"\nLine {self.state.cursor_line + 1}, Col {self.state.cursor_col + 1}", style="dim cyan")

        table = Table.grid()
        table.add_row(syntax)
        table.add_row(cursor_info)

        return Panel(table, title="[bold green]Code Editor[/]", subtitle="[dim]Ctrl+R run | Esc menu[/]", border_style="green")

    def _render_challenge_info(self) -> Panel:
        """Render challenge info."""
        content = Text()
        content.append(self.state.challenge_name + "\n\n", style="bold yellow")
        content.append(self.state.challenge_description, style="white")
        return Panel(content, title="[bold]Challenge[/]", border_style="yellow")

    def _render_tests(self) -> Panel:
        """Render test results."""
        content = Text()
        if self.state.tests_total == 0:
            content.append("Press Ctrl+R to run tests", style="dim")
        else:
            style = "bold green" if self.state.tests_passing == self.state.tests_total else "bold red"
            content.append(f"{self.state.tests_passing}/{self.state.tests_total} passing", style=style)
            if self.state.test_error:
                content.append(f"\n\n{self.state.test_error[:100]}", style="red dim")
        return Panel(content, title="[bold magenta]Tests[/]", border_style="magenta")

    def _render_results(self) -> Panel:
        """Render test results screen."""
        content = Text()
        content.append("Test Results\n\n", style="bold cyan")
        style = "bold green" if self.state.tests_passing == self.state.tests_total else "bold red"
        content.append(f"{self.state.tests_passing}/{self.state.tests_total} tests passing\n\n", style=style)
        if self.state.test_error:
            content.append(f"Error: {self.state.test_error[:200]}\n\n", style="yellow")
        content.append("Press Enter to continue...", style="dim")
        return Panel(content, title="[bold]Results[/]", border_style="cyan")

    def _render_feedback(self) -> Panel:
        """Render feedback screen."""
        content = Text()
        content.append("🎉 Challenge Complete!\n\n", style="bold green")
        content.append(f"+{self.state.xp} XP!\n\n", style="bold yellow")
        content.append("Press Enter to continue...", style="dim")
        return Panel(content, title="[bold yellow]Success![/]", border_style="green")

    def _render_remote_settings(self) -> Panel:
        """Render remote control settings."""
        content = Text()
        content.append("🎮 Remote Control Settings\n\n", style="bold cyan")

        # Status
        if self.state.remote_enabled:
            status = f"[bold green]ENABLED[/] on port {self.state.remote_port}"
            if self.remote_server:
                clients = self.remote_server.client_count
                auth = self.remote_server.auth_count
                status += f" ({auth}/{clients} clients)"
        else:
            status = "[dim]DISABLED[/]"
        content.append(f"Status: {status}\n\n", style="white")

        # Settings
        settings = [
            ("Enable/Disable", "ON" if self.state.remote_enabled else "OFF"),
            ("Port", str(self.state.remote_port) if self.state.remote_port else "(type port)"),
            ("Password", "*" * len(self.state.remote_password) if self.state.remote_password else "(none - no auth)"),
            ("Back to Menu", ""),
        ]

        for i, (label, value) in enumerate(settings):
            if i == self.state.remote_setting_index:
                if i == 1 or i == 2:
                    # Editable fields show cursor
                    content.append(f"  ▶ {label}: ", style="bold cyan reverse")
                    content.append(f"{value}_\n", style="bold yellow")
                else:
                    content.append(f"  ▶ {label} {value}\n", style="bold cyan reverse")
            else:
                content.append(f"    {label}: {value}\n", style="white")

        content.append("\n")
        content.append("↑↓ navigate | Enter toggle/select | Esc back\n", style="dim")
        content.append("On Port/Password: type to edit, backspace to delete", style="dim")

        # Usage instructions
        content.append("\n\n")
        content.append("To connect from client:\n", style="bold")
        content.append(f"  python3 remote-control.py client --host <this-ip> --port {self.state.remote_port}\n", style="dim cyan")

        return Panel(content, title="[bold]Remote Control[/]", border_style="magenta", padding=(1, 2))

    def _render_footer(self) -> Panel:
        """Render footer."""
        content = Text()
        if self.state.phase == GamePhase.CODING:
            content.append("Ctrl+R: Run | Esc: Menu | ↑↓←→: Navigate", style="dim")
            if self.state.tab_complete_enabled:
                content.append(" | Shift+Tab: Complete", style="dim cyan")
            content.append(" | Hold Shift+Tab 3s: Toggle", style="dim")
        else:
            content.append("↑↓/jk: Navigate | Enter: Select | Esc: Back | q: Quit", style="dim")
        if self.state.message:
            content.append(f"\n{self.state.message}", style="yellow")
        return Panel(content, style="on #000000", box=box.SIMPLE)


def run_live():
    """Entry point for the live game loop."""
    console = Console()
    console.clear()
    loop = LiveGameLoop(console)
    loop.run()


# Self-teaching note:
#
# This file demonstrates:
# - Event-driven architecture (NO blocking input!)
# - Rich library for gorgeous TUI (Level 5-6)
# - Terminal raw mode for immediate key reading (Level 6)
# - Enum for type-safe state management (Level 4)
# - Dataclasses for structured data (Level 5)
# - Rich Live displays for real-time updates (Level 6)
#
# NO more janky input() prompts!
