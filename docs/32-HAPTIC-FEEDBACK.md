# Haptic Feedback - Feel Your Code

**The tactile dimension:** Controller vibration that teaches through touch.

---

## The Vision

Coding is traditionally a purely visual activity. LMSP adds **tactile feedback** through controller vibration, creating a multisensory learning experience.

Haptic feedback serves three purposes:

1. **Confirmation** - "Yes, your action worked"
2. **Guidance** - "There's something important here"
3. **Emotion** - "This moment feels like success/frustration"

Done right, haptics become **invisible teachers** - subtle pulses that guide you toward correct patterns without conscious awareness.

---

## Core Principles

### 1. Distinctive Patterns

Each event type has a **unique vibration signature**:

```
Success:     ═══ ═══          (two strong pulses)
Failure:     ═══════          (one long pulse)
Warning:     ═ ═ ═           (three short pulses)
Hint ready:  ═══░░░═══        (pulse-pause-pulse)
Typing:      ═                (micro-pulse per keypress)
```

**Why distinctive?** So you can recognize events **without looking at the screen**.

### 2. Graduated Intensity

Importance determines strength:

```
Critical:   ▓▓▓▓▓ 100% intensity
High:       ▓▓▓▓░  80% intensity
Medium:     ▓▓▓░░  60% intensity
Low:        ▓▓░░░  40% intensity
Subtle:     ▓░░░░  20% intensity
```

### 3. Non-Intrusive

Haptics should **enhance**, not distract:
- No constant vibration (fatigue)
- No jarring unexpected pulses
- Optional intensity adjustment
- Can be fully disabled

### 4. Learnable Language

Like Morse code, haptic patterns form a **tactile language** that becomes intuitive with practice.

---

## Event Catalog

### Test Results

**All tests passing:**
```
Pattern:    ═══ ═══ (double pulse)
Intensity:  80%
Duration:   200ms, pause 100ms, 200ms
Feel:       Satisfying, celebratory
When:       All tests pass on code run
```

**Some tests passing:**
```
Pattern:    ═══ ░░░ ═ (strong, pause, weak)
Intensity:  60%, 40%
Duration:   200ms, pause 150ms, 100ms
Feel:       Partial success, but incomplete
When:       2 of 3 tests pass
```

**All tests failing:**
```
Pattern:    ═══════ (single long pulse)
Intensity:  70%
Duration:   500ms
Feel:       Disappointment, but not harsh
When:       All tests fail
```

**Syntax error:**
```
Pattern:    ═ ═ ═ ═ (rapid taps)
Intensity:  50%
Duration:   100ms × 4
Feel:       "Something's wrong, check your syntax"
When:       Code has syntax errors
```

### Code Actions

**Successful insertion:**
```
Pattern:    ═ (micro-pulse)
Intensity:  20%
Duration:   30ms
Feel:       Barely noticeable confirmation
When:       Each character/chord inserted
```

**Invalid action:**
```
Pattern:    ═░═ (buzz-pause-buzz)
Intensity:  40%
Duration:   80ms, pause 50ms, 80ms
Feel:       "Can't do that here"
When:       Invalid syntax (e.g., return outside function)
```

**Undo:**
```
Pattern:    ░═══ (weak to strong)
Intensity:  30% → 50%
Duration:   150ms
Feel:       Rewinding, pulling back
When:       Undo action performed
```

**Auto-complete accepted:**
```
Pattern:    ═══ ░ ═══ (pulse-tick-pulse)
Intensity:  60%
Duration:   150ms, 50ms, 150ms
Feel:       "Good choice, confirmed"
When:       Smart complete suggestion accepted
```

### Hints and Guidance

**Hint available:**
```
Pattern:    ═══ ░░░ ═══ ░░░ (pulse-pause pattern)
Intensity:  30%
Duration:   120ms, pause 200ms, repeating
Feel:       "Psst, there's help if you want it"
When:       Hint unlocked but not yet viewed
Behavior:   Repeats every 10 seconds until viewed/dismissed
```

**Hint viewed:**
```
Pattern:    ═══ (single pulse)
Intensity:  40%
Duration:   150ms
Feel:       Acknowledgment
When:       Hint dialog opened
```

**Approaching solution:**
```
Pattern:    ═ ░ ═ ░ ═ (accelerating pulse)
Intensity:  30% → 60%
Duration:   100ms, gradually increasing
Feel:       "Getting warmer!"
When:       Code gets closer to passing tests
```

### Emotional Input

**RT/LT pressure feedback:**
```
Pattern:    ═ (continuous subtle pulse)
Intensity:  10% + (trigger_value × 20%)
Duration:   Continuous while trigger held
Feel:       Proportional to your emotional input
When:       During emotional prompts
Behavior:   Intensity matches trigger pressure
```

**Emotional input confirmed:**
```
Pattern:    ═══ (single strong pulse)
Intensity:  70%
Duration:   200ms
Feel:       "Got it, thank you"
When:       A button pressed to confirm emotion
```

### Flow State

**Entering flow:**
```
Pattern:    ═══ ░░░ ═══ ░░░ ═══ (triple pulse)
Intensity:  50%
Duration:   100ms, pause 100ms, repeating
Feel:       "You're in the zone!"
When:       High enjoyment + low frustration + fast progress
```

**Flow maintained:**
```
Pattern:    ═ (periodic subtle pulse)
Intensity:  15%
Duration:   50ms every 30 seconds
Feel:       Gentle reminder you're flowing
When:       Continuous flow state
```

**Flow broken:**
```
Pattern:    ═══ ░░░░░░ (long pulse, fade)
Intensity:  40% → 0%
Duration:   300ms
Feel:       "It's okay, take a breath"
When:       Frustration spike or long pause
```

### Challenge Progress

**Challenge started:**
```
Pattern:    ═══ (single pulse)
Intensity:  50%
Duration:   150ms
Feel:       "Let's begin"
When:       New challenge loaded
```

**Checkpoint reached:**
```
Pattern:    ═══ ░ ═══ (double pulse)
Intensity:  60%
Duration:   150ms, pause 80ms, 150ms
Feel:       Progress marker
When:       25%, 50%, 75% of tests passing
```

**Challenge complete:**
```
Pattern:    ═══ ═══ ═══ (triple pulse, building)
Intensity:  60%, 70%, 80%
Duration:   150ms, pause 100ms, repeating
Feel:       Celebration!
When:       All tests pass, challenge complete
```

**Personal best:**
```
Pattern:    ═══ ░ ═══ ░ ═══ ░ ═══ (quad pulse)
Intensity:  70%, 75%, 80%, 85%
Duration:   150ms, pause 80ms, repeating
Feel:       Extra celebration
When:       Beat previous best time
```

### Multiplayer Events

**Other player typing:**
```
Pattern:    ░═░ (subtle tap)
Intensity:  15%
Duration:   40ms
Feel:       Awareness of other player activity
When:       Other player makes edit (if spectating/coop)
```

**Other player passed test:**
```
Pattern:    ═ ░ ═ (double tap)
Intensity:  30%
Duration:   80ms, pause 50ms, 80ms
Feel:       "Your teammate made progress"
When:       Coop partner passes a test
```

**Race opponent ahead:**
```
Pattern:    ═══ (single pulse)
Intensity:  40%
Duration:   120ms
Feel:       Awareness, not alarm
When:       Opponent completes before you (race mode)
```

**Teaching moment:**
```
Pattern:    ═══ ░░░ ═ (pulse-pause-tap)
Intensity:  35%
Duration:   150ms, pause 200ms, 80ms
Feel:       "Pay attention to this"
When:       Teacher AI highlights something important
```

### Unlocks and Achievements

**Concept unlocked:**
```
Pattern:    ═══ ░ ═══ ░ ═════ (build-up)
Intensity:  50%, 60%, 80%
Duration:   120ms, pause 80ms, then 300ms final
Feel:       "Something new is available!"
When:       New concept/challenge unlocked
```

**Achievement earned:**
```
Pattern:    ═══ ═══ ═══════ (triple + long)
Intensity:  70%, 75%, 90%
Duration:   150ms each, then 400ms
Feel:       Major accomplishment
When:       Achievement unlocked
```

**Level up:**
```
Pattern:    ═══ ░░░ ═══ ░░░ ═══════ (build to climax)
Intensity:  60%, 70%, 100%
Duration:   150ms, pause 100ms, 150ms, pause, 500ms
Feel:       Triumphant
When:       Mastery level increased
```

---

## Controller-Specific Notes

Different controllers have different haptic capabilities:

### Xbox Controllers

**Standard rumble motors:**
- Left motor: Low-frequency (bass rumble)
- Right motor: High-frequency (treble buzz)

**Mapping:**
- Success/celebration: Both motors
- Failure/warning: Left motor only
- Hints/guidance: Right motor only
- Typing feedback: Right motor (subtle)

### PlayStation Controllers (DualSense)

**Advanced haptics:**
- Individual actuators for left/right
- Adaptive triggers with resistance
- Speaker for audio feedback

**Enhanced features:**
- Adaptive trigger resistance for emotional input
  - RT gets slightly harder to pull as you express more enjoyment
  - Creates tactile gradient matching emotional scale
- Directional haptics
  - Hint on left side = check left of screen
  - Success on right = check right side

### Nintendo Pro Controller

**HD Rumble:**
- Precise vibration control
- Can simulate textures

**Enhanced features:**
- Different "textures" for different event types
  - Success feels "smooth"
  - Error feels "rough"
  - Hint feels "gentle wave"

### Generic Controllers

**Basic rumble:**
- Single motor, on/off only
- Limited pattern capability

**Fallback:**
- Use duration to communicate
  - Short = good
  - Long = bad
  - Multiple = special
- Rely more on visual/audio feedback

---

## Adaptive Intensity

The system learns **your preferred intensity level**:

### Auto-Calibration

```
┌──────────────────────────────────────────────────────────┐
│  Haptic Calibration                                       │
│                                                           │
│  Let's find your perfect vibration level.                │
│                                                           │
│  You'll feel 5 different intensities.                    │
│  Pick your favorite!                                     │
│                                                           │
│  [A] Start calibration                                   │
└──────────────────────────────────────────────────────────┘
```

**Calibration process:**
1. Play pattern at 20%, ask "Too weak?"
2. Play pattern at 40%, ask "Just right?"
3. Play pattern at 60%, ask "Too strong?"
4. Play pattern at 80%, ask "Way too strong?"
5. Set baseline from responses

### Personal Preferences

```
┌──────────────────────────────────────────────────────────┐
│  Haptic Settings                                          │
│                                                           │
│  Master Intensity:  ▓▓▓▓▓▓▓░░░ 70%                        │
│                     [D-Pad Left/Right to adjust]          │
│                                                           │
│  Test Pattern: [A] Feel it                               │
│                                                           │
│  Per-Event Settings:                                     │
│    Success:         ▓▓▓▓▓▓▓░░░ 80%                        │
│    Failure:         ▓▓▓▓▓░░░░░ 60%                        │
│    Hints:           ▓▓▓░░░░░░░ 40%                        │
│    Typing:          ▓░░░░░░░░░ 20%                        │
│                                                           │
│  [A] Save  [B] Cancel  [X] Disable All                   │
└──────────────────────────────────────────────────────────┘
```

**Learning preferences:**
- If player frequently disables haptics after certain events, reduce intensity
- If player increases volume, they may want stronger haptics
- If player is in flow state, reduce interruption haptics

---

## Accessibility Modes

### Haptics-Only Mode

For visually impaired players, haptics become primary feedback:

```
Enhanced patterns:
  1 test passing:  ═
  2 tests passing: ═ ═
  3 tests passing: ═ ═ ═
  4 tests passing: ═ ═ ═ ═
  5 tests passing: ═ ═ ═ ═ ═

Syntax error location:
  Line 1: ═ (top of controller)
  Line 5: ═════ (longer duration = further down)

Hint level:
  Level 1: ═
  Level 2: ═ ═
  Level 3: ═ ═ ═
  Level 4: ═ ═ ═ ═ (max hints)
```

**Audio + Haptic pairing:**
- Every haptic pattern paired with audio cue
- Screen reader integration
- Haptic navigation of code (feel indent levels)

### Sensory Sensitivity Mode

For players with sensory processing sensitivities:

```
┌──────────────────────────────────────────────────────────┐
│  Sensory Sensitivity Mode                                 │
│                                                           │
│  Reduces haptic intensity and frequency.                 │
│                                                           │
│  ✓ No surprise vibrations                                │
│  ✓ Gentler patterns                                      │
│  ✓ Fewer interruptions                                   │
│  ✓ Predictable feedback only                             │
│                                                           │
│  [A] Enable  [B] Cancel                                  │
└──────────────────────────────────────────────────────────┘
```

**Changes:**
- Reduce all intensities by 50%
- Disable "surprise" haptics (unlocks, achievements)
- Only haptic on explicit actions (button presses, test runs)
- No background haptics (hints available, flow state)

---

## Integration with Game Events

### Emotional Input Integration

During emotional prompts, haptics **mirror your input**:

```python
def update_emotional_haptics(rt_value: float, lt_value: float):
    """
    Create haptic feedback that mirrors emotional trigger pressure.
    """
    if rt_value > 0.1:  # Right trigger (enjoyment)
        intensity = 0.1 + (rt_value * 0.2)  # 10% to 30%
        pattern = "smooth_pulse"
        controller.rumble(intensity, pattern)

    elif lt_value > 0.1:  # Left trigger (frustration)
        intensity = 0.1 + (lt_value * 0.2)
        pattern = "rough_buzz"
        controller.rumble(intensity, pattern)

    else:  # Neutral
        controller.rumble(0, "none")
```

**Why?** Creates **tactile feedback loop** - you feel your own emotional input, reinforcing the analog nature of the scale.

### Adaptive Learning Integration

The adaptive engine can trigger haptics based on learning patterns:

**Break suggestion:**
```
Pattern:    ═══ ░░░░░░ ═══ ░░░░░░ (fading pulse)
Intensity:  50% → 30%
Duration:   200ms, pause 400ms, repeating
Feel:       "Take a rest"
When:       Adaptive engine suggests break
```

**Flow trigger detected:**
```
Pattern:    ═══════ (sustained rumble)
Intensity:  40%
Duration:   300ms
Feel:       "Keep going, you're on a roll!"
When:       Adaptive engine detects concept that triggers flow
```

**Weakness drilling:**
```
Pattern:    ═ ░ ═ ░ ═ ░ (gentle encouragement)
Intensity:  30%
Duration:   100ms, pause 200ms, repeating
Feel:       "You've got this"
When:       Resurfacing a struggled concept
```

---

## Testing and Development

### Haptic Debug Mode

For developers and curious players:

```
┌──────────────────────────────────────────────────────────┐
│  Haptic Debug Mode                                        │
│                                                           │
│  All haptic events shown on screen:                      │
│                                                           │
│  [TEST_PASS] Double pulse, 80%, 200ms                    │
│  [TYPING] Micro pulse, 20%, 30ms                         │
│  [HINT_READY] Pulse-pause pattern, 30%, repeating        │
│                                                           │
│  Test Patterns:                                          │
│    [A] Test Pass       [B] Test Fail                     │
│    [X] Hint Available  [Y] Challenge Complete            │
│                                                           │
│  [Select] Exit Debug Mode                                │
└──────────────────────────────────────────────────────────┘
```

### Custom Pattern Editor

For advanced users:

```
┌──────────────────────────────────────────────────────────┐
│  Haptic Pattern Editor                                    │
│                                                           │
│  Creating pattern: "my_success"                          │
│                                                           │
│  Timeline (500ms):                                       │
│  ═══ ░░░ ═══ ░░░ ═══                                     │
│  0ms 150  300  450  600                                  │
│                                                           │
│  Intensity:                                              │
│  80% 0%  70% 0%  90%                                     │
│                                                           │
│  [A] Add pulse  [B] Remove  [X] Test  [Y] Save           │
│                                                           │
│  Assign to event: [Select dropdown]                      │
└──────────────────────────────────────────────────────────┘
```

---

## Performance Considerations

### Battery Life

Rumble motors consume significant power:

```
Battery Impact (per hour):
  No haptics:      0% extra drain
  Subtle (20%):    ~2% extra drain
  Medium (50%):    ~5% extra drain
  Strong (80%):    ~8% extra drain
  Constant (100%): ~15% extra drain
```

**Auto-optimization:**
- Reduce intensity on low battery (<20%)
- Disable background haptics on low battery
- Notify user: "Haptics reduced to save battery"

### Latency

Haptic feedback must be **instantaneous**:

```
Target latencies:
  Button press → haptic: <10ms
  Test result → haptic:  <50ms
  Background hint:       No latency requirement
```

**Implementation:**
- Direct hardware access (not queued)
- High-priority thread for haptic events
- Pre-load patterns (don't generate on-demand)

---

## Summary

Haptic feedback transforms LMSP from purely visual to **multisensory learning**:

- **Distinctive patterns** for each event type
- **Graduated intensity** based on importance
- **Non-intrusive design** that enhances, doesn't distract
- **Learnable language** that becomes intuitive
- **Accessibility-first** with modes for all players
- **Controller-specific** taking advantage of hardware capabilities

When done right, haptics become **invisible teachers** - you don't consciously notice them, but you **feel more confident** because of them.

Your controller becomes an extension of your learning, celebrating victories, cushioning failures, and guiding you toward mastery through touch.

---

*Part of the LMSP Input Systems documentation.*
