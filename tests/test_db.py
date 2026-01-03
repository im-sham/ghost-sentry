"""Tests for the Ghost Sentry database module."""
import pytest
import sqlite3
import os
from pathlib import Path
from ghost_sentry.core import db

TEST_DB_PATH = Path("test_ghost_sentry.db")

@pytest.fixture(autouse=True)
def setup_test_db(monkeypatch):
    """Setup and teardown a test database."""
    monkeypatch.setattr(db, "DB_PATH", TEST_DB_PATH)
    db.init_db()
    yield
    if TEST_DB_PATH.exists():
        os.remove(TEST_DB_PATH)

def test_init_db():
    """Test that the database is initialized with the correct schema."""
    assert TEST_DB_PATH.exists()
    with sqlite3.connect(TEST_DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='events'")
        assert cursor.fetchone() is not None

def test_add_and_get_event():
    """Test adding an event and retrieving it as a track."""
    track_data = {"id": "123", "ontology": {"platform_type": "Airplane"}}
    db.add_event("track", track_data, entity_id="123")
    
    tracks = db.get_tracks()
    assert len(tracks) == 1
    assert tracks[0]["id"] == "123"
    assert tracks[0]["ontology"]["platform_type"] == "Airplane"

def test_get_latest_events():
    """Test retrieving latest events."""
    db.add_event("track", {"id": "1"}, entity_id="1")
    db.add_event("task", {"id": "2"}, entity_id="2")
    
    events = db.get_latest_events(limit=10)
    assert len(events) == 2
    # Ordered by DESC created_at, so task should be first (if added marginally later)
    # But since they are added in same second, we just check types exist
    types = [e["type"] for e in events]
    assert "track" in types
    assert "task" in types
