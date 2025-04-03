import sqlite3
from app.infrastructure.db.database_interface import DatabaseInterface


class SQLite(DatabaseInterface):
    def __init__(self):
        self.connection = sqlite3.connect("chatbot.db")
        self.cursor = self.connection.cursor()

    def get_data(self, table_name: str):
        self.cursor.execute(f"SELECT * FROM {table_name}")
        rows = self.cursor.fetchall()
        return [{"table_name": table_name, "data": row} for row in rows]
