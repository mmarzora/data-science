import sqlite3
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use absolute path to the populated database file
DB_PATH = Path("/Users/maitemarzoratti/Documents/data-science/MovieMatch/moviematch/src/database/movies.db")

logger.info(f"Database path configured: {DB_PATH}")
logger.info(f"Database exists: {DB_PATH.exists()}")

def get_db():
    """Get a database connection."""
    logger.info(f"Creating database connection to: {DB_PATH}")
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    
    # Log database info
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM movies")
        count = cursor.fetchone()[0]
        logger.info(f"Database connected successfully, movies count: {count}")
    except Exception as e:
        logger.error(f"Error checking database: {e}")
    
    return conn 