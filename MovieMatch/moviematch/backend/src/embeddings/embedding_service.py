import numpy as np
from sentence_transformers import SentenceTransformer
import sqlite3
import json
from typing import List, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MovieEmbeddingService:
    def __init__(self, db_path: str, model_name: str = 'all-MiniLM-L6-v2'):
        """Initialize the embedding service with a database connection and model.
        
        Args:
            db_path: Path to the SQLite database
            model_name: Name of the sentence-transformer model to use
        """
        self.db_path = db_path
        self.model = SentenceTransformer(model_name)
        
    def _get_movie_text(self, movie: Dict[str, Any]) -> str:
        """Combine movie features into a single text for embedding.
        
        Args:
            movie: Dictionary containing movie data
        Returns:
            Combined text representation of the movie
        """
        features = []
        
        # Add title (most important)
        if movie['title']:
            features.append(movie['title'])
            
        # Add description
        if movie['description']:
            features.append(movie['description'])
            
        # Add genres
        if movie['genres']:
            try:
                genres = json.loads(movie['genres'])
                features.extend(genres)
            except json.JSONDecodeError:
                logger.warning(f"Could not parse genres for movie {movie['title']}")
                
        return " ".join(features)
    
    def generate_embedding(self, movie: Dict[str, Any]) -> np.ndarray:
        """Generate embedding for a single movie.
        
        Args:
            movie: Dictionary containing movie data
        Returns:
            numpy array containing the embedding
        """
        text = self._get_movie_text(movie)
        return self.model.encode(text)
    
    def update_all_embeddings(self):
        """Update embeddings for all movies in the database."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        try:
            # Get all movies without embeddings
            cursor = conn.execute("""
                SELECT id, title, description, genres 
                FROM movies 
                WHERE embedding IS NULL
            """)
            
            movies = cursor.fetchall()
            logger.info(f"Generating embeddings for {len(movies)} movies")
            
            for movie in movies:
                embedding = self.generate_embedding(dict(movie))
                
                # Store embedding as binary
                binary_embedding = embedding.tobytes()
                
                conn.execute("""
                    UPDATE movies 
                    SET embedding = ?, updated_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                """, (binary_embedding, movie['id']))
                
                conn.commit()
                logger.info(f"Updated embedding for movie: {movie['title']}")
                
        except Exception as e:
            logger.error(f"Error updating embeddings: {e}")
            raise
        finally:
            conn.close()
    
    def find_similar_movies(self, movie_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """Find similar movies based on embedding similarity.
        
        Args:
            movie_id: ID of the movie to find similar movies for
            limit: Maximum number of similar movies to return
        Returns:
            List of similar movies with their similarity scores
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        try:
            # Get the target movie's embedding
            cursor = conn.execute("""
                SELECT embedding 
                FROM movies 
                WHERE id = ? AND embedding IS NOT NULL
            """, (movie_id,))
            
            result = cursor.fetchone()
            if not result:
                raise ValueError(f"No embedding found for movie_id {movie_id}")
            
            target_embedding = np.frombuffer(result['embedding'])
            
            # Get all other movies with embeddings
            cursor = conn.execute("""
                SELECT id, title, embedding, rating, release_year 
                FROM movies 
                WHERE id != ? AND embedding IS NOT NULL
            """, (movie_id,))
            
            similar_movies = []
            for movie in cursor:
                embedding = np.frombuffer(movie['embedding'])
                similarity = np.dot(target_embedding, embedding) / (
                    np.linalg.norm(target_embedding) * np.linalg.norm(embedding)
                )
                
                similar_movies.append({
                    'id': movie['id'],
                    'title': movie['title'],
                    'rating': movie['rating'],
                    'release_year': movie['release_year'],
                    'similarity': float(similarity)
                })
            
            # Sort by similarity and return top matches
            similar_movies.sort(key=lambda x: x['similarity'], reverse=True)
            return similar_movies[:limit]
            
        finally:
            conn.close()

if __name__ == "__main__":
    # Example usage
    db_path = "src/database/movies.db"
    embedding_service = MovieEmbeddingService(db_path)
    
    # Update all embeddings
    embedding_service.update_all_embeddings()
    
    # Find similar movies for a specific movie
    similar = embedding_service.find_similar_movies(1)
    print("Similar movies:", similar) 