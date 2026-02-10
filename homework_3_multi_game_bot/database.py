import sqlite3
from config import NAME_DB


def init_db():
    with sqlite3.connect(NAME_DB) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                range_start INTEGER,
                range_end INTEGER,
                amount INTEGER
            )
        """)
        conn.commit()


def save_value(user_id, field, value):
    with sqlite3.connect(NAME_DB) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO users (user_id) VALUES (?)",
            (user_id,)
        )
        cursor.execute(
            f"UPDATE users SET {field} = ? WHERE user_id = ?",
            (value, user_id)
        )
        conn.commit()


def get_user_data(user_id):
    with sqlite3.connect(NAME_DB) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT range_start, range_end, amount
            FROM users
            WHERE user_id = ?
        """, (user_id,))
        return cursor.fetchone()
