import sqlite3
import pandas as pd

class MusicDatabase:
    """Handles all database operations for the music recommendation system"""
    
    def __init__(self, db_path="music_recommendations.db"):
        self.db_path = db_path
        self.init_database()
        self.seed_sample_data()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Songs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS songs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                artist TEXT NOT NULL,
                genre TEXT NOT NULL,
                year INTEGER,
                duration INTEGER,
                energy REAL,
                danceability REAL,
                valence REAL,
                acousticness REAL,
                popularity INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # User ratings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                song_id INTEGER,
                rating INTEGER CHECK(rating >= 1 AND rating <= 5),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (song_id) REFERENCES songs (id)
            )
        ''')
        
        # User preferences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                user_id TEXT PRIMARY KEY,
                preferred_genres TEXT,
                preferred_years TEXT,
                energy_preference REAL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def seed_sample_data(self):
        """Add sample music data if database is empty"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM songs")
        if cursor.fetchone()[0] > 0:
            conn.close()
            return
        
        # Sample songs with audio features
        sample_songs = [
            ("Bohemian Rhapsody", "Queen", "Rock", 1975, 355, 0.8, 0.3, 0.7, 0.1, 95),
            ("Billie Jean", "Michael Jackson", "Pop", 1983, 294, 0.7, 0.8, 0.6, 0.0, 90),
            ("Hotel California", "Eagles", "Rock", 1976, 391, 0.6, 0.4, 0.5, 0.2, 88),
            ("Dancing Queen", "ABBA", "Pop", 1976, 231, 0.9, 0.9, 0.8, 0.1, 85),
            ("Stairway to Heaven", "Led Zeppelin", "Rock", 1971, 482, 0.7, 0.3, 0.6, 0.3, 92),
            ("I Want It That Way", "Backstreet Boys", "Pop", 1999, 213, 0.6, 0.7, 0.8, 0.0, 80),
            ("Smells Like Teen Spirit", "Nirvana", "Grunge", 1991, 301, 0.9, 0.5, 0.4, 0.0, 87),
            ("Sweet Child O' Mine", "Guns N' Roses", "Rock", 1987, 356, 0.8, 0.6, 0.7, 0.0, 89),
            ("Like a Prayer", "Madonna", "Pop", 1989, 340, 0.7, 0.8, 0.7, 0.1, 83),
            ("Wonderwall", "Oasis", "Britpop", 1995, 259, 0.6, 0.5, 0.6, 0.6, 84),
            ("Shape of You", "Ed Sheeran", "Pop", 2017, 234, 0.8, 0.8, 0.9, 0.6, 95),
            ("Blinding Lights", "The Weeknd", "Synthpop", 2019, 200, 0.8, 0.9, 0.3, 0.0, 98),
            ("Bad Guy", "Billie Eilish", "Alternative", 2019, 194, 0.4, 0.7, 0.4, 0.6, 96),
            ("Uptown Funk", "Bruno Mars", "Funk", 2014, 270, 0.9, 0.9, 0.9, 0.0, 93),
            ("Rolling in the Deep", "Adele", "Soul", 2010, 228, 0.8, 0.7, 0.2, 0.3, 91),
            ("Somebody That I Used to Know", "Gotye", "Indie Pop", 2011, 244, 0.6, 0.6, 0.3, 0.8, 86),
            ("Radioactive", "Imagine Dragons", "Alternative Rock", 2012, 187, 0.8, 0.6, 0.5, 0.0, 89),
            ("Happy", "Pharrell Williams", "Pop", 2013, 232, 0.8, 0.9, 0.96, 0.1, 90),
            ("Get Lucky", "Daft Punk", "Electronic", 2013, 248, 0.7, 0.8, 0.9, 0.0, 88),
            ("Can't Stop the Feeling", "Justin Timberlake", "Pop", 2016, 236, 0.9, 0.9, 0.9, 0.1, 87)
        ]
        
        cursor.executemany('''
            INSERT INTO songs (title, artist, genre, year, duration, energy, 
                             danceability, valence, acousticness, popularity)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_songs)
        
        conn.commit()
        conn.close()
    
    def get_all_songs(self) -> pd.DataFrame:
        """Retrieve all songs as a DataFrame"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM songs", conn)
        conn.close()
        return df
    
    def add_rating(self, user_id: str, song_id: int, rating: int):
        """Add or update a user rating for a song"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO user_ratings (user_id, song_id, rating)
            VALUES (?, ?, ?)
        ''', (user_id, song_id, rating))
        
        conn.commit()
        conn.close()
    
    def get_user_ratings(self, user_id: str) -> pd.DataFrame:
        """Get all ratings for a specific user"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query('''
            SELECT ur.*, s.title, s.artist, s.genre 
            FROM user_ratings ur
            JOIN songs s ON ur.song_id = s.id
            WHERE ur.user_id = ?
        ''', conn, params=(user_id,))
        conn.close()
        return df