import os
import sqlite3
import json
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from typing import Optional, List, Any

def parse_embedding(emb: Optional[bytes]) -> Optional[np.ndarray]:
    if emb is None:
        return None
    try:
        return np.frombuffer(emb, dtype=np.float32)
    except Exception:
        return None

def parse_genres(genres_str: str) -> List[str]:
    try:
        return json.loads(genres_str)
    except Exception:
        return []

# --- Data Loading and Processing ---
DB_PATH: str = os.path.join(os.path.dirname(__file__), '../moviematch/backend/src/database/movies.db')

conn: sqlite3.Connection = sqlite3.connect(DB_PATH)
movies_df: pd.DataFrame = pd.read_sql_query("SELECT * FROM movies", conn)

# Process embeddings and keep only valid rows
valid_embeddings: List[np.ndarray] = []
valid_indices: List[int] = []
for idx, row in movies_df.iterrows():
    emb = parse_embedding(row['embedding'])
    if emb is not None and len(emb) > 0:
        valid_embeddings.append(emb)
        valid_indices.append(idx)

if len(valid_embeddings) > 0:
    embeddings: np.ndarray = np.stack(valid_embeddings)
    movies_df = movies_df.iloc[valid_indices].copy().reset_index(drop=True)
    pca = PCA(n_components=2)
    embeddings_2d: np.ndarray = pca.fit_transform(embeddings)
    movies_df['PC1'] = embeddings_2d[:, 0]
    movies_df['PC2'] = embeddings_2d[:, 1]
else:
    print("Warning: No valid embeddings found!")
    embeddings: Optional[np.ndarray] = None
    movies_df = pd.DataFrame(columns=['title', 'genres', 'rating', 'release_year', 'PC1', 'PC2'])

movies_df['genres'] = movies_df['genres'].apply(parse_genres)

# Calculate medians for quadrant boundaries
pc1_median: float = movies_df['PC1'].median() if not movies_df.empty else 0
pc2_median: float = movies_df['PC2'].median() if not movies_df.empty else 0

def assign_quadrant(row: pd.Series) -> str:
    if row['PC1'] >= pc1_median and row['PC2'] >= pc2_median:
        return 'Q1'
    elif row['PC1'] < pc1_median and row['PC2'] >= pc2_median:
        return 'Q2'
    elif row['PC1'] < pc1_median and row['PC2'] < pc2_median:
        return 'Q3'
    else:
        return 'Q4'

movies_df['quadrant'] = movies_df.apply(assign_quadrant, axis=1) if not movies_df.empty else 'Q1'

# Prepare final DataFrame for the app
movies_df = movies_df.rename(columns={'genres_eval': 'genres'}) 