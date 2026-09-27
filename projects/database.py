import sqlite3

from config import DATABASE_PATH


# =========================================================
# SHAHEBAZ MOTORS - DATABASE CONNECTION
# database.py (UPDATED - FULL)
# =========================================================


def get_db():
    """
    Create and return a SQLite database connection.

    Features:
    - Row factory set to sqlite3.Row so rows behave
      like dictionaries (easy conversion to JSON).
    - Foreign key constraints enabled.
    - Check same thread disabled (Flask dev friendly).
    """

    db = sqlite3.connect(
        DATABASE_PATH,
        check_same_thread=False
    )

    db.row_factory = sqlite3.Row

    # Enable foreign key support
    db.execute("PRAGMA foreign_keys = ON")

    return db


# =========================================================
# DATABASE TEST
# =========================================================

def test_connection():
    """
    Test whether the database is reachable.
    Returns True if connection works, False otherwise.
    """

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

        print(
            "Database connection failed:",
            error
        )

        return False