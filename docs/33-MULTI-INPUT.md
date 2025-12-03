# Multi-Input System - Code Anywhere, Anyhow

**The universal approach:** Support every input device, seamlessly.

---

## The Vision

LMSP is **input-agnostic** - it works brilliantly with a controller, but doesn't require one. The same game adapts to:

- **Gamepad** (Xbox, PlayStation, Nintendo, generic)
- **Keyboard + Mouse** (desktop/laptop)
- **Touchscreen** (tablets, phones)
- **Voice** (accessibility, experimental)
- **Hybrid** (touchscreen + gamepad, keyboard + gamepad)

The multi-input system provides:
1. **Automatic detection** - Recognizes available devices
2. **Hot-swapping** - Switch devices mid-session
3. **Unified abstraction** - Same game logic for all inputs
4. **Device-specific optimization** - Each input method feels native

---

## Input Abstraction Layer

All input devices map to a common **abstract interface**:

```python
class InputDevice(Protocol):
    """Protocol that all input devices must implement."""

    def get_action(self) -> Action | None:
        """Get current player action (non-blocking)."""
        ...

    def get_text_input(self) -> str:
        """Get text input (for identifiers, strings)."""
        ...

    def get_emotional_input(self) -> EmotionalSample | None:
        """Get emotional feedback (analog 0.0-1.0)."""
        ...

    def get_navigation(self) -> NavigationAction | None:
        """Get cursor/navigation input."""
        ...

    def rumble(self, pattern: HapticPattern):
        """Provide haptic feedback (if supported)."""
        ...

    @property
    def name(self) -> str:
        """Human-readable device name."""
        ...

    @property
    def capabilities(self) -> set[Capability]:
        """What this device can do."""
        ...
```

**Actions** are high-level intents, not raw input:

```python
class Action(Enum):
    # Code actions
    INSERT_DEF = "insert_def"
    INSERT_IF = "insert_if"
    INSERT_FOR = "insert_for"
    INSERT_RETURN = "insert_return"

    # Edit actions
    UNDO = "undo"
    REDO = "redo"
    DELETE = "delete"
    SMART_COMPLETE = "smart_complete"

    # Navigation
    MOVE_UP = "move_up"
    MOVE_DOWN = "move_down"
    MOVE_LEFT = "move_left"
    MOVE_RIGHT = "move_right"

    # Execution
    RUN_CODE = "run_code"
    VALIDATE = "validate"

    # Help
    SHOW_HINT = "show_hint"
    OPEN_MENU = "open_menu"
```

**Devices translate raw input to Actions:**

```python
# Gamepad translates button presses
gamepad.button_A → Action.INSERT_DEF

# Keyboard translates key combinations
keyboard.key("Ctrl+D") → Action.INSERT_DEF

# Touchscreen translates gestures
touchscreen.tap(button="def") → Action.INSERT_DEF
```

---

## Device Detection

On startup, LMSP detects all available input devices:

```python
class InputManager:
    """Manages all input devices."""

    def __init__(self):
        self.devices: list[InputDevice] = []
        self.active_device: InputDevice | None = None

    def detect_devices(self) -> list[InputDevice]:
        """Scan for available input devices."""
        detected = []

        # Check for gamepad
        if pygame.joystick.get_count() > 0:
            detected.append(GamepadDevice(pygame.joystick.Joystick(0)))

        # Check for keyboard
        if sys.stdin.isatty():
            detected.append(KeyboardDevice())

        # Check for touchscreen
        if has_touchscreen():
            detected.append(TouchscreenDevice())

        # Check for voice input (if enabled)
        if config.voice_enabled and has_microphone():
            detected.append(VoiceDevice())

        return detected

    def select_device(self):
        """Let player choose preferred device."""
        if len(self.devices) == 1:
            self.active_device = self.devices[0]
        else:
            self.active_device = self.prompt_device_selection()
```

**Device selection screen:**

```
┌──────────────────────────────────────────────────────────┐
│  LMSP - Input Device Selection                            │
│                                                           │
│  Available devices:                                      │
│                                                           │
│  1. Xbox Wireless Controller                             │
│     ✓ Radial typing                                      │
│     ✓ Easy mode                                          │
│     ✓ Emotional input (analog triggers)                  │
│     ✓ Haptic feedback                                    │
│                                                           │
│  2. Keyboard + Mouse                                     │
│     ✓ Full keyboard typing                               │
│     ✓ Mouse navigation                                   │
│     ✓ Emotional input (slider)                           │
│     ✗ Haptic feedback                                    │
│                                                           │
│  3. Touchscreen                                          │
│     ✓ Touch typing                                       │
│     ✓ Gesture navigation                                 │
│     ✓ Emotional input (slider)                           │
│     ✗ Haptic feedback (vibration on mobile)              │
│                                                           │
│  Select device: [1] [2] [3]                              │
│  Or press any button/key on preferred device.            │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

---

## Gamepad Mode

**Covered in depth in:**
- [30-RADIAL-TYPING.md](./30-RADIAL-TYPING.md) - Advanced thumbstick input
- [31-EASY-MODE.md](./31-EASY-MODE.md) - Beginner-friendly button mapping
- [32-HAPTIC-FEEDBACK.md](./32-HAPTIC-FEEDBACK.md) - Controller vibration

**Quick reference:**

| Input           | Easy Mode                | Radial Mode              |
|-----------------|--------------------------|--------------------------|
| Face buttons    | Python verbs (def/if/for)| Radial menu triggers     |
| Bumpers         | Undo/Smart-complete      | Shift modifiers          |
| Triggers        | Indent/Dedent            | Emotional analog input   |
| Sticks          | Navigation               | Chord-based typing       |
| Stick clicks    | Run/Validate             | Special actions          |
| D-Pad           | Line navigation          | Menu navigation          |
| Start/Select    | Hint/Menu                | Mode switching           |

---

## Keyboard Mode

Traditional keyboard input with **Python-aware shortcuts**.

### Standard Typing

Normal keyboard typing works as expected:
- Type any character → inserts character
- Backspace → delete
- Enter → newline + auto-indent
- Tab → indent

### Python Shortcuts

```python
KEYBOARD_SHORTCUTS = {
    # Core keywords
    "Ctrl+D": Action.INSERT_DEF,
    "Ctrl+I": Action.INSERT_IF,
    "Ctrl+F": Action.INSERT_FOR,
    "Ctrl+R": Action.INSERT_RETURN,
    "Ctrl+W": Action.INSERT_WHILE,
    "Ctrl+E": Action.INSERT_ELSE,

    # Edit operations
    "Ctrl+Z": Action.UNDO,
    "Ctrl+Y": Action.REDO,
    "Ctrl+Space": Action.SMART_COMPLETE,

    # Execution
    "F5": Action.RUN_CODE,
    "F6": Action.VALIDATE,

    # Navigation
    "Ctrl+Up": Action.MOVE_TO_FUNCTION_START,
    "Ctrl+Down": Action.MOVE_TO_FUNCTION_END,
    "Ctrl+Left": Action.MOVE_WORD_LEFT,
    "Ctrl+Right": Action.MOVE_WORD_RIGHT,

    # Help
    "F1": Action.SHOW_HINT,
    "Esc": Action.OPEN_MENU,
}
```

**Snippet expansion:**

```
Type:           Expands to:
----            -----------
def<Tab>        def |():


if<Tab>         if |:


for<Tab>        for | in :


while<Tab>      while |:


class<Tab>      class |:
                    def __init__(self):


try<Tab>        try:
                    |
                except Exception as e:
                    pass
```

(| indicates cursor position)

### Emotional Input

Since keyboards don't have analog triggers, use **slider UI**:

```
┌──────────────────────────────────────────────────────────┐
│  How was that challenge?                                  │
│                                                           │
│  Frustrating ◄═══════●════════════════════► Enjoyable    │
│                      |                                    │
│                     50%                                   │
│                                                           │
│  [Click and drag slider, or use arrow keys]              │
│  [Enter to confirm]                                      │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

**Keyboard control:**
- Left/Right arrows: Adjust slider
- Shift+Left/Right: Adjust by 10%
- Enter: Confirm
- Esc: Skip (default to neutral)

---

## Touchscreen Mode

Optimized for tablets and phones.

### Layout Design

```
┌──────────────────────────────────────────────────────────┐
│  LMSP - Touchscreen Layout                               │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  ╔═════════════════════════════════════════════════╗     │
│  ║  Code Editor (top 60%)                          ║     │
│  ║                                                  ║     │
│  ║  def hello(name):                               ║     │
│  ║      if name:                                   ║     │
│  ║          return f"Hi {name}"█                   ║     │
│  ║      return "Hello"                             ║     │
│  ║                                                  ║     │
│  ║  [Tap to position cursor]                       ║     │
│  ║  [Pinch to zoom]                                ║     │
│  ║  [Swipe to scroll]                              ║     │
│  ╚═════════════════════════════════════════════════╝     │
│                                                           │
│  ┌─────────────────────────────────────────────────┐     │
│  │  Quick Actions (bottom 20%)                     │     │
│  ├─────────┬─────────┬─────────┬─────────┬─────────┤     │
│  │   def   │   if    │   for   │ return  │  undo   │     │
│  ├─────────┼─────────┼─────────┼─────────┼─────────┤     │
│  │    =    │    +    │    [    │    :    │   run   │     │
│  └─────────┴─────────┴─────────┴─────────┴─────────┘     │
│                                                           │
│  ┌─────────────────────────────────────────────────┐     │
│  │  Keyboard (bottom 20%, tap to show)             │     │
│  │  [Standard touchscreen keyboard]                │     │
│  └─────────────────────────────────────────────────┘     │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

### Gesture Controls

**Single tap:**
- In editor: Position cursor
- On button: Trigger action
- On keyboard: Type character

**Long press:**
- In editor: Show context menu (cut/copy/paste/smart-complete)
- On button: Show alternatives (e.g., long-press "if" → "elif", "else")

**Swipe:**
- Up/Down in editor: Scroll
- Left/Right in editor: Navigate words
- Up from keyboard: Hide keyboard

**Pinch:**
- In editor: Zoom in/out (font size)

**Two-finger swipe:**
- Left: Undo
- Right: Redo

**Shake:**
- Clear current line (with confirmation)

### Touch-Optimized Buttons

Buttons are **large and thumb-friendly**:

```
┌─────────────────────────────────────────────────────────┐
│  Touch Button Design                                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Minimum size: 48×48 dp (Android) / 44×44 pt (iOS)      │
│  Spacing: 8 dp / 8 pt between buttons                   │
│  Active area: Extends 4 dp / 4 pt beyond visual border  │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │          │  │          │  │          │              │
│  │   def    │  │    if    │  │   for    │              │
│  │          │  │          │  │          │              │
│  └──────────┘  └──────────┘  └──────────┘              │
│                                                          │
│  Visual feedback:                                       │
│  - Ripple effect on tap                                 │
│  - Highlight on long-press                              │
│  - Haptic feedback (if device supports)                 │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### On-Screen Keyboard

**Smart keyboard modes:**

1. **Python mode** (default)
   - Common Python keywords as suggestions
   - Operators easily accessible
   - Brackets and delimiters prominent
   - Snake_case suggestions

2. **Identifier mode** (when naming variables)
   - Lowercase letters
   - Underscore prominent
   - No spaces
   - Suggestions from scope

3. **String mode** (when typing strings)
   - Full keyboard
   - Emoji support
   - Escape sequences accessible

4. **Number mode** (when typing numbers)
   - Numeric keypad
   - Math operators
   - Decimal point
   - Scientific notation shortcuts

**Auto-switching:**
- Detects context and switches keyboard mode
- Manual override available
- Previous mode remembered per-context

### Emotional Input

Touch-friendly emotional slider:

```
┌──────────────────────────────────────────────────────────┐
│  How was that?                                            │
│                                                           │
│  ┌────────────────────────────────────────────────────┐  │
│  │                                                     │  │
│  │   Frustrating         Neutral         Enjoyable    │  │
│  │        😤               😐               😊         │  │
│  │                                                     │  │
│  │   ◄════════════════════●════════════════════════►  │  │
│  │                        |                           │  │
│  │                       50%                          │  │
│  │                                                     │  │
│  │   [Drag slider or tap position]                    │  │
│  │                                                     │  │
│  └────────────────────────────────────────────────────┘  │
│                                                           │
│  ┌──────────────────────────────────────────────────┐    │
│  │  [Confirm]                      [Skip]           │    │
│  └──────────────────────────────────────────────────┘    │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

**Enhanced features:**
- Large touch target (full-width slider)
- Emoji visual aids
- Haptic feedback as you drag (if supported)
- Tap-to-jump to position
- Drag for fine control

---

## Voice Input (Experimental)

Accessibility-focused voice control.

### Voice Commands

**Dictation mode:**
```
"Define function hello"     → def hello():
"If name"                   → if name:
"For item in data"          → for item in data:
"Return result"             → return result
```

**Navigation:**
```
"Go to line 5"              → Jump to line 5
"Next line"                 → Move cursor down
"Previous word"             → Move cursor left by word
```

**Editing:**
```
"Delete line"               → Delete current line
"Undo"                      → Undo last action
"Run code"                  → Execute code
```

**Emotional input:**
```
"I feel frustrated"         → Record LT=0.8
"I'm enjoying this"         → Record RT=0.7
"This is neutral"           → Record both=0.5
```

### Voice Recognition Pipeline

```python
class VoiceDevice(InputDevice):
    """Voice input device using speech recognition."""

    def __init__(self):
        self.recognizer = speech_recognition.Recognizer()
        self.mic = speech_recognition.Microphone()
        self.command_map = load_voice_commands()

    def get_action(self) -> Action | None:
        """Listen for voice command."""
        try:
            audio = self.recognizer.listen(self.mic, timeout=1.0)
            text = self.recognizer.recognize_google(audio)
            return self.parse_command(text)
        except speech_recognition.WaitTimeoutError:
            return None

    def parse_command(self, text: str) -> Action:
        """Parse voice command to action."""
        text_lower = text.lower()

        # Check command map
        for pattern, action in self.command_map.items():
            if pattern in text_lower:
                return action

        # Fallback: dictation mode
        return Action.INSERT_TEXT(text)
```

**Challenges:**
- Accuracy (especially for code terms)
- Latency (speech recognition is slow)
- Background noise
- Accent/dialect variations

**Mitigations:**
- Keyword-based (not full natural language)
- Show recognition result before executing
- Allow correction ("No, I said 'for', not 'four'")
- Custom vocabulary (train on Python keywords)

---

## Hybrid Input

Mix and match input devices.

### Common Combinations

**Gamepad + Keyboard:**
- Gamepad: Navigation, execution, emotional input
- Keyboard: Fast typing of custom identifiers
- Switch seamlessly - keyboard typing pauses gamepad

**Touchscreen + Keyboard (Tablet):**
- Touchscreen: Button actions, cursor positioning
- Keyboard: Fast typing
- Best of both worlds

**Gamepad + Voice:**
- Gamepad: Primary input
- Voice: Quick commands while hands occupied
- Useful for teaching mode (talk while doing)

### Hot-Swapping

Switch input devices **mid-session** without interruption:

```python
class InputManager:
    def poll_input(self) -> Action | None:
        """Poll all devices, use first that responds."""
        for device in self.devices:
            action = device.get_action()
            if action:
                # Switch active device if different
                if device != self.active_device:
                    self.active_device = device
                    self.notify_device_switch(device)
                return action
        return None

    def notify_device_switch(self, device: InputDevice):
        """Show brief notification of device change."""
        show_toast(f"Switched to {device.name}")
```

**Visual indicator:**
```
┌──────────────────────────────────────┐
│  ⚙ Switched to Keyboard Mode         │
│  [Dismiss]                           │
└──────────────────────────────────────┘
```

---

## Device Capabilities

Different devices have different **capabilities**:

```python
class Capability(Enum):
    """What a device can do."""
    TYPING = "typing"                 # Can enter text
    ANALOG_INPUT = "analog_input"     # Analog triggers/sliders
    HAPTICS = "haptics"               # Vibration feedback
    PRECISE_CURSOR = "precise_cursor" # Mouse-like precision
    GESTURES = "gestures"             # Touch gestures
    AUDIO_OUTPUT = "audio_output"     # Can play sounds
    VOICE_INPUT = "voice_input"       # Voice commands
```

**Capability matrix:**

| Device         | Typing | Analog | Haptics | Cursor | Gestures | Audio | Voice |
|----------------|--------|--------|---------|--------|----------|-------|-------|
| Gamepad        | Slow   | ✓      | ✓       | No     | ✗        | ✗     | ✗     |
| Keyboard       | ✓      | ✗      | ✗       | ✗      | ✗        | ✗     | ✗     |
| Mouse          | ✗      | ✗      | ✗       | ✓      | ✗        | ✗     | ✗     |
| Touchscreen    | Medium | Slider | Mobile  | ✓      | ✓        | ✗     | ✗     |
| Voice          | ✗      | ✗      | ✗       | ✗      | ✗        | ✗     | ✓     |

**Graceful degradation:**
- If device lacks analog input → use slider UI
- If device lacks haptics → rely on visual/audio feedback
- If device lacks precise cursor → use line-based navigation
- If device lacks gestures → use buttons

---

## Platform-Specific Considerations

### Desktop (Windows/Mac/Linux)

**Advantages:**
- Full keyboard available
- High-resolution display
- Powerful hardware (smooth rendering)
- Multiple input devices

**Challenges:**
- Many possible keyboard layouts
- Gamepad drivers vary by OS
- Window management (full-screen vs windowed)

**Optimizations:**
- Detect keyboard layout, adapt shortcuts
- Use SDL2 for unified gamepad support
- Default to windowed with "Focus Mode" (minimal chrome)

### Mobile (iOS/Android)

**Advantages:**
- Touch-native interface
- Built-in accelerometer (shake gestures)
- Vibration motors (haptic feedback)
- Portability (learn anywhere)

**Challenges:**
- Limited screen space
- On-screen keyboard takes space
- Battery life concerns
- Performance constraints

**Optimizations:**
- Portrait mode: Full-screen code editor, buttons overlay
- Landscape mode: Split view (code left, buttons right)
- Lazy rendering (only render visible code)
- Cloud save (sync across devices)

### Console (Xbox/PlayStation/Nintendo)

**Advantages:**
- Controller-first design perfect fit
- Big screen (living room coding)
- Consistent hardware (easier optimization)

**Challenges:**
- No keyboard fallback
- Limited file system access
- Certification requirements

**Optimizations:**
- Radial typing as primary input
- USB keyboard support (if available)
- Cloud save via platform services

---

## Input Latency

Different input methods have different **latency profiles**:

| Input Method   | Average Latency | Notes                                  |
|----------------|-----------------|----------------------------------------|
| Gamepad (USB)  | 4-8ms           | Hardware-dependent                     |
| Gamepad (BT)   | 10-15ms         | Wireless adds latency                  |
| Keyboard (USB) | 2-5ms           | Fastest input method                   |
| Mouse          | 2-5ms           | Direct hardware access                 |
| Touchscreen    | 10-20ms         | Capacitive touch detection             |
| Voice          | 200-500ms       | Speech recognition processing          |

**Target: <50ms total latency** from input to visual feedback.

**Optimizations:**
- Direct hardware polling (not event queue)
- Render immediately on input
- Pre-render common states
- Separate input thread

---

## Implementation Reference

### Device Plugin System

```python
class InputDevicePlugin(ABC):
    """Base class for input device plugins."""

    @abstractmethod
    def detect(self) -> bool:
        """Check if this device is available."""
        pass

    @abstractmethod
    def initialize(self) -> InputDevice:
        """Initialize and return device instance."""
        pass

    @abstractmethod
    def priority(self) -> int:
        """Priority for auto-selection (higher = preferred)."""
        pass

# Registry
DEVICE_PLUGINS = [
    GamepadPlugin(),
    KeyboardPlugin(),
    TouchscreenPlugin(),
    VoicePlugin(),
]

def detect_and_initialize():
    """Detect all available devices."""
    devices = []
    for plugin in DEVICE_PLUGINS:
        if plugin.detect():
            devices.append(plugin.initialize())

    # Sort by priority
    devices.sort(key=lambda d: d.priority(), reverse=True)

    return devices
```

### Input Event Loop

```python
class InputEventLoop:
    """Main input event loop."""

    def __init__(self, devices: list[InputDevice]):
        self.devices = devices
        self.active_device = devices[0] if devices else None

    async def run(self):
        """Main event loop."""
        while True:
            # Poll all devices (non-blocking)
            for device in self.devices:
                action = device.get_action()
                if action:
                    await self.handle_action(action, device)

            # Small sleep to prevent busy-wait
            await asyncio.sleep(0.001)  # 1ms

    async def handle_action(self, action: Action, device: InputDevice):
        """Route action to appropriate handler."""
        # Switch active device if needed
        if device != self.active_device:
            self.active_device = device

        # Dispatch action
        match action:
            case Action.INSERT_DEF:
                await self.game.insert_def()
            case Action.RUN_CODE:
                await self.game.run_code()
            # ... etc
```

---

## Summary

The multi-input system makes LMSP **truly universal**:

- **Automatic detection** of available devices
- **Hot-swapping** between devices seamlessly
- **Unified abstraction** for all input types
- **Device-specific optimizations** for native feel
- **Graceful degradation** when capabilities missing
- **Hybrid support** for best-of-both-worlds

Whether you're on a couch with a gamepad, at a desk with a keyboard, on a tablet with touch, or using voice for accessibility, LMSP adapts to **your preferred way of interacting**.

The goal: **Code anywhere, anyhow**. The method: **Respect every input method equally**.

---

*Part of the LMSP Input Systems documentation.*
