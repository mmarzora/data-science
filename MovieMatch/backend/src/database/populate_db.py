import sqlite3
import requests
import json
import os
from pathlib import Path
import time
from typing import List, Dict, Any
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database directory if it doesn't exist
DB_DIR = Path(__file__).parent
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "movies.db"

# WatchMode API configuration
WATCHMODE_API_KEY = os.getenv("WATCHMODE_API_KEY")
if not WATCHMODE_API_KEY:
    raise ValueError("WATCHMODE_API_KEY environment variable is required")

WATCHMODE_BASE_URL = "https://api.watchmode.com/v1"

def create_database():
    """Create the movies database with the required schema."""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    cursor.execute("""
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
    )
    """)
    
    # Create indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_movies_title ON movies(title)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_movies_release_year ON movies(release_year)")
    
    conn.commit()
    conn.close()
    logger.info("Database schema created successfully")

def fetch_movies() -> List[Dict[str, Any]]:
    """Fetch movies from WatchMode API."""
    titles_url = f"{WATCHMODE_BASE_URL}/list-titles/"
    
    params = {
        "apiKey": WATCHMODE_API_KEY,
        "types": "movie",
        "limit": 200,  # Fetch 200 movies
        "sort_by": "popularity_desc"  # Sort by popularity
    }
    
    try:
        response = requests.get(titles_url, params=params)
        response.raise_for_status()
        return response.json().get("titles", [])
    except requests.RequestException as e:
        logger.error(f"Error fetching movies from WatchMode API: {e}")
        return []

def get_movie_details(watchmode_id: int) -> Dict[str, Any]:
    """Fetch detailed information for a specific movie."""
    details_url = f"{WATCHMODE_BASE_URL}/title/{watchmode_id}/details/"
    
    params = {
        "apiKey": WATCHMODE_API_KEY,
    }
    
    try:
        response = requests.get(details_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Error fetching details for movie {watchmode_id}: {e}")
        return {}

def populate_database():
    """Populate the database with movies from WatchMode API."""
    logger.info("Creating database schema...")
    create_database()
    
    logger.info("Fetching movies from WatchMode API...")
    movies = fetch_movies()
    
    if not movies:
        logger.error("No movies fetched from API. Aborting database population.")
        return
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    logger.info(f"Found {len(movies)} movies. Fetching details for each...")
    
    for i, movie in enumerate(movies, 1):
        try:
            # Get detailed information for the movie
            details = get_movie_details(movie["id"])
            if not details:
                continue
            
            # Convert rating to float
            rating = details.get("user_rating")
            if rating is not None:
                try:
                    rating = float(rating)
                except (ValueError, TypeError):
                    rating = None
            
            # Extract and format the data
            movie_data = {
                "title": details.get("title"),
                "description": details.get("plot_overview"),
                "release_year": details.get("year"),
                "poster_url": details.get("poster"),
                "genres": json.dumps(details.get("genres", [])),
                "runtime_minutes": details.get("runtime_minutes"),
                "rating": rating,
                "watchmode_id": str(details.get("id"))  # Convert to string to match schema
            }
            
            # Insert the movie into the database
            cursor.execute("""
            INSERT INTO movies (
                title, description, release_year, poster_url,
                genres, runtime_minutes, rating, watchmode_id
            ) VALUES (
                :title, :description, :release_year, :poster_url,
                :genres, :runtime_minutes, :rating, :watchmode_id
            )
            """, movie_data)
            
            logger.info(f"Processed {i}/{len(movies)}: {movie_data['title']}")
            
            # Commit every 10 movies
            if i % 10 == 0:
                conn.commit()
            
            # Sleep to respect API rate limits
            time.sleep(0.5)
            
        except Exception as e:
            logger.error(f"Error processing movie {movie.get('title', 'Unknown')}: {e}")
            continue
    
    # Final commit
    conn.commit()
    conn.close()
    
    logger.info("Database population completed!")

if __name__ == "__main__":
    populate_database() 