from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import json
from pathlib import Path
import sys

# Add parent directory to path to import modules
root_dir = Path(__file__).parent.parent.parent
sys.path.append(str(root_dir))

from src.services.movie_service import MovieService
from src.models.movie import Movie, MovieResponse
from pydantic import BaseModel

app = FastAPI()
movie_service = MovieService()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MovieList(BaseModel):
    movies: List[MovieResponse]

@app.get("/api/movies/random", response_model=MovieList)
async def get_random_movies(limit: int = 20, year_start: Optional[int] = None, minRating: Optional[float] = None):
    """Get random movies with optional filters."""
    try:
        movies = movie_service.get_random_movies(limit, year_start, minRating)
        return {"movies": movies}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/movies/{movie_id}", response_model=MovieResponse)
async def get_movie(movie_id: int):
    """Get a specific movie by ID."""
    try:
        movie = movie_service.get_movie(movie_id)
        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")
        return movie
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/movies/{movie_id}/similar", response_model=MovieList)
async def get_similar_movies(movie_id: int, limit: int = 10):
    """Get similar movies based on embedding similarity."""
    try:
        similar_movies = movie_service.get_similar_movies(movie_id, limit)
        return {"movies": similar_movies}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000) 