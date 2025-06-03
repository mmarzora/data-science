import requests
import time

# Create session
resp = requests.post('http://localhost:8000/api/matching/sessions', 
                    json={'user1_id': 'convergence-test-1', 'user2_id': 'convergence-test-2'})
session_id = resp.json()['session_id']
print(f'Session: {session_id}')

# Submit 35 feedback items to reach convergence
print('Submitting 35 interactions...')
for i in range(35):
    user_id = 'convergence-test-1' if i % 2 == 0 else 'convergence-test-2'
    movie_id = 100 + i
    feedback_type = 'like' if i % 3 != 2 else 'skip'  # Mix of likes and skips
    
    resp = requests.post(f'http://localhost:8000/api/matching/sessions/{session_id}/feedback',
                 json={'user_id': user_id, 'movie_id': movie_id, 'feedback_type': feedback_type})
    
    if i % 10 == 9:
        print(f'  Completed {i+1} interactions')

# Test convergence recommendations
print('\nConvergence recommendations:')
resp = requests.get(f'http://localhost:8000/api/matching/sessions/{session_id}/recommendations?batch_size=5')
data = resp.json()
print(f'Stage: {data["session_stage"]}')
print(f'Interactions: {data["total_interactions"]}')
print('Movies:')
for movie in data['movies'][:3]:
    print(f'  - {movie["title"]} ({movie["genres"]})')

# Test both users get same movies in convergence
print('\nTesting if both users get same recommendations in convergence:')
user1_movies = requests.get(f'http://localhost:8000/api/matching/sessions/{session_id}/recommendations?batch_size=5').json()['movies']
user2_movies = requests.get(f'http://localhost:8000/api/matching/sessions/{session_id}/recommendations?batch_size=5').json()['movies']

user1_titles = [m['title'] for m in user1_movies[:3]]
user2_titles = [m['title'] for m in user2_movies[:3]]

print(f'User 1: {user1_titles}')
print(f'User 2: {user2_titles}')
print(f'Same movies: {user1_titles == user2_titles}') 