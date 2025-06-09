from dash import dcc, html
from .data import movies_df
from .utils import get_unique_genres

genre_options = [{'label': 'All genres', 'value': 'All genres'}]
all_genres = get_unique_genres()
for genre in all_genres:
    genre_count = sum(movies_df['genres'].apply(lambda x: genre in x if x else False))
    genre_options.append({
        'label': f'{genre} ({genre_count} movies)',
        'value': genre
    })

layout = html.Div([
    dcc.Store(id='current-quadrant', data='Q1'),
    html.H1('Movie Quadrant Analysis', className='main-title'),
    html.Div([
        html.Div([
            html.Label('Filter by Genre:', className='genre-filter-label'),
            dcc.Dropdown(
                id='genre-filter',
                options=genre_options,
                value='All genres',
                clearable=False,
                className='genre-filter-dropdown',
            ),
        ], className='genre-filter-container'),
    ], className='controls-row'),
    html.Div([
        dcc.Graph(id='scatter', className='main-scatter'),
        html.Div([
            *[
                html.Button(
                    label,
                    id=btn_id,
                    n_clicks=0,
                    className=f'quadrant-button {qclass}'
                )
                for label, btn_id, qclass in [
                    ('Top Right (Q1)', 'q1-button', 'q1'),
                    ('Top Left (Q2)', 'q2-button', 'q2'),
                    ('Bottom Left (Q3)', 'q3-button', 'q3'),
                    ('Bottom Right (Q4)', 'q4-button', 'q4'),
                ]
            ]
        ], className='quadrant-buttons-row'),
        html.Div(
            id='quad-desc',
            className='quadrant-description'
        ),
        dcc.Graph(id='genre-bar', className='main-genre-bar'),
    ], className='main-visualization'),
    html.Div([
        html.Label('Text Search for Similar Movies:', className='text-search-label'),
        dcc.Input(
            id='text-search',
            type='text',
            value='',
            placeholder='Describe a movie...',
            debounce=True,
            className='text-search-input',
        ),
        html.Div(id='similar-movies', className='similar-movies-root'),
    ], className='text-search-section'),
], className='main-app-container') 