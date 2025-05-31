#!/usr/bin/env python3
"""
Quick test runner for MovieMatch Algorithm
"""

import subprocess
import sys
import requests
import time

def check_server():
    """Check if the backend server is running."""
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def run_basic_test():
    """Run a quick basic test."""
    print("🚀 Running basic algorithm test...")
    
    # Quick test
    try:
        response = requests.post(
            "http://localhost:8000/api/matching/sessions",
            json={"user1_id": "test1", "user2_id": "test2"}
        )
        session_id = response.json()["session_id"]
        print(f"✅ Session created: {session_id}")
        
        # Get recommendations
        recs = requests.get(f"http://localhost:8000/api/matching/sessions/{session_id}/recommendations")
        movies = recs.json()["movies"]
        print(f"✅ Got {len(movies)} recommendations")
        
        # Submit feedback
        feedback = requests.post(
            f"http://localhost:8000/api/matching/sessions/{session_id}/feedback",
            json={"user_id": "test1", "movie_id": movies[0]["id"], "feedback_type": "like"}
        )
        print("✅ Feedback processed successfully")
        
        return True
    except Exception as e:
        print(f"❌ Basic test failed: {e}")
        return False

def main():
    """Main test runner."""
    print("🎬 MovieMatch Algorithm Test Runner")
    print("=" * 40)
    
    # Check if server is running
    print("Checking server status...")
    if not check_server():
        print("❌ Server not running!")
        print("Please start the server first:")
        print("  cd moviematch")
        print("  uvicorn src.backend.main:app --reload")
        return
    
    print("✅ Server is running!")
    
    if len(sys.argv) > 1 and sys.argv[1] == "basic":
        # Run basic test
        success = run_basic_test()
        if success:
            print("\n🎉 Basic test passed! Algorithm is working.")
        else:
            print("\n❌ Basic test failed.")
        return
    
    # Run comprehensive tests
    print("\nRunning comprehensive algorithm tests...")
    print("This will take a few minutes...\n")
    
    try:
        subprocess.run([sys.executable, "test_algorithm.py"], check=True)
    except subprocess.CalledProcessError:
        print("❌ Tests failed!")
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")

if __name__ == "__main__":
    main() 