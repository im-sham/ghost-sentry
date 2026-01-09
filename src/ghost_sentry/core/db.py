"""SQLite database module for Ghost Sentry."""
import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

DB_PATH = Path("ghost_sentry.db")

def init_db():
    """Initialize the database with the required schema."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        # Events Table (unified log)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,  -- 'track' or 'task'
            entity_id TEXT,
            data TEXT,           -- JSON blob
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        # Tasks Table (state machine)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            entity_id TEXT,
            type TEXT,
            state TEXT DEFAULT 'pending',
            assigned_to TEXT,
            data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        # Missions Table (persistence)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS missions (
            id TEXT PRIMARY KEY,
            name TEXT,
            geometries TEXT,  -- JSON blob
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        # Indexes for fast queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_type ON events(type);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_created ON events(created_at);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_state ON tasks(state);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_entity ON tasks(entity_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_missions_created ON missions(created_at);")
        conn.commit()

def add_event(event_type: str, data: dict, entity_id: Optional[str] = None):
    """Add an event to the database."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO events (type, entity_id, data) VALUES (?, ?, ?)",
            (event_type, entity_id, json.dumps(data))
        )
        conn.commit()

def get_tracks():
    """Retrieve all tracks from the database."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT data FROM events WHERE type = 'track' ORDER BY created_at DESC")
        rows = cursor.fetchall()
        return [json.loads(row[0]) for row in rows]

def add_task(task_id: str, entity_id: str, task_type: str, data: Optional[dict] = None, assigned_to: Optional[str] = None):
    """Add a task to the database."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (id, entity_id, type, data, assigned_to) VALUES (?, ?, ?, ?, ?)",
            (task_id, entity_id, task_type, json.dumps(data) if data else None, assigned_to)
        )
        conn.commit()

def update_task_state(task_id: str, state: str):
    """Update the state of a task."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE tasks SET state = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (state, task_id)
        )
        conn.commit()

def get_tasks(state: Optional[str] = None):
    """Retrieve tasks, optionally filtered by state."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        if state:
            cursor.execute("SELECT * FROM tasks WHERE state = ? ORDER BY created_at DESC", (state,))
        else:
            cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC")
        rows = cursor.fetchall()
        return [
            {
                "id": row[0],
                "entity_id": row[1],
                "type": row[2],
                "state": row[3],
                "assigned_to": row[4],
                "data": json.loads(row[5]) if row[5] else None,
                "created_at": row[6],
                "updated_at": row[7]
            }
            for row in rows
        ]

def add_mission(mission_id: str, name: str, geometries: list):
    """Add a mission configuration to the database."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO missions (id, name, geometries) VALUES (?, ?, ?)",
            (mission_id, name, json.dumps(geometries))
        )
        conn.commit()

def get_missions():
    """Retrieve all mission configurations."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, geometries, created_at FROM missions ORDER BY created_at DESC")
        rows = cursor.fetchall()
        return [
            {
                "id": row[0],
                "name": row[1],
                "geometries": json.loads(row[2]),
                "created_at": row[3]
            }
            for row in rows
        ]

def get_track_history(entity_id: str, limit: int = 10) -> list[dict]:
    """Retrieve historical positions for an entity (Audit Recommendation)."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT data, created_at FROM events WHERE entity_id = ? AND type = 'track' ORDER BY created_at DESC, id DESC LIMIT ?",
            (entity_id, limit)
        )
        return [{"data": json.loads(r[0]), "created_at": r[1]} for r in cursor.fetchall()]

def get_latest_events(limit: int = 50):
    """Retrieve the latest events."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM events ORDER BY created_at DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        return [
            {"id": row[0], "type": row[1], "entity_id": row[2], "data": json.loads(row[3]), "created_at": row[4]}
            for row in rows
        ]

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
