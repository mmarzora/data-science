"""
Main FastAPI application for the MovieMatch backend.
"""

import logging
from fastapi import FastAPI, Query, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .config import settings
from .database import init_db, get_db
from .api import movies, matching, embedding_analysis
from .tools.semantic_analyzer import SemanticAnalyzer
from .tools.recommendation_explainer import RecommendationExplainer

# Configure logging
logger = logging.getLogger(__name__)

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
        "http://192.168.1.13:3000",  # Network access
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

# Add explanation endpoint
@app.get("/api/matching/explain/{session_id}/{movie_id}")
async def explain_recommendation(
    session_id: str,
    movie_id: int,
    user1_id: str = Query(..., description="First user ID"),
    user2_id: str = Query(..., description="Second user ID"),
    db: Session = Depends(get_db)
):
    """Get explanation for why a specific movie was recommended."""
    try:
        explainer = RecommendationExplainer()
        explanation = explainer.explain_recommendation(
            db, session_id, movie_id, user1_id, user2_id
        )
        
        if "error" in explanation:
            raise HTTPException(status_code=404, detail=explanation["error"])
        
        return explanation
    except Exception as e:
        logger.error(f"Error explaining recommendation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to explain recommendation: {str(e)}")

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.backend.main:app",
        host="0.0.0.0",  # Bind to all interfaces for network access
        port=8000,
        reload=settings.DEBUG
    ) 