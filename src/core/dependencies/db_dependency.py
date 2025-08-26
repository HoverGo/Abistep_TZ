# src/core/dependencies/db_dependency.py
import sqlite3
from contextlib import contextmanager

from src.core.config import settings


class DBManager:
    def __init__(self, db_url: str = settings.DB_URL):
        self.db_url = db_url
        self.init_db()

    @contextmanager
    def get_conn(self):
        conn = sqlite3.connect(self.db_url)
        try:
            yield conn
        finally:
            conn.close()

    def init_db(self):
        with self.get_conn() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    balance REAL NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transfers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    from_user_id INTEGER NOT NULL,
                    to_user_id INTEGER NOT NULL,
                    amount REAL NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (from_user_id) REFERENCES users (id),
                    FOREIGN KEY (to_user_id) REFERENCES users (id)
                )
            ''')
            
            conn.commit()

db_manager = DBManager(settings.DB_URL)