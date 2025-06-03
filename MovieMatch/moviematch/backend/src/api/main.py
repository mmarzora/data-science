from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import json
import uuid
from typing import List, Optional, Dict
from pydantic import BaseModel
import os
import sys
from pathlib import Path
import logging
from dotenv import load_dotenv
from datetime import datetime
from .routes import matching, movies, embedding_analysis
from ..database.database import init_db
from ..config import settings

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

# Database path - pointing to the populated database with genre names
DB_PATH = Path(__file__).parent.parent / "database" / "movies.db"
logger.info(f"API using database at: {DB_PATH}")
logger.info(f"Database exists: {DB_PATH.exists()}")

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

class CreateSessionRequest(BaseModel):
    user1_id: str
    user2_id: str

class CreateSessionResponse(BaseModel):
    session_id: str

class FeedbackRequest(BaseModel):
    user_id: str
    movie_id: int
    feedback_type: str  # 'like', 'dislike', 'skip'
    time_spent_ms: Optional[int] = None

class FeedbackResponse(BaseModel):
    success: bool
    message: str

app.include_router(matching.router, prefix="/api/matching")
app.include_router(movies.router, prefix="/api/movies")
app.include_router(embedding_analysis.router, prefix="/api/embeddings")

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "MovieMatch API is running"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "moviematch-backend"}

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.backend.main:app",
        host="127.0.0.1",
        port=8000,
        reload=settings.DEBUG
    ) 
