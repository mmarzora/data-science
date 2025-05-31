import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import { auth, db } from './firebase';
import { onAuthStateChanged } from 'firebase/auth';
import { collection, getDocs, enableNetwork, disableNetwork } from 'firebase/firestore';
import SessionManager from './components/SessionManager';
import MovieMatching from './components/MovieMatching';
import { Session, sessionService } from './services/sessionService';

function App() {
  const [user, setUser] = useState<any>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [firebaseError, setFirebaseError] = useState<string | null>(null);
  const [isConnecting, setIsConnecting] = useState(true);
  const [memberId, setMemberId] = useState<string>(() => 
    localStorage.getItem('memberId') || ''
  );

  // Ref to store unsubscribe function for Firestore listener
  const unsubscribeRef = useRef<null | (() => void)>(null);

  // Test and manage Firebase connection
  useEffect(() => {
    let retryCount = 0;
    const maxRetries = 3;

    const testFirebase = async () => {
      try {
        setIsConnecting(true);
        console.log('Testing Firebase connection...');
        await enableNetwork(db);
        const testCollection = collection(db, 'sessions');
        await getDocs(testCollection);
        console.log('Firebase connection successful');
        setFirebaseError(null);
        setIsConnecting(false);
      } catch (error: any) {
        console.error('Firebase connection error:', error);
        if (retryCount < maxRetries) {
          retryCount++;
          console.log(`Retrying connection (attempt ${retryCount}/${maxRetries})...`);
          await disableNetwork(db);
          setTimeout(testFirebase, 2000);
        } else {
          setFirebaseError(`Failed to connect to Firebase: ${error.message}`);
          setIsConnecting(false);
        }
      }
    };

    testFirebase();
    return () => {
      disableNetwork(db).catch(console.error);
    };
  }, []);

  // Authentication listener
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      if (user) {
        setUser(user);
      } else {
        setUser(null);
      }
    });
    return () => unsubscribe();
  }, []);

  // Real-time Firestore session listener
  useEffect(() => {
    // Clean up previous listener
    if (unsubscribeRef.current) {
      unsubscribeRef.current();
      unsubscribeRef.current = null;
    }
    if (session) {
      unsubscribeRef.current = sessionService.subscribeToSession(session.code, (updatedSession) => {
        if (updatedSession) setSession(updatedSession);
      });
    }
    return () => {
      if (unsubscribeRef.current) {
        unsubscribeRef.current();
        unsubscribeRef.current = null;
      }
    };
  }, [session?.code]);

  const handleSessionStart = (newSession: Session) => {
    console.log('Session started:', newSession);
    setSession(newSession);
    if (newSession.members.length > 0) {
      const currentMemberId = newSession.members[newSession.members.length - 1];
      setMemberId(currentMemberId);
      localStorage.setItem('memberId', currentMemberId);
    }
  };

  if (isConnecting) {
    return (
      <div className="App">
        <header className="App-header">
          <h1>MovieMatch</h1>
        </header>
        <main>
          <div className="loading">
            <p>Connecting to server...</p>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>MovieMatch</h1>
      </header>
      <main>
        {firebaseError ? (
          <div className="error-message">
            <p>{firebaseError}</p>
            <button onClick={() => window.location.reload()}>
              Try Again
            </button>
          </div>
        ) : !session ? (
          <SessionManager onSessionStart={handleSessionStart} />
        ) : (
          <div className="session-active">
            <div className="session-info">
              <h2>Session Code: {session.code}</h2>
              <p>Share this code with your movie partner!</p>
            </div>
            <MovieMatching session={session} memberId={memberId} />
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
