import sqlite3
from pathlib import Path

# Get the absolute path to the database file
DB_PATH = Path(__file__).parent / 'movies.db'

def get_db():
    """Get a database connection."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn 