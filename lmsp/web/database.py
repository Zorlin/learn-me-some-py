"""
LMSP SQLite Database
====================

Persistent storage for player progress, XP, mastery, and authentication.

Features:
- Player profiles with optional password protection
- Challenge completion tracking with timestamps
- XP and mastery level persistence
- Gamepad combo unlock sequences
- Session management

Schema:
- players: Core player data and authentication
- completions: Challenge completion history
- mastery: Concept mastery levels
- gamepad_combos: Custom unlock sequences
"""

import sqlite3
import hashlib
import secrets
import json
from pathlib import Path
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field
from contextlib import contextmanager


# Database location
DB_DIR = Path(__file__).parent.parent.parent / "data"
DB_PATH = DB_DIR / "lmsp.db"


@dataclass
class PlayerData:
    """Player data from database."""
    player_id: str
    display_name: Optional[str] = None  # Friendly name shown in UI
    password_hash: Optional[str] = None
    salt: Optional[str] = None
    total_xp: int = 0
    created_at: str = ""
    last_active: str = ""
    gamepad_combo: Optional[str] = None  # JSON-encoded combo sequence


@dataclass
class CompletionData:
    """Challenge completion record."""
    player_id: str
    challenge_id: str
    count: int
    first_completed: str
    last_completed: str
    times: list[float] = field(default_factory=list)
    best_time: Optional[float] = None


@dataclass
class MasteryData:
    """Concept mastery record."""
    player_id: str
    concept_id: str
    mastery_level: float
    updated_at: str


class LMSPDatabase:
    """
    SQLite database manager for LMSP.

    Thread-safe via connection-per-call pattern.
    """

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DB_PATH
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        """Create database directory and tables if needed."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with self._get_connection() as conn:
            self._create_tables(conn)

    @contextmanager
    def _get_connection(self):
        """Get a database connection (context manager)."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        # Enable WAL mode for better concurrent read/write performance
        conn.execute("PRAGMA journal_mode=WAL")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _create_tables(self, conn: sqlite3.Connection):
        """Create all tables if they don't exist."""
        cursor = conn.cursor()

        # Players table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS players (
                player_id TEXT PRIMARY KEY,
                display_name TEXT,
                password_hash TEXT,
                salt TEXT,
                total_xp INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                last_active TEXT NOT NULL,
                gamepad_combo TEXT
            )
        """)

        # Migration: Add display_name column if it doesn't exist
        cursor.execute("PRAGMA table_info(players)")
        columns = [row[1] for row in cursor.fetchall()]
        if "display_name" not in columns:
            cursor.execute("ALTER TABLE players ADD COLUMN display_name TEXT")

        # Completions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS completions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id TEXT NOT NULL,
                challenge_id TEXT NOT NULL,
                count INTEGER DEFAULT 1,
                first_completed TEXT NOT NULL,
                last_completed TEXT NOT NULL,
                times TEXT DEFAULT '[]',
                best_time REAL,
                FOREIGN KEY (player_id) REFERENCES players(player_id),
                UNIQUE(player_id, challenge_id)
            )
        """)

        # Mastery table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mastery (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id TEXT NOT NULL,
                concept_id TEXT NOT NULL,
                mastery_level REAL DEFAULT 0,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (player_id) REFERENCES players(player_id),
                UNIQUE(player_id, concept_id)
            )
        """)

        # Sessions table (for authentication)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                player_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                auth_method TEXT DEFAULT 'password',
                FOREIGN KEY (player_id) REFERENCES players(player_id)
            )
        """)

        # XP History table - tracks every XP gain for time-series graphs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS xp_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id TEXT NOT NULL,
                xp_amount INTEGER NOT NULL,
                reason TEXT NOT NULL,
                challenge_id TEXT,
                solve_time REAL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (player_id) REFERENCES players(player_id)
            )
        """)

        # Emotional feedback table - tracks satisfaction/frustration ratings
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS emotional_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id TEXT NOT NULL,
                challenge_id TEXT,
                stage INTEGER,
                enjoyment REAL NOT NULL DEFAULT 0,
                frustration REAL NOT NULL DEFAULT 0,
                skipped INTEGER NOT NULL DEFAULT 0,
                context TEXT,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (player_id) REFERENCES players(player_id)
            )
        """)

        # =====================================================================
        # The Director - Adaptive Learning AI Tables
        # =====================================================================

        # Director observations - every code submission
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS director_observations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id TEXT NOT NULL,
                challenge_id TEXT NOT NULL,
                success INTEGER NOT NULL,
                error TEXT,
                output TEXT,
                tests_passing INTEGER DEFAULT 0,
                tests_total INTEGER DEFAULT 0,
                time_seconds REAL NOT NULL,
                attempt_number INTEGER NOT NULL,
                concepts TEXT DEFAULT '[]',
                timestamp TEXT NOT NULL,
                FOREIGN KEY (player_id) REFERENCES players(player_id)
            )
        """)

        # Director mastery tracking per concept
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS director_mastery (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id TEXT NOT NULL,
                concept TEXT NOT NULL,
                successes INTEGER DEFAULT 0,
                failures INTEGER DEFAULT 0,
                total_time REAL DEFAULT 0,
                fastest_time REAL,
                first_try_successes INTEGER DEFAULT 0,
                streak INTEGER DEFAULT 0,
                last_attempt TEXT,
                FOREIGN KEY (player_id) REFERENCES players(player_id),
                UNIQUE(player_id, concept)
            )
        """)

        # Director struggles - active problem areas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS director_struggles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id TEXT NOT NULL,
                struggle_key TEXT NOT NULL,
                struggle_type TEXT NOT NULL,
                description TEXT NOT NULL,
                error_message TEXT,
                code_context TEXT,
                frequency INTEGER DEFAULT 1,
                first_seen TEXT NOT NULL,
                last_seen TEXT NOT NULL,
                resolved INTEGER DEFAULT 0,
                FOREIGN KEY (player_id) REFERENCES players(player_id),
                UNIQUE(player_id, struggle_key)
            )
        """)

        # Director state - momentum, frustration, totals
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS director_state (
                player_id TEXT PRIMARY KEY,
                frustration_level REAL DEFAULT 0,
                momentum REAL DEFAULT 0.5,
                total_successes INTEGER DEFAULT 0,
                total_failures INTEGER DEFAULT 0,
                first_try_successes INTEGER DEFAULT 0,
                last_success_time TEXT,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (player_id) REFERENCES players(player_id)
            )
        """)

        # Indexes for common queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_completions_player
            ON completions(player_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_mastery_player
            ON mastery(player_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sessions_player
            ON sessions(player_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_xp_history_player_timestamp
            ON xp_history(player_id, timestamp)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_emotional_feedback_player
            ON emotional_feedback(player_id, challenge_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_director_observations_player
            ON director_observations(player_id, timestamp)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_director_mastery_player
            ON director_mastery(player_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_director_struggles_player
            ON director_struggles(player_id, resolved)
        """)

    # =========================================================================
    # Player Operations
    # =========================================================================

    def get_or_create_player(self, player_id: str) -> PlayerData:
        """Get player data, creating if doesn't exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Try to get existing player
            cursor.execute(
                "SELECT * FROM players WHERE player_id = ?",
                (player_id,)
            )
            row = cursor.fetchone()

            if row:
                return PlayerData(
                    player_id=row["player_id"],
                    display_name=row["display_name"],
                    password_hash=row["password_hash"],
                    salt=row["salt"],
                    total_xp=row["total_xp"],
                    created_at=row["created_at"],
                    last_active=row["last_active"],
                    gamepad_combo=row["gamepad_combo"],
                )

            # Create new player
            now = datetime.now().isoformat()
            cursor.execute(
                """INSERT INTO players (player_id, created_at, last_active, total_xp)
                   VALUES (?, ?, ?, 0)""",
                (player_id, now, now)
            )

            return PlayerData(
                player_id=player_id,
                total_xp=0,
                created_at=now,
                last_active=now,
            )

    def set_display_name(self, player_id: str, display_name: str) -> bool:
        """Set player's display name."""
        self.get_or_create_player(player_id)  # Ensure player exists

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE players SET display_name = ? WHERE player_id = ?",
                (display_name, player_id)
            )
            return True

    def update_player_activity(self, player_id: str):
        """Update last_active timestamp."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE players SET last_active = ? WHERE player_id = ?",
                (datetime.now().isoformat(), player_id)
            )

    def get_player_xp(self, player_id: str) -> int:
        """Get total XP for a player."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT total_xp FROM players WHERE player_id = ?",
                (player_id,)
            )
            row = cursor.fetchone()
            return row["total_xp"] if row else 0

    def add_player_xp(self, player_id: str, xp: int) -> int:
        """Add XP to player, returns new total."""
        self.get_or_create_player(player_id)  # Ensure player exists

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE players SET total_xp = total_xp + ? WHERE player_id = ?",
                (xp, player_id)
            )
            cursor.execute(
                "SELECT total_xp FROM players WHERE player_id = ?",
                (player_id,)
            )
            return cursor.fetchone()["total_xp"]

    # =========================================================================
    # Password & Authentication
    # =========================================================================

    def set_password(self, player_id: str, password: str) -> bool:
        """Set or update player password."""
        self.get_or_create_player(player_id)  # Ensure player exists

        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        ).hex()

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE players SET password_hash = ?, salt = ? WHERE player_id = ?",
                (password_hash, salt, player_id)
            )
            return True

    def verify_password(self, player_id: str, password: str) -> bool:
        """Verify player password."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT password_hash, salt FROM players WHERE player_id = ?",
                (player_id,)
            )
            row = cursor.fetchone()

            if not row or not row["password_hash"]:
                return False

            test_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                row["salt"].encode('utf-8'),
                100000
            ).hex()

            return secrets.compare_digest(test_hash, row["password_hash"])

    def has_password(self, player_id: str) -> bool:
        """Check if player has a password set."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT password_hash FROM players WHERE player_id = ?",
                (player_id,)
            )
            row = cursor.fetchone()
            return bool(row and row["password_hash"])

    def remove_password(self, player_id: str) -> bool:
        """Remove player password (for gamepad-only unlock)."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE players SET password_hash = NULL, salt = NULL WHERE player_id = ?",
                (player_id,)
            )
            return True

    # =========================================================================
    # Gamepad Combo Unlock
    # =========================================================================

    def set_gamepad_combo(self, player_id: str, combo_sequence: list[str]) -> bool:
        """
        Set gamepad combo unlock sequence.

        Example combo: ["A", "B", "A", "A", "L3+R3"]
        The L3+R3 hold is always required at the end.
        """
        self.get_or_create_player(player_id)

        combo_json = json.dumps(combo_sequence)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE players SET gamepad_combo = ? WHERE player_id = ?",
                (combo_json, player_id)
            )
            return True

    def get_gamepad_combo(self, player_id: str) -> Optional[list[str]]:
        """Get gamepad combo sequence for player."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT gamepad_combo FROM players WHERE player_id = ?",
                (player_id,)
            )
            row = cursor.fetchone()

            if row and row["gamepad_combo"]:
                return json.loads(row["gamepad_combo"])
            return None

    def verify_gamepad_combo(self, player_id: str, entered_combo: list[str]) -> bool:
        """Verify entered gamepad combo matches stored combo."""
        stored_combo = self.get_gamepad_combo(player_id)

        if not stored_combo:
            return False

        return entered_combo == stored_combo

    # =========================================================================
    # Session Management
    # =========================================================================

    def create_session(
        self,
        player_id: str,
        auth_method: str = "password",
        hours_valid: int = 24
    ) -> str:
        """Create a new session, returns session_id."""
        session_id = secrets.token_urlsafe(32)
        now = datetime.now()
        expires = datetime(
            now.year, now.month, now.day + (hours_valid // 24),
            now.hour + (hours_valid % 24), now.minute, now.second
        )

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO sessions (session_id, player_id, created_at, expires_at, auth_method)
                   VALUES (?, ?, ?, ?, ?)""",
                (session_id, player_id, now.isoformat(), expires.isoformat(), auth_method)
            )

        return session_id

    def verify_session(self, session_id: str) -> Optional[str]:
        """Verify session is valid, returns player_id or None."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT player_id, expires_at FROM sessions
                   WHERE session_id = ?""",
                (session_id,)
            )
            row = cursor.fetchone()

            if not row:
                return None

            expires = datetime.fromisoformat(row["expires_at"])
            if datetime.now() > expires:
                # Session expired, delete it
                cursor.execute(
                    "DELETE FROM sessions WHERE session_id = ?",
                    (session_id,)
                )
                return None

            return row["player_id"]

    def delete_session(self, session_id: str):
        """Delete a session (logout)."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM sessions WHERE session_id = ?",
                (session_id,)
            )

    def cleanup_expired_sessions(self):
        """Remove all expired sessions."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM sessions WHERE expires_at < ?",
                (datetime.now().isoformat(),)
            )

    # =========================================================================
    # Challenge Completions
    # =========================================================================

    def get_completions(self, player_id: str) -> dict[str, CompletionData]:
        """Get all completions for a player."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM completions WHERE player_id = ?",
                (player_id,)
            )

            completions = {}
            for row in cursor.fetchall():
                times = json.loads(row["times"]) if row["times"] else []
                completions[row["challenge_id"]] = CompletionData(
                    player_id=row["player_id"],
                    challenge_id=row["challenge_id"],
                    count=row["count"],
                    first_completed=row["first_completed"],
                    last_completed=row["last_completed"],
                    times=times,
                    best_time=row["best_time"],
                )

            return completions

    def record_completion(
        self,
        player_id: str,
        challenge_id: str,
        time_seconds: float
    ) -> CompletionData:
        """Record a challenge completion."""
        self.get_or_create_player(player_id)
        now = datetime.now().isoformat()

        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Check for existing completion
            cursor.execute(
                """SELECT * FROM completions
                   WHERE player_id = ? AND challenge_id = ?""",
                (player_id, challenge_id)
            )
            row = cursor.fetchone()

            if row:
                # Update existing
                times = json.loads(row["times"]) if row["times"] else []
                times.append(time_seconds)
                best_time = min(times)

                cursor.execute(
                    """UPDATE completions
                       SET count = count + 1,
                           last_completed = ?,
                           times = ?,
                           best_time = ?
                       WHERE player_id = ? AND challenge_id = ?""",
                    (now, json.dumps(times), best_time, player_id, challenge_id)
                )

                return CompletionData(
                    player_id=player_id,
                    challenge_id=challenge_id,
                    count=row["count"] + 1,
                    first_completed=row["first_completed"],
                    last_completed=now,
                    times=times,
                    best_time=best_time,
                )
            else:
                # New completion
                times = [time_seconds]
                cursor.execute(
                    """INSERT INTO completions
                       (player_id, challenge_id, count, first_completed, last_completed, times, best_time)
                       VALUES (?, ?, 1, ?, ?, ?, ?)""",
                    (player_id, challenge_id, now, now, json.dumps(times), time_seconds)
                )

                return CompletionData(
                    player_id=player_id,
                    challenge_id=challenge_id,
                    count=1,
                    first_completed=now,
                    last_completed=now,
                    times=times,
                    best_time=time_seconds,
                )

    def get_completion_count(self, player_id: str, challenge_id: str) -> int:
        """Get completion count for a specific challenge."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT count FROM completions
                   WHERE player_id = ? AND challenge_id = ?""",
                (player_id, challenge_id)
            )
            row = cursor.fetchone()
            return row["count"] if row else 0

    # =========================================================================
    # Mastery Tracking
    # =========================================================================

    def get_mastery_levels(self, player_id: str) -> dict[str, float]:
        """Get all mastery levels for a player."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT concept_id, mastery_level FROM mastery WHERE player_id = ?",
                (player_id,)
            )

            return {row["concept_id"]: row["mastery_level"] for row in cursor.fetchall()}

    def set_mastery_level(
        self,
        player_id: str,
        concept_id: str,
        mastery_level: float
    ) -> float:
        """Set mastery level for a concept."""
        self.get_or_create_player(player_id)
        now = datetime.now().isoformat()

        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Upsert pattern
            cursor.execute(
                """INSERT INTO mastery (player_id, concept_id, mastery_level, updated_at)
                   VALUES (?, ?, ?, ?)
                   ON CONFLICT(player_id, concept_id)
                   DO UPDATE SET mastery_level = ?, updated_at = ?""",
                (player_id, concept_id, mastery_level, now, mastery_level, now)
            )

            return mastery_level

    def increment_mastery(
        self,
        player_id: str,
        concept_id: str,
        increment: float = 0.5
    ) -> float:
        """Increment mastery level, capped at 4.0."""
        current = self.get_mastery_levels(player_id).get(concept_id, 0)
        new_level = min(4.0, current + increment)
        return self.set_mastery_level(player_id, concept_id, new_level)

    # =========================================================================
    # XP History
    # =========================================================================

    def record_xp_event(
        self,
        player_id: str,
        xp_amount: int,
        reason: str,
        challenge_id: Optional[str] = None,
        solve_time: Optional[float] = None
    ):
        """Record an XP gain event for history tracking."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO xp_history
                   (player_id, xp_amount, reason, challenge_id, solve_time, timestamp)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (player_id, xp_amount, reason, challenge_id, solve_time,
                 datetime.now().isoformat())
            )

    def get_xp_history(
        self,
        player_id: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: Optional[int] = None
    ) -> list[dict]:
        """
        Get XP history for a player, optionally filtered by time range.

        Returns list of dicts with: xp_amount, reason, challenge_id, solve_time, timestamp
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            query = "SELECT * FROM xp_history WHERE player_id = ?"
            params: list = [player_id]

            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time)
            if end_time:
                query += " AND timestamp <= ?"
                params.append(end_time)

            query += " ORDER BY timestamp ASC"

            if limit:
                query += " LIMIT ?"
                params.append(limit)

            cursor.execute(query, params)

            return [
                {
                    "xp_amount": row["xp_amount"],
                    "reason": row["reason"],
                    "challenge_id": row["challenge_id"],
                    "solve_time": row["solve_time"],
                    "timestamp": row["timestamp"],
                }
                for row in cursor.fetchall()
            ]

    def get_xp_stats_by_period(
        self,
        player_id: str,
        period: str = "day"
    ) -> list[dict]:
        """
        Get XP aggregated by time period.

        Args:
            period: 'hour', 'day', 'week', 'month', 'year'

        Returns list of dicts with: period_start, total_xp, event_count
        """
        # SQLite date formatting for grouping
        format_map = {
            "hour": "%Y-%m-%d %H:00:00",
            "day": "%Y-%m-%d",
            "week": "%Y-W%W",
            "month": "%Y-%m",
            "year": "%Y",
        }
        date_format = format_map.get(period, "%Y-%m-%d")

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"""SELECT
                       strftime('{date_format}', timestamp) as period_start,
                       SUM(xp_amount) as total_xp,
                       COUNT(*) as event_count,
                       AVG(solve_time) as avg_solve_time
                   FROM xp_history
                   WHERE player_id = ?
                   GROUP BY period_start
                   ORDER BY period_start ASC""",
                (player_id,)
            )

            return [
                {
                    "period_start": row["period_start"],
                    "total_xp": row["total_xp"],
                    "event_count": row["event_count"],
                    "avg_solve_time": row["avg_solve_time"],
                }
                for row in cursor.fetchall()
            ]

    # =========================================================================
    # Emotional Feedback / Satisfaction
    # =========================================================================

    def record_emotional_feedback(
        self,
        player_id: str,
        enjoyment: float,
        frustration: float,
        challenge_id: Optional[str] = None,
        stage: Optional[int] = None,
        context: Optional[str] = None,
        skipped: bool = False
    ):
        """
        Record emotional feedback for a challenge/stage.

        Args:
            player_id: Player identifier
            enjoyment: Satisfaction rating 0.0-1.0 (RT trigger)
            frustration: Frustration rating 0.0-1.0 (LT trigger)
            challenge_id: Optional challenge this feedback is for
            stage: Optional stage number (for multi-stage challenges)
            context: Additional context string
            skipped: True if player skipped rating (0%/0% submitted without interaction)

        Note: 0%/0% with skipped=False means player deliberately rated neutral.
              0%/0% with skipped=True means player didn't engage with rating.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO emotional_feedback
                   (player_id, challenge_id, stage, enjoyment, frustration, skipped, context, timestamp)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (player_id, challenge_id, stage, enjoyment, frustration,
                 1 if skipped else 0, context, datetime.now().isoformat())
            )

    def get_satisfaction_history(
        self,
        player_id: str,
        challenge_id: Optional[str] = None,
        limit: int = 100
    ) -> list[dict]:
        """
        Get satisfaction/feedback history for a player.

        Returns list of feedback records, newest first.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            if challenge_id:
                cursor.execute(
                    """SELECT * FROM emotional_feedback
                       WHERE player_id = ? AND challenge_id = ?
                       ORDER BY timestamp DESC LIMIT ?""",
                    (player_id, challenge_id, limit)
                )
            else:
                cursor.execute(
                    """SELECT * FROM emotional_feedback
                       WHERE player_id = ?
                       ORDER BY timestamp DESC LIMIT ?""",
                    (player_id, limit)
                )

            return [
                {
                    "challenge_id": row["challenge_id"],
                    "stage": row["stage"],
                    "enjoyment": row["enjoyment"],
                    "frustration": row["frustration"],
                    "skipped": bool(row["skipped"]),
                    "context": row["context"],
                    "timestamp": row["timestamp"],
                }
                for row in cursor.fetchall()
            ]

    def get_challenge_satisfaction_avg(
        self,
        player_id: str,
        challenge_id: str
    ) -> dict:
        """
        Get average satisfaction for a specific challenge.

        Only includes non-skipped ratings.
        Returns: {avg_enjoyment, avg_frustration, rating_count, skipped_count}
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT
                       AVG(CASE WHEN skipped = 0 THEN enjoyment END) as avg_enjoyment,
                       AVG(CASE WHEN skipped = 0 THEN frustration END) as avg_frustration,
                       SUM(CASE WHEN skipped = 0 THEN 1 ELSE 0 END) as rating_count,
                       SUM(CASE WHEN skipped = 1 THEN 1 ELSE 0 END) as skipped_count
                   FROM emotional_feedback
                   WHERE player_id = ? AND challenge_id = ?""",
                (player_id, challenge_id)
            )
            row = cursor.fetchone()

            return {
                "avg_enjoyment": row["avg_enjoyment"] or 0.0,
                "avg_frustration": row["avg_frustration"] or 0.0,
                "rating_count": row["rating_count"] or 0,
                "skipped_count": row["skipped_count"] or 0,
            }

    def calculate_mastery_from_satisfaction(
        self,
        player_id: str,
        challenge_id: str
    ) -> float:
        """
        Calculate mastery adjustment based on satisfaction history.

        High satisfaction + low frustration = mastered
        Low satisfaction OR high frustration = needs more practice

        Returns mastery adjustment factor: 0.0 to 1.0
        """
        stats = self.get_challenge_satisfaction_avg(player_id, challenge_id)

        if stats["rating_count"] == 0:
            return 0.5  # No data, neutral

        # Mastery = high enjoyment * (1 - frustration)
        # This means:
        # - High enjoyment + low frustration = high mastery (~1.0)
        # - High enjoyment + high frustration = medium mastery (~0.5)
        # - Low enjoyment + high frustration = low mastery (~0.0)
        mastery = stats["avg_enjoyment"] * (1 - stats["avg_frustration"])

        return mastery

    # =========================================================================
    # Statistics
    # =========================================================================

    def get_player_stats(self, player_id: str) -> dict:
        """Get comprehensive player statistics."""
        player = self.get_or_create_player(player_id)
        completions = self.get_completions(player_id)
        mastery = self.get_mastery_levels(player_id)

        total_attempts = sum(c.count for c in completions.values())
        unique_challenges = len(completions)
        mastered_concepts = len([m for m in mastery.values() if m >= 4.0])
        learning_concepts = len([m for m in mastery.values() if 0 < m < 4.0])

        # Calculate level from XP
        xp = player.total_xp
        level = 1
        threshold = 100
        while xp >= threshold:
            level += 1
            threshold += level * 100

        return {
            "player_id": player_id,
            "display_name": player.display_name,
            "total_xp": player.total_xp,
            "level": level,
            "total_attempts": total_attempts,
            "unique_challenges": unique_challenges,
            "mastered_concepts": mastered_concepts,
            "learning_concepts": learning_concepts,
            "created_at": player.created_at,
            "last_active": player.last_active,
            "has_password": bool(player.password_hash),
            "has_gamepad_combo": bool(player.gamepad_combo),
        }

    # =========================================================================
    # The Director - Adaptive AI Persistence
    # =========================================================================

    def save_director_observation(
        self,
        player_id: str,
        challenge_id: str,
        success: bool,
        error: Optional[str],
        output: Optional[str],
        tests_passing: int,
        tests_total: int,
        time_seconds: float,
        attempt_number: int,
        concepts: list[str],
        timestamp: str
    ):
        """Save a Director observation to the database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO director_observations
                   (player_id, challenge_id, success, error, output, tests_passing,
                    tests_total, time_seconds, attempt_number, concepts, timestamp)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (player_id, challenge_id, 1 if success else 0, error, output,
                 tests_passing, tests_total, time_seconds, attempt_number,
                 json.dumps(concepts), timestamp)
            )

    def load_director_observations(
        self,
        player_id: str,
        limit: int = 100
    ) -> list[dict]:
        """Load recent observations for a player."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT * FROM director_observations
                   WHERE player_id = ?
                   ORDER BY timestamp DESC
                   LIMIT ?""",
                (player_id, limit)
            )
            return [
                {
                    "player_id": row["player_id"],
                    "challenge_id": row["challenge_id"],
                    "success": bool(row["success"]),
                    "error": row["error"],
                    "output": row["output"],
                    "tests_passing": row["tests_passing"],
                    "tests_total": row["tests_total"],
                    "time_seconds": row["time_seconds"],
                    "attempt_number": row["attempt_number"],
                    "concepts": json.loads(row["concepts"]) if row["concepts"] else [],
                    "timestamp": row["timestamp"],
                }
                for row in cursor.fetchall()
            ]

    def save_director_mastery(
        self,
        player_id: str,
        concept: str,
        successes: int,
        failures: int,
        total_time: float,
        fastest_time: Optional[float],
        first_try_successes: int,
        streak: int,
        last_attempt: str
    ):
        """Save or update Director mastery for a concept."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO director_mastery
                   (player_id, concept, successes, failures, total_time, fastest_time,
                    first_try_successes, streak, last_attempt)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(player_id, concept)
                   DO UPDATE SET
                       successes = ?, failures = ?, total_time = ?, fastest_time = ?,
                       first_try_successes = ?, streak = ?, last_attempt = ?""",
                (player_id, concept, successes, failures, total_time, fastest_time,
                 first_try_successes, streak, last_attempt,
                 successes, failures, total_time, fastest_time,
                 first_try_successes, streak, last_attempt)
            )

    def load_director_mastery(self, player_id: str) -> dict[str, dict]:
        """Load all Director mastery entries for a player."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM director_mastery WHERE player_id = ?",
                (player_id,)
            )
            return {
                row["concept"]: {
                    "successes": row["successes"],
                    "failures": row["failures"],
                    "total_time": row["total_time"],
                    "fastest_time": row["fastest_time"],
                    "first_try_successes": row["first_try_successes"],
                    "streak": row["streak"],
                    "last_attempt": row["last_attempt"],
                }
                for row in cursor.fetchall()
            }

    def save_director_struggle(
        self,
        player_id: str,
        struggle_key: str,
        struggle_type: str,
        description: str,
        error_message: Optional[str],
        code_context: Optional[str],
        frequency: int,
        first_seen: str,
        last_seen: str,
        resolved: bool
    ):
        """Save or update a Director struggle."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO director_struggles
                   (player_id, struggle_key, struggle_type, description, error_message,
                    code_context, frequency, first_seen, last_seen, resolved)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(player_id, struggle_key)
                   DO UPDATE SET
                       frequency = ?, last_seen = ?, resolved = ?""",
                (player_id, struggle_key, struggle_type, description, error_message,
                 code_context, frequency, first_seen, last_seen, 1 if resolved else 0,
                 frequency, last_seen, 1 if resolved else 0)
            )

    def load_director_struggles(self, player_id: str) -> dict[str, dict]:
        """Load all Director struggles for a player."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM director_struggles WHERE player_id = ?",
                (player_id,)
            )
            return {
                row["struggle_key"]: {
                    "type": row["struggle_type"],
                    "description": row["description"],
                    "error_message": row["error_message"],
                    "code_context": row["code_context"],
                    "frequency": row["frequency"],
                    "first_seen": row["first_seen"],
                    "last_seen": row["last_seen"],
                    "resolved": bool(row["resolved"]),
                }
                for row in cursor.fetchall()
            }

    def save_director_state(
        self,
        player_id: str,
        frustration_level: float,
        momentum: float,
        total_successes: int,
        total_failures: int,
        first_try_successes: int,
        last_success_time: Optional[str]
    ):
        """Save Director state (momentum, frustration, totals)."""
        now = datetime.now().isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO director_state
                   (player_id, frustration_level, momentum, total_successes,
                    total_failures, first_try_successes, last_success_time, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(player_id)
                   DO UPDATE SET
                       frustration_level = ?, momentum = ?, total_successes = ?,
                       total_failures = ?, first_try_successes = ?,
                       last_success_time = ?, updated_at = ?""",
                (player_id, frustration_level, momentum, total_successes,
                 total_failures, first_try_successes, last_success_time, now,
                 frustration_level, momentum, total_successes,
                 total_failures, first_try_successes, last_success_time, now)
            )

    def load_director_state(self, player_id: str) -> Optional[dict]:
        """Load Director state for a player."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM director_state WHERE player_id = ?",
                (player_id,)
            )
            row = cursor.fetchone()
            if not row:
                return None
            return {
                "frustration_level": row["frustration_level"],
                "momentum": row["momentum"],
                "total_successes": row["total_successes"],
                "total_failures": row["total_failures"],
                "first_try_successes": row["first_try_successes"],
                "last_success_time": row["last_success_time"],
            }


# Global database instance
_db: Optional[LMSPDatabase] = None


def get_database() -> LMSPDatabase:
    """Get or create the global database instance."""
    global _db
    if _db is None:
        _db = LMSPDatabase()
    return _db


# Self-teaching note:
#
# This file demonstrates:
# - SQLite database operations (Level 5+: databases)
# - Context managers for resource management (Level 4+)
# - Secure password hashing with PBKDF2 (Level 6: security)
# - JSON serialization for complex data types (Level 3+)
# - Dataclasses for structured data (Level 5)
# - Session management patterns (Level 6: web security)
#
# Key architectural decisions:
# - Connection-per-call for thread safety
# - Upsert pattern for idempotent writes
# - Separate tables for different concerns
# - Global singleton pattern for database instance
