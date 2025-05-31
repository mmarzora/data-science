const Database = require('better-sqlite3');
const path = require('path');

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

// Test database connection and table creation
try {
    // Test query
    const result = db.prepare("SELECT name FROM sqlite_master WHERE type='table' AND name='movies'").get();
    console.log('Database initialized successfully');
    console.log('Movies table exists:', result ? true : false);

    // Test insert
    const testMovie = {
        title: 'Test Movie',
        description: 'Test Description',
        release_year: 2024,
        genres: JSON.stringify(['test']),
    };

    const insert = db.prepare(`
        INSERT INTO movies (title, description, release_year, genres)
        VALUES (@title, @description, @release_year, @genres)
    `);

    const info = insert.run(testMovie);
    console.log('Test insert successful:', info.changes === 1);

    // Cleanup test data
    db.prepare('DELETE FROM movies WHERE title = ?').run('Test Movie');
    
} catch (error) {
    console.error('Database initialization failed:', error);
    process.exit(1);
} 