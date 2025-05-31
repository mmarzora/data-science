# MovieMatch Smart Algorithm Integration

This document explains how to use the integrated smart matching algorithm with the MovieMatch frontend.

## 🚀 Quick Start

### 1. Start the Backend Algorithm
```bash
cd moviematch
uvicorn src.backend.main:app --reload --host 127.0.0.1 --port 8000
```

### 2. Start the React Frontend
```bash
cd moviematch
npm start
```

### 3. Configure Backend URL (Optional)
Create a `.env` file in the `moviematch` directory:
```
REACT_APP_BACKEND_URL=http://localhost:8000
```

## 🧠 Features

### Smart Algorithm Toggle
- **Automatic Detection**: Frontend automatically detects if the algorithm backend is available
- **Fallback Mode**: If algorithm is unavailable, falls back to random movie selection
- **Real-time Toggle**: Switch between smart and random modes during session

### Algorithm-Enhanced UI

#### Status Bar
- Shows current algorithm stage (Exploration → Learning → Convergence)
- Displays interaction count and mutual likes
- Shows confidence score as algorithm learns

#### Preference Visualization
- Real-time display of learned genre preferences
- Confidence percentage
- Top 5 genre preferences with visual bars

#### Enhanced Movie Cards
- Time tracking for viewing duration
- Better visual design
- Genre tags with algorithm-aware styling

## 📊 Algorithm Stages

### 1. Exploration (0-10 interactions)
- **Purpose**: Initial preference discovery
- **Behavior**: 70% genre-based, 30% embedding-based recommendations
- **Exploration Rate**: 25% random movies for diversity

### 2. Learning (10-30 interactions)
- **Purpose**: Refine understanding of preferences
- **Behavior**: 50% genre-based, 50% embedding-based recommendations
- **Exploration Rate**: 15% random movies

### 3. Convergence (30+ interactions)
- **Purpose**: Optimize for best matches
- **Behavior**: 30% genre-based, 70% embedding-based recommendations
- **Exploration Rate**: 10% random movies

## 🔄 Data Flow

```
Frontend (React) ←→ Firebase (Session Sync) 
     ↓
Backend Algorithm ←→ Algorithm Database
     ↓
Movie Database
```

### Dual-Path Data Storage
1. **Firebase**: Session management, real-time sync, match detection
2. **Algorithm Backend**: User preferences, embeddings, recommendation engine

## 🎯 Key Components

### MatchingService (`src/services/matchingService.ts`)
```typescript
// Create algorithm session
const session = await matchingService.createSession(user1Id, user2Id);

// Get recommendations
const recs = await matchingService.getRecommendations(sessionId, 10);

// Submit feedback
await matchingService.submitFeedback(sessionId, {
  user_id: userId,
  movie_id: movieId,
  feedback_type: 'like',
  time_spent_ms: 5000
});
```

### SmartMovieMatching Component
- Replaces `MovieMatching` when algorithm is enabled
- Manages algorithm state and recommendations
- Handles dual submission (Firebase + Algorithm)

### SessionManager Integration
- Algorithm availability detection
- Smart matching toggle
- User preference persistence

## 🚧 Error Handling

### Algorithm Unavailable
- Frontend gracefully falls back to random movies
- Toggle is disabled with clear messaging
- No functionality loss

### Network Issues
- Retry mechanisms in place
- Clear error messages to users
- Maintains session continuity

## 📱 Mobile Responsiveness

All algorithm features are fully responsive:
- Collapsible status sections on mobile
- Touch-friendly toggles
- Optimized preference visualization

## 🔧 Customization

### Backend URL Configuration
```javascript
// src/services/matchingService.ts
const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';
```

### Algorithm Parameters
Modify in `src/backend/services/matching_service.py`:
```python
STAGE_THRESHOLDS = {
    'learning': 10,
    'convergence': 30
}
EXPLORATION_RATES = {
    'exploration': 0.25,
    'learning': 0.15,
    'convergence': 0.10
}
```

## 🧪 Testing

### Test Smart Matching
```bash
cd moviematch
python test_algorithm.py
```

### Test Frontend Integration
1. Start backend and frontend
2. Create session with smart matching enabled
3. Verify algorithm status bar appears
4. Submit likes/dislikes and watch preferences learn
5. Check that recommendations adapt over time

## 📈 Monitoring

### Algorithm Performance
- Session statistics endpoint: `/api/matching/sessions/{id}/stats`
- User preferences endpoint: `/api/matching/users/{id}/preferences`
- Health check: `/health`

### Frontend Metrics
- Algorithm availability detection
- Preference learning progress
- Interaction tracking with time spent

## 🔄 Deployment Notes

### Production Configuration
1. Update `REACT_APP_BACKEND_URL` to production backend
2. Ensure both Firebase and algorithm backend are accessible
3. Configure CORS for cross-origin requests
4. Set up monitoring for both services

### Environment Variables
```bash
# Frontend (.env)
REACT_APP_BACKEND_URL=https://your-backend.com

# Backend
DATABASE_URL=your_database_url
CORS_ORIGINS=https://your-frontend.com
```

## 🎬 User Experience

### First Time Users
1. Algorithm starts in exploration mode
2. Shows learning progress in real-time
3. Explains how preferences are being learned

### Returning Users
1. Preferences are persistent across sessions
2. Immediately benefits from previous learning
3. Can see their taste profile evolution

The integration provides a seamless experience that enhances movie discovery while maintaining full backward compatibility with the existing random movie selection system. 