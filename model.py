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
# MOOD MAP
# -------------------------
MOOD_MAP = {
    "sad": "melancholy emotional slow acoustic heartbreak piano soft",
    "happy": "joyful energetic upbeat dance fun positive bright",
    "chill": "calm relaxed lo-fi ambient soft peaceful study sleep",
    "energetic": "high energy fast hype workout intense bass aggressive"
}

# -------------------------
# QUERY EXPANSION
# -------------------------
def expand_query(query, mode):

    if mode == "artist":
        return query + " similar artists songs albums music"

    if mode == "genre":
        return query + " top songs playlist hits artists"

    return MOOD_MAP.get(query.lower(), query)

# -------------------------
# ARTIST POOL EXPANSION
# -------------------------
def get_artist_pool(selected_artist):

    genres = df[df['track_artist'] == selected_artist]['playlist_genre'].unique()
    return df[df['playlist_genre'].isin(genres)]

# -------------------------
# FINAL RECOMMENDER ENGINE
# -------------------------
def search_music(query, mode="mood", top_n=10):

    expanded_query = expand_query(query, mode)

    query_vec = model.encode([expanded_query])
    sim = cosine_similarity(query_vec, text_embeddings)[0]

    audio_boost = df['mood_score'].values

    # MAIN SCORING
    final_score = 0.7 * sim + 0.3 * audio_boost

    # -------------------------
    # SMART POOL
    # -------------------------
    if mode == "artist":
        pool = get_artist_pool(query)
        idxs = pool.index
    else:
        idxs = np.arange(len(df))

    ranked = sorted(idxs, key=lambda i: final_score[i], reverse=True)

    results = []

    seen_artists = set()
    seen_genres = set()

    for i in ranked:

        artist = df.iloc[i]['track_artist']
        genre = df.iloc[i]['playlist_genre']

        # -------------------------
        # DIVERSITY CONTROL
        # -------------------------
        if artist in seen_artists:
            continue

        if len(seen_genres) >= 2 and genre in seen_genres:
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
