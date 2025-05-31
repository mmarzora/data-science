from sentence_transformers import SentenceTransformer
import numpy as np
import sqlite3
import json
from pathlib import Path

class MovieEmbeddings:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.db_path = Path(__file__).parent.parent / 'database' / 'movies.db'
        
    def connect_db(self):
        return sqlite3.connect(str(self.db_path))
        
    def generate_embedding(self, text):
        """Generate embedding for a single text."""
        return self.model.encode(text)
        
    def update_movie_embedding(self, movie_id, description):
        """Update the embedding for a single movie."""
        if not description:
            return
            
        embedding = self.generate_embedding(description)
        
        with self.connect_db() as conn:
            conn.execute(
                "UPDATE movies SET embedding = ? WHERE id = ?",
                (embedding.tobytes(), movie_id)
            )
            
    def update_all_embeddings(self):
        """Update embeddings for all movies in the database."""
        with self.connect_db() as conn:
            # Get all movies without embeddings
            movies = conn.execute(
                "SELECT id, description FROM movies WHERE embedding IS NULL"
            ).fetchall()
            
        print(f"Generating embeddings for {len(movies)} movies...")
        for movie_id, description in movies:
            self.update_movie_embedding(movie_id, description)
            print(f"Updated embedding for movie {movie_id}")
            
    def find_similar_movies(self, movie_id, limit=5):
        """Find similar movies based on embedding similarity."""
        with self.connect_db() as conn:
            # Get the embedding for our target movie
            target_embedding = np.frombuffer(
                conn.execute(
                    "SELECT embedding FROM movies WHERE id = ?",
                    (movie_id,)
                ).fetchone()[0]
            )
            
            # Get all other movies and their embeddings
            movies = conn.execute(
                "SELECT id, title, embedding FROM movies WHERE id != ?",
                (movie_id,)
            ).fetchall()
            
        # Calculate similarities
        similarities = []
        for mid, title, emb in movies:
            if emb is None:
                continue
            embedding = np.frombuffer(emb)
            similarity = np.dot(target_embedding, embedding) / (
                np.linalg.norm(target_embedding) * np.linalg.norm(embedding)
            )
            similarities.append((mid, title, similarity))
            
        # Sort by similarity and return top matches
        similarities.sort(key=lambda x: x[2], reverse=True)
        return similarities[:limit]

if __name__ == "__main__":
    embedder = MovieEmbeddings()
    embedder.update_all_embeddings() 