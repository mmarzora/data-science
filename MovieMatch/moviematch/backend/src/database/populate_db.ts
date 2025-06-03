import Database from 'better-sqlite3';
import dotenv from 'dotenv';
import axios from 'axios';
import { join } from 'path';

// Load environment variables
dotenv.config();

// Create database connection
const db = new Database(join(__dirname, 'movies.db'));

interface Movie {
  id: number;
  title: string;
  description: string;
  release_year: number;
  poster_url: string;
  genres: string[];
  runtime_minutes: number;
  rating: number;
}

async function fetchMoviesFromAPI(limit: number = 20): Promise<Movie[]> {
  try {
    const response = await axios.get(`http://127.0.0.1:8000/api/movies/random?limit=${limit}`);
    return response.data.movies;
  } catch (error) {
    console.error('Error fetching movies from API:', error);
    return [];
  }
}

async function populateDatabase() {
  try {
    // Fetch movies from our FastAPI backend
    const movies = await fetchMoviesFromAPI(200);  // Fetch 200 movies

    // Prepare the insert statement
    const stmt = db.prepare(`
      INSERT OR REPLACE INTO movies (
        title, description, release_year, poster_url, 
        genres, runtime_minutes, rating, watchmode_id
      ) VALUES (
        @title, @description, @release_year, @poster_url,
        @genres, @runtime_minutes, @rating, @watchmode_id
      )
    `);

    // Insert movies in a transaction
    const insertMany = db.transaction((movies: Movie[]) => {
      for (const movie of movies) {
        stmt.run({
          ...movie,
          genres: JSON.stringify(movie.genres)
        });
      }
    });

    insertMany(movies);
    console.log(`Successfully populated database with ${movies.length} movies`);
  } catch (error) {
    console.error('Error populating database:', error);
  }
}

// Run the population if this file is executed directly
if (require.main === module) {
  populateDatabase().then(() => {
    console.log('Database population complete');
    process.exit(0);
  });
} 