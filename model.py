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
# MOOD MAP (INTELLIGENCE LAYER)
# -------------------------
MOOD_MAP = {
    "sad": "melancholy emotional slow acoustic heartbreak piano lonely soft",
    "happy": "joyful energetic upbeat dance party fun positive bright festival",
    "chill": "calm relaxed lo-fi ambient soft peaceful study sleep smooth",
    "energetic": "high energy fast aggressive workout hype intense powerful bass"
}

# -------------------------
# USER MEMORY (PERSONALIZATION)
# -------------------------
USER_PROFILE = {
    "fav_genres": {},
    "fav_artists": {}
}

def update_user_profile(genre, artist):
    USER_PROFILE["fav_genres"][genre] = USER_PROFILE["fav_genres"].get(genre, 0) + 1
    USER_PROFILE["fav_artists"][artist] = USER_PROFILE["fav_artists"].get(artist, 0) + 1

# -------------------------
# FINAL BOSS RECOMMENDER
# -------------------------
def search_by_mood(query, top_n=10):

    expanded_query = MOOD_MAP.get(query.lower(), query)

    query_vec = model.encode([expanded_query])
    sim = cosine_similarity(query_vec, text_embeddings)[0]

    audio_boost = df['mood_score'].values

    # FINAL SCORING SYSTEM
    final_score = (
        0.65 * sim +
        0.25 * audio_boost
    )

    top_idx = final_score.argsort()[::-1]

    results = []

    seen_artists = set()
    seen_genres = set()
    seen_tracks = set()

    for i in top_idx:

        artist = df.iloc[i]['track_artist']
        genre = df.iloc[i]['playlist_genre']

        track_id = f"{artist}_{genre}_{i}"

        # -------------------------
        # HARD DEDUPLICATION
        # -------------------------
        if artist in seen_artists:
            continue

        if track_id in seen_tracks:
            continue

        # -------------------------
        # DIVERSITY CONTROL
        # -------------------------
        if len(seen_genres) >= 2 and genre in seen_genres:
            continue

        # -------------------------
        # PERSONALIZATION BOOST
        # -------------------------
        genre_boost = 0.05 * USER_PROFILE["fav_genres"].get(genre, 0)
        artist_boost = 0.03 * USER_PROFILE["fav_artists"].get(artist, 0)

        score = final_score[i] + genre_boost + artist_boost

        seen_artists.add(artist)
        seen_genres.add(genre)
        seen_tracks.add(track_id)

        results.append({
            "song": artist,
            "genre": genre,
            "score": round(float(score), 3),
            "why": f"mood match + audio features + genre: {genre}"
        })

        if len(results) == top_n:
            break

    return results
