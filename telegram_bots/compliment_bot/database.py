import sqlite3
from datetime import datetime
from config import DB_NAME


def get_connection():
    return sqlite3.connect(DB_NAME)


def create_table():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS compliments (
                user_id INTEGER,
                compliment TEXT,
                date DATETIME
            )
        """)


def save_compliment(user_id, text):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO compliments VALUES (?, ?, ?)",
            (user_id, text, datetime.now())
        )


def get_history(user_id):
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT compliment FROM compliments WHERE user_id = ?",
            (user_id,)
        )
        return [row[0] for row in cursor.fetchall()]
