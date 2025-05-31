import React, { useEffect, useState, useCallback, useMemo, useRef } from 'react';
import { Movie } from '../services/movieService';
import { sessionService, Session } from '../services/sessionService';
import { 
  matchingService, 
  RecommendationsResponse, 
  SessionStats,
  UserPreferences 
} from '../services/matchingService';
import { movieService } from '../services/movieService';
import UserHistory from './UserHistory';
import PreferencesComparison from './PreferencesComparison';
import './SmartMovieMatching.css';

interface SmartMovieMatchingProps {
  session: Session;
  memberId: string;
}

const SmartMovieMatching: React.FC<SmartMovieMatchingProps> = ({ session, memberId }) => {
  // Refs for state management
  const mountedRef = useRef(true);
  const swipeStartTimeRef = useRef<number>(0);
  
  // States
  const [currentMovie, setCurrentMovie] = useState<Movie | null>(null);
  const [movieQueue, setMovieQueue] = useState<Movie[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showHistory, setShowHistory] = useState(false);
  const [matchFound, setMatchFound] = useState<Movie | null>(null);
  const [isPosterLoading, setIsPosterLoading] = useState(true);
  const [isProcessingSwipe, setIsProcessingSwipe] = useState(false);
  const [showPreferences, setShowPreferences] = useState(false);
  const [loadingMatchedMovie, setLoadingMatchedMovie] = useState(false);
  
  // Algorithm-specific states
  const [matchingSessionId, setMatchingSessionId] = useState<string | null>(null);
  const [algorithmState, setAlgorithmState] = useState<RecommendationsResponse | null>(null);
  const [sessionStats, setSessionStats] = useState<SessionStats | null>(null);
  const [userPreferences, setUserPreferences] = useState<UserPreferences | null>(null);
  const [algorithmEnabled, setAlgorithmEnabled] = useState(false);

  const otherMemberId = useMemo(() => 
    session.members.find(id => id !== memberId),
    [session.members, memberId]
  );

  // Add a ref to track previous render state to reduce logging
  const prevRenderStateRef = useRef<string>('');

  // Reset mounted ref
  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
    };
  }, []);

  // Clear error state after 5 seconds
  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => {
        if (mountedRef.current) {
          setError(null);
        }
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [error]);

  // Initialize matching session when both users are present
  useEffect(() => {
    const initializeMatchingSession = async () => {
      if (!otherMemberId || matchingSessionId) return;

      try {
        console.log('Initializing matching session...');
        const response = await matchingService.createSession(memberId, otherMemberId);
        setMatchingSessionId(response.session_id);
        setAlgorithmEnabled(true);
        console.log('Matching session created:', response.session_id);
      } catch (error: any) {
        console.warn('Algorithm not available, falling back to random movies:', error.message);
        setAlgorithmEnabled(false);
      }
    };

    initializeMatchingSession();
  }, [memberId, otherMemberId, matchingSessionId]);

  // Load initial recommendations - Memoized to reduce re-renders
  const loadRecommendations = useCallback(async () => {
    if (!matchingSessionId) return;

    try {
      setLoading(true);
      const recommendations = await matchingService.getRecommendations(matchingSessionId, 10);
      
      if (mountedRef.current) {
        setAlgorithmState(recommendations);
        setMovieQueue(recommendations.movies);
        // Only set currentMovie if it is null and there are movies
        if (currentMovie === null && recommendations.movies.length > 0) {
          console.log('[setCurrentMovie] Setting to first movie from recommendations:', recommendations.movies[0]);
          setCurrentMovie(recommendations.movies[0]);
        }
      }
    } catch (error: any) {
      console.error('Failed to load recommendations:', error);
      setError('Failed to load personalized recommendations');
    } finally {
      if (mountedRef.current) {
        setLoading(false);
      }
    }
  }, [matchingSessionId, currentMovie]);

  // Load recommendations when session is ready
  useEffect(() => {
    if (matchingSessionId && algorithmEnabled) {
      loadRecommendations();
    }
  }, [matchingSessionId, algorithmEnabled, loadRecommendations]);

  // Load session stats periodically - Optimized for stability
  useEffect(() => {
    if (!matchingSessionId) return;

    const loadStats = async () => {
      try {
        const stats = await matchingService.getSessionStats(matchingSessionId);
        const prefs = await matchingService.getUserPreferences(memberId);
        
        if (mountedRef.current) {
          // Only update if data has actually changed to prevent unnecessary re-renders
          setSessionStats(prevStats => {
            if (JSON.stringify(prevStats) !== JSON.stringify(stats)) {
              return stats;
            }
            return prevStats;
          });
          
          setUserPreferences(prevPrefs => {
            if (JSON.stringify(prevPrefs) !== JSON.stringify(prefs)) {
              return prefs;
            }
            return prevPrefs;
          });
        }
      } catch (error) {
        console.error('Failed to load stats:', error);
      }
    };

    loadStats();
    // Increased interval to reduce frequent updates
    const interval = setInterval(loadStats, 30000); // Update every 30 seconds instead of 10
    return () => clearInterval(interval);
  }, [matchingSessionId, memberId]);

  // Handle movie swipe with algorithm feedback
  const handleSwipe = useCallback(async (movieId: number, liked: boolean) => {
    if (isProcessingSwipe || !currentMovie) return;

    setIsProcessingSwipe(true);
    const timeSpent = Date.now() - swipeStartTimeRef.current;

    try {
      // Submit to Firebase (existing functionality)
      await sessionService.updateMovieSwipe(session.id, memberId, movieId, liked);

      // Submit to algorithm if enabled
      if (matchingSessionId && algorithmEnabled) {
        const feedbackType = liked ? 'like' : 'dislike';
        await matchingService.submitFeedback(matchingSessionId, {
          user_id: memberId,
          movie_id: movieId,
          feedback_type: feedbackType,
          time_spent_ms: timeSpent
        });

        // Load fresh recommendations after feedback
        setTimeout(() => {
          loadRecommendations();
        }, 1000);
      }

      // Move to next movie
      const currentIndex = movieQueue.findIndex(m => m.id === movieId);
      const nextIndex = currentIndex + 1;
      
      if (nextIndex < movieQueue.length) {
        console.log('[setCurrentMovie] Advancing to next movie in queue:', movieQueue[nextIndex]);
        setCurrentMovie(movieQueue[nextIndex]);
      } else {
        // No more movies in queue, set to null and wait for new recommendations
        console.log('[setCurrentMovie] No more movies in queue, setting to null');
        setCurrentMovie(null);
        // Load more recommendations
        await loadRecommendations();
      }

    } catch (error: any) {
      console.error('Error processing swipe:', error);
      setError('Failed to process swipe');
    } finally {
      setIsProcessingSwipe(false);
    }
  }, [
    isProcessingSwipe, 
    currentMovie, 
    session.id, 
    memberId, 
    matchingSessionId, 
    algorithmEnabled,
    movieQueue,
    loadRecommendations
  ]);

  // Handle like button
  const handleLike = useCallback(() => {
    if (currentMovie) {
      handleSwipe(currentMovie.id, true);
    }
  }, [currentMovie, handleSwipe]);

  // Handle dislike button
  const handleDislike = useCallback(() => {
    if (currentMovie) {
      handleSwipe(currentMovie.id, false);
    }
  }, [currentMovie, handleSwipe]);

  // Track time spent viewing each movie
  useEffect(() => {
    if (currentMovie) {
      swipeStartTimeRef.current = Date.now();
    }
  }, [currentMovie]);

  // Check for matches in Firebase - Optimized to reduce re-renders
  const checkForMatches = useCallback(async () => {
    if (!session.matches || session.matches.length === 0) {
      // Only log once when there are no matches, not repeatedly
      return;
    }

    const latestMatchId = session.matches[session.matches.length - 1];
    
    // Check if this user liked the matched movie
    const userHistory = session.userHistory[memberId] || [];
    const userLikedMatch = userHistory.some(h => h.movieId === latestMatchId && h.decision);
    
    // Check if the other user also liked the matched movie
    const otherUserHistory = otherMemberId ? (session.userHistory[otherMemberId] || []) : [];
    const otherUserLikedMatch = otherUserHistory.some(h => h.movieId === latestMatchId && h.decision);
    
    // Only show match modal if:
    // 1. This user liked the movie
    // 2. The other user also liked the movie (mutual like)
    // 3. We haven't already shown this match
    if (userLikedMatch && otherUserLikedMatch && (!matchFound || matchFound.id !== latestMatchId)) {
      console.log('🎉 Match detected!', { 
        movieId: latestMatchId, 
        userLiked: userLikedMatch, 
        otherUserLiked: otherUserLikedMatch,
        memberId,
        otherMemberId 
      });
      
      setLoadingMatchedMovie(true);
      
      try {
        // First try to find the movie in our current queue
        let matchedMovie = movieQueue.find(m => m.id === latestMatchId);
        
        // If not found in queue, try to fetch from algorithm recommendations if available
        if (!matchedMovie && matchingSessionId) {
          try {
            const recommendations = await matchingService.getRecommendations(matchingSessionId, 50);
            matchedMovie = recommendations.movies.find(m => m.id === latestMatchId);
          } catch (error) {
            console.warn('Could not fetch from algorithm:', error);
          }
        }
        
        // If still not found, use current movie as fallback (shouldn't happen often)
        if (!matchedMovie && currentMovie?.id === latestMatchId) {
          matchedMovie = currentMovie;
        }
        
        // Final fallback: fetch movie details directly from the movie service
        if (!matchedMovie) {
          try {
            console.log('🔍 Fetching movie details from movie service for ID:', latestMatchId);
            const movieFromService = await movieService.getMovieDetails(latestMatchId);
            if (movieFromService) {
              matchedMovie = movieFromService;
            }
          } catch (error) {
            console.warn('Could not fetch movie details from movie service:', error);
          }
        }
        
        if (matchedMovie) {
          console.log('📽️ Showing match modal for movie:', matchedMovie.title);
          console.log('📽️ Movie data:', {
            title: matchedMovie.title,
            poster_url: matchedMovie.poster_url,
            description: matchedMovie.description,
            genres: matchedMovie.genres,
            release_year: matchedMovie.release_year
          });
          setMatchFound(matchedMovie);
        } else {
          console.warn('⚠️ Could not find movie data for match:', latestMatchId);
        }
      } catch (error) {
        console.error('Error retrieving matched movie:', error);
      } finally {
        setLoadingMatchedMovie(false);
      }
    }
  }, [session.matches, session.userHistory, memberId, otherMemberId, matchFound, matchingSessionId, movieQueue, currentMovie]);

  useEffect(() => {
    checkForMatches();
  }, [checkForMatches]);

  // Only log renders when state actually changes
  const currentRenderState = JSON.stringify({
    currentMovie: currentMovie?.title,
    algorithmEnabled,
    matchingSessionId,
    sessionMatches: session.matches?.length || 0,
    userHistoryLength: (session.userHistory[memberId] || []).length
  });

  if (prevRenderStateRef.current !== currentRenderState) {
    console.log('🎬 Rendering SmartMovieMatching with:', { 
      currentMovie: currentMovie?.title, 
      algorithmEnabled, 
      matchingSessionId,
      sessionMatches: session.matches?.length || 0,
      userHistoryLength: (session.userHistory[memberId] || []).length
    });
    prevRenderStateRef.current = currentRenderState;
  }

  if (loading) {
    return (
      <div className="movie-matching">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading personalized recommendations...</p>
          {algorithmEnabled && (
            <small>Powered by MovieMatch Algorithm</small>
          )}
          {/* Debug info */}
          <div style={{ marginTop: '20px', fontSize: '0.8rem', color: 'rgba(255,255,255,0.7)' }}>
            Debug: Session ID: {session.id}, Member ID: {memberId}, Other Member: {otherMemberId || 'waiting...'}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="movie-matching">
        <div className="error-container">
          <p className="error-message">{error}</p>
          <button onClick={loadRecommendations} className="retry-button">
            Try Again
          </button>
          {/* Debug info */}
          <div style={{ marginTop: '20px', fontSize: '0.8rem', color: '#6c757d' }}>
            Debug: Algorithm enabled: {algorithmEnabled ? 'Yes' : 'No'}, Session: {matchingSessionId || 'None'}
          </div>
        </div>
      </div>
    );
  }

  if (!currentMovie) {
    return (
      <div className="movie-matching">
        <div className="no-movies-container">
          <p>No more movies available</p>
          <button onClick={loadRecommendations} className="retry-button">
            Load More
          </button>
          {/* Debug info */}
          <div style={{ marginTop: '20px', fontSize: '0.8rem', color: '#6c757d' }}>
            Debug: Queue length: {movieQueue.length}, Algorithm: {algorithmEnabled ? 'enabled' : 'disabled'}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="movie-matching">
      {/* Algorithm Status Bar */}
      {algorithmEnabled && algorithmState && (
        <div className="algorithm-status">
          <div className="status-info">
            <span className={`stage-badge stage-${algorithmState.session_stage}`}>
              {algorithmState.session_stage.toUpperCase()}
            </span>
            <span className="interactions">
              {algorithmState.total_interactions} interactions
            </span>
            {algorithmState.mutual_likes > 0 && (
              <span className="mutual-likes">
                🎯 {algorithmState.mutual_likes} mutual likes
              </span>
            )}
          </div>
          {userPreferences && userPreferences.confidence_score > 0 && (
            <div className="confidence-score">
              Confidence: {(userPreferences.confidence_score * 100).toFixed(0)}%
            </div>
          )}
        </div>
      )}

      {/* Preferences Comparison */}
      {algorithmEnabled && matchingSessionId && otherMemberId && showPreferences && (
        <PreferencesComparison
          user1Id={memberId}
          user2Id={otherMemberId}
          user1Name="You"
          user2Name="Partner"
          matchingSessionId={matchingSessionId}
        />
      )}

      {/* Movie Card */}
      <div className="movie-card">
        {isPosterLoading && (
          <div className="poster-loading">
            <div className="loading-spinner"></div>
          </div>
        )}
        
        <img
          src={currentMovie.poster_url || '/placeholder-poster.jpg'}
          alt={`${currentMovie.title} poster`}
          className="movie-poster"
          onLoad={() => setIsPosterLoading(false)}
          onError={() => setIsPosterLoading(false)}
          style={{ display: isPosterLoading ? 'none' : 'block' }}
        />
        
        <div className="movie-info">
          <h2 className="movie-title">{currentMovie.title}</h2>
          <div className="movie-meta">
            <span className="movie-year">{currentMovie.release_year}</span>
            <span className="movie-rating">⭐ {currentMovie.rating}</span>
            {currentMovie.runtime_minutes && (
              <span className="movie-runtime">{currentMovie.runtime_minutes}min</span>
            )}
          </div>
          
          {currentMovie.genres && (
            <div className="movie-genres">
              {(Array.isArray(currentMovie.genres) ? currentMovie.genres : JSON.parse(currentMovie.genres)).map((genre: string) => (
                <span key={genre} className="genre-tag">{genre}</span>
              ))}
            </div>
          )}
          
          {currentMovie.description && (
            <p className="movie-description">{currentMovie.description}</p>
          )}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="action-buttons">
        <button
          className="dislike-button"
          onClick={handleDislike}
          disabled={isProcessingSwipe}
        >
          👎 Pass
        </button>
        
        <button
          className="like-button"
          onClick={handleLike}
          disabled={isProcessingSwipe}
        >
          👍 Like
        </button>
      </div>

      {/* Toggle Buttons */}
      <div className="toggle-buttons">
        {algorithmEnabled && otherMemberId && (
          <button
            className="preferences-toggle"
            onClick={() => setShowPreferences(!showPreferences)}
          >
            {showPreferences ? 'Hide Preferences' : 'Show Taste Profiles'}
          </button>
        )}
        
        <button
          className="history-toggle"
          onClick={() => setShowHistory(!showHistory)}
        >
          {showHistory ? 'Hide History' : 'Show History'}
        </button>
      </div>

      {/* User History */}
      {showHistory && (
        <UserHistory
          history={session.userHistory[memberId] || []}
          movies={{}} // Empty for now, would need to load movie details
          onClose={() => setShowHistory(false)}
        />
      )}

      {/* Match Found Modal */}
      {matchFound && (
        <div className="match-modal-overlay" onClick={() => setMatchFound(null)}>
          <div className="match-modal" onClick={e => e.stopPropagation()}>
            {/* 1. Celebration message */}
            <div className="match-celebration">
              <div className="celebration-text">🎉 IT'S A MATCH! 🎉</div>
              <div className="celebration-subtitle">You both loved this movie!</div>
            </div>

            {/* 2. Movie card (vertical layout) */}
            <div className="matched-movie-card vertical">
              <div className="matched-poster-container">
                <img
                  src={matchFound.poster_url || '/placeholder-poster.jpg'}
                  alt={`${matchFound.title} poster`}
                  className="matched-poster"
                  onError={(e) => {
                    console.log('🖼️ Poster failed to load:', matchFound.poster_url);
                    (e.target as HTMLImageElement).src = '/placeholder-poster.jpg';
                  }}
                  onLoad={() => {
                    console.log('🖼️ Poster loaded successfully:', matchFound.poster_url);
                  }}
                />
              </div>
              <div className="matched-movie-details">
                <h3 className="matched-title">{matchFound.title || 'Unknown Title'}</h3>
                <div className="matched-meta">
                  {matchFound.release_year && (
                    <span className="matched-year">{matchFound.release_year}</span>
                  )}
                  {matchFound.rating && (
                    <span className="matched-rating">⭐ {matchFound.rating}</span>
                  )}
                  {matchFound.runtime_minutes && (
                    <span className="matched-runtime">{matchFound.runtime_minutes}min</span>
                  )}
                </div>
                {matchFound.genres && (
                  <div className="matched-genres">
                    {(Array.isArray(matchFound.genres) 
                      ? matchFound.genres 
                      : JSON.parse(matchFound.genres || '[]')).slice(0, 3).map((genre: string) => (
                      <span key={genre} className="matched-genre-tag">{genre}</span>
                    ))}
                  </div>
                )}
                {matchFound.description && (
                  <p className="matched-description">
                    {matchFound.description.length > 150 
                      ? `${matchFound.description.substring(0, 150)}...` 
                      : matchFound.description}
                  </p>
                )}
              </div>
            </div>

            {/* 3. Continue Swiping button */}
            <div className="match-actions">
              <button 
                className="close-match-button"
                onClick={() => setMatchFound(null)}
              >
                Continue Swiping
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Loading Match Modal */}
      {loadingMatchedMovie && (
        <div className="match-modal-overlay">
          <div className="match-modal loading-match">
            <div className="loading-spinner"></div>
            <p>Loading match details...</p>
          </div>
        </div>
      )}
      
      {isProcessingSwipe && (
        <div className="processing-overlay">
          <div className="loading-spinner"></div>
        </div>
      )}
    </div>
  );
};

export default SmartMovieMatching;