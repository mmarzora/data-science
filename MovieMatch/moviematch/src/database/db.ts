import Database from 'better-sqlite3';
import path from 'path';

// Initialize database
const db = new Database(path.join(__dirname, 'movies.db'));

// Enable WAL mode for better performance
db.pragma('journal_mode = WAL');

// Create movies table
db.exec(`
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

  -- Index for faster searches
  CREATE INDEX IF NOT EXISTS idx_movies_title ON movies(title);
  CREATE INDEX IF NOT EXISTS idx_movies_release_year ON movies(release_year);
`);

export default db; 