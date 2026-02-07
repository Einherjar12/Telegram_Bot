import sqlite3
from config import DB_NAME


def get_connection():
    return sqlite3.connect(DB_NAME)


def create_table():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS counters (
                user_id INTEGER PRIMARY KEY,
                count INTEGER DEFAULT 0
            )
        """)


def get_count(user_id):
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT count FROM counters WHERE user_id = ?",
            (user_id,)
        )
        row = cursor.fetchone()
        return row[0] if row else 0


def increment_count(user_id):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO counters (user_id, count)
            VALUES (?, 1)
            ON CONFLICT(user_id)
            DO UPDATE SET count = count + 1
        """, (user_id,))


def reset_count(user_id):
    with get_connection() as conn:
        conn.execute(
            "UPDATE counters SET count = 0 WHERE user_id = ?",
            (user_id,)
        )
