import React, { useState, useEffect } from 'react';
import './RecommendationExplanation.css';

interface ExplanationData {
  movie_id: number;
  movie_title: string;
  explanation: string;
  reasoning: string;
  confidence: number;
}

interface RecommendationExplanationProps {
  sessionId: string;
  movieId: number;
  user1Id: string;
  user2Id: string;
  user1Name?: string;
  user2Name?: string;
  onClose?: () => void;
}

const RecommendationExplanation: React.FC<RecommendationExplanationProps> = ({
  sessionId,
  movieId,
  user1Id,
  user2Id,
  user1Name = "You",
  user2Name = "Partner",
  onClose
}) => {
  const [explanation, setExplanation] = useState<ExplanationData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchExplanation = async () => {
      try {
        setLoading(true);
        
        // Dynamic API URL configuration
        const getAPIBaseURL = () => {
          if (typeof window !== 'undefined') {
            const hostname = window.location.hostname;
            if (hostname === 'localhost' || hostname === '127.0.0.1') {
              return 'http://localhost:8000';
            } else {
              // Use the network IP for cross-device access
              return 'http://192.168.1.13:8000';
            }
          }
          return 'http://localhost:8000';
        };

        const response = await fetch(
          `${getAPIBaseURL()}/api/matching/explain/${sessionId}/${movieId}?user1_id=${user1Id}&user2_id=${user2Id}`
        );

        if (!response.ok) {
          throw new Error('Failed to fetch explanation');
        }

        const data = await response.json();
        setExplanation(data);
      } catch (err: any) {
        console.error('Error fetching explanation:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchExplanation();
  }, [sessionId, movieId, user1Id, user2Id]);

  if (loading) {
    return (
      <div className="explanation-modal">
        <div className="explanation-content">
          <div className="explanation-loading">
            <div className="loading-spinner"></div>
            <p>Analyzing recommendation...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error || !explanation) {
    return (
      <div className="explanation-modal">
        <div className="explanation-content">
          <div className="explanation-header">
            <h3>Explanation Not Available</h3>
            {onClose && <button className="close-btn" onClick={onClose}>×</button>}
          </div>
          <p>Unable to explain this recommendation: {error || 'Unknown error'}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="explanation-modal">
      <div className="explanation-content">
        <div className="explanation-header">
          <h3>🤔 Why "{explanation.movie_title}"?</h3>
          {onClose && <button className="close-btn" onClick={onClose}>×</button>}
        </div>
        <div className="primary-explanation">
          <h4>📝 Main Reason</h4>
          <p className="explanation-text">{explanation.explanation}</p>
        </div>
        <div className="confidence-section">
          <h4>🔍 Reasoning</h4>
          <p>{explanation.reasoning}</p>
        </div>
        <div className="confidence-section">
          <h4>📈 Confidence</h4>
          <p>{(explanation.confidence * 100).toFixed(0)}%</p>
        </div>
      </div>
    </div>
  );
};

export default RecommendationExplanation; 