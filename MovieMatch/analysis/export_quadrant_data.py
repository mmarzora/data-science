import sqlite3
import pandas as pd
import numpy as np
import json
from sklearn.decomposition import PCA

# Path to the SQLite database
DB_PATH = '../moviematch/backend/src/database/movies.db'
# Output JSON file
OUTPUT_PATH = 'quadrant_data.json'

# Connect to the database
conn = sqlite3.connect(DB_PATH)

# Load movies table
movies_df = pd.read_sql_query("SELECT * FROM movies", conn)

# Parse embeddings (stored as bytes)
def parse_embedding(emb):
    if emb is None:
        return None
    return np.frombuffer(emb, dtype=np.float32)

embeddings = np.stack([
    parse_embedding(row['embedding']) for _, row in movies_df.iterrows()
    if row['embedding'] is not None
])

# Only keep rows with valid embeddings
valid_idx = [i for i, row in movies_df.iterrows() if row['embedding'] is not None]
movies_df = movies_df.iloc[valid_idx].reset_index(drop=True)

# PCA to 2D
pca = PCA(n_components=2)
embeddings_2d = pca.fit_transform(embeddings)
movies_df['PC1'] = embeddings_2d[:, 0]
movies_df['PC2'] = embeddings_2d[:, 1]

# Parse genres (stored as stringified list)
def parse_genres(genres_str):
    try:
        return json.loads(genres_str)
    except Exception:
        return []

movies_df['genres_eval'] = movies_df['genres'].apply(parse_genres)

# Calculate medians for quadrant boundaries
pc1_median = movies_df['PC1'].median()
pc2_median = movies_df['PC2'].median()

def assign_quadrant(row):
    if row['PC1'] >= pc1_median and row['PC2'] >= pc2_median:
        return 'Q1'  # Top-right
    elif row['PC1'] < pc1_median and row['PC2'] >= pc2_median:
        return 'Q2'  # Top-left
    elif row['PC1'] < pc1_median and row['PC2'] < pc2_median:
        return 'Q3'  # Bottom-left
    else:
        return 'Q4'  # Bottom-right

movies_df['quadrant'] = movies_df.apply(assign_quadrant, axis=1)

# Select relevant fields for export
export_fields = ['id', 'title', 'PC1', 'PC2', 'quadrant', 'genres_eval', 'rating', 'release_year']
export_df = movies_df[export_fields].copy()
export_df = export_df.rename(columns={'genres_eval': 'genres'})

# Convert to records and save as JSON
export_data = export_df.to_dict(orient='records')
with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
    json.dump(export_data, f, ensure_ascii=False, indent=2)

print(f"Exported {len(export_data)} movies to {OUTPUT_PATH}") 