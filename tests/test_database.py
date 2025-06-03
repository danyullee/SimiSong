import pytest
import sqlite3
import os
from backend.database import MusicDatabase

# Fixture to create a fresh database for each test
@pytest.fixture
def test_db():
    # Use in-memory database for testing
    db = MusicDatabase(":memory:")
    yield db
    # Cleanup (not strictly needed for in-memory DB)

def test_database_initialization(test_db):
    """Test if tables are created properly"""
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    
    # Check if tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    assert 'songs' in tables
    assert 'user_ratings' in tables
    assert 'user_preferences' in tables
    conn.close()

def test_seed_sample_data(test_db):
    """Test if sample data is seeded correctly"""
    songs = test_db.get_all_songs()
    assert len(songs) > 0  # Should have seeded data
    
    # Check specific sample song exists
    sample_song = songs[songs['title'] == 'Bohemian Rhapsody'].iloc[0]
    assert sample_song['artist'] == 'Queen'
    assert sample_song['genre'] == 'Rock'

def test_add_and_get_ratings(test_db):
    """Test rating functionality"""
    test_db.add_rating("test_user", 1, 5)
    ratings = test_db.get_user_ratings("test_user")
    
    assert len(ratings) == 1
    assert ratings.iloc[0]['song_id'] == 1
    assert ratings.iloc[0]['rating'] == 5