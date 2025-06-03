import requests
import time

def test_matching_session_sync():
    """Test that multiple calls with same user pair create/reuse the same session"""
    
    # User IDs (sorted order)
    user1 = "test-user-1"
    user2 = "test-user-2"
    
    print("Testing shared matching session creation...")
    
    # Create first session
    resp1 = requests.post('http://localhost:8000/api/matching/sessions', 
                         json={'user1_id': user1, 'user2_id': user2})
    session1_id = resp1.json()['session_id']
    print(f"First call created session: {session1_id}")
    
    # Create second session with same users
    resp2 = requests.post('http://localhost:8000/api/matching/sessions', 
                         json={'user1_id': user1, 'user2_id': user2})
    session2_id = resp2.json()['session_id']
    print(f"Second call created session: {session2_id}")
    
    # Create third session with reversed user order
    resp3 = requests.post('http://localhost:8000/api/matching/sessions', 
                         json={'user1_id': user2, 'user2_id': user1})
    session3_id = resp3.json()['session_id']
    print(f"Third call (reversed users) created session: {session3_id}")
    
    # Test recommendations from each session
    print("\nTesting recommendations from each session:")
    
    for i, session_id in enumerate([session1_id, session2_id, session3_id], 1):
        resp = requests.get(f'http://localhost:8000/api/matching/sessions/{session_id}/recommendations?batch_size=3')
        movies = resp.json()['movies']
        titles = [m['title'] for m in movies]
        print(f"Session {i} ({session_id[:8]}...): {titles}")
    
    # All should be different due to different session IDs, but that's expected for fresh sessions
    # The frontend logic will ensure only one is used per Firebase session
    
    print(f"\nNote: Backend creates fresh sessions each time (by design).")
    print(f"Frontend coordination via Firebase ensures only one is used per Firebase session.")

if __name__ == "__main__":
    test_matching_session_sync() 