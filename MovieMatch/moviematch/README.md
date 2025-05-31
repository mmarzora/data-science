# MovieMatch

A movie matching application that helps pairs of users find movies they both want to watch.

## Project Structure

```
moviematch/
├── src/                    # Frontend React application
│   ├── components/         # React components
│   ├── services/          # Frontend services
│   ├── database/          # Database utilities
│   └── types/             # TypeScript type definitions
│
├── backend/               # Python FastAPI backend
│   ├── src/
│   │   ├── api/          # API endpoints
│   │   ├── models/       # Database models
│   │   ├── services/     # Business logic
│   │   └── database/     # Database management
│   └── requirements.txt   # Python dependencies
│
├── public/                # Static assets
├── package.json          # Frontend dependencies
└── tsconfig.json         # TypeScript configuration
```

## Setup Instructions

1. Frontend Setup:
```bash
# Install frontend dependencies
npm install

# Start development server
npm start
```

2. Backend Setup:
```bash
# Create Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
cd backend
pip install -r requirements.txt

# Start backend server
uvicorn src.api.main:app --reload
```

3. Database Setup:
```bash
# Initialize the database
python backend/src/database/init_db.py

# Populate with sample data
python backend/src/database/populate_db.py
```

## Architecture Overview

### Frontend
- React with TypeScript
- Firebase for authentication and real-time session management
- Axios for API communication
- Modern UI components with CSS modules

### Backend
- FastAPI for high-performance API endpoints
- SQLite database for movie storage
- Sentence transformers for movie similarity matching
- Real-time session management

### Key Features
- Real-time movie matching between pairs
- Smart movie recommendations
- Session management
- Movie preference synchronization
- Beautiful, responsive UI

## Development Guidelines

1. **Code Organization**
   - Keep components small and focused
   - Use TypeScript for type safety
   - Follow React best practices

2. **State Management**
   - Use React hooks for local state
   - Firebase for real-time state
   - Clear state cleanup on unmount

3. **Error Handling**
   - Proper error boundaries
   - User-friendly error messages
   - Graceful fallbacks

4. **Testing**
   - Unit tests for components
   - Integration tests for API
   - End-to-end testing

## API Endpoints

### Movies
- `GET /api/movies/random` - Get random movies
- `GET /api/movies/{id}` - Get movie details
- `GET /api/movies/{id}/similar` - Get similar movies

### Sessions
- Real-time session management through Firebase
- Movie swipe synchronization
- Match detection

## Database Schema

### Movies Table
- id: Primary key
- title: Movie title
- description: Movie description
- release_year: Release year
- poster_url: URL to movie poster
- genres: JSON array of genres
- runtime_minutes: Movie duration
- rating: Movie rating
- embedding: Movie embedding for similarity matching

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License
