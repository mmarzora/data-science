from typing import List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
import json
from pathlib import Path

from src.models.movie import Movie, MovieResponse
from src.database.db import get_db

class MovieService:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def get_movie_embedding(self, title: str, description: str, genres: List[str]) -> bytes:
        """Generate embedding for a movie based on its metadata."""
        text = f"{title} {description} {' '.join(genres)}"
        embedding = self.model.encode([text])[0]
        return embedding.tobytes()

    def bytes_to_array(self, embedding_bytes: bytes) -> np.ndarray:
        """Convert bytes back to numpy array."""
        return np.frombuffer(embedding_bytes, dtype=np.float32)

    def get_random_movies(self, limit: int = 20, year_start: Optional[int] = None, minRating: Optional[float] = None) -> List[MovieResponse]:
        """Get random movies with optional filters."""
        query = "SELECT * FROM movies WHERE 1=1"
        params = []
        
        if year_start:
            query += " AND release_year >= ?"
            params.append(year_start)
        
        if minRating:
            query += " AND rating >= ?"
            params.append(minRating)
        
        query += " ORDER BY RANDOM() LIMIT ?"
        params.append(limit)
        
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute(query, params)
            movies = cursor.fetchall()
            
            # Convert rows to MovieResponse objects
            result = []
            for movie in movies:
                movie_dict = dict(movie)
                movie_dict['genres'] = json.loads(movie_dict['genres']) if movie_dict['genres'] else []
                result.append(MovieResponse(**movie_dict))
            
            return result
        finally:
            db.close()

    def get_movie(self, movie_id: int) -> Optional[MovieResponse]:
        """Get a specific movie by ID."""
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute("SELECT * FROM movies WHERE id = ?", (movie_id,))
            movie = cursor.fetchone()
            
            if not movie:
                return None
            
            movie_dict = dict(movie)
            movie_dict['genres'] = json.loads(movie_dict['genres']) if movie_dict['genres'] else []
            return MovieResponse(**movie_dict)
        finally:
            db.close()

    def get_similar_movies(self, movie_id: int, limit: int = 10) -> List[MovieResponse]:
        """Get similar movies based on embedding similarity."""
        db = get_db()
        cursor = db.cursor()
        try:
            # Get the source movie's embedding
            cursor.execute("SELECT embedding FROM movies WHERE id = ?", (movie_id,))
            result = cursor.fetchone()
            
            if not result:
                return []
            
            source_embedding = self.bytes_to_array(result['embedding'])
            
            # Get all other movies' embeddings and calculate similarity
            cursor.execute("""
                SELECT id, title, description, release_year, poster_url, genres, 
                       runtime_minutes, rating, embedding 
                FROM movies 
                WHERE id != ?
            """, (movie_id,))
            movies = cursor.fetchall()
            
            similarities = []
            for movie in movies:
                movie_dict = dict(movie)
                movie_dict['genres'] = json.loads(movie_dict['genres']) if movie_dict['genres'] else []
                
                target_embedding = self.bytes_to_array(movie['embedding'])
                similarity = np.dot(source_embedding, target_embedding) / (
                    np.linalg.norm(source_embedding) * np.linalg.norm(target_embedding)
                )
                similarities.append((similarity, movie_dict))
            
            # Sort by similarity and return top N
            similarities.sort(key=lambda x: x[0], reverse=True)
            return [MovieResponse(**movie) for _, movie in similarities[:limit]]
        finally:
            db.close() 