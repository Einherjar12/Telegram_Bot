import sqlite3
from config import DB_NAME

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.fill_data()

    def create_tables(self):
        # Таблица тренеров
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS coaches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            info TEXT
        )
        """)

        # Таблица групповых занятий
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            info TEXT
        )
        """)

        # Таблица расписания
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day TEXT,
            lesson TEXT
        )
        """)
        self.conn.commit()

    def fill_data(self):
        # Тренеры
        self.cursor.execute("SELECT COUNT(*) FROM coaches")
        if self.cursor.fetchone()[0] == 0:
            self.cursor.executemany(
                "INSERT INTO coaches (name, info) VALUES (?, ?)",
                [
                    ("Иванов", "Силовой тренер 💪 Опыт 5 лет"),
                    ("Петров", "Фитнес и кардио 🏃"),
                    ("Смирнова", "Йога и растяжка 🧘‍♀️")
                ]
            )

        # Групповые занятия
        self.cursor.execute("SELECT COUNT(*) FROM groups")
        if self.cursor.fetchone()[0] == 0:
            self.cursor.executemany(
                "INSERT INTO groups (name, info) VALUES (?, ?)",
                [
                    ("Йога", "Спокойная тренировка для тела и души"),
                    ("Пилатес", "Укрепление мышц корпуса"),
                    ("CrossFit", "Интенсивные тренировки 💥")
                ]
            )

        # Расписание
        self.cursor.execute("SELECT COUNT(*) FROM schedule")
        if self.cursor.fetchone()[0] == 0:
            self.cursor.executemany(
                "INSERT INTO schedule (day, lesson) VALUES (?, ?)",
                [
                    ("today", "Йога — 10:00"),
                    ("today", "CrossFit — 18:00"),
                    ("week", "Пилатес — Пн, Ср 17:00"),
                    ("week", "Йога — Вт, Чт 10:00")
                ]
            )
        self.conn.commit()

    # Методы для бота
    def get_coaches(self):
        self.cursor.execute("SELECT name, info FROM coaches")
        return dict(self.cursor.fetchall())  # возвращаем словарь {имя: инфо}

    def get_groups(self):
        self.cursor.execute("SELECT name, info FROM groups")
        return dict(self.cursor.fetchall())

    def get_schedule(self, day):
        self.cursor.execute("SELECT lesson FROM schedule WHERE day=?", (day,))
        return [row[0] for row in self.cursor.fetchall()]

