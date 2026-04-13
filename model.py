import pandas as pd
import numpy as np
import pickle
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from collections import Counter

# -------------------------
# LOAD DATA
# -------------------------
df = pd.read_csv("music_df.csv")
text_embeddings = pickle.load(open("text_embeddings.pkl", "rb"))

# -------------------------
# TRANSFORMER
# -------------------------
model = SentenceTransformer('all-MiniLM-L6-v2')

# -------------------------
# MOOD MAP
# -------------------------
MOOD_MAP = {
    "sad": "melancholy emotional slow acoustic heartbreak piano soft",
    "happy": "joyful energetic upbeat dance fun positive bright",
    "chill": "calm relaxed lo-fi ambient soft peaceful study sleep",
    "energetic": "high energy fast hype workout intense bass aggressive"
}

# -------------------------
# EXPAND QUERY
# -------------------------
def expand_query(query, mode):

    if mode == "artist":
        return query + " similar artists songs albums music"

    if mode == "genre":
        return query + " top songs playlist hits artists"

    return MOOD_MAP.get(query.lower(), query)

# -------------------------
# ARTIST EXPANSION
# -------------------------
def get_artist_pool(selected_artist):
    genres = df[df['track_artist'] == selected_artist]['playlist_genre'].unique()
    return df[df['playlist_genre'].isin(genres)]

# -------------------------
# FINAL RECOMMENDER (FIXED VERSION)
# -------------------------
def search_music(query, mode="mood", top_n=10):

    expanded_query = expand_query(query, mode)

    query_vec = model.encode([expanded_query])
    sim = cosine_similarity(query_vec, text_embeddings)[0]

    audio_boost = df['mood_score'].values

    # -------------------------
    # BASE SCORE
    # -------------------------
    final_score = 0.55 * sim + 0.25 * audio_boost

    # -------------------------
    # SMART POOL
    # -------------------------
    if mode == "artist":
        pool = get_artist_pool(query)
        idxs = pool.index
    else:
        idxs = np.arange(len(df))

    ranked = sorted(idxs, key=lambda i: final_score[i], reverse=True)

    # -------------------------
    # DIVERSITY CONTROL
    # -------------------------
    results = []
    seen_artists = set()
    genre_counts = Counter()

    for i in ranked:

        artist = df.iloc[i]['track_artist']
        genre = df.iloc[i]['playlist_genre']

        # avoid duplicates
        if artist in seen_artists:
            continue

        # genre penalty (ANTI CLUSTERING FIX)
        penalty = genre_counts[genre] * 0.05
        score = final_score[i] - penalty

        seen_artists.add(artist)
        genre_counts[genre] += 1

        results.append({
            "song": artist,
            "genre": genre,
            "score": round(float(score), 3)
        })

        if len(results) == top_n:
            break

    return results
