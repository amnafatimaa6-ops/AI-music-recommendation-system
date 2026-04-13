import pandas as pd
import numpy as np
import pickle
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# -------------------------
# LOAD DATA
# -------------------------
df = pd.read_csv("music_df.csv")

text_embeddings = pickle.load(open("text_embeddings.pkl", "rb"))
audio_matrix = np.load("audio_matrix.npy")

audio_features = [
    'energy','danceability','valence',
    'tempo','loudness','speechiness',
    'mood_score','intensity','dance_index','rap_score'
]

# -------------------------
# MODEL (Transformer)
# -------------------------
model = SentenceTransformer('all-MiniLM-L6-v2')

# -------------------------
# SIMILARITY
# -------------------------
text_similarity = cosine_similarity(text_embeddings)
audio_similarity = cosine_similarity(audio_matrix)

final_similarity = (0.65 * text_similarity) + (0.35 * audio_similarity)

# -------------------------
# RECOMMENDER
# -------------------------
def recommend(song_index, top_n=10):
    scores = list(enumerate(final_similarity[song_index]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)

    results = []
    for i, score in scores[1:top_n+1]:
        results.append({
            "song": df.iloc[i]['track_artist'],
            "genre": df.iloc[i]['playlist_genre'],
            "score": round(score, 3)
        })

    return results

# -------------------------
# NLP SEARCH (TRANSFORMER)
# -------------------------
def search_by_mood(query, top_n=10):
    query_vec = model.encode([query])
    sim = cosine_similarity(query_vec, text_embeddings)[0]

    top_idx = sim.argsort()[-top_n:][::-1]

    results = []
    for i in top_idx:
        results.append({
            "song": df.iloc[i]['track_artist'],
            "genre": df.iloc[i]['playlist_genre'],
            "score": round(sim[i], 3)
        })

    return results
