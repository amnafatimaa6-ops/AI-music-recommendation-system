import pandas as pd
import numpy as np
import pickle
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

df = pd.read_csv("music_df.csv")
text_embeddings = pickle.load(open("text_embeddings.pkl", "rb"))

model = SentenceTransformer('all-MiniLM-L6-v2')

MOOD_MAP = {
    "sad": "melancholy emotional slow acoustic heartbreak piano",
    "happy": "joyful energetic upbeat dance fun positive",
    "chill": "calm relaxed lo-fi ambient soft peaceful",
    "energetic": "high energy fast hype workout intense bass"
}

# -------------------------
# SMART EXPANSION ENGINE
# -------------------------
def expand_query(query, mode):

    if mode == "artist":
        return query + " similar artists songs albums music"

    if mode == "genre":
        return query + " top artists songs albums playlist"

    return MOOD_MAP.get(query.lower(), query)

# -------------------------
# FINAL RECOMMENDER
# -------------------------
def search_music(query, mode="mood", top_n=10):

    expanded_query = expand_query(query, mode)

    query_vec = model.encode([expanded_query])
    sim = cosine_similarity(query_vec, text_embeddings)[0]

    audio_boost = df['mood_score'].values

    final_score = 0.7 * sim + 0.3 * audio_boost

    top_idx = final_score.argsort()[::-1]

    results = []

    seen_artists = set()
    seen_genres = set()

    for i in top_idx:

        artist = df.iloc[i]['track_artist']
        genre = df.iloc[i]['playlist_genre']

        # REMOVE DUPLICATES
        if artist in seen_artists:
            continue

        seen_artists.add(artist)
        seen_genres.add(genre)

        results.append({
            "song": artist,
            "genre": genre,
            "score": round(float(final_score[i]), 3)
        })

        if len(results) == top_n:
            break

    return results
