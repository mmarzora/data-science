from dash import Output, Input, State, callback_context, html
import numpy as np
from .data import movies_df, embeddings
from .utils import describe_quadrant, get_scatter_traces, get_quadrant_shapes, get_genre_bar, embed_text

def register_callbacks(app):
    @app.callback(
        Output('scatter', 'figure'),
        Output('quad-desc', 'children'),
        Output('genre-bar', 'figure'),
        Output('current-quadrant', 'data'),
        Output('q1-button', 'className'),
        Output('q2-button', 'className'),
        Output('q3-button', 'className'),
        Output('q4-button', 'className'),
        Output('similar-movies', 'children'),
        Input('genre-filter', 'value'),
        Input('text-search', 'value'),
        Input('q1-button', 'n_clicks'),
        Input('q2-button', 'n_clicks'),
        Input('q3-button', 'n_clicks'),
        Input('q4-button', 'n_clicks'),
        State('current-quadrant', 'data')
    )
    def update_dashboard(current_genre, text_search, q1_clicks, q2_clicks, q3_clicks, q4_clicks, current_quadrant):
        ctx = callback_context
        if ctx.triggered:
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            if button_id == 'q1-button':
                current_quadrant = 'Q1'
            elif button_id == 'q2-button':
                current_quadrant = 'Q2'
            elif button_id == 'q3-button':
                current_quadrant = 'Q3'
            elif button_id == 'q4-button':
                current_quadrant = 'Q4'
        filtered_df = movies_df.copy()
        if current_genre != 'All genres':
            filtered_df = filtered_df[filtered_df['genres'].apply(lambda x: current_genre in x if x else False)]
        similar_movies = []
        similar_movies_div = ''
        if text_search and embeddings is not None and text_search.strip():
            query_emb = embed_text(text_search)
            from sklearn.metrics.pairwise import cosine_similarity
            sims = cosine_similarity([query_emb], embeddings)[0]
            top_idx = np.argsort(sims)[::-1][:5]
            similar_movies = [movies_df.iloc[i].to_dict() for i in top_idx]
            similarities = [sims[i] for i in top_idx]
            if similar_movies:
                similar_movies_div = html.Div([
                    html.H4('Top 5 Most Similar Movies', className='similar-movies-title'),
                    html.Div([
                        html.Div([
                            html.Div([
                                html.Span(f"{i+1}.", className='similar-movie-rank'),
                                html.Span(m['title'], className='similar-movie-title'),
                                html.Span(f"{similarities[i]:.3f}", className='similar-movie-similarity'),
                            ], className='similar-movie-header'),
                            html.Div([
                                *(html.Span(genre, className='similar-movie-genre') for genre in (m['genres'] or []))
                            ], className='similar-movie-genres'),
                            html.Div([
                                html.Span(f"Rating: {m.get('rating', 'N/A')}", className='similar-movie-rating'),
                                html.Span(f"Year: {m.get('release_year', 'N/A')}", className='similar-movie-year'),
                            ], className='similar-movie-meta'),
                            html.Div(m.get('description', ''), className='similar-movie-description'),
                        ], className='similar-movie-card')
                        for i, m in enumerate(similar_movies)
                    ], className='similar-movies-list')
                ], className='similar-movies-section')
            else:
                similar_movies_div = html.Div('No similar movies found.', style={'color': '#888'})
        else:
            similar_movies_div = ''
        quad_movies = [m for m in filtered_df.to_dict('records') if m['quadrant'] == current_quadrant]
        scatter_fig = get_scatter_traces(filtered_df, current_quadrant, current_genre)
        import plotly.graph_objs as go
        scatter_fig = go.Figure(scatter_fig)
        scatter_fig.update_layout(
            title='Movies by Quadrant (PCA)',
            xaxis=dict(title='PC1', zeroline=False),
            yaxis=dict(title='PC2', zeroline=False),
            legend=dict(orientation='h', x=0.5, xanchor='center', y=-0.2),
            margin=dict(t=80, l=50, r=20, b=80),
            plot_bgcolor='#f7f7f7',
            paper_bgcolor='#fff',
            shapes=get_quadrant_shapes(current_quadrant),
        )
        quad_desc = describe_quadrant(quad_movies, current_quadrant)
        genre_bar_fig = get_genre_bar(quad_movies, current_quadrant)
        return (
            scatter_fig,
            quad_desc,
            genre_bar_fig,
            current_quadrant,
            'quadrant-button q1 selected' if current_quadrant == 'Q1' else 'quadrant-button q1',
            'quadrant-button q2 selected' if current_quadrant == 'Q2' else 'quadrant-button q2',
            'quadrant-button q3 selected' if current_quadrant == 'Q3' else 'quadrant-button q3',
            'quadrant-button q4 selected' if current_quadrant == 'Q4' else 'quadrant-button q4',
            similar_movies_div
        ) 