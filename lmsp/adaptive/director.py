"""
The Director - Adaptive Learning System
=======================================

An invisible AI system that watches the learner's journey and shapes
their experience in real-time.

The Director:
- Observes failure patterns and frustration signals
- Identifies knowledge gaps from failed code execution
- Generates dynamic micro-lessons for struggles
- Adjusts difficulty and pacing invisibly
- Works on behalf of the learner: "What do they need to unstick this?"

Unlike a simple recommendation engine, The Director is proactive and creative.
It doesn't just pick from existing content - it can CREATE new lessons.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime, timedelta
import json
import re
from pathlib import Path


class StruggleType(Enum):
    """Types of struggles The Director can detect."""
    SYNTAX_ERROR = "syntax_error"          # Basic Python syntax issues
    TYPE_ERROR = "type_error"              # Type mismatches
    LOGIC_ERROR = "logic_error"            # Code runs but wrong output
    CONCEPT_GAP = "concept_gap"            # Missing prerequisite knowledge
    PATTERN_UNFAMILIAR = "pattern"         # Doesn't recognize common patterns
    TOOLING_CONFUSION = "tooling"          # IDE/environment issues
    FRUSTRATION_SPIRAL = "frustration"     # Emotional state degrading
    STRING_VS_IDENTIFIER = "string_vs_identifier"  # Comparing 'foo' to foo (common gotcha!)
    OPERATOR_ORDER_TYPO = "operator_order_typo"    # =- instead of -= (very common typo!)
    OUTPUT_FORMAT_MISMATCH = "output_format"       # Printed raw value instead of formatted string
    STRING_CONCAT_TYPE_ERROR = "string_concat_type"  # "text" + number without str()
    RANGE_OFF_BY_ONE = "range_off_by_one"  # Zero-indexing confusion: range(5) vs range(1,6)
    RANGE_SINGLE_ARG_ALWAYS_ZERO = "range_single_arg"  # range(n) ALWAYS starts at 0, no exceptions
    PRINT_VS_RETURN = "print_vs_return"  # return print(...) instead of return ... (print returns None!)
    RETURN_VS_PRINT = "return_vs_print"  # returned value when challenge expected print() output
    ACCIDENTAL_NONE_OUTPUT = "accidental_none"  # output has extra "None" from print() return value
    FSTRING_SYNTAX = "fstring_syntax"  # f-string mistakes: forgot f prefix, wrong braces, etc.

    # Container/query-processing challenges
    RETURN_IN_LOOP = "return_in_loop"  # Using return inside loop instead of append() - exits immediately!
    CONTAINER_STATE_BUG = "container_state"  # Forgetting to initialize or track container state
    COMMAND_DISPATCH_MISSING = "command_dispatch"  # Missing if/elif branch for a command
    BOOLEAN_VS_STRING_RESULT = "boolean_vs_string"  # Returning True/False instead of "true"/"false"
    MEDIAN_EMPTY_CRASH = "median_empty"  # Accessing median when container is empty
    MEDIAN_EVEN_ODD = "median_even_odd"  # Wrong middle index for even vs odd length
    GET_NEXT_BOUNDARY = "get_next_boundary"  # GET_NEXT when target >= all values
    REMOVE_WITHOUT_CHECK = "remove_without_check"  # Calling .remove() without checking existence
    INTEGER_DIVISION_FLOAT = "int_div_float"  # Using / instead of // for integer division


@dataclass
class Struggle:
    """A detected struggle point."""
    type: StruggleType
    description: str
    code_context: Optional[str] = None
    error_message: Optional[str] = None
    frequency: int = 1
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    resolved: bool = False


@dataclass
class DirectorObservation:
    """What The Director sees from a code submission."""
    player_id: str
    challenge_id: str
    code: str
    success: bool
    error: Optional[str]
    output: Optional[str]
    tests_passing: int
    tests_total: int
    time_seconds: float
    attempt_number: int
    timestamp: datetime = field(default_factory=datetime.now)
    concepts: List[str] = field(default_factory=list)  # Concepts this challenge teaches


@dataclass
class Mastery:
    """Tracking mastery of a concept or challenge."""
    concept: str
    successes: int = 0
    failures: int = 0
    total_time: float = 0.0
    fastest_time: float = float('inf')
    first_try_successes: int = 0  # Solved on first attempt
    streak: int = 0  # Current success streak
    last_attempt: datetime = field(default_factory=datetime.now)

    @property
    def success_rate(self) -> float:
        total = self.successes + self.failures
        return self.successes / total if total > 0 else 0.0

    @property
    def avg_time(self) -> float:
        return self.total_time / self.successes if self.successes > 0 else 0.0

    @property
    def mastery_score(self) -> float:
        """0-1 score indicating mastery level."""
        if self.successes < 2:
            return 0.0

        # Factors: success rate, speed improvement, first-try rate, streak
        rate_score = self.success_rate
        first_try_rate = self.first_try_successes / self.successes if self.successes > 0 else 0
        streak_bonus = min(0.2, self.streak * 0.05)  # Up to 0.2 bonus for streaks

        return min(1.0, (rate_score * 0.5) + (first_try_rate * 0.3) + streak_bonus)


@dataclass
class DirectorIntervention:
    """An action The Director takes to help the learner."""
    type: str  # "hint", "micro_lesson", "redirect", "encouragement", "new_challenge"
    content: str
    reason: str
    confidence: float
    generated_challenge: Optional[dict] = None  # If type is "new_challenge"


class Director:
    """
    The AI Director that shapes the learning experience.

    Works invisibly in the background, watching for:
    - Repeated failures on the same concept
    - Error patterns that indicate knowledge gaps
    - Frustration signals from emotional feedback
    - Opportunities to reinforce or redirect

    Can generate NEW curriculum dynamically when existing content
    doesn't address the learner's specific struggle.
    """

    def __init__(self, player_id: str, api_key: Optional[str] = None, db=None):
        self.player_id = player_id
        self._api_key = api_key
        self._client = None
        self._db = db  # Database for persistence

        # Observation history
        self._observations: List[DirectorObservation] = []
        self._struggles: Dict[str, Struggle] = {}
        self._mastery: Dict[str, Mastery] = {}  # Concept/challenge mastery tracking

        # Director state
        self._frustration_level = 0.0  # 0-1 scale
        self._momentum = 0.5  # 0-1, how well they're progressing
        self._last_success_time: Optional[datetime] = None

        # Performance tracking
        self._total_successes = 0
        self._total_failures = 0
        self._first_try_successes = 0

        # Configurable thresholds
        self.frustration_threshold = 0.7  # When to intervene
        self.struggle_count_threshold = 3  # Attempts before helping
        self.time_stuck_threshold = 300  # Seconds before suggesting redirect

        # Load from database if available
        if self._db:
            self._load_from_db()

    def _load_from_db(self):
        """Load Director state from database."""
        if not self._db:
            return

        # Load state (momentum, frustration, totals)
        state = self._db.load_director_state(self.player_id)
        if state:
            self._frustration_level = state["frustration_level"]
            self._momentum = state["momentum"]
            self._total_successes = state["total_successes"]
            self._total_failures = state["total_failures"]
            self._first_try_successes = state["first_try_successes"]
            if state["last_success_time"]:
                self._last_success_time = datetime.fromisoformat(state["last_success_time"])

        # Load observations (last 100 for analysis)
        obs_data = self._db.load_director_observations(self.player_id, limit=100)
        for o in reversed(obs_data):  # Reverse to get chronological order
            self._observations.append(DirectorObservation(
                player_id=o["player_id"],
                challenge_id=o["challenge_id"],
                code="",  # Don't store full code
                success=o["success"],
                error=o["error"],
                output=o["output"],
                tests_passing=o["tests_passing"],
                tests_total=o["tests_total"],
                time_seconds=o["time_seconds"],
                attempt_number=o["attempt_number"],
                timestamp=datetime.fromisoformat(o["timestamp"]),
                concepts=o["concepts"],
            ))

        # Load mastery entries
        mastery_data = self._db.load_director_mastery(self.player_id)
        for concept, m in mastery_data.items():
            self._mastery[concept] = Mastery(
                concept=concept,
                successes=m["successes"],
                failures=m["failures"],
                total_time=m["total_time"],
                fastest_time=m["fastest_time"] if m["fastest_time"] else float('inf'),
                first_try_successes=m["first_try_successes"],
                streak=m["streak"],
                last_attempt=datetime.fromisoformat(m["last_attempt"]) if m["last_attempt"] else datetime.now(),
            )

        # Load struggles
        struggles_data = self._db.load_director_struggles(self.player_id)
        for key, s in struggles_data.items():
            self._struggles[key] = Struggle(
                type=StruggleType(s["type"]),
                description=s["description"],
                error_message=s["error_message"],
                code_context=s["code_context"],
                frequency=s["frequency"],
                first_seen=datetime.fromisoformat(s["first_seen"]),
                last_seen=datetime.fromisoformat(s["last_seen"]),
                resolved=s["resolved"],
            )

    def _persist(self, observation: Optional[DirectorObservation] = None):
        """Persist current state to database."""
        if not self._db:
            return

        # Save the observation
        if observation:
            self._db.save_director_observation(
                player_id=observation.player_id,
                challenge_id=observation.challenge_id,
                success=observation.success,
                error=observation.error,
                output=observation.output,
                tests_passing=observation.tests_passing,
                tests_total=observation.tests_total,
                time_seconds=observation.time_seconds,
                attempt_number=observation.attempt_number,
                concepts=observation.concepts,
                timestamp=observation.timestamp.isoformat(),
            )

        # Save Director state
        self._db.save_director_state(
            player_id=self.player_id,
            frustration_level=self._frustration_level,
            momentum=self._momentum,
            total_successes=self._total_successes,
            total_failures=self._total_failures,
            first_try_successes=self._first_try_successes,
            last_success_time=self._last_success_time.isoformat() if self._last_success_time else None,
        )

    def _persist_mastery(self, concept: str):
        """Persist a specific mastery entry."""
        if not self._db or concept not in self._mastery:
            return

        m = self._mastery[concept]
        self._db.save_director_mastery(
            player_id=self.player_id,
            concept=concept,
            successes=m.successes,
            failures=m.failures,
            total_time=m.total_time,
            fastest_time=m.fastest_time if m.fastest_time != float('inf') else None,
            first_try_successes=m.first_try_successes,
            streak=m.streak,
            last_attempt=m.last_attempt.isoformat(),
        )

    def _persist_struggle(self, key: str):
        """Persist a specific struggle entry."""
        if not self._db or key not in self._struggles:
            return

        s = self._struggles[key]
        self._db.save_director_struggle(
            player_id=self.player_id,
            struggle_key=key,
            struggle_type=s.type.value,
            description=s.description,
            error_message=s.error_message,
            code_context=s.code_context,
            frequency=s.frequency,
            first_seen=s.first_seen.isoformat(),
            last_seen=s.last_seen.isoformat(),
            resolved=s.resolved,
        )

    def _get_client(self):
        """Lazy-load the Z.ai client."""
        if self._client is None:
            try:
                # Try to import from player-zero
                import sys
                sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "player-zero"))
                from player_zero.client import get_client
                self._client = get_client()
            except ImportError:
                # Fallback - no AI available
                self._client = None
        return self._client

    def observe(self, observation: DirectorObservation):
        """
        Process an observation from the learner's session.

        This is the main entry point - called after every code submission.
        The Director learns from BOTH successes and failures.
        """
        self._observations.append(observation)

        # Update momentum
        if observation.success:
            self._total_successes += 1
            self._momentum = min(1.0, self._momentum + 0.1)
            self._frustration_level = max(0.0, self._frustration_level - 0.2)
            self._last_success_time = observation.timestamp

            # Track first-try successes
            if observation.attempt_number == 1:
                self._first_try_successes += 1

            # Analyze the success - what did they master?
            self._analyze_success(observation)
        else:
            self._total_failures += 1
            self._momentum = max(0.0, self._momentum - 0.05)

            # Analyze the failure - what are they struggling with?
            struggles = self._analyze_failure(observation)
            for struggle in struggles:
                self._record_struggle(struggle)

            # Update mastery tracking for failures too
            self._record_failure(observation)

        # Persist observation and state to SQLite (WAL mode for responsiveness)
        self._persist(observation)

    def observe_emotion(self, enjoyment: float, frustration: float):
        """
        Process emotional feedback.

        Called when learner rates their experience.
        """
        # Blend with existing frustration level
        self._frustration_level = (self._frustration_level * 0.7) + (frustration * 0.3)

        # High enjoyment reduces frustration impact
        if enjoyment > 0.7:
            self._frustration_level *= 0.8

    def should_intervene(self) -> bool:
        """
        Decide if The Director should step in.

        Returns True if:
        - Frustration is too high
        - Stuck on same error too long
        - Multiple failed attempts with no progress
        """
        # Check frustration level
        if self._frustration_level >= self.frustration_threshold:
            return True

        # Check for repeated struggles
        for struggle in self._struggles.values():
            if not struggle.resolved and struggle.frequency >= self.struggle_count_threshold:
                return True

        # Check time since last success
        if self._last_success_time:
            time_stuck = (datetime.now() - self._last_success_time).total_seconds()
            if time_stuck > self.time_stuck_threshold:
                return True

        return False

    def get_intervention(self) -> Optional[DirectorIntervention]:
        """
        Get The Director's recommended intervention.

        This is where the magic happens - analyzing what the learner
        needs and potentially generating new content to help them.
        """
        if not self.should_intervene():
            return None

        # Find the most pressing struggle
        worst_struggle = self._find_worst_struggle()

        if worst_struggle is None:
            # General frustration, no specific struggle
            return DirectorIntervention(
                type="encouragement",
                content="Take a breath! You're making progress even when it doesn't feel like it.",
                reason="High frustration without specific struggle detected",
                confidence=0.6,
            )

        # Try to get AI-powered help
        client = self._get_client()
        if client:
            return self._get_ai_intervention(worst_struggle)

        # Fallback to rule-based intervention
        return self._get_rule_based_intervention(worst_struggle)

    def _analyze_failure(self, obs: DirectorObservation) -> List[Struggle]:
        """Analyze a failed submission to identify struggles."""
        struggles = []

        # Combine error and output for analysis (pytest puts errors in output)
        error_text = ((obs.error or "") + "\n" + (obs.output or "")).lower()

        if not error_text.strip():
            # No error info at all - generic logic error
            if obs.tests_passing < obs.tests_total:
                struggles.append(Struggle(
                    type=StruggleType.LOGIC_ERROR,
                    description="Code runs but doesn't produce expected output",
                    code_context=obs.code[-500:] if obs.code else None,
                ))
            return struggles

        # Syntax errors
        if "syntaxerror" in error_text or "indentationerror" in error_text:
            struggles.append(Struggle(
                type=StruggleType.SYNTAX_ERROR,
                description="Python syntax issue",
                error_message=obs.error,
                code_context=obs.code[-500:] if obs.code else None,
            ))

        # Type errors - check for specific patterns first
        if "typeerror" in error_text:
            # STRING_CONCAT_TYPE_ERROR: Trying to concatenate string with non-string
            # Error: "can only concatenate str (not "int") to str"
            concat_match = re.search(
                r'can only concatenate str \(not ["\'](\w+)["\']\) to str',
                error_text,
                re.IGNORECASE
            )
            if concat_match:
                wrong_type = concat_match.group(1)
                # Try to find the variable name that caused the issue
                var_hint = ""
                if obs.code and wrong_type == "int":
                    # Look for + with variables that might be integers (age, count, num, etc.)
                    int_var_pattern = re.search(
                        r'["\'][^"\']*["\']\s*\+\s*(\w*(?:age|count|num|year|day|score|total|id|level)\w*)',
                        obs.code, re.IGNORECASE
                    )
                    if int_var_pattern:
                        var_hint = f" (looks like '{int_var_pattern.group(1)}' needs str())"
                struggles.append(Struggle(
                    type=StruggleType.STRING_CONCAT_TYPE_ERROR,
                    description=f"Tried to combine string with {wrong_type}{var_hint}",
                    error_message=f"Use str() to convert: str({wrong_type}_value) or use f-strings",
                    code_context=obs.code[-500:] if obs.code else None,
                ))
            else:
                # Generic type error
                struggles.append(Struggle(
                    type=StruggleType.TYPE_ERROR,
                    description="Type mismatch or wrong operation on type",
                    error_message=obs.error,
                    code_context=obs.code[-500:] if obs.code else None,
                ))

        # Name errors - often indicate concept gaps
        if "nameerror" in error_text:
            # Extract the undefined name from output (case-insensitive search)
            full_text = (obs.error or "") + "\n" + (obs.output or "")
            match = re.search(r"name '(\w+)' is not defined", full_text, re.IGNORECASE)
            if match:
                undefined_name = match.group(1)
                struggles.append(Struggle(
                    type=StruggleType.CONCEPT_GAP,
                    description=f"Using '{undefined_name}' before defining it",
                    error_message=obs.error,
                ))
            else:
                struggles.append(Struggle(
                    type=StruggleType.CONCEPT_GAP,
                    description="Using a variable before defining it",
                    error_message=obs.error,
                ))

        # Index/Key errors
        if "indexerror" in error_text or "keyerror" in error_text:
            struggles.append(Struggle(
                type=StruggleType.PATTERN_UNFAMILIAR,
                description="Accessing data that doesn't exist",
                error_message=obs.error,
            ))

        # Assertion errors from tests - likely logic errors
        if "assertionerror" in error_text and not struggles:
            struggles.append(Struggle(
                type=StruggleType.LOGIC_ERROR,
                description="Code runs but doesn't produce expected output",
                code_context=obs.code[-500:] if obs.code else None,
            ))

        # OUTPUT_FORMAT_MISMATCH: Printed raw value instead of formatted string
        # Very common: user prints just the number/value instead of the required format
        # e.g., prints "5" when expected "Your name has 5 letters"
        if obs.output and obs.code:
            output_stripped = obs.output.strip()
            # Check if output looks like a raw value (short, simple)
            is_raw_value = (
                len(output_stripped) <= 10 and
                (output_stripped.isdigit() or
                 output_stripped.replace('.', '').isdigit() or
                 output_stripped in ('True', 'False', 'None'))
            )

            # Check if test expected something longer/formatted
            if is_raw_value and 'assert' in error_text:
                # Look for expected string patterns in error
                expected_match = re.search(r"expected[:\s]+['\"](.{15,})['\"]", error_text, re.IGNORECASE)
                if expected_match or 'got:' in error_text.lower():
                    struggles.append(Struggle(
                        type=StruggleType.OUTPUT_FORMAT_MISMATCH,
                        description=f"Printed '{output_stripped}' but challenge wanted formatted output",
                        error_message="Check the exact output format requested in the instructions",
                        code_context=obs.code[-500:] if obs.code else None,
                    ))

        # OPERATOR_ORDER_TYPO: =- instead of -= (and similar)
        # Very common typo that silently does the wrong thing!
        # health =- damage assigns -damage, not health - damage
        if obs.code:
            # Look for =- =+ =* =/ patterns (wrong order)
            operator_typo_pattern = re.compile(r'(\w+)\s*=([+\-*/])\s*(\w+)')
            for match in operator_typo_pattern.finditer(obs.code):
                var, op, val = match.groups()
                # Check if the correct compound operator exists elsewhere
                # or if output suggests wrong value (e.g., negative when should be positive)
                correct_op = f'{op}='
                if correct_op not in obs.code:
                    # They used =- but never -=, likely a typo
                    # Check output for signs of wrong value
                    if obs.output and (
                        (op == '-' and '-' in obs.output) or  # Got negative when subtracting
                        (op == '+' and obs.tests_passing < obs.tests_total)
                    ):
                        struggles.append(Struggle(
                            type=StruggleType.OPERATOR_ORDER_TYPO,
                            description=f"Wrote '{var} ={op} {val}' instead of '{var} {op}= {val}'",
                            error_message=f"={op} assigns {op}{val}, but {op}= modifies {var}",
                            code_context=obs.code[-500:] if obs.code else None,
                        ))
                        break

        # RANGE_OFF_BY_ONE and RANGE_SINGLE_ARG_ALWAYS_ZERO: Zero-indexing confusion
        # Common: range(5) gives 0-4, but learner expected 1-5
        # Even experienced devs forget: range(n) ALWAYS starts at 0!
        if obs.code and obs.output:
            if 'range(' in obs.code:
                output_lines = obs.output.strip().split('\n')
                if output_lines and output_lines[0].strip() == '0':
                    # Output starts with 0 - check if they're using single-arg range
                    # Pattern: range(4) or range(5) - single argument, no comma
                    single_arg_match = re.search(r'range\s*\(\s*(\d+)\s*\)', obs.code)

                    if single_arg_match and 'starts with 0' in error_text:
                        # They used range(n) expecting to start at 1
                        struggles.append(Struggle(
                            type=StruggleType.RANGE_SINGLE_ARG_ALWAYS_ZERO,
                            description="range(n) ALWAYS starts at 0 - you can't change this with just one argument",
                            error_message="range(5) → 0,1,2,3,4. For 1-5, you MUST use range(1, 6) with TWO arguments",
                            code_context=obs.code[-500:] if obs.code else None,
                        ))
                    elif 'starts with 0' in error_text or 'expected 5 lines' in error_text or '1' in error_text:
                        # General off-by-one confusion
                        struggles.append(Struggle(
                            type=StruggleType.RANGE_OFF_BY_ONE,
                            description="range() starts at 0 by default, not 1",
                            error_message="range(5) gives 0,1,2,3,4 - use range(1, 6) for 1,2,3,4,5",
                            code_context=obs.code[-500:] if obs.code else None,
                        ))

        # PRINT_VS_RETURN: Using return print(...) instead of return ...
        # print() returns None! This is a VERY common beginner mistake
        # Pattern: return print(something) or return print(f"...")
        if obs.code and 'return print' in obs.code.replace(' ', ''):
            # More reliable check with regex to handle whitespace
            if re.search(r'return\s+print\s*\(', obs.code):
                # Check if they got None back (which happens with return print())
                if 'none' in error_text.lower() or "expected 'added" in error_text.lower():
                    struggles.append(Struggle(
                        type=StruggleType.PRINT_VS_RETURN,
                        description="Using 'return print(...)' - but print() returns None!",
                        error_message="print() displays text but returns None. Use 'return f\"...\"' directly!",
                        code_context=obs.code[-500:] if obs.code else None,
                    ))

        # RETURN_IN_LOOP: Using return inside a loop instead of results.append()
        # Pattern: for ... in ...: ... return ... (return inside loop body)
        # This exits immediately instead of building a list!
        if obs.code:
            # Check for return statement inside a for loop (indented under it)
            # Look for pattern: for line, then indented return
            has_for_loop = re.search(r'\bfor\s+\w+\s+in\s+', obs.code)
            if has_for_loop:
                # Check if there's a return inside the loop body (not at function end)
                # Simple heuristic: return appears between 'for' and the end, with higher indentation
                lines = obs.code.split('\n')
                in_loop = False
                loop_indent = 0
                for line in lines:
                    stripped = line.lstrip()
                    current_indent = len(line) - len(stripped)

                    if stripped.startswith('for ') and ' in ' in stripped:
                        in_loop = True
                        loop_indent = current_indent
                    elif in_loop and current_indent <= loop_indent and stripped and not stripped.startswith('#'):
                        # Dedented back out of loop
                        in_loop = False
                    elif in_loop and stripped.startswith('return ') and current_indent > loop_indent:
                        # Found return inside loop!
                        # Check if result looks truncated (got single value or short list)
                        if (error_text and ('got:' in error_text or 'expected' in error_text)) or \
                           (obs.output and obs.output.strip() in ['', '""', "''", 'true', 'false']):
                            struggles.append(Struggle(
                                type=StruggleType.RETURN_IN_LOOP,
                                description="Using 'return' inside loop - exits after first iteration!",
                                error_message="Use results.append() to build the list, then return results at the END",
                                code_context=obs.code[-500:] if obs.code else None,
                            ))
                            break

        # FSTRING_SYNTAX: Forgot f prefix or wrong braces
        # Pattern: return "{item}" when they meant f"{item}"
        if obs.code and obs.output:
            # Look for string literals that contain {variable} but no f prefix
            forgot_f_pattern = re.search(r'return\s+["\'].*\{(\w+)\}.*["\']', obs.code)
            if forgot_f_pattern and not re.search(r'return\s+f["\']', obs.code):
                var_name = forgot_f_pattern.group(1)
                if '{' + var_name + '}' in obs.output:
                    # They literally printed {item} instead of the value
                    struggles.append(Struggle(
                        type=StruggleType.FSTRING_SYNTAX,
                        description=f"Forgot the 'f' prefix - printed literal '{{...}}' instead of value",
                        error_message=f"Use f\"...{{...}}\" not \"...{{...}}\" to insert values",
                        code_context=obs.code[-500:] if obs.code else None,
                    ))

        # RETURN_VS_PRINT: Returned a value when the challenge expected print() output
        # Opposite of PRINT_VS_RETURN - they used return when they should have used print
        # Pattern: function returns value but tests check stdout
        if obs.code and obs.output:
            # Check if they're returning but not printing
            has_return = re.search(r'\breturn\s+[^\s]', obs.code)
            has_print = 'print(' in obs.code

            if has_return and not has_print:
                # Check if tests were expecting printed output
                if ('expected' in error_text and ('stdout' in error_text or 'output' in error_text)):
                    struggles.append(Struggle(
                        type=StruggleType.RETURN_VS_PRINT,
                        description="Returning value but challenge expected print() output",
                        error_message="Some challenges want you to print(), not return. Check the instructions!",
                        code_context=obs.code[-500:] if obs.code else None,
                    ))
                # Also detect by checking if output is empty but return is used
                elif not obs.output.strip() and 'assert' in error_text:
                    # Empty output + return statement = might need print instead
                    if 'expected' in error_text:
                        struggles.append(Struggle(
                            type=StruggleType.RETURN_VS_PRINT,
                            description="Returning value but nothing was printed",
                            error_message="This challenge checks what you print, not what you return. Use print()!",
                            code_context=obs.code[-500:] if obs.code else None,
                        ))

        # ACCIDENTAL_NONE_OUTPUT: Output has extra "None" from print() return value
        # Pattern: print(print("something")) or just evaluating print() in REPL-like context
        # Also: having both return AND print when only one is needed
        if obs.output:
            output_lines = obs.output.strip().split('\n')
            # Check if any line is just "None" (common sign of accidental print return)
            has_none_line = any(line.strip() == 'None' for line in output_lines)

            if has_none_line:
                # Check for nested print (the classic mistake)
                if obs.code and re.search(r'print\s*\(\s*print\s*\(', obs.code):
                    struggles.append(Struggle(
                        type=StruggleType.ACCIDENTAL_NONE_OUTPUT,
                        description="Nested print() - the inner print returns None!",
                        error_message="print(print('hi')) prints 'hi' then 'None'. Just use print('hi')!",
                        code_context=obs.code[-500:] if obs.code else None,
                    ))
                # Check if they have both return and print in same function
                elif obs.code and 'return' in obs.code and 'print(' in obs.code:
                    # Both return and print - one might be extra
                    struggles.append(Struggle(
                        type=StruggleType.ACCIDENTAL_NONE_OUTPUT,
                        description="Extra 'None' in output - mixing print() and return?",
                        error_message="If challenge wants a return value, don't print. If it wants output, don't return. Pick one!",
                        code_context=obs.code[-500:] if obs.code else None,
                    ))
                # Generic case - None showed up unexpectedly
                elif 'none' in error_text and 'expected' in error_text:
                    struggles.append(Struggle(
                        type=StruggleType.ACCIDENTAL_NONE_OUTPUT,
                        description="Output includes unexpected 'None'",
                        error_message="Something is returning/printing None when it shouldn't. Check your print() and return statements!",
                        code_context=obs.code[-500:] if obs.code else None,
                    ))

        # STRING_VS_IDENTIFIER: Comparing string params to function names
        # Detect pattern: if x == identifier (without quotes) when comparing string args
        # Common in dispatcher functions: if operation == add instead of if operation == 'add'
        if obs.code:
            # Look for if/elif with bare identifier comparisons
            # Pattern: if param == identifier where identifier is also a function name
            string_vs_id_pattern = re.compile(
                r'if\s+(\w+)\s*==\s*([a-z_][a-z0-9_]*)\s*:',
                re.IGNORECASE
            )
            matches = string_vs_id_pattern.findall(obs.code)

            for var_name, identifier in matches:
                # Check if the identifier is also defined as a function in the code
                func_def_pattern = f'def {identifier}\\s*\\('
                if re.search(func_def_pattern, obs.code):
                    # They're comparing a variable to a function name - likely should be a string!
                    # Also check if result was empty list/None (indicating no branch matched)
                    if '[] ==' in error_text or 'none ==' in error_text:
                        struggles.append(Struggle(
                            type=StruggleType.STRING_VS_IDENTIFIER,
                            description=f"Comparing '{var_name}' to function '{identifier}' instead of string '{identifier}'",
                            error_message=f"if {var_name} == {identifier} should be if {var_name} == '{identifier}'",
                            code_context=obs.code[-500:] if obs.code else None,
                        ))
                        break  # One is enough

        return struggles

    def _record_struggle(self, struggle: Struggle):
        """Record or update a struggle in our tracking."""
        key = f"{struggle.type.value}:{struggle.description[:50]}"

        if key in self._struggles:
            existing = self._struggles[key]
            existing.frequency += 1
            existing.last_seen = datetime.now()
        else:
            self._struggles[key] = struggle

        # Persist this struggle entry to SQLite
        self._persist_struggle(key)

    def _analyze_success(self, obs: DirectorObservation):
        """
        Analyze a successful submission to track mastery.

        The Director learns from successes too:
        - What concepts is the learner mastering?
        - How fast are they solving challenges?
        - Are they improving over time?
        """
        # Track mastery for the challenge itself
        self._record_mastery(obs.challenge_id, obs, is_success=True)

        # Track mastery for each concept the challenge teaches
        for concept in obs.concepts:
            self._record_mastery(concept, obs, is_success=True)

        # Mark related struggles as potentially resolved
        # If they succeed after struggling, the struggle is resolved
        for key, struggle in self._struggles.items():
            if not struggle.resolved:
                # Check if this success relates to the struggle
                if obs.challenge_id in key or any(c in key for c in obs.concepts):
                    struggle.resolved = True
                    # Persist the resolved status
                    self._persist_struggle(key)

    def _record_failure(self, obs: DirectorObservation):
        """Record a failure in mastery tracking."""
        # Track failures for the challenge
        self._record_mastery(obs.challenge_id, obs, is_success=False)

        # Track failures for each concept
        for concept in obs.concepts:
            self._record_mastery(concept, obs, is_success=False)

    def _record_mastery(self, key: str, obs: DirectorObservation, is_success: bool):
        """Update mastery tracking for a concept or challenge."""
        if key not in self._mastery:
            self._mastery[key] = Mastery(concept=key)

        mastery = self._mastery[key]
        mastery.last_attempt = obs.timestamp

        if is_success:
            mastery.successes += 1
            mastery.total_time += obs.time_seconds
            mastery.fastest_time = min(mastery.fastest_time, obs.time_seconds)
            mastery.streak += 1

            if obs.attempt_number == 1:
                mastery.first_try_successes += 1
        else:
            mastery.failures += 1
            mastery.streak = 0  # Reset streak on failure

        # Persist this mastery entry to SQLite
        self._persist_mastery(key)

    def get_mastered_concepts(self) -> List[str]:
        """Get list of concepts the learner has mastered (score > 0.7)."""
        return [
            m.concept for m in self._mastery.values()
            if m.mastery_score > 0.7
        ]

    def get_struggling_concepts(self) -> List[str]:
        """Get list of concepts the learner is struggling with (score < 0.3)."""
        return [
            m.concept for m in self._mastery.values()
            if m.mastery_score < 0.3 and (m.successes + m.failures) >= 2
        ]

    def get_learning_velocity(self) -> float:
        """
        Calculate learning velocity based on recent performance.

        Returns a -1 to 1 score:
        - Positive = improving (getting faster, more first-try successes)
        - Negative = struggling (slowing down, more attempts needed)
        - Zero = stable
        """
        if len(self._observations) < 6:
            return 0.0

        # Compare recent vs older observations
        older = self._observations[-10:-5] if len(self._observations) >= 10 else self._observations[:len(self._observations)//2]
        recent = self._observations[-5:]

        if not older or not recent:
            return 0.0

        older_success_rate = sum(1 for o in older if o.success) / len(older)
        recent_success_rate = sum(1 for o in recent if o.success) / len(recent)

        # Calculate velocity as change in success rate
        velocity = recent_success_rate - older_success_rate

        # Also factor in time improvement for successes
        older_times = [o.time_seconds for o in older if o.success]
        recent_times = [o.time_seconds for o in recent if o.success]

        if older_times and recent_times:
            older_avg = sum(older_times) / len(older_times)
            recent_avg = sum(recent_times) / len(recent_times)
            if older_avg > 0:
                time_improvement = (older_avg - recent_avg) / older_avg
                velocity += time_improvement * 0.3  # Time is weighted less than success

        return max(-1.0, min(1.0, velocity))

    def _find_worst_struggle(self) -> Optional[Struggle]:
        """Find the most pressing unresolved struggle."""
        unresolved = [s for s in self._struggles.values() if not s.resolved]
        if not unresolved:
            return None

        # Sort by frequency * recency
        def score(s: Struggle) -> float:
            recency = 1.0 / (1 + (datetime.now() - s.last_seen).total_seconds() / 60)
            return s.frequency * recency

        return max(unresolved, key=score)

    def _get_ai_intervention(self, struggle: Struggle) -> DirectorIntervention:
        """Use Claude to generate a smart intervention."""
        client = self._get_client()
        if not client:
            return self._get_rule_based_intervention(struggle)

        # Build context for Claude
        prompt = f"""You are The Director - an invisible AI that helps learners unstick themselves.

A learner is struggling with: {struggle.type.value}
Description: {struggle.description}
Error message: {struggle.error_message or 'N/A'}
Code context: {struggle.code_context or 'N/A'}
Times stuck: {struggle.frequency}

Their frustration level: {self._frustration_level:.0%}
Their momentum: {self._momentum:.0%}

What do they need to learn RIGHT NOW to get unstuck?

Options:
1. A brief hint (1-2 sentences, don't give away the answer)
2. A micro-lesson (3-5 sentences explaining the concept they're missing)
3. A redirect to a simpler challenge
4. Generate a NEW mini-challenge that teaches exactly what they need

Respond with JSON:
{{
    "intervention_type": "hint" | "micro_lesson" | "redirect" | "new_challenge",
    "content": "Your intervention content",
    "reason": "Why this will help",
    "confidence": 0.0-1.0,
    "new_challenge": {{  // Only if intervention_type is "new_challenge"
        "name": "Challenge name",
        "description": "What they'll learn",
        "skeleton_code": "def solution():\\n    pass",
        "test_cases": ["input -> expected output"],
        "hints": ["Hint 1", "Hint 2"]
    }}
}}
"""

        try:
            response = client.chat(prompt, system="You are The Director, a benevolent AI that shapes learning experiences. Be concise, helpful, and encouraging.")
            data = json.loads(response.content)

            return DirectorIntervention(
                type=data.get("intervention_type", "hint"),
                content=data.get("content", "Keep going, you've got this!"),
                reason=data.get("reason", "AI-generated intervention"),
                confidence=data.get("confidence", 0.7),
                generated_challenge=data.get("new_challenge"),
            )
        except Exception as e:
            # Fallback if AI fails
            return self._get_rule_based_intervention(struggle)

    def _get_rule_based_intervention(self, struggle: Struggle) -> DirectorIntervention:
        """Fallback rule-based intervention when AI isn't available."""
        interventions = {
            StruggleType.SYNTAX_ERROR: DirectorIntervention(
                type="hint",
                content="Check your colons, parentheses, and indentation. Python is picky about these!",
                reason="Syntax errors are usually punctuation or whitespace",
                confidence=0.8,
            ),
            StruggleType.TYPE_ERROR: DirectorIntervention(
                type="micro_lesson",
                content="Python has different types: strings ('hello'), numbers (42), lists ([1,2,3]). You can't mix them freely - 'hello' + 5 doesn't work, but 'hello' + str(5) does!",
                reason="Type errors indicate type confusion",
                confidence=0.7,
            ),
            StruggleType.CONCEPT_GAP: DirectorIntervention(
                type="redirect",
                content="You might be missing a prerequisite concept. Let's try a simpler challenge first.",
                reason="NameError often means jumping ahead",
                confidence=0.6,
            ),
            StruggleType.LOGIC_ERROR: DirectorIntervention(
                type="hint",
                content="Your code runs but gives wrong results. Try adding print() statements to see what's happening at each step.",
                reason="Logic errors need debugging",
                confidence=0.7,
            ),
            StruggleType.PATTERN_UNFAMILIAR: DirectorIntervention(
                type="micro_lesson",
                content="When accessing items in a list or dict, make sure the index/key exists first. Use len() to check list size, or 'key in dict' to check if a key exists.",
                reason="Index/Key errors are common pattern gaps",
                confidence=0.7,
            ),
            StruggleType.FRUSTRATION_SPIRAL: DirectorIntervention(
                type="encouragement",
                content="Every expert was once a beginner. The fact that you're stuck means you're learning something new!",
                reason="High frustration needs emotional support",
                confidence=0.5,
            ),
            StruggleType.STRING_VS_IDENTIFIER: DirectorIntervention(
                type="micro_lesson",
                content="Python gotcha alert! 🎯 When comparing, 'add' (with quotes) is a STRING, but add (no quotes) refers to the FUNCTION itself. They're completely different things! Use quotes when you're matching against text like 'add', 'subtract', etc.",
                reason="Comparing string parameter to function object instead of string literal",
                confidence=0.95,
            ),
            StruggleType.OPERATOR_ORDER_TYPO: DirectorIntervention(
                type="micro_lesson",
                content="Operator order matters! 🔄 `health -= damage` SUBTRACTS damage from health. But `health =- damage` ASSIGNS negative damage to health (completely different!). The operator comes BEFORE the equals sign: -= += *= /=",
                reason="Wrote =- instead of -= (assigns negative value instead of subtracting)",
                confidence=0.95,
            ),
            StruggleType.OUTPUT_FORMAT_MISMATCH: DirectorIntervention(
                type="hint",
                content="📋 Check the output format! The challenge wants a specific message, not just the raw value. Look for text like 'Print: \"Your name has X letters\"' in the instructions - you need to match that exact format using an f-string or string concatenation.",
                reason="Printed raw value but challenge expected formatted string output",
                confidence=0.9,
            ),
            StruggleType.STRING_CONCAT_TYPE_ERROR: DirectorIntervention(
                type="micro_lesson",
                content="🔤 Python won't automatically convert numbers to text! When combining strings with `+`, everything must be a string.\n\n**Two fixes:**\n1. Use `str()`: `\"Age: \" + str(age)`\n2. Use f-strings (easier!): `f\"Age: {age}\"`\n\nF-strings automatically convert values inside `{}`!",
                reason="Tried to concatenate string with int/float without converting",
                confidence=0.95,
            ),
            StruggleType.RANGE_OFF_BY_ONE: DirectorIntervention(
                type="micro_lesson",
                content="🔢 Zero-indexing gotcha! Python counts from 0, not 1.\n\n`range(5)` → 0, 1, 2, 3, 4 (starts at 0!)\n`range(1, 6)` → 1, 2, 3, 4, 5 (starts at 1, stops BEFORE 6)\n\nTo get numbers 1-5, use `range(1, 6)` - the second number is always one MORE than you want to end at!",
                reason="Used range(n) expecting 1-n, but got 0 to n-1",
                confidence=0.95,
            ),
            StruggleType.RANGE_SINGLE_ARG_ALWAYS_ZERO: DirectorIntervention(
                type="micro_lesson",
                content="⚠️ **Critical insight:** `range(n)` with ONE argument ALWAYS starts at 0. No exceptions!\n\n• `range(4)` → 0, 1, 2, 3\n• `range(5)` → 0, 1, 2, 3, 4\n• `range(100)` → 0, 1, 2, ... 99\n\n**To start at 1, you MUST use TWO arguments:**\n`range(1, 6)` → 1, 2, 3, 4, 5\n\nThe first arg is START, second is STOP (exclusive). No shortcut!",
                reason="Tried different numbers in range(n) hoping to start at 1 - but single-arg range always starts at 0",
                confidence=0.98,
            ),
            StruggleType.PRINT_VS_RETURN: DirectorIntervention(
                type="micro_lesson",
                content="🖨️ **print() vs return - they're completely different!**\n\n• `print(x)` → Shows x on screen, returns `None`\n• `return x` → Gives x back to the caller\n\n❌ **Wrong:** `return print(f\"Added {item}\")`\n✅ **Right:** `return f\"Added {item}\"`\n\n`print()` is for displaying to humans. `return` is for giving values back to code!",
                reason="Used return print(...) but print() returns None",
                confidence=0.98,
            ),
            StruggleType.FSTRING_SYNTAX: DirectorIntervention(
                type="micro_lesson",
                content="🔤 **F-string gotcha!** You need the `f` prefix to make `{variables}` work!\n\n❌ **Wrong:** `\"Hello {name}\"` → Literally prints `{name}`\n✅ **Right:** `f\"Hello {name}\"` → Prints the actual value\n\nThe `f` before the quote tells Python to look for `{...}` and insert values!",
                reason="String literal with {braces} but missing f prefix",
                confidence=0.95,
            ),
            StruggleType.RETURN_VS_PRINT: DirectorIntervention(
                type="micro_lesson",
                content="📤 **return vs print() - different purposes!**\n\n• `return x` → Gives x back to the code that called the function (invisible to user)\n• `print(x)` → Shows x on the screen (visible to user)\n\n**Check the challenge instructions:**\n- \"Print the result\" → use `print()`\n- \"Return the result\" → use `return`\n\nSome challenges check what you PRINT, not what you RETURN!",
                reason="Used return but challenge expected printed output",
                confidence=0.90,
            ),
            StruggleType.ACCIDENTAL_NONE_OUTPUT: DirectorIntervention(
                type="micro_lesson",
                content="👻 **The mysterious 'None' in your output!**\n\nThis usually means:\n\n1. **Nested print:** `print(print('hi'))` → prints 'hi' then 'None'\n   ✅ Fix: Just `print('hi')`\n\n2. **Mixed return + print:** Function prints AND returns\n   ✅ Fix: Pick one based on what the challenge wants\n\n3. **Printing a None value:** A variable or function returned None\n   ✅ Fix: Check what you're printing - is it what you expect?\n\nRemember: `print()` returns `None`, so printing the result of print() gives you None!",
                reason="Output contains unexpected 'None' - likely from print() return value",
                confidence=0.92,
            ),
            # Container/query-processing challenges
            StruggleType.RETURN_IN_LOOP: DirectorIntervention(
                type="micro_lesson",
                content="🔄 **Return vs Append in loops!**\n\nWhen building a list of results inside a loop, DON'T use `return` - it exits immediately!\n\n❌ **Wrong:**\n```python\nfor query in queries:\n    if command == 'ADD':\n        return ''  # EXITS the function after first query!\n```\n\n✅ **Right:**\n```python\nresults = []\nfor query in queries:\n    if command == 'ADD':\n        results.append('')  # Adds to list, continues loop\nreturn results  # Returns the full list at the END\n```\n\n`return` = exit function NOW\n`append` = add to list, keep going",
                reason="Using return inside loop exits immediately instead of building result list",
                confidence=0.95,
            ),
            StruggleType.CONTAINER_STATE_BUG: DirectorIntervention(
                type="micro_lesson",
                content="📦 **Container state tracking!**\n\nWhen building a container (list/dict that processes queries), you need:\n\n1. **Initialize before the loop:** `container = []` or `results = []`\n2. **Track BOTH the data AND the results separately**\n3. **Don't reset state inside the loop!**\n\n```python\nresults = []      # Track outputs\ncontainer = []    # Track actual data\nfor query in queries:\n    # Process each query, update BOTH\n```",
                reason="Container state not properly initialized or tracked across queries",
                confidence=0.9,
            ),
            StruggleType.COMMAND_DISPATCH_MISSING: DirectorIntervention(
                type="micro_lesson",
                content="🎯 **Missing command handler!**\n\nWhen processing queries like `['ADD', '5']` or `['REMOVE', '3']`, you need:\n\n```python\nif command == 'ADD':\n    # handle ADD\nelif command == 'REMOVE':\n    # handle REMOVE\nelif command == 'COUNT':\n    # handle COUNT\n# ... ALL commands need handlers!\n```\n\n**Check:** Does your code handle EVERY command type the challenge mentions?",
                reason="Missing if/elif branch for one of the command types",
                confidence=0.9,
            ),
            StruggleType.BOOLEAN_VS_STRING_RESULT: DirectorIntervention(
                type="micro_lesson",
                content="🔤 **Boolean vs String result!**\n\nMany challenges want string output, not Python booleans:\n\n❌ **Wrong:** `return True` or `results.append(True)`\n✅ **Right:** `return \"true\"` or `results.append(\"true\")`\n\n**Python booleans:** `True`, `False` (capital, no quotes)\n**String results:** `\"true\"`, `\"false\"` (lowercase, with quotes)\n\nCheck what the challenge expects - usually it's the string version!",
                reason="Returning Python boolean instead of string 'true'/'false'",
                confidence=0.95,
            ),
            StruggleType.MEDIAN_EMPTY_CRASH: DirectorIntervention(
                type="micro_lesson",
                content="📊 **Median of empty list crashes!**\n\nYou can't get the median of nothing:\n\n❌ `sorted([])[len([])//2]` → IndexError!\n\n**Always check first:**\n```python\nif len(container) == 0:\n    results.append(\"\")  # Empty string for no median\nelse:\n    # Safe to calculate median now\n```",
                reason="Trying to access median when container is empty",
                confidence=0.95,
            ),
            StruggleType.MEDIAN_EVEN_ODD: DirectorIntervention(
                type="micro_lesson",
                content="📐 **Median index formula!**\n\nFor a sorted list, the 'lower median' index is:\n\n```python\nmiddle_index = (len(sorted_list) - 1) // 2\n```\n\n**Examples:**\n- `[1, 5, 9]` → index (3-1)//2 = 1 → value 5 ✓\n- `[1, 4, 5, 10]` → index (4-1)//2 = 1 → value 4 ✓\n\n**Remember:** Sort first, then index into the sorted list!",
                reason="Wrong middle index calculation for median",
                confidence=0.9,
            ),
            StruggleType.GET_NEXT_BOUNDARY: DirectorIntervention(
                type="micro_lesson",
                content="🔍 **GET_NEXT boundary case!**\n\nWhen finding 'next greater' value:\n\n```python\ngreater = [x for x in container if x > target]\nif greater:\n    return str(min(greater))  # Smallest of the greater values\nelse:\n    return \"\"  # Nothing is greater!\n```\n\n**Edge cases:**\n- Target >= all values → return \"\"\n- Empty container → return \"\"\n- Multiple equal values → still find next GREATER",
                reason="GET_NEXT returns wrong result when target >= all values",
                confidence=0.9,
            ),
            StruggleType.REMOVE_WITHOUT_CHECK: DirectorIntervention(
                type="micro_lesson",
                content="🗑️ **REMOVE needs a check first!**\n\nCalling `.remove(x)` on a list crashes if x isn't there:\n\n❌ `container.remove(5)` → ValueError if 5 not in list!\n\n**Always check:**\n```python\nif value in container:\n    container.remove(value)\n    results.append(\"true\")\nelse:\n    results.append(\"false\")\n```",
                reason="Calling .remove() without checking if value exists",
                confidence=0.95,
            ),
            StruggleType.INTEGER_DIVISION_FLOAT: DirectorIntervention(
                type="micro_lesson",
                content="➗ **Integer division: // not /**\n\nPython has TWO division operators:\n\n- `/` → float division: `5 / 2` = `2.5`\n- `//` → integer division: `5 // 2` = `2`\n\n**For indices, always use //**:\n```python\nmiddle = len(data) // 2  # Integer index!\n```\n\nList indices must be integers, not floats!",
                reason="Using / instead of // for integer division (especially for indices)",
                confidence=0.95,
            ),
        }

        return interventions.get(struggle.type, DirectorIntervention(
            type="encouragement",
            content="You're doing great! Programming is hard, but you're making progress.",
            reason="Generic encouragement",
            confidence=0.4,
        ))

    def mark_struggle_resolved(self, struggle_key: str):
        """Mark a struggle as resolved after successful completion."""
        if struggle_key in self._struggles:
            self._struggles[struggle_key].resolved = True
            self._persist_struggle(struggle_key)

    def get_difficulty_suggestion(self) -> Optional[dict]:
        """
        Analyze recent performance and suggest difficulty adjustment.

        Returns suggestion dict or None if no change recommended:
        {
            "direction": "easier" | "harder",
            "reason": str,
            "confidence": float,
            "suggested_difficulty": "easy" | "normal" | "hard",
            "suggested_hints": "full" | "partial" | "none"
        }
        """
        if len(self._observations) < 5:
            # Not enough data yet
            return None

        # Analyze recent observations (last 10)
        recent = self._observations[-10:]
        successes = sum(1 for o in recent if o.success)
        failures = len(recent) - successes
        success_rate = successes / len(recent)

        # Check for struggle patterns
        active_struggles = len([s for s in self._struggles.values() if not s.resolved])

        # Breezing through: High success rate + high momentum + fast times
        avg_time = sum(o.time_seconds for o in recent) / len(recent)
        is_breezing = (
            success_rate >= 0.9 and
            self._momentum >= 0.8 and
            avg_time < 30  # Very fast solves
        )

        # Struggling: High failure rate OR high frustration OR many active struggles
        is_struggling = (
            success_rate <= 0.3 or
            self._frustration_level >= 0.6 or
            active_struggles >= 3
        )

        if is_breezing:
            return {
                "direction": "harder",
                "reason": f"You're crushing it! {int(success_rate * 100)}% success rate with fast solve times.",
                "confidence": min(0.9, success_rate),
                "suggested_difficulty": "hard",
                "suggested_hints": "partial",
            }
        elif is_struggling:
            # Determine severity
            if self._frustration_level >= 0.7 or success_rate <= 0.2:
                return {
                    "direction": "easier",
                    "reason": "You seem to be having a tough time. No shame in adjusting!",
                    "confidence": 0.8,
                    "suggested_difficulty": "easy",
                    "suggested_hints": "full",
                }
            else:
                return {
                    "direction": "easier",
                    "reason": f"Hit a few bumps ({active_struggles} areas to work on). More hints might help.",
                    "confidence": 0.6,
                    "suggested_difficulty": "normal",
                    "suggested_hints": "full",
                }

        return None

    def get_shadow_adjustments(self) -> dict:
        """
        Get silent adjustments for challenge selection.

        These adjustments influence recommendations without changing visible settings.
        This is ethical adaptive design - we help even when suggestions are disabled.

        Returns:
        {
            "difficulty_bias": float (-1 to 1, negative = easier bias),
            "avoid_concepts": list[str],  # Concepts causing frustration
            "prefer_concepts": list[str], # Concepts where they're building momentum
            "micro_challenge_candidates": list[str],  # Weak spots to address
            "reason": str  # For transparency in AI tab
        }
        """
        # Calculate difficulty bias based on recent performance
        difficulty_bias = 0.0

        if len(self._observations) >= 3:
            recent = self._observations[-5:]
            success_rate = sum(1 for o in recent if o.success) / len(recent)

            # Shift bias based on performance
            if success_rate < 0.3:
                difficulty_bias = -0.3  # Easier bias
            elif success_rate > 0.8 and self._momentum > 0.7:
                difficulty_bias = 0.2  # Slightly harder bias
            elif self._frustration_level > 0.5:
                difficulty_bias = -0.2  # Ease off when frustrated

        # Use mastery tracking for more accurate concept analysis
        avoid_concepts = self.get_struggling_concepts()
        prefer_concepts = self.get_mastered_concepts()
        micro_candidates = []

        # Add struggles as micro-challenge candidates
        for key, struggle in self._struggles.items():
            if struggle.resolved:
                continue

            if struggle.type == StruggleType.CONCEPT_GAP:
                if struggle.frequency >= 2:
                    micro_candidates.append(struggle.description)

        # Also add low-mastery concepts as candidates for micro-challenges
        for concept, mastery in self._mastery.items():
            if 0.2 < mastery.mastery_score < 0.5 and concept not in micro_candidates:
                # Sweet spot: not total failure, but needs work
                micro_candidates.append(concept)

        # Factor in learning velocity for smarter adjustments
        velocity = self.get_learning_velocity()
        if velocity > 0.3:
            # Improving quickly - can handle slightly harder content
            difficulty_bias = min(0.3, difficulty_bias + 0.1)
        elif velocity < -0.3:
            # Struggling more over time - ease off
            difficulty_bias = max(-0.4, difficulty_bias - 0.1)

        # Generate reason for transparency
        reasons = []
        if difficulty_bias < 0:
            reasons.append("easing difficulty slightly")
        elif difficulty_bias > 0:
            reasons.append("increasing challenge slightly")
        if avoid_concepts:
            reasons.append(f"avoiding frustrating concepts")
        if micro_candidates:
            reasons.append(f"preparing micro-challenges for weak spots")

        return {
            "difficulty_bias": round(difficulty_bias, 2),
            "avoid_concepts": avoid_concepts[:5],  # Limit to top 5
            "prefer_concepts": prefer_concepts[:5],
            "micro_challenge_candidates": micro_candidates[:3],
            "reason": "; ".join(reasons) if reasons else "no adjustments needed",
        }

    def get_flow_recommendation(self, available_challenges: List[dict] = None) -> dict:
        """
        Get a recommendation optimized for flow state.

        Flow state requires:
        - Challenge slightly above current skill (not too easy, not too hard)
        - Building on recent momentum
        - Avoiding frustration triggers
        - Respecting learning velocity

        Returns a recommendation dict with flow state context.
        """
        # Gather current state
        velocity = self.get_learning_velocity()
        shadow = self.get_shadow_adjustments()
        frustration = self._frustration_level
        momentum = self._momentum

        # Determine optimal difficulty zone for flow
        # Flow = skill matches challenge. Too easy = boredom. Too hard = anxiety.
        if velocity > 0.2 and momentum > 0.6:
            # Improving and momentum high - can handle slightly harder
            difficulty_target = "slightly_harder"
            reason_prefix = "You're on a roll! "
        elif velocity < -0.2 or frustration > 0.5:
            # Struggling or frustrated - ease off
            difficulty_target = "easier"
            reason_prefix = "Let's build some momentum. "
        elif momentum < 0.3:
            # Low momentum - need a win
            difficulty_target = "easy_win"
            reason_prefix = "Time for a confidence boost! "
        else:
            # Stable - maintain current level
            difficulty_target = "balanced"
            reason_prefix = ""

        # Concepts to prefer/avoid based on Director insights
        prefer = shadow.get("prefer_concepts", [])
        avoid = shadow.get("avoid_concepts", [])

        # Check for active struggles that need addressing
        worst_struggle = self._find_worst_struggle()
        if worst_struggle and worst_struggle.frequency >= 3:
            # High-frequency struggle - might need a prerequisite challenge
            micro_lesson_needed = True
            struggle_concept = worst_struggle.description[:30]
        else:
            micro_lesson_needed = False
            struggle_concept = None

        # Build flow context
        flow_context = {
            "difficulty_target": difficulty_target,
            "reason_prefix": reason_prefix,
            "prefer_concepts": prefer,
            "avoid_concepts": avoid,
            "micro_lesson_needed": micro_lesson_needed,
            "struggle_concept": struggle_concept,
            "learning_velocity": round(velocity, 2),
            "momentum": round(momentum, 2),
            "frustration": round(frustration, 2),
            "difficulty_bias": shadow.get("difficulty_bias", 0),
        }

        # Generate human-readable reason
        if difficulty_target == "slightly_harder":
            flow_context["reason"] = reason_prefix + "Time to level up!"
        elif difficulty_target == "easier":
            flow_context["reason"] = reason_prefix + "A good challenge for right now."
        elif difficulty_target == "easy_win":
            flow_context["reason"] = reason_prefix + "You've got this one!"
        else:
            flow_context["reason"] = "Perfect time to learn something new!"

        return flow_context

    def score_challenge_for_flow(self, challenge: dict) -> float:
        """
        Score a challenge for how well it matches current flow state.

        Returns 0-1 score (higher = better fit for flow).
        """
        flow = self.get_flow_recommendation()
        score = 0.5  # Base score

        challenge_level = challenge.get("level", 1)
        challenge_concepts = challenge.get("concepts", [])
        challenge_id = challenge.get("id", "")

        # Difficulty matching
        target = flow["difficulty_target"]
        if target == "easy_win" and challenge_level <= 1:
            score += 0.3
        elif target == "easier" and challenge_level <= 2:
            score += 0.2
        elif target == "slightly_harder" and challenge_level >= 2:
            score += 0.2
        elif target == "balanced":
            score += 0.1

        # Concept preferences
        for concept in challenge_concepts:
            if concept in flow["prefer_concepts"]:
                score += 0.15
            if concept in flow["avoid_concepts"]:
                score -= 0.3

        # Check mastery - prefer challenges where player has some but not full mastery
        for concept in challenge_concepts:
            mastery = self._mastery.get(concept)
            if mastery:
                if 0.3 <= mastery.mastery_score <= 0.7:
                    # Sweet spot - building mastery
                    score += 0.1
                elif mastery.mastery_score > 0.9:
                    # Already mastered - less interesting
                    score -= 0.1

        # Momentum bonus - if player just completed similar challenges, boost related ones
        if self._observations:
            recent_ids = [o.challenge_id for o in self._observations[-3:] if o.success]
            # Could check for related challenges here

        return max(0.0, min(1.0, score))

    def get_state(self) -> dict:
        """Get The Director's current state for debugging/analytics."""
        # Get top mastered and struggling concepts with scores
        mastered = [
            {"concept": m.concept, "score": round(m.mastery_score, 2), "streak": m.streak}
            for m in sorted(self._mastery.values(), key=lambda x: -x.mastery_score)[:5]
            if m.mastery_score > 0.5
        ]
        struggling = [
            {"concept": m.concept, "score": round(m.mastery_score, 2), "failures": m.failures}
            for m in sorted(self._mastery.values(), key=lambda x: x.mastery_score)[:5]
            if m.mastery_score < 0.4 and (m.successes + m.failures) >= 2
        ]

        return {
            "player_id": self.player_id,
            "frustration_level": self._frustration_level,
            "momentum": self._momentum,
            "observation_count": len(self._observations),
            "active_struggles": len([s for s in self._struggles.values() if not s.resolved]),
            "should_intervene": self.should_intervene(),
            "difficulty_suggestion": self.get_difficulty_suggestion(),
            "shadow_adjustments": self.get_shadow_adjustments(),
            # New mastery-based insights
            "learning_velocity": round(self.get_learning_velocity(), 2),
            "total_successes": self._total_successes,
            "total_failures": self._total_failures,
            "first_try_rate": round(self._first_try_successes / self._total_successes, 2) if self._total_successes > 0 else 0,
            "mastered_concepts": mastered,
            "struggling_concepts": struggling,
            "concepts_tracked": len(self._mastery),
        }


# Global directors per player (in-memory with SQLite persistence)
_directors: Dict[str, Director] = {}


def get_director(player_id: str, db=None) -> Director:
    """
    Get or create a Director for a player.

    Args:
        player_id: Player identifier
        db: Optional database instance for persistence.
            If provided, Director will load state from and persist to SQLite.
    """
    if player_id not in _directors:
        _directors[player_id] = Director(player_id, db=db)
    elif db is not None and _directors[player_id]._db is None:
        # Upgrade an existing Director to use persistence
        _directors[player_id]._db = db
        _directors[player_id]._load_from_db()
    return _directors[player_id]


# Self-teaching note:
#
# This file demonstrates:
# - AI-augmented systems (Level 6+)
# - Dataclasses for structured data (Level 5)
# - Enum for categorization (Level 4)
# - Strategy pattern for interventions (Level 5)
# - Lazy initialization pattern (Level 4)
# - JSON communication with AI (Level 5)
#
# The Director represents advanced AI integration - using
# language models not just for chat, but as a decision-making
# component in a larger system.
