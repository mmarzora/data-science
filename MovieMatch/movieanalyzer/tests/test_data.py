import numpy as np
import pytest
import pandas as pd
from movieanalyzer import data

def test_parse_embedding_valid():
    arr = np.array([1.0, 2.0, 3.0], dtype=np.float32)
    emb_bytes = arr.tobytes()
    result = data.parse_embedding(emb_bytes)
    assert isinstance(result, np.ndarray)
    assert np.allclose(result, arr)

def test_parse_embedding_none():
    assert data.parse_embedding(None) is None

def test_parse_embedding_invalid():
    # Not a valid float32 buffer
    assert data.parse_embedding(b'notanembedding') is None

def test_parse_genres_valid():
    genres_str = '["Action", "Comedy"]'
    genres = data.parse_genres(genres_str)
    assert genres == ["Action", "Comedy"]

def test_parse_genres_empty():
    assert data.parse_genres('') == []

def test_parse_genres_invalid():
    assert data.parse_genres('notjson') == []

def test_assign_quadrant():
    # Use medians from data.py
    pc1_median = data.pc1_median
    pc2_median = data.pc2_median
    # Q1
    row = pd.Series({'PC1': pc1_median + 1, 'PC2': pc2_median + 1})
    assert data.assign_quadrant(row) == 'Q1'
    # Q2
    row = pd.Series({'PC1': pc1_median - 1, 'PC2': pc2_median + 1})
    assert data.assign_quadrant(row) == 'Q2'
    # Q3
    row = pd.Series({'PC1': pc1_median - 1, 'PC2': pc2_median - 1})
    assert data.assign_quadrant(row) == 'Q3'
    # Q4
    row = pd.Series({'PC1': pc1_median + 1, 'PC2': pc2_median - 1})
    assert data.assign_quadrant(row) == 'Q4' 