from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import json
from typing import List, Optional, Dict
from pydantic import BaseModel
import os
from pathlib import Path
import logging
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="MovieMatch API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Specific to frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database path
DB_PATH = Path(__file__).parent.parent.parent.parent / "moviematch" / "src" / "database" / "movies.db"

class Movie(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    release_year: Optional[int] = None
    poster_url: Optional[str] = None
    genres: List[str] = []  # Will be stored as JSON in DB
    runtime_minutes: Optional[int] = None
    rating: Optional[float] = None  # REAL in DB
    watchmode_id: Optional[str] = None  # TEXT in DB
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class MovieList(BaseModel):
    movies: List[Movie]

class MovieSimilarity(BaseModel):
    id: int
    title: str
    rating: Optional[float] = None  # Changed to float to match DB
    release_year: Optional[int] = None
    similarity: float

def get_db():
    """Create a database connection."""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(status_code=500, detail="Database connection error")

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "MovieMatch API is running"}

@app.get("/api/movies", response_model=MovieList)
async def get_movies(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    year: Optional[int] = None,
    min_rating: Optional[float] = None
):
    """Get a paginated list of movies with optional filters."""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Build query with filters
        query = "SELECT * FROM movies WHERE 1=1"
        params = []
        
        if year:
            query += " AND release_year = ?"
            params.append(year)
            
        if min_rating:
            query += " AND rating >= ?"  # rating is already REAL in DB
            params.append(min_rating)
        
        # Add pagination
        query += " ORDER BY release_year DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        movies = []
        for row in cursor.fetchall():
            movie_dict = dict(row)
            movie_dict['genres'] = json.loads(movie_dict['genres']) if movie_dict['genres'] else []
            movies.append(movie_dict)
            
        conn.close()
        return {"movies": movies}
    except Exception as e:
        logger.error(f"Error fetching movies: {e}")
        raise HTTPException(status_code=500, detail="Error fetching movies")

@app.get("/api/movies/random", response_model=MovieList)
async def get_random_movies(
    limit: int = Query(20, ge=1, le=50),
    year_start: Optional[int] = None,
    min_rating: Optional[float] = None
):
    """Get random movies with optional filters."""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        query = "SELECT * FROM movies WHERE 1=1"
        params = []
        
        if year_start:
            query += " AND release_year >= ?"
            params.append(year_start)
        
        if min_rating:
            query += " AND rating >= ?"  # rating is already REAL in DB
            params.append(min_rating)
        
        query += " ORDER BY RANDOM() LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        movies = []
        for row in cursor.fetchall():
            movie_dict = dict(row)
            movie_dict['genres'] = json.loads(movie_dict['genres']) if movie_dict['genres'] else []
            movies.append(movie_dict)
            
        conn.close()
        return {"movies": movies}
    except Exception as e:
        logger.error(f"Error fetching random movies: {e}")
        raise HTTPException(status_code=500, detail="Error fetching random movies")

@app.get("/api/movies/{movie_id}", response_model=Movie)
async def get_movie(movie_id: int):
    """Get details for a specific movie."""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM movies WHERE id = ?", (movie_id,))
        movie = cursor.fetchone()
        
        if movie is None:
            raise HTTPException(status_code=404, detail="Movie not found")
            
        movie_dict = dict(movie)
        movie_dict['genres'] = json.loads(movie_dict['genres']) if movie_dict['genres'] else []
        
        conn.close()
        return movie_dict
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching movie {movie_id}: {e}")
        raise HTTPException(status_code=500, detail="Error fetching movie")

@app.get("/api/movies/{movie_id}/similar", response_model=MovieList)
async def get_similar_movies(
    movie_id: int,
    limit: int = Query(5, ge=1, le=20)
):
    """Get similar movies based on embedding similarity."""
    try:
        from src.embeddings.generate_embeddings import MovieEmbeddings
        embedder = MovieEmbeddings()
        similar_movies = embedder.find_similar_movies(movie_id, limit)
        return {"movies": similar_movies}
    except Exception as e:
        logger.error(f"Error finding similar movies for {movie_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error finding similar movies"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 