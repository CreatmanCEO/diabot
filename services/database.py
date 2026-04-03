"""Async SQLite database service."""

import json
import aiosqlite
from datetime import datetime, timezone

from models.schemas import User


class Database:
    """Async SQLite database manager."""

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self._db: aiosqlite.Connection | None = None

    async def init(self) -> None:
        """Initialize database connection and create tables."""
        self._db = await aiosqlite.connect(self.db_path)
        self._db.row_factory = aiosqlite.Row
        await self._create_tables()

    async def close(self) -> None:
        """Close database connection."""
        if self._db:
            await self._db.close()

    async def _create_tables(self) -> None:
        """Create all tables if they don't exist."""
        await self._db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                timezone TEXT DEFAULT 'Europe/Moscow',
                he_grams INTEGER DEFAULT 12,
                language TEXT DEFAULT 'ru',
                is_active BOOLEAN DEFAULT 1,
                onboarding_completed BOOLEAN DEFAULT 0,
                consent_given_at TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS meals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(user_id),
                timestamp TEXT NOT NULL DEFAULT (datetime('now')),
                date TEXT NOT NULL,
                items_json TEXT NOT NULL,
                totals_json TEXT NOT NULL,
                photo_file_id TEXT,
                original_text TEXT,
                timezone TEXT DEFAULT 'Europe/Moscow'
            );

            CREATE INDEX IF NOT EXISTS idx_meals_user_date ON meals(user_id, date);

            CREATE TABLE IF NOT EXISTS glucose_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(user_id),
                value REAL NOT NULL,
                reading_type TEXT,
                timestamp TEXT NOT NULL DEFAULT (datetime('now')),
                date TEXT NOT NULL,
                note TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_glucose_user_date ON glucose_readings(user_id, date);

            CREATE TABLE IF NOT EXISTS allowed_users (
                user_id INTEGER PRIMARY KEY,
                added_by INTEGER NOT NULL,
                added_at TEXT DEFAULT (datetime('now'))
            );
        """)
        await self._db.commit()

    # --- Users ---

    async def create_user(self, user_id: int, username: str | None = None) -> None:
        """Create a new user record."""
        await self._db.execute(
            "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
            (user_id, username),
        )
        await self._db.commit()

    async def get_user(self, user_id: int) -> User | None:
        """Get user by Telegram user ID."""
        cursor = await self._db.execute(
            "SELECT * FROM users WHERE user_id = ?", (user_id,)
        )
        row = await cursor.fetchone()
        if row is None:
            return None
        return User(
            user_id=row["user_id"],
            username=row["username"],
            timezone=row["timezone"],
            he_grams=row["he_grams"],
            language=row["language"],
            is_active=bool(row["is_active"]),
            onboarding_completed=bool(row["onboarding_completed"]),
            consent_given_at=row["consent_given_at"],
            created_at=row["created_at"],
        )

    async def update_user(self, user_id: int, **kwargs) -> None:
        """Update user fields. Pass field=value pairs."""
        if not kwargs:
            return
        set_clause = ", ".join(f"{k} = ?" for k in kwargs)
        values = list(kwargs.values()) + [user_id]
        await self._db.execute(
            f"UPDATE users SET {set_clause} WHERE user_id = ?", values
        )
        await self._db.commit()

    async def complete_onboarding(self, user_id: int) -> None:
        """Mark user onboarding as completed with consent timestamp."""
        now = datetime.now(timezone.utc).isoformat()
        await self._db.execute(
            "UPDATE users SET onboarding_completed = 1, consent_given_at = ? WHERE user_id = ?",
            (now, user_id),
        )
        await self._db.commit()

    # --- Meals ---

    async def save_meal(
        self,
        user_id: int,
        date: str,
        items_json: str,
        totals_json: str,
        photo_file_id: str | None = None,
        original_text: str | None = None,
        timezone: str = "Europe/Moscow",
    ) -> int:
        """Save a meal record. Returns the meal ID."""
        cursor = await self._db.execute(
            """INSERT INTO meals (user_id, date, items_json, totals_json, photo_file_id, original_text, timezone)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (user_id, date, items_json, totals_json, photo_file_id, original_text, timezone),
        )
        await self._db.commit()
        return cursor.lastrowid

    async def get_meals_by_date(self, user_id: int, date: str) -> list[dict]:
        """Get all meals for a user on a specific date."""
        cursor = await self._db.execute(
            "SELECT * FROM meals WHERE user_id = ? AND date = ? ORDER BY timestamp",
            (user_id, date),
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

    async def get_meals_week(self, user_id: int, dates: list[str]) -> list[dict]:
        """Get meals for a user across multiple dates."""
        placeholders = ",".join("?" for _ in dates)
        cursor = await self._db.execute(
            f"SELECT * FROM meals WHERE user_id = ? AND date IN ({placeholders}) ORDER BY date, timestamp",
            [user_id] + dates,
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

    async def get_meals_history(self, user_id: int, limit: int = 5) -> list[dict]:
        """Get the last N meals for a user."""
        cursor = await self._db.execute(
            "SELECT * FROM meals WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
            (user_id, limit),
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

    async def delete_last_meal(self, user_id: int) -> bool:
        """Delete the most recent meal. Returns True if a meal was deleted."""
        cursor = await self._db.execute(
            "SELECT id FROM meals WHERE user_id = ? ORDER BY timestamp DESC LIMIT 1",
            (user_id,),
        )
        row = await cursor.fetchone()
        if row is None:
            return False
        await self._db.execute("DELETE FROM meals WHERE id = ?", (row["id"],))
        await self._db.commit()
        return True

    # --- Glucose ---

    async def save_glucose(
        self,
        user_id: int,
        value: float,
        date: str,
        reading_type: str | None = None,
        note: str | None = None,
    ) -> int:
        """Save a glucose reading. Returns the reading ID."""
        cursor = await self._db.execute(
            """INSERT INTO glucose_readings (user_id, value, date, reading_type, note)
               VALUES (?, ?, ?, ?, ?)""",
            (user_id, value, date, reading_type, note),
        )
        await self._db.commit()
        return cursor.lastrowid

    async def get_glucose_by_date(self, user_id: int, date: str) -> list[dict]:
        """Get glucose readings for a user on a specific date."""
        cursor = await self._db.execute(
            "SELECT * FROM glucose_readings WHERE user_id = ? AND date = ? ORDER BY timestamp",
            (user_id, date),
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

    # --- Allowed Users ---

    async def add_allowed_user(self, user_id: int, added_by: int) -> None:
        """Add a user to the allowed list."""
        await self._db.execute(
            "INSERT OR IGNORE INTO allowed_users (user_id, added_by) VALUES (?, ?)",
            (user_id, added_by),
        )
        await self._db.commit()

    async def remove_allowed_user(self, user_id: int) -> None:
        """Remove a user from the allowed list."""
        await self._db.execute("DELETE FROM allowed_users WHERE user_id = ?", (user_id,))
        await self._db.commit()

    async def is_user_allowed(self, user_id: int) -> bool:
        """Check if a user is in the allowed list."""
        cursor = await self._db.execute(
            "SELECT 1 FROM allowed_users WHERE user_id = ?", (user_id,)
        )
        return await cursor.fetchone() is not None

    async def get_allowed_users(self) -> list[dict]:
        """Get all allowed users."""
        cursor = await self._db.execute(
            "SELECT * FROM allowed_users ORDER BY added_at"
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

    # --- Data Management ---

    async def delete_all_user_data(self, user_id: int) -> None:
        """Delete all data for a user (GDPR compliance)."""
        await self._db.execute("DELETE FROM meals WHERE user_id = ?", (user_id,))
        await self._db.execute("DELETE FROM glucose_readings WHERE user_id = ?", (user_id,))
        await self._db.execute("DELETE FROM allowed_users WHERE user_id = ?", (user_id,))
        await self._db.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        await self._db.commit()

    async def export_user_data(self, user_id: int) -> dict:
        """Export all user data as a dictionary."""
        user = await self.get_user(user_id)
        meals = await self._db.execute(
            "SELECT * FROM meals WHERE user_id = ? ORDER BY timestamp", (user_id,)
        )
        meal_rows = await meals.fetchall()

        glucose = await self._db.execute(
            "SELECT * FROM glucose_readings WHERE user_id = ? ORDER BY timestamp", (user_id,)
        )
        glucose_rows = await glucose.fetchall()

        return {
            "user": {
                "user_id": user.user_id,
                "username": user.username,
                "timezone": user.timezone,
                "he_grams": user.he_grams,
                "language": user.language,
                "created_at": user.created_at,
            } if user else None,
            "meals": [dict(row) for row in meal_rows],
            "glucose_readings": [dict(row) for row in glucose_rows],
        }

    # --- Helpers ---

    async def execute_fetchall(self, query: str, params: tuple = ()) -> list:
        """Execute a query and return all rows as tuples."""
        cursor = await self._db.execute(query, params)
        return await cursor.fetchall()
