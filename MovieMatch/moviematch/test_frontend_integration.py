#!/usr/bin/env python3
"""
Test script to verify frontend-backend integration is working
"""

import requests
import json
import time

def test_backend_endpoints():
    """Test all backend endpoints that the frontend will use"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Frontend-Backend Integration...")
    print("=" * 50)
    
    # Test 1: Health Check
    print("1. Testing Health Check...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Health check passed: {data}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return False
    
    # Test 2: Create Session
    print("\n2. Testing Session Creation...")
    try:
        session_data = {
            "user1_id": "test_user_1",
            "user2_id": "test_user_2"
        }
        response = requests.post(f"{base_url}/api/matching/sessions", json=session_data)
        if response.status_code == 200:
            session_result = response.json()
            session_id = session_result["session_id"]
            print(f"   ✅ Session created: {session_id}")
        else:
            print(f"   ❌ Session creation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Session creation error: {e}")
        return False
    
    # Test 3: Get Recommendations
    print("\n3. Testing Recommendations...")
    try:
        response = requests.get(f"{base_url}/api/matching/sessions/{session_id}/recommendations?batch_size=5")
        if response.status_code == 200:
            recs = response.json()
            print(f"   ✅ Got {len(recs['movies'])} recommendations")
            print(f"   📊 Session stage: {recs['session_stage']}")
            print(f"   🎯 Total interactions: {recs['total_interactions']}")
        else:
            print(f"   ❌ Recommendations failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Recommendations error: {e}")
        return False
    
    # Test 4: Submit Feedback
    print("\n4. Testing Feedback Submission...")
    try:
        feedback_data = {
            "user_id": "test_user_1",
            "movie_id": recs['movies'][0]['id'],
            "feedback_type": "like",
            "time_spent_ms": 5000
        }
        response = requests.post(f"{base_url}/api/matching/sessions/{session_id}/feedback", json=feedback_data)
        if response.status_code == 200:
            feedback_result = response.json()
            print(f"   ✅ Feedback submitted: {feedback_result['message']}")
        else:
            print(f"   ❌ Feedback failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Feedback error: {e}")
        return False
    
    # Test 5: Get User Preferences
    print("\n5. Testing User Preferences...")
    try:
        response = requests.get(f"{base_url}/api/matching/users/test_user_1/preferences")
        if response.status_code == 200:
            prefs = response.json()
            print(f"   ✅ User preferences retrieved")
            print(f"   🎭 Total interactions: {prefs['total_interactions']}")
            print(f"   📈 Confidence score: {prefs['confidence_score']:.2f}")
        else:
            print(f"   ❌ User preferences failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ User preferences error: {e}")
        return False
    
    # Test 6: Get Session Stats
    print("\n6. Testing Session Statistics...")
    try:
        response = requests.get(f"{base_url}/api/matching/sessions/{session_id}/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"   ✅ Session stats retrieved")
            print(f"   📊 Session stage: {stats['session_stage']}")
            print(f"   🎯 Total interactions: {stats['total_interactions']}")
        else:
            print(f"   ❌ Session stats failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Session stats error: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All frontend integration tests passed!")
    print(f"🌐 Frontend: http://localhost:3000")
    print(f"🚀 Backend: http://localhost:8000")
    print("\n📋 Next Steps:")
    print("1. Open http://localhost:3000 in your browser")
    print("2. Create a session and enable smart matching")
    print("3. Watch the algorithm learn your preferences!")
    
    return True

def test_frontend_accessibility():
    """Test if frontend is accessible"""
    print("\n🌐 Testing Frontend Accessibility...")
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("   ✅ Frontend is accessible")
            return True
        else:
            print(f"   ❌ Frontend returned: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Frontend not accessible: {e}")
        return False

if __name__ == "__main__":
    # Test frontend accessibility
    frontend_ok = test_frontend_accessibility()
    
    # Test backend integration
    backend_ok = test_backend_endpoints()
    
    if frontend_ok and backend_ok:
        print("\n🚀 Integration is ready! Open http://localhost:3000 to try it out!")
    else:
        print("\n❌ Some tests failed. Check the services are running properly.") 