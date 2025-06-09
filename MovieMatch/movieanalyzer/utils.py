import numpy as np
import plotly.graph_objs as go
from typing import List, Dict, Any
from .data import movies_df, embeddings, pc1_median, pc2_median
from sentence_transformers import SentenceTransformer

quad_colors: Dict[str, str] = { 'Q1': '#0074D9', 'Q2': '#2ECC40', 'Q3': '#FF4136', 'Q4': '#FF851B' }
quadrants: List[str] = ['Q1', 'Q2', 'Q3', 'Q4']

# Instantiate the model once (global)
_embedding_model: SentenceTransformer = SentenceTransformer('all-MiniLM-L6-v2')

def get_unique_genres() -> List[str]:
    all_genres = set()
    for genres in movies_df['genres']:
        if genres:
            all_genres.update(genres)
    return sorted(list(all_genres))

def describe_quadrant(movies: List[Dict[str, Any]], quadrant: str) -> str:
    n = len(movies)
    if n == 0:
        return f"{quadrant}: No movies in this quadrant."
    genre_counts: Dict[str, int] = {}
    for m in movies:
        for g in m['genres']:
            genre_counts[g] = genre_counts.get(g, 0) + 1
    sorted_genres = sorted(genre_counts.items(), key=lambda x: -x[1])
    top = sorted_genres[:5]
    if len(top) == 1:
        desc = f"mostly {top[0][0]}"
    elif len(top) == 2:
        desc = f"mostly {top[0][0]} and {top[1][0]}"
    else:
        desc = f"mostly {top[0][0]}, {top[1][0]}, and {top[2][0]}"
    percent = [(g, round(100*c/n, 1)) for g, c in top]
    details = ', '.join(f"{g} ({p}%)" for g, p in percent)
    top_movies = sorted(movies, key=lambda m: m.get('rating', 0), reverse=True)[:3]
    if top_movies:
        top_movies_str = ', '.join(f"{m['title']} ({m.get('rating', '')})" for m in top_movies)
        top_movies_text = f" Top rated: {top_movies_str}."
    else:
        top_movies_text = ''
    mean_pc1 = np.mean([m['PC1'] for m in movies])
    mean_pc2 = np.mean([m['PC2'] for m in movies])
    closest = sorted(movies, key=lambda m: (m['PC1']-mean_pc1)**2 + (m['PC2']-mean_pc2)**2)[:3]
    if closest:
        closest_str = ', '.join(
            f"{m['title']} (dist: {np.sqrt((m['PC1']-mean_pc1)**2 + (m['PC2']-mean_pc2)**2):.2f})"
            for m in closest
        )
        closest_text = f" Closest to quadrant center: {closest_str}."
    else:
        closest_text = ''
    return f"{quadrant} ({n} movies): This quadrant contains {desc} movies. Top genres: {details}.{top_movies_text}{closest_text}"

def get_scatter_traces(df: Any, current_quadrant: str, current_genre: str) -> List[go.Scatter]:
    if df.empty:
        return [go.Scatter(x=[], y=[], mode='markers', name='No data', marker=dict(color='#ccc'))]
    traces = []
    for q in quadrants:
        quad_movies = df[df['quadrant'] == q]
        if current_genre != 'All genres':
            quad_movies = quad_movies[quad_movies['genres'].apply(lambda x: current_genre in x if x else False)]
        if len(quad_movies) == 0:
            continue
        hover_texts = []
        for _, row in quad_movies.iterrows():
            genres_str = ', '.join(str(g) for g in (row['genres'] or []))
            hover_text = (
                f"<b>{row['title']}</b><br>"
                f"Genres: {genres_str}<br>"
                f"Rating: {row.get('rating', '')}<br>"
                f"Year: {row.get('release_year', '')}"
            )
            hover_texts.append(hover_text)
        traces.append(go.Scatter(
            x=quad_movies['PC1'].tolist(),
            y=quad_movies['PC2'].tolist(),
            text=hover_texts,
            mode='markers',
            name=q,
            marker=dict(color=quad_colors[q], size=10, opacity=1, line=dict(width=1, color='#fff')),
            hoverinfo='text',
        ))
    return traces

def get_quadrant_shapes(active_quadrant: str) -> List[Dict[str, Any]]:
    if movies_df.empty:
        return []
    alpha = 0.13
    shapes = []
    pc1_min, pc1_max = movies_df['PC1'].min(), movies_df['PC1'].max() if not movies_df.empty else (-1, 1)
    pc2_min, pc2_max = movies_df['PC2'].min(), movies_df['PC2'].max() if not movies_df.empty else (-1, 1)
    if active_quadrant == 'Q1':
        shapes.append(dict(type='rect', xref='x', yref='y', x0=pc1_median, x1=pc1_max, y0=pc2_median, y1=pc2_max, fillcolor=quad_colors['Q1'], opacity=alpha, line=dict(width=0)))
    if active_quadrant == 'Q2':
        shapes.append(dict(type='rect', xref='x', yref='y', x0=pc1_min, x1=pc1_median, y0=pc2_median, y1=pc2_max, fillcolor=quad_colors['Q2'], opacity=alpha, line=dict(width=0)))
    if active_quadrant == 'Q3':
        shapes.append(dict(type='rect', xref='x', yref='y', x0=pc1_min, x1=pc1_median, y0=pc2_min, y1=pc2_median, fillcolor=quad_colors['Q3'], opacity=alpha, line=dict(width=0)))
    if active_quadrant == 'Q4':
        shapes.append(dict(type='rect', xref='x', yref='y', x0=pc1_median, x1=pc1_max, y0=pc2_min, y1=pc2_median, fillcolor=quad_colors['Q4'], opacity=alpha, line=dict(width=0)))
    shapes.append(dict(type='line', xref='x', yref='paper', x0=pc1_median, x1=pc1_median, y0=0, y1=1, line=dict(color='#888', width=2, dash='dot')))
    shapes.append(dict(type='line', xref='paper', yref='y', x0=0, x1=1, y0=pc2_median, y1=pc2_median, line=dict(color='#888', width=2, dash='dot')))
    return shapes

def get_genre_bar(quad_movies: List[Dict[str, Any]], q: str) -> go.Figure:
    genre_counts: Dict[str, int] = {}
    for m in quad_movies:
        for g in m['genres']:
            genre_counts[g] = genre_counts.get(g, 0) + 1
    sorted_genres = sorted(genre_counts.items(), key=lambda x: -x[1])
    hover_text = []
    for genre, _ in sorted_genres:
        movies_in_genre = [m for m in quad_movies if genre in m['genres']]
        top3 = sorted(movies_in_genre, key=lambda m: m.get('rating', 0), reverse=True)[:3]
        if top3:
            top3_str = '<br>'.join(f"{m['title']} ({m.get('rating', '')})" for m in top3)
            hover_text.append(f"{genre}<br>Top rated:<br>{top3_str}")
        else:
            hover_text.append(genre)
    return go.Figure([
        go.Bar(
            x=[g for g, _ in sorted_genres],
            y=[c for _, c in sorted_genres],
            marker=dict(color=quad_colors[q]),
            customdata=hover_text,
            hovertemplate='%{x}<br>Count: %{y}<br>%{customdata}<extra></extra>',
        )
    ]).update_layout(
        title=f"Genre Composition for {q}",
        yaxis=dict(title='Count', rangemode='tozero'),
        margin=dict(t=40, l=50, r=20, b=80),
        plot_bgcolor='#f7f7f7',
        paper_bgcolor='#fff',
    )

def embed_text(text: str) -> np.ndarray:
    """Generate embedding for a single text using the same model as in generate_embeddings.py."""
    return _embedding_model.encode(text) 