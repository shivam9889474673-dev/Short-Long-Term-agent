from contextlib import closing
import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent.parent / "soul.db"


def initialize_database():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    memory_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)


def save_memory(user_id, memory_type, content):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        with conn:
            conn.execute(
                """
                INSERT INTO memories (user_id, memory_type, content)
                VALUES (?, ?, ?)
                """,
                (user_id, memory_type, content),
            )


def get_memories(user_id):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT id, memory_type, content, created_at
            FROM memories
            WHERE user_id = ?
            ORDER BY id DESC
            """,
            (user_id,),
        ).fetchall()

    return [dict(row) for row in rows]


def delete_memory(memory_id, user_id):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        with conn:
            cursor = conn.execute(
                "DELETE FROM memories WHERE id = ? AND user_id = ?",
                (memory_id, user_id),
            )
            return cursor.rowcount > 0