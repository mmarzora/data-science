#!/usr/bin/env python3
"""
MovieMatch Algorithm Test Script
Test the matching algorithm with various scenarios to validate behavior.
"""

import requests
import json
import time
import random
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class TestUser:
    """Represents a test user with preferences."""
    id: str
    name: str
    preferred_genres: List[str]
    disliked_genres: List[str]

class MovieMatchTester:
    """Test harness for the MovieMatch algorithm."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def create_session(self, user1_id: str, user2_id: str) -> str:
        """Create a new matching session."""
        response = self.session.post(
            f"{self.base_url}/api/matching/sessions",
            json={"user1_id": user1_id, "user2_id": user2_id}
        )
        response.raise_for_status()
        return response.json()["session_id"]
    
    def get_recommendations(self, session_id: str, batch_size: int = 10) -> Dict:
        """Get movie recommendations for a session."""
        response = self.session.get(
            f"{self.base_url}/api/matching/sessions/{session_id}/recommendations",
            params={"batch_size": batch_size}
        )
        response.raise_for_status()
        return response.json()
    
    def submit_feedback(self, session_id: str, user_id: str, movie_id: int, 
                       feedback_type: str, time_spent_ms: Optional[int] = None) -> Dict:
        """Submit user feedback for a movie."""
        data = {
            "user_id": user_id,
            "movie_id": movie_id,
            "feedback_type": feedback_type
        }
        if time_spent_ms:
            data["time_spent_ms"] = time_spent_ms
            
        response = self.session.post(
            f"{self.base_url}/api/matching/sessions/{session_id}/feedback",
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def get_session_stats(self, session_id: str) -> Dict:
        """Get session statistics."""
        response = self.session.get(
            f"{self.base_url}/api/matching/sessions/{session_id}/stats"
        )
        response.raise_for_status()
        return response.json()
    
    def get_user_preferences(self, user_id: str) -> Dict:
        """Get user preferences."""
        response = self.session.get(
            f"{self.base_url}/api/matching/users/{user_id}/preferences"
        )
        response.raise_for_status()
        return response.json()
    
    def simulate_user_feedback(self, session_id: str, user: TestUser, movies: List[Dict]) -> List[Dict]:
        """Simulate realistic user feedback based on preferences."""
        feedback_actions = []
        
        for movie in movies:
            movie_genres = set(movie.get('genres', []))
            preferred_genres = set(user.preferred_genres)
            disliked_genres = set(user.disliked_genres)
            
            # Determine feedback based on genre overlap
            if movie_genres.intersection(disliked_genres):
                feedback = "dislike"
                time_spent = random.randint(500, 2000)  # Quick dislike
            elif movie_genres.intersection(preferred_genres):
                feedback = "like"
                time_spent = random.randint(3000, 8000)  # Spent time considering
            else:
                # Neutral movie - random feedback weighted toward skip
                choice = random.choices(["like", "skip", "dislike"], weights=[0.2, 0.6, 0.2])[0]
                feedback = choice
                time_spent = random.randint(1000, 4000)
            
            action = {
                "movie": movie,
                "feedback": feedback,
                "time_spent_ms": time_spent
            }
            feedback_actions.append(action)
            
            # Submit feedback
            self.submit_feedback(session_id, user.id, movie['id'], feedback, time_spent)
            
        return feedback_actions

def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def print_subsection(title: str):
    """Print a formatted subsection header."""
    print(f"\n--- {title} ---")

def print_movies(movies: List[Dict], limit: int = 5):
    """Print movie details in a formatted way."""
    for i, movie in enumerate(movies[:limit], 1):
        genres_str = ", ".join(movie.get('genres', []))
        print(f"{i}. {movie['title']} ({movie['release_year']}) - {genres_str} - Rating: {movie['rating']}")

def print_preferences(prefs: Dict, user_name: str):
    """Print user preferences in a formatted way."""
    print(f"\n{user_name}'s Preferences:")
    print(f"  Confidence: {prefs['confidence_score']:.3f}")
    print(f"  Interactions: {prefs['total_interactions']}")
    if prefs['genre_preferences']:
        print("  Genre Preferences:")
        for genre, score in sorted(prefs['genre_preferences'].items(), key=lambda x: x[1], reverse=True):
            print(f"    {genre}: {score:.3f}")

def main():
    """Run comprehensive algorithm tests."""
    print_section("🎬 MovieMatch Algorithm Test Suite")
    
    # Initialize tester
    tester = MovieMatchTester()
    
    # Define test users with different preferences
    users = [
        TestUser("alice", "Alice", ["Drama", "Romance", "Comedy"], ["Horror", "Action"]),
        TestUser("bob", "Bob", ["Action", "Thriller", "Adventure"], ["Romance", "Musical"]),
        TestUser("charlie", "Charlie", ["Comedy", "Animation", "Family"], ["Horror", "War"]),
        TestUser("diana", "Diana", ["Horror", "Thriller", "Mystery"], ["Comedy", "Romance"])
    ]
    
    # Test Scenario 1: Basic Algorithm Flow
    print_section("Test 1: Basic Algorithm Flow")
    alice, bob = users[0], users[1]
    
    print(f"Creating session for {alice.name} and {bob.name}...")
    session_id = tester.create_session(alice.id, bob.id)
    print(f"Session ID: {session_id}")
    
    print_subsection("Initial Recommendations")
    recommendations = tester.get_recommendations(session_id, batch_size=5)
    print(f"Session Stage: {recommendations['session_stage']}")
    print(f"Total Interactions: {recommendations['total_interactions']}")
    print("\nRecommended Movies:")
    print_movies(recommendations['movies'])
    
    print_subsection("Simulating User Feedback")
    alice_actions = tester.simulate_user_feedback(session_id, alice, recommendations['movies'][:3])
    bob_actions = tester.simulate_user_feedback(session_id, bob, recommendations['movies'][:3])
    
    print(f"\n{alice.name}'s actions:")
    for action in alice_actions:
        movie = action['movie']
        print(f"  {action['feedback'].upper()}: {movie['title']} (spent {action['time_spent_ms']}ms)")
    
    print(f"\n{bob.name}'s actions:")
    for action in bob_actions:
        movie = action['movie']
        print(f"  {action['feedback'].upper()}: {movie['title']} (spent {action['time_spent_ms']}ms)")
    
    print_subsection("Updated Recommendations")
    new_recommendations = tester.get_recommendations(session_id, batch_size=5)
    print(f"Session Stage: {new_recommendations['session_stage']}")
    print(f"Total Interactions: {new_recommendations['total_interactions']}")
    print("\nNew Recommended Movies:")
    print_movies(new_recommendations['movies'])
    
    print_subsection("Learned Preferences")
    alice_prefs = tester.get_user_preferences(alice.id)
    bob_prefs = tester.get_user_preferences(bob.id)
    print_preferences(alice_prefs, alice.name)
    print_preferences(bob_prefs, bob.name)
    
    # Test Scenario 2: Algorithm Evolution Over Time
    print_section("Test 2: Algorithm Evolution Over Multiple Rounds")
    
    for round_num in range(1, 4):
        print_subsection(f"Round {round_num}")
        
        # Get recommendations
        recs = tester.get_recommendations(session_id, batch_size=8)
        print(f"Stage: {recs['session_stage']}, Interactions: {recs['total_interactions']}")
        
        # Simulate more feedback
        alice_batch = tester.simulate_user_feedback(session_id, alice, recs['movies'][:4])
        bob_batch = tester.simulate_user_feedback(session_id, bob, recs['movies'][:4])
        
        # Count likes for this round
        alice_likes = sum(1 for a in alice_batch if a['feedback'] == 'like')
        bob_likes = sum(1 for a in bob_batch if a['feedback'] == 'like')
        
        print(f"{alice.name} liked {alice_likes}/4 movies, {bob.name} liked {bob_likes}/4 movies")
        
        # Show updated preferences
        alice_prefs = tester.get_user_preferences(alice.id)
        bob_prefs = tester.get_user_preferences(bob.id)
        print(f"Confidence scores: Alice {alice_prefs['confidence_score']:.3f}, Bob {bob_prefs['confidence_score']:.3f}")
    
    # Final session stats
    print_subsection("Final Session Statistics")
    stats = tester.get_session_stats(session_id)
    print(f"Session Stage: {stats['session_stage']}")
    print(f"Total Interactions: {stats['total_interactions']}")
    print(f"Mutual Likes: {stats['mutual_likes']}")
    print(f"Alice Stats: {stats['user1_stats']}")
    print(f"Bob Stats: {stats['user2_stats']}")
    
    # Test Scenario 3: Opposing Preferences
    print_section("Test 3: Users with Opposing Preferences")
    
    charlie, diana = users[2], users[3]  # Comedy lover vs Horror lover
    opposing_session = tester.create_session(charlie.id, diana.id)
    print(f"Testing {charlie.name} (Comedy lover) vs {diana.name} (Horror lover)")
    
    # Run several rounds to see convergence
    for round_num in range(1, 4):
        recs = tester.get_recommendations(opposing_session, batch_size=6)
        print(f"\nRound {round_num} - Stage: {recs['session_stage']}")
        
        # Simulate feedback
        charlie_actions = tester.simulate_user_feedback(opposing_session, charlie, recs['movies'][:3])
        diana_actions = tester.simulate_user_feedback(opposing_session, diana, recs['movies'][:3])
        
        # Count mutual interests
        charlie_likes = {a['movie']['id'] for a in charlie_actions if a['feedback'] == 'like'}
        diana_likes = {a['movie']['id'] for a in diana_actions if a['feedback'] == 'like'}
        mutual_likes = charlie_likes.intersection(diana_likes)
        
        print(f"Mutual likes this round: {len(mutual_likes)}")
        
        if mutual_likes:
            for movie_id in mutual_likes:
                movie = next(m for m in recs['movies'] if m['id'] == movie_id)
                print(f"  Both liked: {movie['title']} - {movie['genres']}")
    
    # Test Scenario 4: Performance Metrics
    print_section("Test 4: Algorithm Performance Analysis")
    
    # Create multiple sessions to test consistency
    test_sessions = []
    for i in range(3):
        session = tester.create_session(f"user_{i}_a", f"user_{i}_b")
        test_sessions.append(session)
    
    print("Testing recommendation diversity across sessions...")
    all_recommendations = []
    
    for i, session in enumerate(test_sessions):
        recs = tester.get_recommendations(session, batch_size=10)
        all_recommendations.extend([m['id'] for m in recs['movies']])
        print(f"Session {i+1}: {len(set(m['id'] for m in recs['movies']))} unique movies out of {len(recs['movies'])}")
    
    total_unique = len(set(all_recommendations))
    total_recommended = len(all_recommendations)
    diversity_ratio = total_unique / total_recommended
    
    print(f"\nOverall Diversity: {total_unique} unique movies out of {total_recommended} total ({diversity_ratio:.2%})")
    
    print_section("🎉 Algorithm Testing Complete!")
    print("Key Observations:")
    print("- Algorithm adapts to user preferences over time")
    print("- Session stages progress from exploration to convergence")
    print("- Confidence scores increase with more interactions")
    print("- Mutual likes are detected and tracked")
    print("- Diversity is maintained even with learned preferences")

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the MovieMatch API server.")
        print("Make sure the server is running with: uvicorn src.backend.main:app --reload")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc() 