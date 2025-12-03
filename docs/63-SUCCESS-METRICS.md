# Success Metrics

Comprehensive metrics for measuring LMSP's effectiveness as a learning platform.

---

## Overview

LMSP success is measured across five dimensions:

1. **Learning Efficacy** - Does it actually teach Python better?
2. **Engagement** - Do learners stick with it?
3. **Controller Adoption** - Do people use the gamepad?
4. **Multiplayer Impact** - Does AI collaboration help?
5. **Platform Health** - Is the system reliable?

Each dimension has quantitative targets and measurement strategies.

---

## 1. Learning Efficacy

### 1.1 Concept Retention

**Definition:** Percentage of concepts recalled 30 days after learning.

**Target:** >80% retention at 30 days

**Baseline:** Traditional passive learning ~40% retention at 30 days

**Measurement Strategy:**

```python
async def measure_retention(player_id: str, concept: str, days: int = 30) -> float:
    """
    Measure concept retention over time.

    1. Identify when concept was mastered (mastery level 3+)
    2. Wait `days` days
    3. Present recall challenge (no hints)
    4. Measure success rate
    """
    profile = load_profile(player_id)

    # Find mastery date
    mastery_date = profile.get_mastery_date(concept)
    if not mastery_date:
        return None

    # Wait for retention period
    days_since_mastery = (datetime.now() - mastery_date).days
    if days_since_mastery < days:
        return None  # Too soon

    # Present recall challenge
    challenge = get_recall_challenge(concept)
    result = await present_challenge(player_id, challenge, hints_disabled=True)

    return 1.0 if result.success else 0.0
```

**Cohort Analysis:**
- Track cohorts by starting date
- Compare retention curves over time
- Identify concepts with poor retention (need better teaching)

**Success Threshold:**
- **Excellent:** >85% retention at 30 days
- **Good:** 70-85% retention
- **Needs Work:** <70% retention

**Data Collection:**
- Automatic recall challenges scheduled by spaced repetition system
- Opt-in for research participants (with consent)
- Anonymized aggregation

---

### 1.2 Time to Proficiency

**Definition:** Time from starting a concept to achieving mastery (level 3).

**Target:** 50% faster than traditional courses

**Baseline:**
- Traditional course: ~4 hours per concept (avg)
- LMSP target: ~2 hours per concept

**Measurement Strategy:**

```python
def measure_time_to_proficiency(player_id: str, concept: str) -> float:
    """
    Calculate time from first attempt to mastery.

    Returns: Time in hours
    """
    profile = load_profile(player_id)
    attempts = profile.get_attempts_for_concept(concept)

    if not attempts:
        return None

    first_attempt = min(a.timestamp for a in attempts)
    mastery_time = profile.get_mastery_date(concept)

    if not mastery_time:
        return None  # Not mastered yet

    return (mastery_time - first_attempt) / 3600  # Convert to hours
```

**Segmentation:**
- By concept level (Level 0-6)
- By player background (beginner vs experienced)
- By fun factor type (puzzle, speedrun, etc.)

**Success Threshold:**
- **Excellent:** <1.5 hours per concept
- **Good:** 1.5-2.5 hours
- **Needs Work:** >2.5 hours

**Confounding Variables:**
- Break time (not counted)
- Prior experience (segment by background)
- Challenge difficulty (normalize by level)

---

### 1.3 Flow State Frequency

**Definition:** Percentage of session time spent in flow state.

**Target:** >30% of session time in flow

**Baseline:** Traditional learning rarely achieves flow

**Measurement Strategy:**

```python
def measure_flow_frequency(session: Session) -> float:
    """
    Calculate percentage of session in flow state.

    Flow criteria:
    - High enjoyment (>0.7)
    - Low frustration (<0.3)
    - Rapid progress (challenges completed quickly)
    - No breaks/hints needed
    """
    total_time = session.duration
    flow_time = 0.0

    for segment in session.segments:
        if (segment.avg_enjoyment > 0.7 and
            segment.avg_frustration < 0.3 and
            segment.challenges_completed > 0 and
            segment.hints_used == 0):
            flow_time += segment.duration

    return flow_time / total_time
```

**Flow Indicators:**
- Emotional state: High enjoyment + low frustration
- Behavioral: Fast completion, no hints
- Temporal: Long uninterrupted streaks

**Success Threshold:**
- **Excellent:** >40% flow state
- **Good:** 25-40%
- **Needs Work:** <25%

**Optimization:**
- Track which concepts trigger flow
- Optimize adaptive engine to maintain flow
- Identify flow-breaking patterns

---

### 1.4 Mastery Depth

**Definition:** Quality of understanding, measured by performance on novel challenges.

**Target:** 90%+ success on novel challenges for mastered concepts

**Measurement Strategy:**

```python
async def measure_mastery_depth(player_id: str, concept: str) -> float:
    """
    Test mastery with novel challenges not seen during learning.

    1. Verify concept is mastered
    2. Present 3 novel challenges (not in concept's challenge set)
    3. Measure success rate
    """
    profile = load_profile(player_id)

    if profile.get_mastery(concept) < 3:
        return None  # Not mastered

    # Get novel challenges
    novel_challenges = get_novel_challenges(concept, count=3)

    # Present without hints
    results = []
    for challenge in novel_challenges:
        result = await present_challenge(player_id, challenge, hints_disabled=True)
        results.append(result.success)

    return sum(results) / len(results)
```

**Novel Challenge Criteria:**
- Not in concept's challenge set
- Tests same underlying skill
- Different context/application

**Success Threshold:**
- **Excellent:** >95% success on novel challenges
- **Good:** 85-95%
- **Needs Work:** <85%

---

### 1.5 Transfer Learning

**Definition:** Ability to apply learned concepts to new domains.

**Target:** 80%+ success on cross-domain challenges

**Measurement Strategy:**

```python
async def measure_transfer(player_id: str, source_concept: str, target_domain: str) -> float:
    """
    Test if skills transfer to new domain.

    Example:
    - Source: "list_comprehensions" (learned in data processing context)
    - Target: "game_development" (apply to game logic)
    """
    profile = load_profile(player_id)

    if profile.get_mastery(source_concept) < 3:
        return None

    # Get cross-domain challenge
    challenge = get_cross_domain_challenge(source_concept, target_domain)
    result = await present_challenge(player_id, challenge)

    return 1.0 if result.success else 0.0
```

**Domains:**
- Data processing
- Web development
- Game development
- Automation
- Scientific computing

**Success Threshold:**
- **Excellent:** >85% transfer success
- **Good:** 70-85%
- **Needs Work:** <70%

---

## 2. Engagement

### 2.1 Session Length

**Definition:** Average duration of a single learning session.

**Target:** 25-35 minutes (sweet spot)

**Rationale:**
- Too short (<15 min): Not enough time to reach flow
- Too long (>45 min): Fatigue and diminishing returns
- Optimal: 25-35 min for sustained focus

**Measurement Strategy:**

```python
def measure_session_length(player_id: str, days: int = 30) -> dict:
    """
    Analyze session lengths over time.

    Returns:
    - Average session length
    - Distribution (histogram)
    - Trend (increasing/decreasing/stable)
    """
    profile = load_profile(player_id)
    sessions = profile.get_sessions(last_n_days=days)

    lengths = [s.duration / 60 for s in sessions]  # Convert to minutes

    return {
        "avg_length": np.mean(lengths),
        "median_length": np.median(lengths),
        "distribution": np.histogram(lengths, bins=[0, 10, 20, 30, 40, 50, 60]),
        "trend": calculate_trend(lengths)
    }
```

**Success Threshold:**
- **Excellent:** Avg 28-32 minutes
- **Good:** 20-28 or 32-40 minutes
- **Needs Work:** <20 or >40 minutes

**Interventions:**
- If too short: Encourage flow state, reduce friction
- If too long: Suggest breaks, detect fatigue

---

### 2.2 Return Rate

**Definition:** Percentage of players who return the next day.

**Target:** >60% next-day return rate

**Baseline:**
- Traditional courses: ~30% next-day return
- Mobile games: ~40% next-day return

**Measurement Strategy:**

```python
def measure_return_rate(cohort_start_date: date, day: int = 1) -> float:
    """
    Measure return rate for a cohort.

    day=1: Next-day return
    day=7: Week-later return
    day=30: Month-later return
    """
    cohort = get_cohort(cohort_start_date)
    total = len(cohort)

    returned = 0
    for player_id in cohort:
        profile = load_profile(player_id)
        if profile.has_session_on_day(cohort_start_date + timedelta(days=day)):
            returned += 1

    return returned / total
```

**Cohort Tracking:**
- Day 1 (next day): >60%
- Day 7 (week later): >40%
- Day 30 (month later): >25%

**Success Threshold:**
- **Excellent:** >70% next-day return
- **Good:** 50-70%
- **Needs Work:** <50%

**Churn Analysis:**
- When do players drop off?
- What concepts cause churn?
- What recovers churn (notifications, new content)?

---

### 2.3 Completion Rate

**Definition:** Percentage of started curricula that are completed.

**Target:** >70% complete chosen curriculum

**Baseline:**
- MOOCs: ~10% completion
- Traditional courses: ~60% completion

**Measurement Strategy:**

```python
def measure_completion_rate(player_id: str) -> float:
    """
    Measure curriculum completion.

    For project-driven learners:
    - Did they complete the path to their goal?

    For exploratory learners:
    - Did they master majority of attempted concepts?
    """
    profile = load_profile(player_id)

    if profile.has_project_goal():
        # Project-driven: complete path to goal
        goal = profile.project_goal
        required_concepts = goal.required_concepts
        mastered = [c for c in required_concepts if profile.get_mastery(c) >= 3]
        return len(mastered) / len(required_concepts)
    else:
        # Exploratory: mastery rate of attempted concepts
        attempted = profile.get_attempted_concepts()
        mastered = [c for c in attempted if profile.get_mastery(c) >= 3]
        return len(mastered) / len(attempted) if attempted else 0.0
```

**Success Threshold:**
- **Excellent:** >80% completion
- **Good:** 60-80%
- **Needs Work:** <60%

**Drop-off Analysis:**
- Which concepts cause abandonment?
- Is scaffolding insufficient?
- Is pacing too fast/slow?

---

### 2.4 Streak Length

**Definition:** Longest consecutive days with at least one session.

**Target:** Median streak >7 days

**Measurement Strategy:**

```python
def measure_streaks(player_id: str) -> dict:
    """
    Analyze learning streaks.

    Returns:
    - Current streak
    - Longest streak
    - Total streaks >3 days
    """
    profile = load_profile(player_id)
    sessions = profile.get_all_sessions()

    # Get unique session dates
    dates = sorted(set(s.date for s in sessions))

    # Find streaks
    streaks = []
    current_streak = 1

    for i in range(1, len(dates)):
        if (dates[i] - dates[i-1]).days == 1:
            current_streak += 1
        else:
            if current_streak > 0:
                streaks.append(current_streak)
            current_streak = 1

    if current_streak > 0:
        streaks.append(current_streak)

    return {
        "current_streak": streaks[-1] if streaks else 0,
        "longest_streak": max(streaks) if streaks else 0,
        "total_streaks_3plus": sum(1 for s in streaks if s >= 3)
    }
```

**Success Threshold:**
- **Excellent:** Median streak >14 days
- **Good:** Median streak 7-14 days
- **Needs Work:** Median streak <7 days

**Streak Incentives:**
- Visualize streaks in UI
- Celebrate milestones (7, 14, 30 days)
- Gentle reminders (not nagging)

---

### 2.5 Challenge Attempts per Session

**Definition:** Average number of challenges attempted per session.

**Target:** 4-6 challenges per session

**Rationale:**
- Too few (<3): Not enough practice
- Too many (>8): Rushing, shallow learning
- Optimal: 4-6 for depth + variety

**Measurement Strategy:**

```python
def measure_attempts_per_session(player_id: str, days: int = 30) -> float:
    """
    Calculate average challenges per session.
    """
    profile = load_profile(player_id)
    sessions = profile.get_sessions(last_n_days=days)

    attempts_per_session = [len(s.attempts) for s in sessions]
    return np.mean(attempts_per_session)
```

**Success Threshold:**
- **Excellent:** 4-6 challenges/session
- **Good:** 3-4 or 6-8
- **Needs Work:** <3 or >8

---

## 3. Controller Adoption

### 3.1 Easy Mode Graduation

**Definition:** Percentage of players who transition from Easy Mode to Radial Typing.

**Target:** 80% graduate within 10 hours

**Measurement Strategy:**

```python
def measure_easy_mode_graduation(player_id: str) -> dict:
    """
    Track transition from Easy Mode to Radial Typing.

    Returns:
    - Hours in Easy Mode before switching
    - Still in Easy Mode? (bool)
    - Radial typing WPM after switch
    """
    profile = load_profile(player_id)

    easy_mode_sessions = profile.get_sessions(input_mode="easy_mode")
    radial_sessions = profile.get_sessions(input_mode="radial")

    if not radial_sessions:
        # Still in Easy Mode
        total_easy_hours = sum(s.duration for s in easy_mode_sessions) / 3600
        return {
            "graduated": False,
            "hours_in_easy": total_easy_hours
        }

    # Graduated
    first_radial = min(s.timestamp for s in radial_sessions)
    easy_hours = sum(s.duration for s in easy_mode_sessions if s.timestamp < first_radial) / 3600

    # Measure WPM after switching
    radial_wpm = profile.get_typing_speed(input_mode="radial", after=first_radial)

    return {
        "graduated": True,
        "hours_in_easy": easy_hours,
        "radial_wpm": radial_wpm
    }
```

**Success Threshold:**
- **Excellent:** >85% graduate within 8 hours
- **Good:** 70-85% within 10 hours
- **Needs Work:** <70% or >12 hours

**Training Effectiveness:**
- Is Easy Mode teaching the foundations?
- Are radial menus intuitive?
- Do players feel ready to switch?

---

### 3.2 Radial Typing Speed

**Definition:** Words per minute (WPM) using radial thumbstick typing.

**Target:** 20+ WPM after 5 hours practice

**Baseline:**
- Keyboard typing: 40-60 WPM (average)
- Radial typing (no practice): ~5 WPM
- Radial typing (5 hours practice): 20 WPM target

**Measurement Strategy:**

```python
def measure_radial_wpm(player_id: str) -> dict:
    """
    Track radial typing speed over time.

    Returns:
    - Current WPM
    - WPM progression (by hour of practice)
    - Plateau detection
    """
    profile = load_profile(player_id)
    radial_sessions = profile.get_sessions(input_mode="radial")

    # Calculate WPM for each session
    wpm_by_hour = []
    cumulative_hours = 0

    for session in radial_sessions:
        cumulative_hours += session.duration / 3600
        wpm = calculate_wpm(session.keystrokes, session.duration)
        wpm_by_hour.append((cumulative_hours, wpm))

    return {
        "current_wpm": wpm_by_hour[-1][1] if wpm_by_hour else 0,
        "progression": wpm_by_hour,
        "hours_practiced": cumulative_hours
    }
```

**Learning Curve:**
- 1 hour: ~8 WPM
- 3 hours: ~15 WPM
- 5 hours: ~20 WPM
- 10 hours: ~30 WPM

**Success Threshold:**
- **Excellent:** >25 WPM after 5 hours
- **Good:** 18-25 WPM
- **Needs Work:** <18 WPM

**Optimization:**
- Which chords are slowest? (improve layout)
- Are players using optimal techniques?
- Is training mode effective?

---

### 3.3 Emotional Input Usage

**Definition:** Percentage of emotional prompts answered using triggers (vs text).

**Target:** >90% use triggers for feedback

**Rationale:**
- Triggers are faster and more granular than text
- High usage indicates controller comfort

**Measurement Strategy:**

```python
def measure_emotional_input_usage(player_id: str) -> dict:
    """
    Track how players respond to emotional prompts.

    Returns:
    - Trigger usage rate
    - Text usage rate
    - Complex response rate (Y button → text)
    """
    profile = load_profile(player_id)
    emotional_records = profile.get_emotional_history()

    trigger_responses = sum(1 for r in emotional_records if r.input_method == "trigger")
    text_responses = sum(1 for r in emotional_records if r.input_method == "text")
    complex_responses = sum(1 for r in emotional_records if r.input_method == "complex")

    total = len(emotional_records)

    return {
        "trigger_rate": trigger_responses / total,
        "text_rate": text_responses / total,
        "complex_rate": complex_responses / total
    }
```

**Success Threshold:**
- **Excellent:** >95% trigger usage
- **Good:** 85-95%
- **Needs Work:** <85%

---

### 3.4 Controller Preference

**Definition:** Percentage of players who choose controller over keyboard.

**Target:** 60%+ prefer controller after trying both

**Measurement Strategy:**

```python
def measure_controller_preference(player_id: str) -> dict:
    """
    Determine input preference based on usage patterns.

    Returns:
    - Primary input mode (keyboard/gamepad/touch)
    - Percentage time in each mode
    - Explicit preference (if set)
    """
    profile = load_profile(player_id)
    sessions = profile.get_all_sessions()

    mode_time = {
        "keyboard": 0,
        "gamepad": 0,
        "touch": 0
    }

    for session in sessions:
        mode_time[session.input_mode] += session.duration

    total_time = sum(mode_time.values())
    mode_percentages = {k: v/total_time for k, v in mode_time.items()}

    primary_mode = max(mode_percentages, key=mode_percentages.get)

    return {
        "primary_mode": primary_mode,
        "percentages": mode_percentages,
        "explicit_preference": profile.settings.preferred_input
    }
```

**Success Threshold:**
- **Excellent:** >70% controller preference
- **Good:** 50-70%
- **Needs Work:** <50%

---

## 4. Multiplayer Impact

### 4.1 AI Interaction Quality

**Definition:** Player satisfaction with AI teaching/collaboration.

**Target:** >4/5 average satisfaction

**Measurement Strategy:**

```python
async def measure_ai_quality(player_id: str) -> dict:
    """
    Collect feedback on AI interactions.

    After each multiplayer session:
    - Rate AI helpfulness (1-5)
    - Rate AI personality (1-5)
    - Rate AI teaching quality (1-5)
    """
    profile = load_profile(player_id)
    multiplayer_sessions = profile.get_sessions(mode="multiplayer")

    ratings = {
        "helpfulness": [],
        "personality": [],
        "teaching": []
    }

    for session in multiplayer_sessions:
        if session.ai_feedback:
            ratings["helpfulness"].append(session.ai_feedback.helpfulness)
            ratings["personality"].append(session.ai_feedback.personality)
            ratings["teaching"].append(session.ai_feedback.teaching)

    return {
        "avg_helpfulness": np.mean(ratings["helpfulness"]),
        "avg_personality": np.mean(ratings["personality"]),
        "avg_teaching": np.mean(ratings["teaching"]),
        "overall": np.mean([np.mean(v) for v in ratings.values()])
    }
```

**Success Threshold:**
- **Excellent:** >4.5/5 average
- **Good:** 3.8-4.5/5
- **Needs Work:** <3.8/5

**Qualitative Feedback:**
- What did AI do well?
- What was frustrating?
- Suggestions for improvement?

---

### 4.2 COOP Completion Rate

**Definition:** Percentage of COOP sessions that complete the challenge.

**Target:** >80% complete challenges in COOP mode

**Measurement Strategy:**

```python
def measure_coop_completion(days: int = 30) -> float:
    """
    Measure COOP success rate.

    Completed = both players agree challenge is complete AND tests pass
    """
    coop_sessions = get_sessions(mode="coop", last_n_days=days)

    completed = sum(1 for s in coop_sessions if s.challenge_completed)
    total = len(coop_sessions)

    return completed / total if total > 0 else 0.0
```

**Success Threshold:**
- **Excellent:** >85% completion
- **Good:** 70-85%
- **Needs Work:** <70%

**Failure Analysis:**
- Why do COOP sessions fail?
- Is AI too passive/aggressive?
- Are humans comfortable collaborating?

---

### 4.3 RACE Engagement

**Definition:** Percentage of players who try competitive mode.

**Target:** >60% try RACE mode at least once

**Measurement Strategy:**

```python
def measure_race_engagement(cohort_start_date: date, days: int = 30) -> dict:
    """
    Track RACE mode adoption.

    Returns:
    - Percentage who try RACE mode
    - Average RACE sessions per player
    - Win rate (human vs AI)
    """
    cohort = get_cohort(cohort_start_date)

    tried_race = 0
    total_race_sessions = 0
    human_wins = 0
    total_races = 0

    for player_id in cohort:
        profile = load_profile(player_id)
        race_sessions = profile.get_sessions(mode="race", last_n_days=days)

        if race_sessions:
            tried_race += 1
            total_race_sessions += len(race_sessions)

            for session in race_sessions:
                total_races += 1
                if session.winner == player_id:
                    human_wins += 1

    return {
        "adoption_rate": tried_race / len(cohort),
        "avg_sessions": total_race_sessions / tried_race if tried_race > 0 else 0,
        "human_win_rate": human_wins / total_races if total_races > 0 else 0
    }
```

**Success Threshold:**
- **Excellent:** >70% try RACE mode
- **Good:** 50-70%
- **Needs Work:** <50%

**Balance:**
- Human win rate should be ~50% (fair AI)
- Too easy (>70%): AI not challenging
- Too hard (<30%): AI discouraging

---

### 4.4 Teaching Mode Usage

**Definition:** Percentage of advanced players who use teaching mode.

**Target:** >40% of transcended players teach

**Measurement Strategy:**

```python
def measure_teaching_usage(days: int = 30) -> dict:
    """
    Track teaching mode engagement.

    Eligible = at least one concept at mastery level 4 (transcended)
    """
    profiles = get_all_profiles()

    eligible = [p for p in profiles if p.has_transcended_concept()]
    teachers = [p for p in eligible if p.has_sessions(mode="teach", last_n_days=days)]

    return {
        "eligible_count": len(eligible),
        "teacher_count": len(teachers),
        "adoption_rate": len(teachers) / len(eligible) if eligible else 0,
        "avg_sessions": np.mean([len(p.get_sessions(mode="teach")) for p in teachers])
    }
```

**Success Threshold:**
- **Excellent:** >50% of eligible teach
- **Good:** 30-50%
- **Needs Work:** <30%

---

## 5. Platform Health

### 5.1 Test Coverage

**Definition:** Percentage of code covered by automated tests.

**Target:** >90% coverage

**Measurement Strategy:**

```bash
# Run tests with coverage
pytest tests/ --cov=lmsp --cov-report=json

# Parse coverage report
python -m lmsp.tools.coverage_report
```

**Success Threshold:**
- **Excellent:** >95% coverage
- **Good:** 85-95%
- **Needs Work:** <85%

**Palace Integration:**
- Strict mode requires tests pass
- TDD enforced by development workflow

---

### 5.2 Build Reliability

**Definition:** Percentage of builds that pass all tests.

**Target:** 100% (strict mode)

**Measurement Strategy:**

```python
def measure_build_reliability(repo: str, days: int = 30) -> dict:
    """
    Track build success rate from CI/CD.
    """
    builds = get_ci_builds(repo, last_n_days=days)

    passed = sum(1 for b in builds if b.status == "passed")
    total = len(builds)

    return {
        "success_rate": passed / total,
        "total_builds": total,
        "failed_builds": [b for b in builds if b.status != "passed"]
    }
```

**Success Threshold:**
- **Excellent:** 100% builds pass
- **Good:** 95-100%
- **Needs Work:** <95%

---

### 5.3 Crash Rate

**Definition:** Percentage of sessions that crash/error.

**Target:** <0.1% crash rate

**Measurement Strategy:**

```python
def measure_crash_rate(days: int = 30) -> dict:
    """
    Track crashes and errors.

    Crash = unhandled exception causing session termination
    Error = handled exception that degrades experience
    """
    sessions = get_all_sessions(last_n_days=days)

    crashes = sum(1 for s in sessions if s.crashed)
    errors = sum(1 for s in sessions if s.had_errors)
    total = len(sessions)

    return {
        "crash_rate": crashes / total,
        "error_rate": errors / total,
        "crash_details": [s.error_log for s in sessions if s.crashed]
    }
```

**Success Threshold:**
- **Excellent:** 0% crashes
- **Good:** <0.05%
- **Needs Work:** >0.1%

**Error Tracking:**
- Sentry/Rollbar integration
- Automatic crash reports
- User feedback mechanism

---

### 5.4 Performance (Latency)

**Definition:** Response time for key interactions.

**Targets:**
- Controller input: <50ms
- Test validation: <2s
- Emotional prompt: <100ms
- Multiplayer sync: <200ms

**Measurement Strategy:**

```python
def measure_latency(player_id: str, days: int = 7) -> dict:
    """
    Track latency for key operations.
    """
    profile = load_profile(player_id)
    sessions = profile.get_sessions(last_n_days=days)

    latencies = {
        "controller_input": [],
        "test_validation": [],
        "emotional_prompt": [],
        "multiplayer_sync": []
    }

    for session in sessions:
        for event in session.events:
            if event.type == "input":
                latencies["controller_input"].append(event.latency)
            elif event.type == "test":
                latencies["test_validation"].append(event.latency)
            elif event.type == "emotion":
                latencies["emotional_prompt"].append(event.latency)
            elif event.type == "sync":
                latencies["multiplayer_sync"].append(event.latency)

    return {
        "controller_p50": np.percentile(latencies["controller_input"], 50),
        "controller_p95": np.percentile(latencies["controller_input"], 95),
        "test_p50": np.percentile(latencies["test_validation"], 50),
        "test_p95": np.percentile(latencies["test_validation"], 95),
        # ... etc
    }
```

**Success Threshold:**
- **Excellent:** All targets met at p95
- **Good:** All targets met at p50
- **Needs Work:** Any target missed at p50

---

### 5.5 Extension Adoption

**Definition:** Percentage of players using community content.

**Target:** >20% use community concepts/challenges

**Measurement Strategy:**

```python
def measure_extension_adoption(days: int = 30) -> dict:
    """
    Track community content usage.
    """
    profiles = get_all_profiles()

    using_extensions = sum(1 for p in profiles if p.has_community_content())
    total = len(profiles)

    # Top community concepts
    concept_usage = defaultdict(int)
    for profile in profiles:
        for concept in profile.get_community_concepts():
            concept_usage[concept] += 1

    return {
        "adoption_rate": using_extensions / total,
        "top_concepts": sorted(concept_usage.items(), key=lambda x: x[1], reverse=True)[:10]
    }
```

**Success Threshold:**
- **Excellent:** >30% use extensions
- **Good:** 15-30%
- **Needs Work:** <15%

---

## Measurement Infrastructure

### Data Collection

**Telemetry Pipeline:**
```python
class TelemetryCollector:
    """
    Collect anonymized usage data.

    Privacy-first:
    - Opt-in only
    - No PII
    - Local-first storage
    - Aggregate-only uploads
    """

    def __init__(self):
        self.buffer = []
        self.opt_in = False

    def record_event(self, event_type: str, data: dict):
        """Record event if opt-in enabled."""
        if not self.opt_in:
            return

        event = {
            "type": event_type,
            "timestamp": time.time(),
            "data": self.anonymize(data)
        }
        self.buffer.append(event)

    def anonymize(self, data: dict) -> dict:
        """Remove PII from data."""
        # Hash player IDs
        # Remove code content (keep structure only)
        # Remove any identifying info
        return sanitized_data

    def flush(self):
        """Upload aggregated metrics."""
        if len(self.buffer) < 100:
            return  # Batch uploads

        aggregated = self.aggregate(self.buffer)
        upload_to_analytics(aggregated)
        self.buffer.clear()
```

### Analysis Dashboard

**Metrics Dashboard:**
- Real-time tracking
- Cohort analysis
- A/B testing support
- Anomaly detection
- Exportable reports

**Tools:**
- Metabase/Grafana for visualization
- PostgreSQL for storage
- Python notebooks for deep analysis

---

## Success Criteria Summary

| Dimension | Metric | Target | Baseline | Threshold |
|-----------|--------|--------|----------|-----------|
| **Learning Efficacy** |
| Retention | 30-day recall | >80% | ~40% | 70%+ |
| Time to Proficiency | Hours to mastery | <2h | ~4h | <2.5h |
| Flow State | % time in flow | >30% | Rare | 25%+ |
| Mastery Depth | Novel challenge success | >90% | N/A | 85%+ |
| Transfer Learning | Cross-domain success | >80% | N/A | 70%+ |
| **Engagement** |
| Session Length | Average minutes | 25-35 | Varies | 20-40 |
| Return Rate | Next-day return | >60% | ~30% | 50%+ |
| Completion Rate | Curriculum complete | >70% | ~10% | 60%+ |
| Streak Length | Consecutive days | >7 | N/A | 5+ |
| Attempts/Session | Challenges per session | 4-6 | N/A | 3-8 |
| **Controller Adoption** |
| Easy Mode Grad | % who switch | >80% | N/A | 70%+ |
| Radial WPM | Typing speed | >20 | ~5 | 18+ |
| Trigger Usage | Emotional input | >90% | N/A | 85%+ |
| Controller Pref | Primary input | >60% | N/A | 50%+ |
| **Multiplayer** |
| AI Quality | Satisfaction | >4/5 | N/A | 3.8/5+ |
| COOP Complete | Success rate | >80% | N/A | 70%+ |
| RACE Engage | Try competitive | >60% | N/A | 50%+ |
| Teaching Usage | Teach mode | >40% | N/A | 30%+ |
| **Platform** |
| Test Coverage | Code coverage | >90% | N/A | 85%+ |
| Build Reliability | Build success | 100% | N/A | 95%+ |
| Crash Rate | Session crashes | <0.1% | N/A | <0.5% |
| Latency (p95) | Response time | <50ms | N/A | <100ms |
| Extension Use | Community content | >20% | N/A | 15%+ |

---

## Continuous Improvement

### Feedback Loop

```
Measure → Analyze → Hypothesize → Experiment → Measure
    ↑                                              ↓
    └──────────────────────────────────────────────┘
```

**Process:**
1. **Measure:** Collect metrics continuously
2. **Analyze:** Identify patterns and outliers
3. **Hypothesize:** Form theories about improvements
4. **Experiment:** A/B test changes
5. **Measure:** Validate impact
6. **Iterate:** Repeat

### A/B Testing Framework

```python
class ABTest:
    """
    A/B testing framework for LMSP.
    """

    def __init__(self, name: str, variants: list[str]):
        self.name = name
        self.variants = variants
        self.assignments = {}

    def assign(self, player_id: str) -> str:
        """Assign player to variant (sticky)."""
        if player_id not in self.assignments:
            self.assignments[player_id] = random.choice(self.variants)
        return self.assignments[player_id]

    def measure(self, metric: str) -> dict:
        """Compare metric across variants."""
        results = {}
        for variant in self.variants:
            players = [p for p, v in self.assignments.items() if v == variant]
            results[variant] = calculate_metric(players, metric)
        return results
```

**Example Tests:**
- Radial layout A vs B
- Easy mode scaffolding variations
- AI teaching styles
- Emotional prompt frequency

---

*Rigorous measurement enables data-driven improvement and validates LMSP's effectiveness as a learning platform.*
