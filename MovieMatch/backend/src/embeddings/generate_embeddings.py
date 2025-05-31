from sentence_transformers import SentenceTransformer
import numpy as np
import sqlite3
import json
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MovieEmbeddings:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        """Initialize the embedding generator with a model."""
        self.model = SentenceTransformer(model_name)
        self.db_path = Path(__file__).parent.parent / 'database' / 'movies.db'
        
    def connect_db(self):
        """Create a database connection."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn
        
    def _get_movie_text(self, title: str, description: str, genres: list) -> str:
        """Combine movie features into a single text for embedding."""
        features = []
        
        # Add title (most important)
        if title:
            features.append(title)
            
        # Add description
        if description:
            features.append(description)
            
        # Add genres
        if genres:
            features.extend(genres)
                
        return " ".join(features)
        
    def generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for a single text."""
        return self.model.encode(text)
        
    def update_movie_embedding(self, movie_id: int, title: str, description: str, genres: str):
        """Update the embedding for a single movie."""
        try:
            # Parse genres from JSON string
            genre_list = json.loads(genres) if genres else []
            
            # Generate text representation
            text = self._get_movie_text(title, description, genre_list)
            if not text.strip():
                logger.warning(f"No text to generate embedding for movie {movie_id}")
                return
                
            # Generate embedding
            embedding = self.generate_embedding(text)
            
            # Store in database
            with self.connect_db() as conn:
                conn.execute(
                    """
                    UPDATE movies 
                    SET embedding = ?, 
                        updated_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                    """,
                    (embedding.tobytes(), movie_id)
                )
                logger.info(f"Updated embedding for movie {movie_id}: {title}")
                
        except Exception as e:
            logger.error(f"Error updating embedding for movie {movie_id}: {e}")
            
    def update_all_embeddings(self):
        """Update embeddings for all movies in the database."""
        with self.connect_db() as conn:
            # Get all movies without embeddings
            movies = conn.execute("""
                SELECT id, title, description, genres 
                FROM movies 
                WHERE embedding IS NULL
            """).fetchall()
            
        logger.info(f"Generating embeddings for {len(movies)} movies...")
        
        for movie in movies:
            self.update_movie_embedding(
                movie['id'],
                movie['title'],
                movie['description'],
                movie['genres']
            )
            
    def find_similar_movies(self, movie_id: int, limit: int = 5) -> list:
        """Find similar movies based on embedding similarity."""
        with self.connect_db() as conn:
            # Get the embedding for our target movie
            result = conn.execute(
                "SELECT embedding FROM movies WHERE id = ? AND embedding IS NOT NULL",
                (movie_id,)
            ).fetchone()
            
            if not result:
                logger.warning(f"No embedding found for movie {movie_id}")
                return []
                
            target_embedding = np.frombuffer(result[0])
            
            # Get all other movies and their embeddings
            movies = conn.execute("""
                SELECT id, title, embedding, rating, release_year 
                FROM movies 
                WHERE id != ? AND embedding IS NOT NULL
            """, (movie_id,)).fetchall()
            
            # Calculate similarities
            similarities = []
            for movie in movies:
                embedding = np.frombuffer(movie['embedding'])
                similarity = np.dot(target_embedding, embedding) / (
                    np.linalg.norm(target_embedding) * np.linalg.norm(embedding)
                )
                
                similarities.append({
                    'id': movie['id'],
                    'title': movie['title'],
                    'rating': float(movie['rating']) if movie['rating'] is not None else None,
                    'release_year': movie['release_year'],
                    'similarity': float(similarity)
                })
            
            # Sort by similarity and return top matches
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            return similarities[:limit]

if __name__ == "__main__":
    # Create embeddings for all movies
    embedder = MovieEmbeddings()
    embedder.update_all_embeddings() 