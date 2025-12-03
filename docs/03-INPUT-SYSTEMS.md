# Input Systems: Controller & Emotional

**Status:** Documentation skeleton - to be filled

## Overview

Multi-modal input handling: gamepad, keyboard, emotional triggers, and radial typing.

### Table of Contents
- Input Architecture
- Gamepad Handling
- Radial Thumbstick Typing
- Easy Mode (Training Wheels)
- Emotional Input System
- Keyboard Fallback
- Touch Input

### Key Components
- `lmsp/input/gamepad.py` - Controller handling
- `lmsp/input/radial.py` - Radial thumbstick typing
- `lmsp/input/emotional.py` - RT/LT emotional input
- `lmsp/input/keyboard.py` - Keyboard fallback
- `lmsp/input/touch.py` - Touchscreen input

### Dependencies
- pygame for gamepad input
- Custom radial menu system
- Emotional state tracking

### Testing Strategy
- Unit tests for input mapping
- Mock gamepad events
- Emotional input validation

## To Be Completed

- [ ] Input architecture diagram
- [ ] Gamepad event mapping
- [ ] Radial chord mapping table
- [ ] Easy mode button specifications
- [ ] Emotional dimension definitions
- [ ] Keyboard binding configuration
- [ ] Touch input gestures
