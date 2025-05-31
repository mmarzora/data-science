import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import { v4 as uuidv4 } from 'uuid';
import SessionCreate from './SessionCreate';
import SessionJoin from './SessionJoin';
import { sessionService, Session } from '../services/sessionService';

interface SessionManagerProps {
  onSessionStart: (session: Session) => void;
}

const SessionManager: React.FC<SessionManagerProps> = ({ onSessionStart }) => {
  const memberIdRef = useRef<string>(uuidv4());
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [sessionCode, setSessionCode] = useState<string | null>(null);
  const [currentSession, setCurrentSession] = useState<Session | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSessionUpdate = useCallback((updatedSession: Session | null) => {
    console.log('[SessionManager] Firestore update received:', updatedSession);
    if (updatedSession) {
      setCurrentSession(updatedSession);
      setSessionCode(updatedSession.code);
      onSessionStart(updatedSession);
    }
  }, [onSessionStart]);

  useEffect(() => {
    if (!sessionId || !memberIdRef.current) return;
    return sessionService.subscribeToSession(sessionId, handleSessionUpdate);
  }, [sessionId, handleSessionUpdate]);

  const handleSessionCreated = useCallback(async (id: string, code: string) => {
    setSessionId(id);
    setSessionCode(code);
    
    try {
      const session = await sessionService.joinSession(code, memberIdRef.current);
      handleSessionUpdate(session);
    } catch (error) {
      console.error('Failed to create session:', error);
    }
  }, [handleSessionUpdate]);

  const handleSessionJoined = useCallback(async (id: string) => {
    if (sessionId === id) return;

    setSessionId(id);
    
    try {
      const session = await sessionService.joinSession(id, memberIdRef.current);
      handleSessionUpdate(session);
    } catch (error) {
      console.error('Failed to join session:', error);
      setSessionId(null);
      setSessionCode(null);
      setCurrentSession(null);
    }
  }, [sessionId, handleSessionUpdate]);

  const handleManualRefresh = useCallback(async () => {
    if (!sessionId) return;

    setIsRefreshing(true);
    try {
      const session = await sessionService.joinSession(sessionId, memberIdRef.current);
      handleSessionUpdate(session);
    } catch (err) {
      console.error('Manual refresh error:', err);
      setError('Failed to refresh session.');
    } finally {
      setIsRefreshing(false);
    }
  }, [sessionId, handleSessionUpdate]);

  const otherMemberId = useMemo(() => 
    currentSession?.members.find(id => id !== memberIdRef.current),
    [currentSession?.members]
  );

  const isSessionReady = useMemo(() => 
    currentSession?.members.length === 2,
    [currentSession?.members.length]
  );

  const sessionStyles = useMemo(() => ({
    container: {
      display: 'flex', 
      flexDirection: 'column' as const,
      gap: '10px',
      marginBottom: '20px',
      padding: '15px',
      backgroundColor: '#f8f9fa',
      borderRadius: '8px',
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
      position: 'relative' as const
    },
    header: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center'
    },
    code: {
      fontSize: '24px', 
      fontWeight: 'bold' as const,
      margin: '10px 0'
    },
    testButton: {
      position: 'absolute' as const,
      top: '10px',
      right: '10px',
      padding: '10px 20px',
      backgroundColor: 'red',
      color: 'white',
      border: 'none',
      borderRadius: '4px',
      cursor: 'pointer',
      zIndex: 9999,
      fontWeight: 'bold' as const
    },
    refreshButton: {
      padding: '10px 20px',
      backgroundColor: '#4a90e2',
      color: 'white',
      border: 'none',
      borderRadius: '8px',
      cursor: isRefreshing ? 'not-allowed' : 'pointer',
      display: 'flex',
      alignItems: 'center',
      gap: '8px',
      opacity: isRefreshing ? 0.7 : 1,
      transition: 'all 0.2s ease',
      fontSize: '16px',
      fontWeight: 'bold' as const,
      zIndex: 1000
    }
  }), [isRefreshing]);

  if (!sessionCode) {
    return (
      <>
        <SessionCreate 
          onSessionCreated={handleSessionCreated} 
          userId={memberIdRef.current}
        />
        <div className="divider">or</div>
        <SessionJoin 
          onSessionJoined={handleSessionJoined}
          memberId={memberIdRef.current}
        />
      </>
    );
  }

  return (
    <div className="session-manager">
      <div className="session-code">
        <div style={sessionStyles.container}>
          <button style={sessionStyles.testButton}>
            Test Button
          </button>
          <div style={sessionStyles.header}>
            <h2 style={{ margin: 0 }}>Your Session Code</h2>
            <button 
              onClick={handleManualRefresh}
              className="refresh-button"
              disabled={isRefreshing}
              style={sessionStyles.refreshButton}
            >
              <span style={{ 
                display: 'inline-block',
                animation: isRefreshing ? 'spin 1s linear infinite' : 'none'
              }}>
                🔄
              </span>
              {isRefreshing ? 'Refreshing...' : 'Refresh Session'}
            </button>
          </div>
          <p className="code" style={sessionStyles.code}>{sessionCode}</p>
          <p style={{ margin: 0 }}>Share this code with your movie partner!</p>
        </div>
        {currentSession && (
          <div className="session-status" style={{ position: 'relative' }}>
            <button style={sessionStyles.testButton}>
              Test Button
            </button>
            <p className="members-count">
              Members in session: {currentSession.members.length}/2
            </p>
            <p className="member-id">
              Your ID: {memberIdRef.current.slice(0, 8)}...
            </p>
            {isSessionReady ? (
              <p className="other-member">
                Paired with: {otherMemberId?.slice(0, 8)}...
              </p>
            ) : (
              <p className="waiting-message">Waiting for partner to join...</p>
            )}
          </div>
        )}
      </div>

      <style>
        {`
          @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
          .session-manager {
            position: relative;
          }
          .refresh-button:hover {
            background-color: #357abd !important;
            transform: translateY(-1px);
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
          }
        `}
      </style>
    </div>
  );
};

export default React.memo(SessionManager); 