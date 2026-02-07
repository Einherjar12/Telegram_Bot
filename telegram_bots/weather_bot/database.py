import sqlite3
from config import DB_NAME


class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # Таблица для избранного города
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather_prefs (
            user_id INTEGER PRIMARY KEY,
            favourite_city TEXT
        )
        """)

        # Таблица для истории запросов
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            city TEXT NOT NULL,
            weather TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        self.conn.commit()

    # Избранный город
    def set_favourite_city(self, user_id, city):
        self.cursor.execute("""
        INSERT OR REPLACE INTO weather_prefs (user_id, favourite_city)
        VALUES (?, ?)
        """, (user_id, city))
        self.conn.commit()

    def get_favourite_city(self, user_id):
        self.cursor.execute("""
        SELECT favourite_city FROM weather_prefs WHERE user_id = ?
        """, (user_id,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    # История запросов
    def save_history(self, user_id, city, weather):
        self.cursor.execute("""
        INSERT INTO weather_history (user_id, city, weather)
        VALUES (?, ?, ?)
        """, (user_id, city, weather))
        self.conn.commit()

    def get_history(self, user_id, limit=5):
        self.cursor.execute("""
        SELECT city, weather, timestamp
        FROM weather_history
        WHERE user_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
        """, (user_id, limit))
        return self.cursor.fetchall()
