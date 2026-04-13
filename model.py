import pandas as pd
import numpy as np
import pickle
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# ----------------------
# LOAD DATA
# ----------------------
df = pd.read_csv("music_df.csv")

text_embeddings = pickle.load(open("text_embeddings.pkl", "rb"))
audio_matrix = np.load("audio_matrix.npy")

# ----------------------
# TRANSFORMER MODEL
# ----------------------
model = SentenceTransformer('all-MiniLM-L6-v2')

# ----------------------
# SIMILARITY MATRIX
# ----------------------
text_similarity = cosine_similarity(text_embeddings)
audio_similarity = cosine_similarity(audio_matrix)

final_similarity = (0.65 * text_similarity) + (0.35 * audio_similarity)

# ----------------------
# RECOMMEND FUNCTION (NO DUPLICATES)
# ----------------------
def search_by_mood(query, top_n=10):
    query_vec = model.encode([query])
    sim = cosine_similarity(query_vec, text_embeddings)[0]

    top_idx = sim.argsort()[::-1]

    results = []
    seen_artists = set()

    for i in top_idx:
        artist = df.iloc[i]['track_artist']

        if artist in seen_artists:
            continue

        seen_artists.add(artist)

        results.append({
            "song": artist,
            "genre": df.iloc[i]['playlist_genre'],
            "score": round(sim[i], 3)
        })

        if len(results) == top_n:
            break

    return results
