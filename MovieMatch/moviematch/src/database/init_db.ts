import db from './db';

// Test database connection and table creation
try {
    // Test query
    const result = db.prepare('SELECT name FROM sqlite_master WHERE type="table" AND name="movies"').get();
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