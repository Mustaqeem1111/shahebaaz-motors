import sqlite3
import os
import logging
from datetime import datetime

from config import DATABASE_PATH


# =========================================================
# SHAHEBAZ MOTORS - DATABASE CONNECTION
# database.py (UPDATED - DEFAULT PASSWORD)
# =========================================================

logger = logging.getLogger(__name__)


def get_db():
    """Create and return a SQLite database connection."""

    db = sqlite3.connect(
        DATABASE_PATH,
        check_same_thread=False,
        timeout=30.0
    )

    db.row_factory = sqlite3.Row

    # ---------- PERFORMANCE & CONCURRENCY ----------
    db.execute("PRAGMA foreign_keys = ON")
    db.execute("PRAGMA journal_mode = WAL")
    db.execute("PRAGMA synchronous = NORMAL")
    db.execute("PRAGMA cache_size = -64000")
    db.execute("PRAGMA temp_store = MEMORY")
    db.execute("PRAGMA busy_timeout = 30000")
    db.execute("PRAGMA mmap_size = 268435456")

    return db


# =========================================================
# DATABASE TEST
# =========================================================

def test_connection():
    """Test whether the database is reachable."""

    try:
        db = get_db()

        try:
            cursor = db.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            return result is not None
        finally:
            db.close()

    except Exception as error:
        logger.error(f"Database connection failed: {error}")
        return False


# =========================================================
# ADMIN USERS TABLE
# =========================================================

def init_admin_users_table():
    """
    Create admin_users table if not exists.
    Also creates a default admin user if table is empty.

    NOTE: Default password sirf pehli baar admin banane ke liye.
    Baad mein Forgot Password se change hota hai.
    """

    from werkzeug.security import generate_password_hash

    db = get_db()

    try:
        cursor = db.cursor()

        # Create table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_users (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                username TEXT UNIQUE NOT NULL,

                email TEXT UNIQUE NOT NULL,

                password_hash TEXT NOT NULL,

                reset_token TEXT,

                reset_token_expiry TEXT,

                created_at TEXT NOT NULL,

                updated_at TEXT NOT NULL

            )
        """)

        # Check if default admin exists
        cursor.execute(
            "SELECT COUNT(*) FROM admin_users WHERE username = ?",
            ("adminn",)
        )

        count = cursor.fetchone()[0]

        if count == 0:
            # Default password — sirf pehli baar
            default_password = "Shahebaz@Motors2026!"

            admin_email = os.getenv(
                "SHAHEBAZ_ADMIN_EMAIL",
                "mahalatbademustaqeem@gmail.com"
            )

            now = datetime.now().isoformat(timespec="seconds")

            cursor.execute("""
                INSERT INTO admin_users (
                    username,
                    email,
                    password_hash,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                "adminn",
                admin_email,
                generate_password_hash(default_password),
                now,
                now
            ))

            logger.info(f"Default admin user created: {admin_email}")

        db.commit()

    except Exception as error:
        logger.error(f"Failed to init admin_users table: {error}")

    finally:
        db.close()


# =========================================================
# DATABASE MAINTENANCE
# =========================================================

def optimize_database():
    """Run periodic maintenance on the database."""

    try:
        db = get_db()

        try:
            db.execute("VACUUM")
            db.execute("ANALYZE")
            db.commit()

            logger.info("Database optimization completed")
            return True

        finally:
            db.close()

    except Exception as error:
        logger.error(f"Database optimization failed: {error}")
        return False