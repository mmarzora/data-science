import sqlite3
import numpy as np
import sys
from scipy.spatial.distance import cosine

DB_PATH = '../moviematch/backend/src/database/movies.db'

def get_actor_embedding(conn, name):
    cur = conn.cursor()
    cur.execute('SELECT id, name, embedding FROM actors WHERE name = ?', (name,))
    row = cur.fetchone()
    if row is None:
        return None, None, None
    emb = np.frombuffer(row[2], dtype=np.float32)
    return row[0], row[1], emb

def get_all_actors(conn):
    cur = conn.cursor()
    cur.execute('SELECT id, name, embedding FROM actors')
    rows = cur.fetchall()
    actors = []
    for row in rows:
        emb = np.frombuffer(row[2], dtype=np.float32)
        actors.append((row[0], row[1], emb))
    return actors

def find_most_similar(actor_name):
    conn = sqlite3.connect(DB_PATH)
    try:
        actor_id, name, emb = get_actor_embedding(conn, actor_name)
        if emb is None:
            print(f'Actor "{actor_name}" not found in database.')
            return
        all_actors = get_all_actors(conn)
        best_sim = -1
        best_actor = None
        for other_id, other_name, other_emb in all_actors:
            if other_id == actor_id:
                continue
            sim = 1 - cosine(emb, other_emb)
            print(sim)
            if sim > best_sim:
                best_sim = sim
                best_actor = (other_id, other_name, sim)
        if best_actor:
            print(f'Most similar actor to "{actor_name}" is "{best_actor[1]}" (ID: {best_actor[0]}) with similarity {best_actor[2]:.4f}')
        else:
            print('No other actors found in database.')
    finally:
        conn.close()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python actor_similarity.py "Actor Name"')
        sys.exit(1)
    actor_name = sys.argv[1]
    find_most_similar(actor_name) 