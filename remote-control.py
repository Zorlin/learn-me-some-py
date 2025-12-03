#!/usr/bin/env python3
"""
LMSP Remote Control - Gamepad Input Forwarding
===============================================

Forward gamepad inputs from local machine to remote host running LMSP.

Usage:
    # On the remote host (where LMSP runs):
    python3 remote-control.py server --port 9999

    # On local machine (where gamepad is connected):
    python3 remote-control.py client --host remote.example.com --port 9999

Protocol:
    Simple JSON over TCP. Each message is a JSON object followed by newline.
    {
        "type": "button" | "axis" | "key",
        "name": "A" | "B" | "UP" | "DOWN" | "LT" | "RT" | etc,
        "value": 0.0-1.0 for axes, 0 or 1 for buttons
    }
"""

import argparse
import json
import socket
import sys
import threading
import time
from dataclasses import dataclass
from typing import Optional, Callable, Dict, Any

# Try to import pygame for gamepad support
try:
    import pygame
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False


@dataclass
class GamepadEvent:
    """A gamepad input event."""
    event_type: str  # "button", "axis", "hat", "key"
    name: str        # Button/axis name
    value: float     # 0-1 for axes, 0/1 for buttons

    def to_json(self) -> str:
        return json.dumps({
            "type": self.event_type,
            "name": self.name,
            "value": self.value,
        })

    @classmethod
    def from_json(cls, data: str) -> "GamepadEvent":
        obj = json.loads(data)
        return cls(
            event_type=obj["type"],
            name=obj["name"],
            value=obj["value"],
        )


# Mapping pygame button indices to names
BUTTON_NAMES = {
    0: "A",
    1: "B",
    2: "X",
    3: "Y",
    4: "LB",
    5: "RB",
    6: "BACK",
    7: "START",
    8: "GUIDE",
    9: "LS",
    10: "RS",
}

# Mapping pygame axis indices to names
AXIS_NAMES = {
    0: "LEFT_X",
    1: "LEFT_Y",
    2: "RIGHT_X",
    3: "RIGHT_Y",
    4: "LT",
    5: "RT",
}

# Hat (d-pad) mappings
HAT_NAMES = {
    (0, 1): "UP",
    (0, -1): "DOWN",
    (-1, 0): "LEFT",
    (1, 0): "RIGHT",
    (0, 0): "CENTER",
}


class GamepadReader:
    """Read gamepad inputs using pygame."""

    def __init__(self, callback: Callable[[GamepadEvent], None]):
        self.callback = callback
        self.running = False
        self.joystick = None

    def start(self):
        """Start reading gamepad in a thread."""
        if not HAS_PYGAME:
            print("ERROR: pygame not installed. Run: pip install pygame")
            return False

        pygame.init()
        pygame.joystick.init()

        if pygame.joystick.get_count() == 0:
            print("ERROR: No gamepad detected!")
            return False

        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()
        print(f"Gamepad connected: {self.joystick.get_name()}")

        self.running = True
        self._reader_thread = threading.Thread(target=self._read_loop, daemon=True)
        self._reader_thread.start()
        return True

    def stop(self):
        """Stop reading."""
        self.running = False
        pygame.quit()

    def _read_loop(self):
        """Main reading loop."""
        # Track previous values to only send changes
        prev_buttons = {}
        prev_axes = {}
        prev_hats = {}

        while self.running:
            pygame.event.pump()

            # Read buttons
            for i in range(self.joystick.get_numbuttons()):
                val = self.joystick.get_button(i)
                if prev_buttons.get(i) != val:
                    prev_buttons[i] = val
                    name = BUTTON_NAMES.get(i, f"BTN_{i}")
                    self.callback(GamepadEvent("button", name, float(val)))

            # Read axes
            for i in range(self.joystick.get_numaxes()):
                val = self.joystick.get_axis(i)
                # Deadzone
                if abs(val) < 0.1:
                    val = 0.0
                # Only send if changed significantly
                if abs(prev_axes.get(i, 0) - val) > 0.05:
                    prev_axes[i] = val
                    name = AXIS_NAMES.get(i, f"AXIS_{i}")
                    # Normalize triggers (usually -1 to 1, we want 0 to 1)
                    if name in ("LT", "RT"):
                        val = (val + 1) / 2
                    self.callback(GamepadEvent("axis", name, val))

            # Read hats (d-pad)
            for i in range(self.joystick.get_numhats()):
                val = self.joystick.get_hat(i)
                if prev_hats.get(i) != val:
                    prev_hats[i] = val
                    name = HAT_NAMES.get(val, "HAT_UNKNOWN")
                    if name != "CENTER":
                        self.callback(GamepadEvent("hat", name, 1.0))

            time.sleep(0.016)  # ~60Hz


class RemoteControlServer:
    """Server that receives gamepad events and injects them."""

    def __init__(self, port: int, inject_callback: Callable[[GamepadEvent], None]):
        self.port = port
        self.inject_callback = inject_callback
        self.running = False
        self.clients: list = []

    def start(self):
        """Start server."""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("0.0.0.0", self.port))
        self.sock.listen(5)
        self.running = True

        print(f"Remote Control Server listening on port {self.port}")
        print("Waiting for gamepad client connection...")

        self._accept_thread = threading.Thread(target=self._accept_loop, daemon=True)
        self._accept_thread.start()

    def stop(self):
        """Stop server."""
        self.running = False
        self.sock.close()
        for client in self.clients:
            client.close()

    def _accept_loop(self):
        """Accept incoming connections."""
        while self.running:
            try:
                client, addr = self.sock.accept()
                print(f"Client connected from {addr}")
                self.clients.append(client)
                threading.Thread(
                    target=self._handle_client, args=(client,), daemon=True
                ).start()
            except Exception as e:
                if self.running:
                    print(f"Accept error: {e}")

    def _handle_client(self, client: socket.socket):
        """Handle a client connection."""
        buffer = ""
        try:
            while self.running:
                data = client.recv(4096).decode("utf-8")
                if not data:
                    break
                buffer += data

                # Process complete messages (newline-delimited JSON)
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if line.strip():
                        try:
                            event = GamepadEvent.from_json(line)
                            self.inject_callback(event)
                        except json.JSONDecodeError:
                            print(f"Invalid JSON: {line}")
        except Exception as e:
            print(f"Client error: {e}")
        finally:
            client.close()
            if client in self.clients:
                self.clients.remove(client)
            print("Client disconnected")


class RemoteControlClient:
    """Client that reads local gamepad and sends to server."""

    def __init__(self, host: str, port: int, password: Optional[str] = None):
        self.host = host
        self.port = port
        self.password = password
        self.sock: Optional[socket.socket] = None
        self.connected = False
        self.authenticated = False

    def connect(self):
        """Connect to server."""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            self.connected = True
            print(f"Connected to {self.host}:{self.port}")

            # Authenticate if password provided
            if self.password:
                self._authenticate()

            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False

    def _authenticate(self):
        """Send authentication."""
        if self.sock and self.password:
            auth_msg = json.dumps({"type": "auth", "password": self.password}) + "\n"
            self.sock.sendall(auth_msg.encode("utf-8"))
            # Read response
            try:
                self.sock.settimeout(5)
                response = self.sock.recv(1024).decode("utf-8")
                if '"ok"' in response:
                    print("Authentication successful")
                    self.authenticated = True
                else:
                    print("Authentication failed!")
                self.sock.settimeout(None)
            except socket.timeout:
                print("Authentication timeout")
            except Exception as e:
                print(f"Auth error: {e}")

    def send_event(self, event: GamepadEvent):
        """Send event to server."""
        if self.connected and self.sock:
            try:
                msg = event.to_json() + "\n"
                self.sock.sendall(msg.encode("utf-8"))
            except Exception as e:
                print(f"Send error: {e}")
                self.connected = False

    def close(self):
        """Close connection."""
        if self.sock:
            self.sock.close()
        self.connected = False


class KeyboardInputInjector:
    """Inject keyboard events from gamepad inputs."""

    def __init__(self):
        # Map gamepad events to keyboard keys
        self.mappings = {
            ("button", "A"): "\n",       # A = Enter
            ("button", "B"): "\x1b",     # B = Escape
            ("hat", "UP"): "UP",
            ("hat", "DOWN"): "DOWN",
            ("hat", "LEFT"): "LEFT",
            ("hat", "RIGHT"): "RIGHT",
            ("button", "START"): "\n",   # Start = Enter
            ("button", "BACK"): "\x1b",  # Back = Escape
        }
        self.event_queue: list[str] = []
        self.lock = threading.Lock()

    def inject(self, event: GamepadEvent):
        """Inject a gamepad event as keyboard input."""
        key = (event.event_type, event.name)
        if key in self.mappings and event.value > 0.5:
            mapped = self.mappings[key]
            with self.lock:
                self.event_queue.append(mapped)
            print(f"Injected: {event.name} -> {repr(mapped)}")

    def get_pending(self) -> list[str]:
        """Get and clear pending injected keys."""
        with self.lock:
            events = self.event_queue.copy()
            self.event_queue.clear()
        return events


# Global injector for server mode
_injector: Optional[KeyboardInputInjector] = None


def get_injector() -> KeyboardInputInjector:
    """Get global injector instance."""
    global _injector
    if _injector is None:
        _injector = KeyboardInputInjector()
    return _injector


def run_server(port: int):
    """Run the server that receives gamepad inputs."""
    injector = get_injector()

    def on_event(event: GamepadEvent):
        injector.inject(event)

    server = RemoteControlServer(port, on_event)
    server.start()

    print("\nServer running. Press Ctrl+C to stop.")
    print("Injected events will be forwarded to LMSP.\n")

    # Keep running
    try:
        while True:
            # Print any pending events (for debugging)
            pending = injector.get_pending()
            for key in pending:
                print(f"  -> Key: {repr(key)}")
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.stop()


def run_client(host: str, port: int, password: Optional[str] = None):
    """Run the client that reads local gamepad."""
    if not HAS_PYGAME:
        print("ERROR: pygame required for client mode")
        print("Install with: pip install pygame")
        sys.exit(1)

    client = RemoteControlClient(host, port, password)
    if not client.connect():
        sys.exit(1)

    def on_event(event: GamepadEvent):
        client.send_event(event)
        # Only print non-axis events (too noisy otherwise)
        if event.event_type != "axis":
            print(f"Sent: {event.event_type} {event.name} = {event.value}")

    reader = GamepadReader(on_event)
    if not reader.start():
        sys.exit(1)

    print("\nClient running. Press Ctrl+C to stop.")
    print("Gamepad inputs will be sent to server.\n")

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        reader.stop()
        client.close()


def main():
    parser = argparse.ArgumentParser(
        description="LMSP Remote Control - Forward gamepad inputs over network"
    )
    subparsers = parser.add_subparsers(dest="mode", required=True)

    # Server mode
    server_parser = subparsers.add_parser("server", help="Run input receiver on remote host")
    server_parser.add_argument("--port", "-p", type=int, default=9999, help="Port to listen on")

    # Client mode
    client_parser = subparsers.add_parser("client", help="Run gamepad reader on local machine")
    client_parser.add_argument("--host", "-H", required=True, help="Remote host to connect to")
    client_parser.add_argument("--port", "-p", type=int, default=9999, help="Port to connect to")
    client_parser.add_argument("--password", "-P", help="Password for authentication (if server requires it)")

    args = parser.parse_args()

    if args.mode == "server":
        run_server(args.port)
    elif args.mode == "client":
        run_client(args.host, args.port, args.password)


if __name__ == "__main__":
    main()
