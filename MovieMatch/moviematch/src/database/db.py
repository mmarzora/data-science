import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / 'movies.db'

def init_db():
    """Initialize the database with the required schema."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute('PRAGMA journal_mode = WAL')
    
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            release_year INTEGER,
            poster_url TEXT,
            genres TEXT,  -- Stored as JSON array
            runtime_minutes INTEGER,
            rating REAL,  -- e.g., IMDB rating
            embedding BLOB,  -- Store as binary
            watchmode_id TEXT,  -- to track source API ID
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_movies_title ON movies(title);
        CREATE INDEX IF NOT EXISTS idx_movies_release_year ON movies(release_year);
    ''')
    
    conn.commit()
    conn.close()

def get_db():
    """Get a database connection with row factory enabled."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

# Initialize the database when this module is imported
init_db() 