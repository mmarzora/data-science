# 🎬 MovieMatch Algorithm Testing Guide

## Overview

The MovieMatch algorithm is a sophisticated recommendation system that learns user preferences and optimizes for couple compatibility. It combines genre preferences with movie embeddings and adapts over time.

## Quick Start

### 1. Start the Backend Server
```bash
cd moviematch
uvicorn src.backend.main:app --reload --host 127.0.0.1 --port 8000
```

### 2. Run Basic Test
```bash
python run_tests.py basic
```

### 3. Run Comprehensive Tests
```bash
python test_algorithm.py
```

## Algorithm Features

### 🧠 **Adaptive Learning**
- **Genre Preferences**: Learns from user likes/dislikes for different movie genres
- **Embedding Vectors**: Develops user preference vectors in semantic movie space
- **Confidence Scoring**: Builds confidence as more data is collected

### 👥 **Dual-User Optimization**
- **Intersection Strategy**: Finds movies both users might enjoy
- **Mutual Like Detection**: Tracks when both users like the same movie
- **Compromise Scoring**: Balances preferences to avoid favoring one user

### 🎯 **Anti-Overfitting Mechanisms**
- **Exploration Budget**: Reserves 20-40% of recommendations for exploration
- **Diversity Constraints**: Ensures variety in genres and movie types
- **Decaying Learning Rate**: Prevents drastic changes from single interactions

### 📈 **Stage Evolution**
1. **Exploration** (0-10 interactions): High exploration, genre-focused
2. **Learning** (10-30 interactions): Balanced approach, rapid adaptation
3. **Convergence** (30+ interactions): Refined recommendations, embedding-heavy

## API Endpoints

### Create Session
```bash
curl -X POST http://localhost:8000/api/matching/sessions \
  -H "Content-Type: application/json" \
  -d '{"user1_id": "alice", "user2_id": "bob"}'
```

### Get Recommendations
```bash
curl "http://localhost:8000/api/matching/sessions/{session_id}/recommendations?batch_size=10"
```

### Submit Feedback
```bash
curl -X POST http://localhost:8000/api/matching/sessions/{session_id}/feedback \
  -H "Content-Type: application/json" \
  -d '{"user_id": "alice", "movie_id": 123, "feedback_type": "like", "time_spent_ms": 5000}'
```

### Get Session Stats
```bash
curl "http://localhost:8000/api/matching/sessions/{session_id}/stats"
```

### Get User Preferences
```bash
curl "http://localhost:8000/api/matching/users/{user_id}/preferences"
```

## Test Scenarios

### 1. **Basic Flow Test**
- Creates session for two users
- Gets initial recommendations
- Simulates realistic feedback
- Shows preference learning

### 2. **Evolution Over Time**
- Tracks algorithm adaptation over multiple rounds
- Shows confidence score increases
- Demonstrates stage progression

### 3. **Opposing Preferences**
- Tests users with conflicting tastes (Comedy vs Horror)
- Validates convergence to middle ground
- Shows mutual like detection

### 4. **Performance Analysis**
- Tests recommendation diversity
- Validates consistency across sessions
- Measures algorithm effectiveness

## Understanding the Output

### User Preferences Example
```
Alice's Preferences:
  Confidence: 0.650
  Interactions: 13
  Genre Preferences:
    Comedy: 0.824    # High preference (likes comedy)
    Drama: 0.752     # Good preference  
    Action: 0.376    # Low preference (dislikes action)
```

### Session Statistics Example
```
Session Stage: learning
Total Interactions: 30
Mutual Likes: 8          # Both users liked 8 movies
Alice Stats: {'likes': 12, 'dislikes': 2, 'skips': 1}
Bob Stats: {'likes': 10, 'dislikes': 1, 'skips': 4}
```

## Customizing Tests

### Create Custom User Profiles
```python
custom_user = TestUser(
    id="user123",
    name="Custom User", 
    preferred_genres=["Sci-Fi", "Thriller"],
    disliked_genres=["Musical", "Romance"]
)
```

### Adjust Algorithm Parameters
Edit `moviematch/src/backend/services/matching_service.py`:
```python
INITIAL_LEARNING_RATE = 0.3  # How fast to learn initially
EXPLORATION_BUDGET = 0.25    # % of recs for exploration
EXPLORATION_STAGE_LIMIT = 10 # When to move to learning stage
```

## Troubleshooting

### Server Not Responding
```bash
# Check if server is running
curl http://localhost:8000/health

# Kill existing processes
lsof -ti:8000 | xargs kill -9

# Restart server
cd moviematch
uvicorn src.backend.main:app --reload
```

### Database Issues
The algorithm automatically creates SQLite tables on first run. If you encounter database errors:
```bash
# Delete and recreate database
rm moviematch/src/database/movies.db
# Restart server to recreate tables
```

### Testing Specific Scenarios
```python
# Run only basic connectivity test
python run_tests.py basic

# Create custom test with specific users
from test_algorithm import MovieMatchTester, TestUser

tester = MovieMatchTester()
user1 = TestUser("test1", "User1", ["Action"], ["Romance"])
user2 = TestUser("test2", "User2", ["Comedy"], ["Horror"])
# ... custom test logic
```

## Next Steps

1. **Integration**: Use these endpoints in your React frontend
2. **Optimization**: Tune parameters based on real user behavior
3. **Enhancement**: Add features like time-of-day preferences, social features
4. **Monitoring**: Track algorithm performance in production

The algorithm is production-ready and can handle real user interactions! 