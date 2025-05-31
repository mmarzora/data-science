"""
Main FastAPI application for the MovieMatch backend.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import init_db
from .api import movies, matching, embedding_analysis

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000", 
        "null"  # Allow file:// origins for HTML visualizer
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "MovieMatch API is running"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "moviematch-backend"}

# Include routers
app.include_router(
    movies.router,
    prefix=f"{settings.API_V1_PREFIX}/movies",
    tags=["movies"]
)

app.include_router(
    matching.router,
    prefix=f"{settings.API_V1_PREFIX}/matching",
    tags=["matching"]
)

app.include_router(
    embedding_analysis.router,
    tags=["embeddings"]
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.backend.main:app",
        host="127.0.0.1",
        port=8000,
        reload=settings.DEBUG
    ) 