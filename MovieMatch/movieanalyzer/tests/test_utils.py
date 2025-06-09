import numpy as np
import pytest
from movieanalyzer import utils, data

def test_get_unique_genres():
    genres = utils.get_unique_genres()
    assert isinstance(genres, list)
    assert all(isinstance(g, str) for g in genres)
    # Should match unique genres in movies_df
    flat = [g for genres in data.movies_df['genres'] for g in (genres or [])]
    assert set(genres) == set(flat)

def test_describe_quadrant():
    # Use a non-empty quadrant
    q = 'Q1'
    movies = [m for m in data.movies_df.to_dict('records') if m['quadrant'] == q]
    desc = utils.describe_quadrant(movies, q)
    assert isinstance(desc, str)
    assert desc.startswith(q)
    # Edge: empty
    assert 'No movies' in utils.describe_quadrant([], 'QX')

def test_get_scatter_traces():
    traces = utils.get_scatter_traces(data.movies_df, 'Q1', 'All genres')
    assert isinstance(traces, list)
    assert all(hasattr(t, 'to_plotly_json') for t in traces)
    # Edge: empty DataFrame
    import pandas as pd
    empty_df = pd.DataFrame(columns=data.movies_df.columns)
    traces_empty = utils.get_scatter_traces(empty_df, 'Q1', 'All genres')
    assert isinstance(traces_empty, list)

def test_get_quadrant_shapes():
    shapes = utils.get_quadrant_shapes('Q1')
    assert isinstance(shapes, list)
    if data.movies_df.empty:
        assert shapes == []
    else:
        assert any(s.get('type') == 'rect' for s in shapes)

def test_get_genre_bar():
    q = 'Q1'
    movies = [m for m in data.movies_df.to_dict('records') if m['quadrant'] == q]
    fig = utils.get_genre_bar(movies, q)
    assert hasattr(fig, 'to_plotly_json')

def test_embed_text():
    emb = utils.embed_text('The Matrix')
    assert isinstance(emb, np.ndarray)
    assert emb.ndim == 1
    # Should match embedding dimension
    assert emb.shape[0] == data.embeddings.shape[1] 