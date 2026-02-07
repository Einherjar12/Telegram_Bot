import sqlite3
from config import DB_NAME


def get_connection():
    return sqlite3.connect(DB_NAME)


def create_table():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS random_stats (
                user_id INTEGER PRIMARY KEY,
                coins_flipped INTEGER DEFAULT 0,
                numbers_generated INTEGER DEFAULT 0
            )
        """)


def inc_coin(user_id):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO random_stats (user_id, coins_flipped)
            VALUES (?, 1)
            ON CONFLICT(user_id)
            DO UPDATE SET coins_flipped = coins_flipped + 1
        """, (user_id,))


def inc_number(user_id):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO random_stats (user_id, numbers_generated)
            VALUES (?, 1)
            ON CONFLICT(user_id)
            DO UPDATE SET numbers_generated = numbers_generated + 1
        """, (user_id,))
