import { initializeApp } from 'firebase/app';
import { getFirestore, enableIndexedDbPersistence } from 'firebase/firestore';
import { getAuth } from 'firebase/auth';
import { getStorage } from 'firebase/storage';

// Your web app's Firebase configuration
const firebaseConfig = {
    apiKey: "AIzaSyDOKm1NK5bg2ssvdYhyYV-mLhoyuknaH9I",
    authDomain: "movie-match-16db7.firebaseapp.com",
    projectId: "movie-match-16db7",
    storageBucket: "movie-match-16db7.appspot.com",
    messagingSenderId: "1086358558339",
    appId: "1:1086358558339:web:55a8dd53aa94d1f6d52db6"
};

console.log('Initializing Firebase with config:', { ...firebaseConfig, apiKey: '[HIDDEN]' });

// Initialize Firebase
const app = initializeApp(firebaseConfig);
console.log('Firebase app initialized successfully');

// Initialize Firestore with settings
const db = getFirestore(app);

// Enable offline persistence
enableIndexedDbPersistence(db)
  .then(() => {
    console.log('Firestore persistence enabled');
  })
  .catch((err) => {
    if (err.code === 'failed-precondition') {
      console.warn('Multiple tabs open, persistence can only be enabled in one tab at a time.');
    } else if (err.code === 'unimplemented') {
      console.warn('The current browser does not support persistence.');
    }
  });

// Initialize other services
const auth = getAuth(app);
const storage = getStorage(app);

export { db, auth, storage };
export default app; 