/*
 * LMSP Gamepad Support
 * ====================
 *
 * JavaScript Gamepad API integration for controller input.
 * Provides smooth, responsive gamepad handling for couch gaming.
 *
 * Features:
 * - Automatic gamepad detection
 * - Button press handling
 * - Analog stick support
 * - Trigger (RT/LT) analog input for emotional feedback
 * - Connection/disconnection events
 */

// Gamepad state
let gamepad = null;
let gamepadIndex = null;

// Button mappings (standard gamepad layout)
const BUTTON_MAPPING = {
    A: 0,
    B: 1,
    X: 2,
    Y: 3,
    LB: 4,
    RB: 5,
    LT: 6,
    RT: 7,
    SELECT: 8,
    START: 9,
    L_STICK: 10,
    R_STICK: 11,
    DPAD_UP: 12,
    DPAD_DOWN: 13,
    DPAD_LEFT: 14,
    DPAD_RIGHT: 15,
};

// Initialize gamepad support
function initGamepad() {
    window.addEventListener("gamepadconnected", onGamepadConnected);
    window.addEventListener("gamepaddisconnected", onGamepadDisconnected);

    // Start polling loop
    requestAnimationFrame(updateGamepad);
}

// Handle gamepad connection
function onGamepadConnected(e) {
    console.log("Gamepad connected:", e.gamepad.id);
    gamepad = e.gamepad;
    gamepadIndex = e.gamepad.index;

    // Update UI
    const status = document.getElementById("gamepad-status");
    if (status) {
        status.textContent = `🎮 ${e.gamepad.id}`;
        status.classList.add("connected");
    }

    // Emit custom event
    window.dispatchEvent(new CustomEvent("lmsp-gamepad-connected", {
        detail: {
            id: e.gamepad.id,
            index: e.gamepad.index,
            buttons: e.gamepad.buttons.length,
            axes: e.gamepad.axes.length,
        }
    }));
}

// Handle gamepad disconnection
function onGamepadDisconnected(e) {
    console.log("Gamepad disconnected:", e.gamepad.id);
    gamepad = null;
    gamepadIndex = null;

    // Update UI
    const status = document.getElementById("gamepad-status");
    if (status) {
        status.textContent = "⚙️ Gamepad Disconnected";
        status.classList.remove("connected");
    }

    // Emit custom event
    window.dispatchEvent(new CustomEvent("lmsp-gamepad-disconnected"));
}

// Main gamepad update loop
function updateGamepad() {
    if (gamepadIndex !== null) {
        // Get fresh gamepad state
        const gamepads = navigator.getGamepads();
        gamepad = gamepads[gamepadIndex];

        if (gamepad) {
            // Process button presses
            processButtons(gamepad);

            // Process analog sticks
            processAnalogSticks(gamepad);

            // Process triggers (for emotional feedback)
            processTriggers(gamepad);
        }
    }

    // Continue polling
    requestAnimationFrame(updateGamepad);
}

// Process button presses
function processButtons(gamepad) {
    gamepad.buttons.forEach((button, index) => {
        if (button.pressed) {
            handleButtonPress(index, button.value);
        }
    });
}

// Process analog sticks
function processAnalogSticks(gamepad) {
    // Left stick (axes 0, 1)
    const leftX = gamepad.axes[0];
    const leftY = gamepad.axes[1];

    // Right stick (axes 2, 3)
    const rightX = gamepad.axes[2];
    const rightY = gamepad.axes[3];

    // Apply deadzone
    const deadzone = 0.15;

    if (Math.abs(leftX) > deadzone || Math.abs(leftY) > deadzone) {
        window.dispatchEvent(new CustomEvent("lmsp-stick-left", {
            detail: { x: leftX, y: leftY }
        }));
    }

    if (Math.abs(rightX) > deadzone || Math.abs(rightY) > deadzone) {
        window.dispatchEvent(new CustomEvent("lmsp-stick-right", {
            detail: { x: rightX, y: rightY }
        }));
    }
}

// Process triggers (RT/LT for emotional feedback)
function processTriggers(gamepad) {
    // LT and RT are often buttons 6 and 7 with analog values
    const ltButton = gamepad.buttons[BUTTON_MAPPING.LT];
    const rtButton = gamepad.buttons[BUTTON_MAPPING.RT];

    const ltValue = ltButton ? ltButton.value : 0;
    const rtValue = rtButton ? rtButton.value : 0;

    // Emit trigger events for emotional feedback
    if (ltValue > 0.01 || rtValue > 0.01) {
        window.dispatchEvent(new CustomEvent("lmsp-triggers", {
            detail: {
                left: ltValue,   // Frustration
                right: rtValue,  // Enjoyment
            }
        }));
    }
}

// Handle individual button presses
let lastButtonState = {};

function handleButtonPress(buttonIndex, value) {
    // Debounce: only fire once per press
    if (lastButtonState[buttonIndex]) {
        return;
    }
    lastButtonState[buttonIndex] = true;

    // Emit button event
    window.dispatchEvent(new CustomEvent("lmsp-button", {
        detail: {
            button: buttonIndex,
            value: value,
            name: getButtonName(buttonIndex),
        }
    }));

    // Handle common button actions
    switch(buttonIndex) {
        case BUTTON_MAPPING.A:
            handleAButton();
            break;
        case BUTTON_MAPPING.B:
            handleBButton();
            break;
        case BUTTON_MAPPING.X:
            handleXButton();
            break;
        case BUTTON_MAPPING.Y:
            handleYButton();
            break;
        case BUTTON_MAPPING.START:
            handleStartButton();
            break;
    }

    // Clear button state after short delay
    setTimeout(() => {
        lastButtonState[buttonIndex] = false;
    }, 200);
}

// Get button name from index
function getButtonName(index) {
    for (const [name, buttonIndex] of Object.entries(BUTTON_MAPPING)) {
        if (buttonIndex === index) {
            return name;
        }
    }
    return `Button ${index}`;
}

// Button action handlers
function handleAButton() {
    console.log("A button pressed - Confirm");
    // Trigger HTMX or form submission
    const activeElement = document.activeElement;
    if (activeElement && activeElement.tagName === "BUTTON") {
        activeElement.click();
    }
}

function handleBButton() {
    console.log("B button pressed - Back");
    // Navigate back or cancel
    window.history.back();
}

function handleXButton() {
    console.log("X button pressed");
}

function handleYButton() {
    console.log("Y button pressed");
}

function handleStartButton() {
    console.log("Start button pressed - Menu");
    // Toggle menu or settings
}

// Utility: Check if gamepad is connected
function isGamepadConnected() {
    return gamepad !== null;
}

// Utility: Get current trigger values
function getTriggerValues() {
    if (!gamepad) return { left: 0, right: 0 };

    const ltButton = gamepad.buttons[BUTTON_MAPPING.LT];
    const rtButton = gamepad.buttons[BUTTON_MAPPING.RT];

    return {
        left: ltButton ? ltButton.value : 0,
        right: rtButton ? rtButton.value : 0,
    };
}

// Initialize on page load
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initGamepad);
} else {
    initGamepad();
}

// Export for use in other scripts
window.LMSP = window.LMSP || {};
window.LMSP.gamepad = {
    isConnected: isGamepadConnected,
    getTriggers: getTriggerValues,
};

// Self-teaching note:
//
// This file demonstrates:
// - JavaScript Gamepad API (Browser API for controller support)
// - Event-driven programming with custom events
// - Animation frame loop for smooth polling
// - Debouncing for button presses
// - Deadzone handling for analog sticks
// - State management in JavaScript
//
// Prerequisites:
// - JavaScript basics (functions, objects, events)
// - Browser APIs (requestAnimationFrame, CustomEvent)
// - Event handling patterns
//
// The Gamepad API is used by:
// - Steam Big Picture Mode
// - Xbox Cloud Gaming
// - Stadia
// - Console web browsers
//
// This implementation provides smooth, responsive controller support
// for couch gaming on OLED TVs!
