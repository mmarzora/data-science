# MovieMatch Backend

This directory contains all the backend services for MovieMatch.

## Directory Structure

```
backend/
├── src/
│   ├── api/            # FastAPI application and endpoints
│   │   └── main.py     # Main FastAPI application
│   └── embeddings/     # Movie embedding generation and services
│       ├── generate_embeddings.py  # Script to generate movie embeddings
│       └── embedding_service.py    # Embedding service implementation
```

## Components

### API (src/api)
Contains the FastAPI application that serves as the main backend API for MovieMatch. This handles:
- Movie recommendations
- Session management
- Database operations

### Embeddings (src/embeddings)
Contains the code for generating and managing movie embeddings:
- Embedding generation scripts
- Embedding service for similarity calculations
- Integration with the movie database

## Setup and Running

[Add setup instructions here once development environment is finalized] 