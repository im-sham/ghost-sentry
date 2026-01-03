import pytest
import sqlite3
import json
from ghost_sentry.core import db
from ghost_sentry.core.tasks import TaskState

@pytest.fixture
def clean_db(monkeypatch, tmp_path):
    """Fixture to provide a clean temporary database for each test."""
    db_file = tmp_path / "test_ghost_sentry.db"
    monkeypatch.setattr(db, "DB_PATH", db_file)
    db.init_db()
    return db_file

def test_add_and_get_tasks(clean_db):
    """Test that tasks can be added and retrieved."""
    db.add_task("task-1", "entity-1", "VERIFICATION", {"info": "test"}, "drone-alpha")
    
    tasks = db.get_tasks()
    assert len(tasks) == 1
    assert tasks[0]["id"] == "task-1"
    assert tasks[0]["state"] == "pending"
    assert tasks[0]["assigned_to"] == "drone-alpha"

def test_task_state_update(clean_db):
    """Test updating task states."""
    db.add_task("task-1", "entity-1", "VERIFICATION")
    
    db.update_task_state("task-1", "in_progress")
    tasks = db.get_tasks(state="in_progress")
    assert len(tasks) == 1
    assert tasks[0]["state"] == "in_progress"
    
    db.update_task_state("task-1", "completed")
    tasks = db.get_tasks(state="completed")
    assert len(tasks) == 1
    assert tasks[0]["state"] == "completed"

def test_get_tasks_filtering(clean_db):
    """Test task filtering by state."""
    db.add_task("task-1", "entity-1", "VERIFICATION")
    db.add_task("task-2", "entity-2", "VERIFICATION")
    db.update_task_state("task-2", "completed")
    
    pending = db.get_tasks(state="pending")
    completed = db.get_tasks(state="completed")
    
    assert len(pending) == 1
    assert pending[0]["id"] == "task-1"
    assert len(completed) == 1
    assert completed[0]["id"] == "task-2"

def test_track_history_retrieval(clean_db):
    """Test track history retrieval (audit recommendation)."""
    entity_id = "test-entity"
    for i in range(5):
        db.add_event("track", {"lat": 33.0 + i}, entity_id=entity_id)
        
    history = db.get_track_history(entity_id, limit=3)
    assert len(history) == 3
    assert history[0]["data"]["lat"] == 37.0 # Latest first
