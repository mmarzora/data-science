#!/usr/bin/env python3

import requests
import random
import json
from typing import Dict, List, Optional

class TestUser:
    """Test user with preferences."""
    def __init__(self, user_id: str, name: str, preferred_genres: List[str], disliked_genres: List[str]):
        self.id = user_id
        self.name = name
        self.preferred_genres = preferred_genres
        self.disliked_genres = disliked_genres

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
    
    def get_recommendations(self, session_id: str, user_id: str, batch_size: int = 10) -> Dict:
        """Get movie recommendations for a session and specific user."""
        response = self.session.get(
            f"{self.base_url}/api/matching/sessions/{session_id}/recommendations",
            params={"batch_size": batch_size, "user_id": user_id}
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
    
    def simulate_user_swipe(self, session_id: str, user: TestUser, movie: Dict) -> Dict:
        """Simulate a single user swipe based on preferences."""
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
        
        # Submit feedback
        self.submit_feedback(session_id, user.id, movie['id'], feedback, time_spent)
        
        return {
            "movie": movie,
            "feedback": feedback,
            "time_spent_ms": time_spent
        }

def analyze_batch_composition(movies: List[Dict], batch_size: int, exploration_rate: float = 0.25) -> Dict:
    """Analyze which movies are likely exploitation vs exploration."""
    exploration_count = int(batch_size * exploration_rate)
    exploitation_count = batch_size - exploration_count
    
    return {
        "total_movies": len(movies),
        "exploitation_movies": movies[:exploitation_count],
        "exploration_movies": movies[exploitation_count:] if len(movies) > exploitation_count else [],
        "exploitation_count": exploitation_count,
        "exploration_count": exploration_count
    }

def print_movie_info(movie: Dict, index: int, movie_type: str = "") -> None:
    """Print formatted movie information."""
    genres_str = ", ".join(movie.get('genres', []))
    type_prefix = f"[{movie_type}] " if movie_type else ""
    print(f"  {index+1:2d}. {type_prefix}{movie['title']} ({movie['release_year']}) - {genres_str} - Rating: {movie['rating']}")

def main():
    """Test 2 users swiping 10 times each and analyze movie distribution."""
    print("🎬 Testing User Swipe Distribution")
    print("=" * 50)
    
    # Initialize tester
    tester = MovieMatchTester()
    
    # Define test users with different preferences
    alice = TestUser("alice", "Alice", ["Drama", "Romance", "Comedy"], ["Horror", "Action"])
    bob = TestUser("bob", "Bob", ["Action", "Thriller", "Adventure"], ["Romance", "Musical"])
    
    print(f"👥 Users:")
    print(f"   Alice likes: {', '.join(alice.preferred_genres)} | dislikes: {', '.join(alice.disliked_genres)}")
    print(f"   Bob likes: {', '.join(bob.preferred_genres)} | dislikes: {', '.join(bob.disliked_genres)}")
    print()
    
    # Create session
    print("🚀 Creating session...")
    session_id = tester.create_session(alice.id, bob.id)
    print(f"   Session ID: {session_id}")
    print()
    
    # Test each user getting recommendations and swiping
    for user in [alice, bob]:
        print(f"🎯 Testing {user.name}'s recommendations:")
        print("-" * 30)
        
        # Get recommendations for this user
        try:
            batch_size = 10
            recommendations = tester.get_recommendations(session_id, user.id, batch_size)
            movies = recommendations['movies']
            
            print(f"   Session Stage: {recommendations.get('session_stage', 'unknown')}")
            print(f"   Total Interactions: {recommendations.get('total_interactions', 0)}")
            print(f"   Batch Size: {len(movies)}")
            print()
            
            # Analyze batch composition
            analysis = analyze_batch_composition(movies, batch_size)
            
            print(f"   📊 Batch Analysis:")
            print(f"      Exploitation movies (top-scoring): {analysis['exploitation_count']}")
            print(f"      Exploration movies (random): {analysis['exploration_count']}")
            print()
            
            print(f"   🎬 Movies {user.name} will see (in order):")
            
            # Show exploitation movies
            if analysis['exploitation_movies']:
                print("      📈 Exploitation (Top-scoring) Movies:")
                for i, movie in enumerate(analysis['exploitation_movies']):
                    print_movie_info(movie, i, "TOP")
            
            # Show exploration movies
            if analysis['exploration_movies']:
                print("      🎲 Exploration (Random) Movies:")
                for i, movie in enumerate(analysis['exploration_movies']):
                    print_movie_info(movie, i + len(analysis['exploitation_movies']), "RAND")
            
            print()
            
            # Simulate user swiping through first 10 movies
            print(f"   🎮 Simulating {user.name}'s 10 swipes:")
            swipe_results = []
            
            for i, movie in enumerate(movies[:10]):  # User sees first 10 in order
                result = tester.simulate_user_swipe(session_id, user, movie)
                swipe_results.append(result)
                
                # Determine if this was exploitation or exploration
                movie_type = "TOP" if i < analysis['exploitation_count'] else "RAND"
                reaction_emoji = "👍" if result['feedback'] == 'like' else "👎" if result['feedback'] == 'dislike' else "⏭️"
                
                print(f"      {i+1:2d}. [{movie_type}] {movie['title']} → {reaction_emoji} {result['feedback'].upper()} ({result['time_spent_ms']}ms)")
            
            # Summary
            likes = sum(1 for r in swipe_results if r['feedback'] == 'like')
            dislikes = sum(1 for r in swipe_results if r['feedback'] == 'dislike')
            skips = sum(1 for r in swipe_results if r['feedback'] == 'skip')
            
            exploitation_swipes = min(10, analysis['exploitation_count'])
            exploration_swipes = max(0, 10 - analysis['exploitation_count'])
            
            print(f"   📈 {user.name}'s Summary:")
            print(f"      Total swipes: 10")
            print(f"      Exploitation movies seen: {exploitation_swipes}")
            print(f"      Exploration movies seen: {exploration_swipes}")
            print(f"      Reactions: {likes} likes, {dislikes} dislikes, {skips} skips")
            print()
            
        except Exception as e:
            print(f"   ❌ Error getting recommendations for {user.name}: {e}")
            print()
            continue
    
    print("🎉 Test Complete!")
    print("\n💡 Key Insights:")
    print("   - Users see movies in the exact order returned by the backend")
    print("   - Exploitation movies (top-scoring) come first in the batch")
    print("   - Exploration movies (random) come at the end")
    print("   - If users don't swipe through the entire batch, they may miss exploration movies")
    print("   - Each user gets personalized recommendations based on their feedback history")

if __name__ == "__main__":
    main() 