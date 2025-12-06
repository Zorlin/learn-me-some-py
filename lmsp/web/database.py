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

import bcrypt  # Never roll your own crypto - use industry standard bcrypt


# Database location
DB_DIR = Path(__file__).parent.parent.parent / "data"
DB_PATH = DB_DIR / "lmsp.db"


def calculate_level(xp: int) -> int:
    """
    Calculate player level from XP.

    Progressive system where each level requires more XP:
    - Level 1: 0-99 XP
    - Level 2: 100-299 XP (need 100 more)
    - Level 3: 300-599 XP (need 300 more)
    - Level 4: 600-999 XP (need 400 more)
    - etc.

    This is the SINGLE SOURCE OF TRUTH for level calculation.
    Frontend should use backend-provided level, not calculate it.
    """
    level = 1
    threshold = 100
    while xp >= threshold:
        level += 1
        threshold += level * 100
    return level


@dataclass
class PlayerData:
    """Player data from database."""
    player_id: str
    display_name: Optional[str] = None  # Friendly name shown in UI
    password_hash: Optional[str] = None
    salt: Optional[str] = None  # Deprecated - bcrypt embeds salt in hash
    total_xp: int = 0
    created_at: str = ""
    last_active: str = ""
    gamepad_combo: Optional[str] = None  # JSON-encoded combo sequence
    is_admin: bool = False  # First created player is admin


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

        # Migration: Add is_admin column if it doesn't exist
        if "is_admin" not in columns:
            cursor.execute("ALTER TABLE players ADD COLUMN is_admin INTEGER DEFAULT 0")
            # Make the first existing player (by created_at) the admin
            cursor.execute("""
                UPDATE players SET is_admin = 1
                WHERE player_id = (
                    SELECT player_id FROM players ORDER BY created_at ASC LIMIT 1
                )
            """)

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

        # Lesson/challenge access tracking - when user opens a lesson
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lesson_access (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id TEXT NOT NULL,
                lesson_id TEXT NOT NULL,
                lesson_type TEXT NOT NULL DEFAULT 'challenge',
                accessed_at TEXT NOT NULL,
                FOREIGN KEY (player_id) REFERENCES players(player_id)
            )
        """)

        # Speedrun runs - tracks each interview prep attempt
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS speedrun_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT UNIQUE NOT NULL,
                player_id TEXT NOT NULL,
                run_type TEXT NOT NULL DEFAULT 'interview_prep',
                started_at TEXT NOT NULL,
                ended_at TEXT,
                total_time_seconds REAL,
                total_items INTEGER NOT NULL,
                completed_items INTEGER DEFAULT 0,
                total_attempts INTEGER DEFAULT 0,
                total_failures INTEGER DEFAULT 0,
                status TEXT DEFAULT 'in_progress',
                notes TEXT,
                FOREIGN KEY (player_id) REFERENCES players(player_id)
            )
        """)

        # Speedrun splits - per-item timing within a run
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS speedrun_splits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                item_id TEXT NOT NULL,
                item_order INTEGER NOT NULL,
                accessed_at TEXT,
                completed_at TEXT,
                solve_time_seconds REAL,
                attempts INTEGER DEFAULT 0,
                failures INTEGER DEFAULT 0,
                status TEXT DEFAULT 'pending',
                FOREIGN KEY (run_id) REFERENCES speedrun_runs(run_id)
            )
        """)

        # Node settings table (registration mode, etc.)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS node_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # Initialize default settings
        cursor.execute("""
            INSERT OR IGNORE INTO node_settings (key, value, updated_at)
            VALUES ('registration_mode', 'open', datetime('now'))
        """)

        # Invite codes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS invite_codes (
                code TEXT PRIMARY KEY,
                created_by TEXT NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT,
                max_uses INTEGER DEFAULT 1,
                uses INTEGER DEFAULT 0,
                note TEXT,
                active INTEGER DEFAULT 1,
                FOREIGN KEY (created_by) REFERENCES players(player_id)
            )
        """)

        # Track which invite code was used by each player
        cursor.execute("PRAGMA table_info(players)")
        columns = [row[1] for row in cursor.fetchall()]
        if "invited_by_code" not in columns:
            cursor.execute("ALTER TABLE players ADD COLUMN invited_by_code TEXT")

        # Indexes for common queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_lesson_access_player
            ON lesson_access(player_id, lesson_id, accessed_at)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_speedrun_runs_player
            ON speedrun_runs(player_id, started_at)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_speedrun_splits_run
            ON speedrun_splits(run_id, item_order)
        """)
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

    def list_players(self) -> list[dict]:
        """List all players with basic profile info for the profile picker."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT player_id, display_name, total_xp, created_at, last_active,
                       password_hash IS NOT NULL as has_password,
                       gamepad_combo IS NOT NULL as has_gamepad_combo,
                       COALESCE(is_admin, 0) as is_admin
                FROM players
                ORDER BY last_active DESC
            """)
            rows = cursor.fetchall()
            return [
                {
                    "player_id": row["player_id"],
                    "display_name": row["display_name"],
                    "total_xp": row["total_xp"],
                    "level": calculate_level(row["total_xp"]),  # Backend is source of truth
                    "created_at": row["created_at"],
                    "last_active": row["last_active"],
                    "has_password": bool(row["has_password"]),
                    "has_gamepad_combo": bool(row["has_gamepad_combo"]),
                    "is_admin": bool(row["is_admin"]),
                }
                for row in rows
            ]

    def identify_players_by_combo(self, combo: list[str]) -> list[str]:
        """Find player(s) whose gamepad combo matches the given sequence.

        Returns list of player_ids that match. Usually 0 or 1, but could be
        multiple if users set the same combo (edge case for conflict handling).
        """
        import json
        combo_json = json.dumps(combo)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT player_id FROM players WHERE gamepad_combo = ?",
                (combo_json,)
            )
            return [row["player_id"] for row in cursor.fetchall()]

    def migrate_player_data(
        self,
        from_player_id: str,
        to_player_id: str,
        delete_source: bool = True
    ) -> dict:
        """
        Migrate all data from one player_id to another.

        Used for "Import existing" feature - migrate default profile to named profile.

        Args:
            from_player_id: Source player to migrate from
            to_player_id: Destination player to migrate to
            delete_source: If True, delete the source player after migration

        Returns:
            Dict with migration stats (tables affected, rows migrated)
        """
        stats = {
            "completions": 0,
            "mastery": 0,
            "xp_history": 0,
            "emotional_feedback": 0,
            "director_observations": 0,
            "director_mastery": 0,
            "director_struggles": 0,
            "director_state": 0,
            "lesson_access": 0,
            "speedrun_runs": 0,
            "speedrun_splits": 0,
            "sessions": 0,
        }

        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Check source exists
            cursor.execute(
                "SELECT * FROM players WHERE player_id = ?",
                (from_player_id,)
            )
            source = cursor.fetchone()
            if not source:
                raise ValueError(f"Source player '{from_player_id}' not found")

            # Create destination if doesn't exist, or get existing
            now = datetime.now().isoformat()
            cursor.execute(
                "SELECT * FROM players WHERE player_id = ?",
                (to_player_id,)
            )
            dest = cursor.fetchone()

            if dest:
                # Merge XP into existing destination
                cursor.execute(
                    "UPDATE players SET total_xp = total_xp + ? WHERE player_id = ?",
                    (source["total_xp"], to_player_id)
                )
            else:
                # Create new destination with source's data
                cursor.execute(
                    """INSERT INTO players
                       (player_id, display_name, password_hash, salt, total_xp,
                        created_at, last_active, gamepad_combo, is_admin)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (to_player_id, source["display_name"], source["password_hash"],
                     source["salt"], source["total_xp"], now, now,
                     source["gamepad_combo"], source["is_admin"])
                )

            # Migrate all related tables
            tables_with_player_id = [
                "completions",
                "mastery",
                "xp_history",
                "emotional_feedback",
                "director_observations",
                "director_mastery",
                "director_struggles",
                "director_state",
                "lesson_access",
                "speedrun_runs",
                "sessions",
            ]

            for table in tables_with_player_id:
                cursor.execute(
                    f"UPDATE {table} SET player_id = ? WHERE player_id = ?",
                    (to_player_id, from_player_id)
                )
                stats[table] = cursor.rowcount

            # Migrate speedrun_splits via run_id (indirect relationship)
            cursor.execute(
                """UPDATE speedrun_splits SET run_id = run_id
                   WHERE run_id IN (SELECT run_id FROM speedrun_runs WHERE player_id = ?)""",
                (to_player_id,)  # Already updated, just count
            )
            # Count splits that belong to migrated runs
            cursor.execute(
                """SELECT COUNT(*) FROM speedrun_splits
                   WHERE run_id IN (SELECT run_id FROM speedrun_runs WHERE player_id = ?)""",
                (to_player_id,)
            )
            stats["speedrun_splits"] = cursor.fetchone()[0]

            # Delete source player if requested
            if delete_source:
                cursor.execute(
                    "DELETE FROM players WHERE player_id = ?",
                    (from_player_id,)
                )

        return stats

    # =========================================================================
    # Password & Authentication
    # =========================================================================

    def set_password(self, player_id: str, password: str) -> bool:
        """Set or update player password using bcrypt."""
        self.get_or_create_player(player_id)  # Ensure player exists

        # Use bcrypt with automatic salt generation (cost factor 12)
        password_hash = bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt(rounds=12)
        ).decode('utf-8')

        with self._get_connection() as conn:
            cursor = conn.cursor()
            # bcrypt embeds the salt in the hash, so salt column is NULL for bcrypt
            cursor.execute(
                "UPDATE players SET password_hash = ?, salt = NULL WHERE player_id = ?",
                (password_hash, player_id)
            )
            return True

    def verify_password(self, player_id: str, password: str) -> bool:
        """Verify player password using bcrypt."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT password_hash FROM players WHERE player_id = ?",
                (player_id,)
            )
            row = cursor.fetchone()

            if not row or not row["password_hash"]:
                return False

            return bcrypt.checkpw(
                password.encode('utf-8'),
                row["password_hash"].encode('utf-8')
            )

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

        return {
            "player_id": player_id,
            "display_name": player.display_name,
            "total_xp": player.total_xp,
            "level": calculate_level(player.total_xp),  # Use single source of truth
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
    # Admin Operations
    # =========================================================================

    def is_admin(self, player_id: str) -> bool:
        """Check if a player is an admin."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT is_admin FROM players WHERE player_id = ?",
                (player_id,)
            )
            row = cursor.fetchone()
            return bool(row and row["is_admin"])

    def set_admin(self, player_id: str, is_admin: bool) -> bool:
        """Set or remove admin status for a player."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE players SET is_admin = ? WHERE player_id = ?",
                (1 if is_admin else 0, player_id)
            )
            return cursor.rowcount > 0

    def delete_player(self, player_id: str) -> dict:
        """
        Delete a player and all their associated data.
        Returns stats about what was deleted.
        """
        stats = {
            "player": 0,
            "completions": 0,
            "mastery": 0,
            "xp_history": 0,
            "emotional_feedback": 0,
            "director_observations": 0,
            "director_mastery": 0,
            "director_struggles": 0,
            "director_state": 0,
            "lesson_access": 0,
            "speedrun_runs": 0,
            "speedrun_splits": 0,
            "sessions": 0,
        }

        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Delete from all related tables
            tables = [
                "completions",
                "mastery",
                "xp_history",
                "emotional_feedback",
                "director_observations",
                "director_mastery",
                "director_struggles",
                "director_state",
                "lesson_access",
                "sessions",
            ]

            for table in tables:
                cursor.execute(
                    f"DELETE FROM {table} WHERE player_id = ?",
                    (player_id,)
                )
                stats[table] = cursor.rowcount

            # Delete speedrun splits via run_id
            cursor.execute(
                """DELETE FROM speedrun_splits
                   WHERE run_id IN (SELECT run_id FROM speedrun_runs WHERE player_id = ?)""",
                (player_id,)
            )
            stats["speedrun_splits"] = cursor.rowcount

            # Delete speedrun runs
            cursor.execute(
                "DELETE FROM speedrun_runs WHERE player_id = ?",
                (player_id,)
            )
            stats["speedrun_runs"] = cursor.rowcount

            # Finally delete the player
            cursor.execute(
                "DELETE FROM players WHERE player_id = ?",
                (player_id,)
            )
            stats["player"] = cursor.rowcount

        return stats

    def get_node_stats(self) -> dict:
        """Get aggregate statistics across all players on this node."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Player counts
            cursor.execute("SELECT COUNT(*) as total FROM players")
            total_players = cursor.fetchone()["total"]

            cursor.execute(
                "SELECT COUNT(*) as active FROM players WHERE last_active > datetime('now', '-7 days')"
            )
            active_players_last_7_days = cursor.fetchone()["active"]

            cursor.execute("SELECT SUM(total_xp) as total_xp FROM players")
            total_xp_earned = cursor.fetchone()["total_xp"] or 0

            # Security stats
            cursor.execute(
                "SELECT COUNT(*) as count FROM players WHERE password_hash IS NOT NULL"
            )
            players_with_password = cursor.fetchone()["count"]

            cursor.execute(
                "SELECT COUNT(*) as count FROM players WHERE gamepad_combo IS NOT NULL"
            )
            players_with_gamepad = cursor.fetchone()["count"]

            # Players with ANY security (no double-counting)
            cursor.execute(
                "SELECT COUNT(*) as count FROM players WHERE password_hash IS NOT NULL OR gamepad_combo IS NOT NULL"
            )
            players_secured = cursor.fetchone()["count"]

            # Challenge stats - total completions (sum of all completion counts)
            cursor.execute(
                "SELECT COUNT(*) as total, SUM(count) as total_completions FROM completions"
            )
            row = cursor.fetchone()
            unique_completions = row["total"] or 0
            total_completions = row["total_completions"] or 0

            # Challenges completed in last 7 days
            cursor.execute(
                "SELECT COUNT(*) as count FROM completions WHERE last_completed > datetime('now', '-7 days')"
            )
            challenges_completed_last_7_days = cursor.fetchone()["count"]

            # Director stats
            cursor.execute(
                "SELECT COUNT(*) as total FROM director_observations"
            )
            total_observations = cursor.fetchone()["total"]

            # Session stats
            cursor.execute(
                "SELECT COUNT(*) as total FROM sessions WHERE expires_at > datetime('now')"
            )
            active_sessions = cursor.fetchone()["total"]

            # Top players by XP
            cursor.execute(
                """SELECT player_id, display_name, total_xp
                   FROM players ORDER BY total_xp DESC LIMIT 10"""
            )
            top_players = [
                {
                    "player_id": row["player_id"],
                    "display_name": row["display_name"],
                    "total_xp": row["total_xp"],
                    "level": calculate_level(row["total_xp"]),
                }
                for row in cursor.fetchall()
            ]

            return {
                # Frontend expected fields
                "total_players": total_players,
                "total_completions": total_completions,
                "total_xp_earned": total_xp_earned,
                "players_with_password": players_with_password,
                "players_with_gamepad": players_with_gamepad,
                "players_secured": players_secured,  # Has password OR gamepad (no double-counting)
                "challenges_completed_last_7_days": challenges_completed_last_7_days,
                "active_players_last_7_days": active_players_last_7_days,
                # Extra fields for future use
                "unique_completions": unique_completions,
                "total_observations": total_observations,
                "active_sessions": active_sessions,
                "top_players": top_players,
            }

    # =========================================================================
    # Settings & Invite Codes
    # =========================================================================

    def get_setting(self, key: str, default: str = "") -> str:
        """Get a node setting value."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT value FROM node_settings WHERE key = ?",
                (key,)
            )
            row = cursor.fetchone()
            return row["value"] if row else default

    def set_setting(self, key: str, value: str) -> bool:
        """Set a node setting value."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO node_settings (key, value, updated_at)
                   VALUES (?, ?, datetime('now'))
                   ON CONFLICT(key) DO UPDATE SET value = ?, updated_at = datetime('now')""",
                (key, value, value)
            )
            return True

    def get_registration_mode(self) -> str:
        """Get registration mode: 'open', 'invite_only', or 'closed'."""
        return self.get_setting("registration_mode", "open")

    def set_registration_mode(self, mode: str) -> bool:
        """Set registration mode."""
        if mode not in ("open", "invite_only", "closed"):
            raise ValueError(f"Invalid registration mode: {mode}")
        return self.set_setting("registration_mode", mode)

    def create_invite_code(
        self,
        created_by: str,
        max_uses: int = 1,
        expires_days: Optional[int] = None,
        note: str = ""
    ) -> str:
        """Create a new invite code."""
        code = secrets.token_urlsafe(8)  # Short, URL-safe code
        now = datetime.now()
        expires_at = None
        if expires_days:
            expires_at = (now + timedelta(days=expires_days)).isoformat()

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO invite_codes
                   (code, created_by, created_at, expires_at, max_uses, note)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (code, created_by, now.isoformat(), expires_at, max_uses, note)
            )
        return code

    def list_invite_codes(self, include_inactive: bool = False) -> list[dict]:
        """List all invite codes."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if include_inactive:
                cursor.execute(
                    "SELECT * FROM invite_codes ORDER BY created_at DESC"
                )
            else:
                cursor.execute(
                    """SELECT * FROM invite_codes
                       WHERE active = 1 AND (expires_at IS NULL OR expires_at > datetime('now'))
                       ORDER BY created_at DESC"""
                )
            return [
                {
                    "code": row["code"],
                    "created_by": row["created_by"],
                    "created_at": row["created_at"],
                    "expires_at": row["expires_at"],
                    "max_uses": row["max_uses"],
                    "uses": row["uses"],
                    "note": row["note"],
                    "active": bool(row["active"]),
                }
                for row in cursor.fetchall()
            ]

    def validate_invite_code(self, code: str) -> tuple[bool, str]:
        """
        Validate an invite code.
        Returns (is_valid, error_message).
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM invite_codes WHERE code = ?",
                (code,)
            )
            row = cursor.fetchone()

            if not row:
                return False, "Invalid invite code"
            if not row["active"]:
                return False, "Invite code has been deactivated"
            if row["expires_at"] and datetime.fromisoformat(row["expires_at"]) < datetime.now():
                return False, "Invite code has expired"
            if row["uses"] >= row["max_uses"]:
                return False, "Invite code has reached maximum uses"

            return True, ""

    def use_invite_code(self, code: str, player_id: str) -> bool:
        """Mark an invite code as used by a player."""
        valid, _ = self.validate_invite_code(code)
        if not valid:
            return False

        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Increment uses
            cursor.execute(
                "UPDATE invite_codes SET uses = uses + 1 WHERE code = ?",
                (code,)
            )
            # Record which code the player used
            cursor.execute(
                "UPDATE players SET invited_by_code = ? WHERE player_id = ?",
                (code, player_id)
            )
            return True

    def deactivate_invite_code(self, code: str) -> bool:
        """Deactivate an invite code."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE invite_codes SET active = 0 WHERE code = ?",
                (code,)
            )
            return cursor.rowcount > 0

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
        limit: int = 100,
        since: Optional[str] = None,
        challenge_id: Optional[str] = None
    ) -> list[dict]:
        """Load recent observations for a player.

        Args:
            player_id: Player to load observations for
            limit: Max observations to return
            since: Only return observations after this ISO timestamp
            challenge_id: Only return observations for this challenge
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            conditions = ["player_id = ?"]
            params: list = [player_id]

            if since:
                conditions.append("timestamp > ?")
                params.append(since)
            if challenge_id:
                conditions.append("challenge_id = ?")
                params.append(challenge_id)

            params.append(limit)

            cursor.execute(
                f"""SELECT * FROM director_observations
                   WHERE {' AND '.join(conditions)}
                   ORDER BY timestamp DESC
                   LIMIT ?""",
                params
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

    # =========================================================================
    # Lesson Access Tracking
    # =========================================================================

    def record_lesson_access(
        self,
        player_id: str,
        lesson_id: str,
        lesson_type: str = "challenge"
    ) -> str:
        """
        Record when a player accesses a lesson/challenge.
        Returns the access timestamp.
        """
        now = datetime.now().isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO lesson_access
                   (player_id, lesson_id, lesson_type, accessed_at)
                   VALUES (?, ?, ?, ?)""",
                (player_id, lesson_id, lesson_type, now)
            )
        return now

    def get_lesson_access(
        self,
        player_id: str,
        lesson_id: str,
        since: Optional[str] = None
    ) -> Optional[dict]:
        """
        Get the most recent access time for a lesson.
        If 'since' is provided, only returns access after that time.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if since:
                cursor.execute(
                    """SELECT * FROM lesson_access
                       WHERE player_id = ? AND lesson_id = ? AND accessed_at > ?
                       ORDER BY accessed_at DESC LIMIT 1""",
                    (player_id, lesson_id, since)
                )
            else:
                cursor.execute(
                    """SELECT * FROM lesson_access
                       WHERE player_id = ? AND lesson_id = ?
                       ORDER BY accessed_at DESC LIMIT 1""",
                    (player_id, lesson_id)
                )
            row = cursor.fetchone()
            if not row:
                return None
            return {
                "lesson_id": row["lesson_id"],
                "lesson_type": row["lesson_type"],
                "accessed_at": row["accessed_at"],
            }

    def get_all_lesson_access(
        self,
        player_id: str,
        since: Optional[str] = None
    ) -> list[dict]:
        """
        Get all lesson access records for a player.
        If 'since' is provided, only returns access after that time.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if since:
                cursor.execute(
                    """SELECT * FROM lesson_access
                       WHERE player_id = ? AND accessed_at > ?
                       ORDER BY accessed_at DESC""",
                    (player_id, since)
                )
            else:
                cursor.execute(
                    """SELECT * FROM lesson_access
                       WHERE player_id = ?
                       ORDER BY accessed_at DESC LIMIT 100""",
                    (player_id,)
                )
            return [
                {
                    "lesson_id": row["lesson_id"],
                    "lesson_type": row["lesson_type"],
                    "accessed_at": row["accessed_at"],
                }
                for row in cursor.fetchall()
            ]

    # =========================================================================
    # Speedrun Logging - Persistent run history for graphs and proof
    # =========================================================================

    def create_speedrun(
        self,
        run_id: str,
        player_id: str,
        item_ids: list[str],
        run_type: str = "interview_prep",
        notes: str = ""
    ) -> str:
        """
        Create a new speedrun and initialize splits for all items.
        Returns the run_id.
        """
        now = datetime.now().isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Create the run
            cursor.execute(
                """INSERT INTO speedrun_runs
                   (run_id, player_id, run_type, started_at, total_items, notes)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (run_id, player_id, run_type, now, len(item_ids), notes)
            )
            # Create splits for each item
            for i, item_id in enumerate(item_ids):
                cursor.execute(
                    """INSERT INTO speedrun_splits
                       (run_id, item_id, item_order, status)
                       VALUES (?, ?, ?, 'pending')""",
                    (run_id, item_id, i)
                )
        return run_id

    def update_speedrun_split(
        self,
        run_id: str,
        item_id: str,
        accessed_at: Optional[str] = None,
        completed_at: Optional[str] = None,
        solve_time_seconds: Optional[float] = None,
        attempts: Optional[int] = None,
        failures: Optional[int] = None,
        status: Optional[str] = None
    ):
        """Update a split within a run."""
        updates = []
        params = []
        if accessed_at is not None:
            updates.append("accessed_at = ?")
            params.append(accessed_at)
        if completed_at is not None:
            updates.append("completed_at = ?")
            params.append(completed_at)
        if solve_time_seconds is not None:
            updates.append("solve_time_seconds = ?")
            params.append(solve_time_seconds)
        if attempts is not None:
            updates.append("attempts = ?")
            params.append(attempts)
        if failures is not None:
            updates.append("failures = ?")
            params.append(failures)
        if status is not None:
            updates.append("status = ?")
            params.append(status)

        if not updates:
            return

        params.extend([run_id, item_id])
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"""UPDATE speedrun_splits
                   SET {', '.join(updates)}
                   WHERE run_id = ? AND item_id = ?""",
                params
            )

    def complete_speedrun(
        self,
        run_id: str,
        total_time_seconds: float,
        completed_items: int,
        total_attempts: int,
        total_failures: int,
        status: str = "completed"
    ):
        """Mark a speedrun as complete with final stats."""
        now = datetime.now().isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE speedrun_runs
                   SET ended_at = ?, total_time_seconds = ?,
                       completed_items = ?, total_attempts = ?,
                       total_failures = ?, status = ?
                   WHERE run_id = ?""",
                (now, total_time_seconds, completed_items,
                 total_attempts, total_failures, status, run_id)
            )

    def get_speedrun(self, run_id: str) -> Optional[dict]:
        """Get a speedrun by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM speedrun_runs WHERE run_id = ?",
                (run_id,)
            )
            row = cursor.fetchone()
            if not row:
                return None
            return dict(row)

    def get_speedrun_splits(self, run_id: str) -> list[dict]:
        """Get all splits for a run, ordered by item_order."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT * FROM speedrun_splits
                   WHERE run_id = ?
                   ORDER BY item_order""",
                (run_id,)
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_speedrun_history(
        self,
        player_id: str,
        run_type: str = "interview_prep",
        limit: int = 50
    ) -> list[dict]:
        """Get speedrun history for a player, most recent first."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT * FROM speedrun_runs
                   WHERE player_id = ? AND run_type = ?
                   ORDER BY started_at DESC
                   LIMIT ?""",
                (player_id, run_type, limit)
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_speedrun_stats(self, player_id: str, run_type: str = "interview_prep") -> dict:
        """Get aggregate stats for speedruns."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Total runs
            cursor.execute(
                """SELECT COUNT(*) as total,
                          COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed,
                          MIN(total_time_seconds) as best_time,
                          AVG(total_time_seconds) as avg_time
                   FROM speedrun_runs
                   WHERE player_id = ? AND run_type = ? AND status = 'completed'""",
                (player_id, run_type)
            )
            row = cursor.fetchone()
            return {
                "total_runs": row["total"] or 0,
                "completed_runs": row["completed"] or 0,
                "best_time": row["best_time"],
                "avg_time": row["avg_time"],
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
