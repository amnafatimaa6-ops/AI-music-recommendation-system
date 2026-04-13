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

# -------------------------
# TRANSFORMER MODEL
# -------------------------
model = SentenceTransformer('all-MiniLM-L6-v2')

# -------------------------
# MOOD INTELLIGENCE LAYER
# -------------------------
MOOD_MAP = {
    "sad": "melancholy emotional slow soft acoustic heartbreak lonely piano",
    "happy": "joyful energetic upbeat dance party fun positive festival bright",
    "chill": "calm relaxed soft lo-fi smooth peaceful ambient sleep study",
    "energetic": "high energy fast aggressive workout hype intense powerful bass"
}

# -------------------------
# SEARCH FUNCTION (IMPROVED)
# -------------------------
def search_by_mood(query, top_n=10):

    expanded_query = MOOD_MAP.get(query.lower(), query)

    query_vec = model.encode([expanded_query])
    sim = cosine_similarity(query_vec, text_embeddings)[0]

    # audio boost (important improvement)
    audio_boost = df['mood_score'].values

    final_score = sim + (0.2 * audio_boost)

    top_idx = final_score.argsort()[::-1]

    results = []
    seen_artists = set()

    for i in top_idx:
        artist = df.iloc[i]['track_artist']

        # remove duplicates
        if artist in seen_artists:
            continue

        seen_artists.add(artist)

        results.append({
            "song": artist,
            "genre": df.iloc[i]['playlist_genre'],
            "score": round(float(final_score[i]), 3)
        })

        if len(results) == top_n:
            break

    return results
