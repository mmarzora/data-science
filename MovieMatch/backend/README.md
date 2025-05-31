# MovieMatch Backend

This is the backend service for MovieMatch, providing movie data and API endpoints.

## Setup

1. Create a Python virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your WatchMode API key:
   - Get an API key from [WatchMode](https://api.watchmode.com/)
   - Set it as an environment variable:
     ```bash
     export WATCHMODE_API_KEY=your_api_key_here
     ```
     On Windows:
     ```cmd
     set WATCHMODE_API_KEY=your_api_key_here
     ```

## Database Setup

To populate the database with movies:

```bash
python src/database/populate_db.py
```

This will:
- Create the database if it doesn't exist
- Fetch 200 popular movies from WatchMode API
- Store them in the local SQLite database

## Running the Server

Start the FastAPI server:

```bash
uvicorn src.api.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

- `GET /`: Health check endpoint
- `GET /movies`: Get paginated list of movies
  - Query parameters:
    - `limit` (optional, default: 50): Number of movies to return
    - `offset` (optional, default: 0): Number of movies to skip
- `GET /movies/{movie_id}`: Get details for a specific movie

## Development

The backend is built with:
- FastAPI for the REST API
- SQLite for the database
- WatchMode API for movie data

Key files:
- `src/api/main.py`: Main API endpoints
- `src/database/populate_db.py`: Database population script 