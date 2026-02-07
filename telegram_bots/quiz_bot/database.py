import sqlite3
from config import DB_NAME

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS quiz_results (
            user_id INTEGER PRIMARY KEY,
            correct_answers INTEGER DEFAULT 0,
            total_questions INTEGER DEFAULT 0
        )
        """)
        self.conn.commit()

    def add_user_if_not_exists(self, user_id):
        self.cursor.execute("""
        INSERT OR IGNORE INTO quiz_results (user_id) VALUES (?)
        """, (user_id,))
        self.conn.commit()

    def update_result(self, user_id, correct_increment=0, total_increment=1):
        self.cursor.execute("""
        UPDATE quiz_results
        SET correct_answers = correct_answers + ?,
            total_questions = total_questions + ?
        WHERE user_id = ?
        """, (correct_increment, total_increment, user_id))
        self.conn.commit()

    def get_result(self, user_id):
        self.cursor.execute("""
        SELECT correct_answers, total_questions
        FROM quiz_results
        WHERE user_id = ?
        """, (user_id,))
        result = self.cursor.fetchone()
        return result if result else (0, 0)
