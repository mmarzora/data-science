"""
SQLAlchemy models for the MovieMatch backend.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Float, DateTime, LargeBinary, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Movie(Base):
    """Movie model."""
    
    __tablename__ = "movies"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    description = Column(Text)
    release_year = Column(Integer, index=True)
    poster_url = Column(String)
    genres = Column(String)  # JSON array stored as string
    runtime_minutes = Column(Integer)
    rating = Column(Float)
    embedding = Column(LargeBinary)
    watchmode_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "release_year": self.release_year,
            "poster_url": self.poster_url,
            "genres": self.genres,  # Will be parsed as JSON by the API
            "runtime_minutes": self.runtime_minutes,
            "rating": self.rating,
            "watchmode_id": self.watchmode_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        } 